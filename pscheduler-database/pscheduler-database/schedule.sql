--
-- Functions that manage the schedule of runs
--

-- NOTE:  These functions implement a very simplistic first-come, first-served schedule.


-- Find a time for a soonest-start task to start.
-- TODO: Probably want to support bounding the time for <PT30M-type starts.
CREATE OR REPLACE FUNCTION schedule_soonest_available(
    duration INTERVAL,
    after TIMESTAMP WITH TIME ZONE DEFAULT now())
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
DECLARE
    last_end TIMESTAMP WITH TIME ZONE DEFAULT NULL;
    run_rec RECORD;
BEGIN
    -- Easy case: Nothing on the schedule right now.  This will also
    -- cover no runs being scheduled at all.

    IF NOT EXISTS (SELECT * FROM run
       	   	   WHERE times && tstzrange(after, after+duration, '[)')) THEN
       RETURN normalized_now();
    END IF;

    -- Examine the gaps between runs and see if there's enough space
    -- for the task.

    FOR run_rec IN (SELECT times FROM run ORDER BY times)
    LOOP
	IF last_end IS NULL THEN
	   last_end := upper(run_rec.times);
	   CONTINUE;
	END IF;

	IF (lower(run_rec.times) - last_end) >= duration THEN
	   RETURN last_end;
	END IF;
	last_end := upper(run_rec.times);
    END LOOP;

    -- If we got here, there was no suitable gap between scheduled
    -- runs.  Schedule after whatever we had for the last end time.
    RETURN last_end;

END;
$$ LANGUAGE plpgsql;


-- Reschedule a single task by its id
CREATE OR REPLACE FUNCTION schedule_reschedule(
       task_id BIGINT,
       earliest TIMESTAMP WITH TIME ZONE DEFAULT now())
RETURNS VOID
AS $$
DECLARE
   task_rec RECORD;
   starting_iteration NUMERIC;
   repeats_left NUMERIC DEFAULT NULL;
   stop_after TIMESTAMP WITH TIME ZONE;
   remaining_time_horizon INTERVAL;
BEGIN

     IF earliest < now() THEN
     	RAISE EXCEPTION 'Cannot reschedule runs that started in the past.';
     END IF;

     SELECT * INTO task_rec FROM task WHERE id = task_id;
     IF NOT FOUND THEN
     	RAISE EXCEPTION 'No task with ID %', task_id;
     END IF;

     earliest := normalized_time(earliest);

     -- We don't care about non-repeaters that have already been run.
     IF (task_rec.repeat IS NULL) AND (TASK_REC.repeats > 0) THEN
     	RETURN;
     END IF;

     -- Nothing can happen before the task starts.
     earliest := GREATEST(earliest, task_rec.start);

     -- Clear out old runs that haven't happened yet
     DELETE FROM run
     WHERE
	task = task_id
	AND lower(times) >= earliest;

     -- Figure out the time that the first run can be scheduled within
     -- our window.

     IF task_rec.repeat IS NOT NULL THEN
          starting_iteration := TRUNC(
     			EXTRACT(EPOCH FROM (earliest - task_rec.start)
		        / EXTRACT(EPOCH FROM task_rec.repeat)) );

	  earliest := earliest + (task_rec.repeat * starting_iteration);
     END IF;


     -- Figure out how far ahead in time we can schedule runs that
     -- don't go past the scheduling time horizon.
     stop_after := LEAST( task_rec.until, (normalized_now() + schedule_time_horizon()) )
     		   - task_rec.duration;

     -- Figure out how many runs we can schedule.
     IF task_rec.max_runs IS NOT NULL THEN
     	-- The easy case, when the task tells us.
     	repeats_left := task_rec.max_runs - task_rec.repeats;
     ELSE
	-- Now until the edge of the time horizon
	remaining_time_horizon := schedule_time_horizon() - (earliest - normalized_now());
	repeats_left := ROUND(EXTRACT(EPOCH FROM remaining_time_horizon)
		     / EXTRACT(EPOCH FROM task_rec.repeat));
     END IF;

     -- Adjust out anything on the schedule before our starting time
     repeats_left := repeats_left
     		  - run_runs_between(task_id, normalized_now(), earliest);

     -- Reschedule all runs

     -- TODO: Remove this.
     -- raise notice 'T% RL=%  Start @ %   Stop + %', task_id, repeats_left, earliest, stop_after;
     WHILE (repeats_left > 0) AND (earliest < stop_after)
     LOOP
	-- TODO: Remove this.
	--raise notice 'T% RL=%  SA=%', task_id, repeats_left, earliest;
	-- TODO: If this run would overlap, try to slip it.
	INSERT INTO run (task, times)
	VALUES (task_id, tstzrange(earliest, earliest + task_rec.duration, '[)'));
	repeats_left := repeats_left - 1;
	earliest := earliest + task_rec.repeat;
     END LOOP;

     NOTIFY schedule_change;
     RETURN;
END;
$$ LANGUAGE plpgsql;



-- Reschedule every task
CREATE OR REPLACE FUNCTION schedule_reschedule_all()
RETURNS VOID
AS $$
DECLARE
	task_rec RECORD;
BEGIN
	FOR task_rec IN SELECT id FROM task
	LOOP
		EXECUTE schedule_reschedule(task_rec.id);
	END LOOP;
END;
$$ LANGUAGE plpgsql;



-- What's coming on the schedule and what to execute

DROP VIEW IF EXISTS schedule_upcoming;
CREATE OR REPLACE VIEW schedule_upcoming
AS
    SELECT
      run.id AS run,
      lower(run.times) - normalized_wall_clock() AS start_in,
      tool.name AS tool,
      -- Note that these bits have to be done in pieces because PgSQL
      -- has no way to turn dates and intervals to ISO 8601.
      -- TODO: See if this is actually the case.
      task.participant AS participant,
      task.json #> '{test}' AS test,
      lower(run.times) AS start,
      task.duration AS duration
    FROM
        run
	JOIN task ON task.id = run.task
	JOIN tool ON tool.id = task.tool
    WHERE
        run.state = run_state_pending()
        AND lower(run.times) >= normalized_now()
    ORDER BY run.times;
;
