--
-- Functions that manage the schedule of runs
--


-- Schedule, for use by the REST API

DROP VIEW IF EXISTS schedule;
CREATE OR REPLACE VIEW schedule
AS
    SELECT
        run.times,
	run.priority,
        task.uuid AS task,
        run.uuid AS run,
        run_state.enum AS state_enum,
        run_state.display AS state_display,
	run.errors AS errors,
        -- TODO: Pull full JSON with details when that's available.  See #95.
        task.json AS task_json,
	task.cli AS task_cli,
	tool.json AS tool_json,
	test.json as test_json
    FROM
        run
        JOIN run_state ON run_state.id = run.state
        JOIN task ON task.id = run.task
	JOIN tool ON tool.id = task.tool
	JOIN test ON test.id = task.test
    ORDER BY run.times
;



-- What's coming on the schedule and what to execute

-- TODO: Can probably clean this up a bit since the runner won't be
-- using as much of it.

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
      run.part_data_full AS part_data_full,
      task.json #> '{test}' AS test,
      lower(run.times) AS start,
      task.duration AS duration,
      test.scheduling_class
    FROM
        run
	JOIN task ON task.id = run.task
	JOIN tool ON tool.id = task.tool
        JOIN test ON test.id = task.test
    WHERE
        run.state = run_state_pending()
        AND lower(run.times) >= normalized_now()
    ORDER BY run.times;
;



-- What tasks need a run scheduled and when.  This explicitly excludes
-- background tasks, which are handled separately.

DROP VIEW IF EXISTS schedule_runs_to_schedule;
CREATE OR REPLACE VIEW schedule_runs_to_schedule
AS

    -- TODO: Need to go through this and make sure the subqueries
    -- aren't selecting columns that aren't used.

    WITH interim AS (

        -- Non-repeating tasks with no runs scheduled

        SELECT
            task.id AS task,
	    task.uuid,
	    participant_key AS key,
            task.enabled,
            task.added,
            task.duration,
            task.slip,
            task.max_runs,
            task.runs,
            task.until,
            greatest(normalized_now(), task.start) AS trynext,
	    task.participant,
            test.scheduling_class,
	    task.json,
	    task.participants,
	    task.json -> 'debug' AS debug
        FROM
            task
            JOIN test ON test.id = task.test
        WHERE
	    repeat IS NULL
	    AND repeat_cron IS NULL
	    AND NOT EXISTS (SELECT * FROM run WHERE run.task = task.id)

        UNION ALL

        -- Interval-repeating tasks without runs

        SELECT
            task.id AS task,
            task.uuid,
	    participant_key AS key,
            task.enabled,
            task.added,
            task.duration,
            task.slip,
            task.max_runs,
            task.runs,
            task.until,
            greatest(task.start, normalized_now()) AS trynext,
            task.participant,
            test.scheduling_class,
	    task.json,
	    task.participants,
	    task.json -> 'debug' AS debug
        FROM
            task
            JOIN test on test.id = task.test
        WHERE
	    task.repeat IS NOT NULL
            AND (until IS NULL OR until > normalized_now())
	    AND runs = 0

	UNION ALL

        -- Interval-repeating tasks with runs

        SELECT
            task.id AS task,
            task.uuid,
	    participant_key AS key,
            task.enabled,
            task.added,
            duration,
            task.slip,
            task.max_runs,
            task.runs,
            task.until,
            task_next_run(task.first_start,
                         greatest(normalized_now(), task.start, run_latest.latest),
                         task.repeat, NULL) AS trynext,
            task.participant,
            (SELECT scheduling_class FROM test WHERE test.id = task.test) AS scheduling_class,
	    task.json,
	    task.participants,
	    task.json -> 'debug' AS debug
       FROM
            task
	    JOIN run_latest ON run_latest.task = task.id
        WHERE
            task.repeat IS NOT NULL
	    AND task.runs > 0
	    AND EXISTS (SELECT * FROM run WHERE run.task = task.id)

	UNION ALL

        -- Cron-repeating tasks with or without runs

        SELECT
            task.id AS task,
            task.uuid,
	    participant_key AS key,
            task.enabled,
            task.added,
            duration,
            task.slip,
            task.max_runs,
            task.runs,
            task.until,
            task_next_run(task.first_start,
                         greatest(
			     normalized_now(),
			     task.start,
			     task.first_start,
			     (SELECT latest FROM run_latest where task = task.id)
			 ),
                         NULL, task.repeat_cron) AS trynext,
            task.participant,
            (SELECT scheduling_class FROM test WHERE test.id = task.test) AS scheduling_class,
	    task.json,
	    task.participants,
	    task.json -> 'debug' AS debug
       FROM
            task
        WHERE
            task.repeat_cron IS NOT NULL
	    AND task.enabled

    )
    SELECT
        task,
	uuid,
	key,
	runs,
        trynext,
	slip,
	scheduling_class.anytime,
	json,
	participants,
	debug
    FROM
        interim
        JOIN scheduling_class
             ON scheduling_class.id = interim.scheduling_class,
        configurables
    WHERE
        enabled
	AND participant = 0
        AND ( (max_runs IS NULL) OR (runs < max_runs) )
        AND ( (until IS NULL) OR (trynext < until) )
	-- This grabs Anything that fits the scheduling horizon or
	-- runs background-multi.  Note that we adjust out anything
	-- where the amount of slip could put a run's start time over
	-- the edge of the horizon.  The horizon is far enough out
	-- that once the start time falls far enough that slip will
	-- work, the scheduler will pick it up in plenty of time.  See
	-- #1064 for the bug that brought this behavior about.
        AND (
            trynext < (
	        normalized_now()                   -- From now
		+ schedule_horizon                 -- To the horizon
		- COALESCE(slip, 'P0D'::INTERVAL)  -- Less any slip that might put us over
	    )
            OR scheduling_class = scheduling_class_background_multi()
        )
    ORDER BY trynext, added
;




-- Runs that overlap but shouldn't (for diagnostic use)
DROP VIEW IF EXISTS schedule_overlap;
CREATE OR REPLACE VIEW schedule_overlap
AS
    SELECT
        r1.id AS r1_id,
        r1.task AS r1_task,
        r2.id AS r2_id,
        r2.task AS r2_task,
        r1.times AS r1_times,
        r2.times AS r2_times
    FROM
        run_conflictable r1
        JOIN run_conflictable r2
            ON r2.id <> r1.id
            AND r1.times && r2.times
            AND r1.state <> run_state_nonstart()
            AND r2.state <> run_state_nonstart()
            AND r1.added < r2.added
        ORDER BY
          r1.times,
          r2.times
;



-- Return a schedule with bounded past and future window sizes, mostly
-- for use by the monitor.

DO $$ BEGIN PERFORM drop_function_all('schedule_monitor'); END $$;

CREATE OR REPLACE FUNCTION schedule_monitor(
    window_size INTEGER
)
RETURNS TABLE (
    ppf INTEGER,
    times TSTZRANGE,
    task UUID,
    run UUID,
    state_enum TEXT,
    state_display TEXT,
    task_json JSONB,
    task_cli JSON,
    priority INTEGER
)
AS $$
DECLARE
    normalized_time TIMESTAMP WITH TIME ZONE;
BEGIN

    normalized_time := normalized_now();

    RETURN QUERY

        SELECT

            CASE  -- Past/Present/Future
                WHEN upper(run.times) < normalized_time THEN -1
                WHEN lower(run.times) > normalized_time THEN 1
                ELSE 0
            END AS ppf,
            run.times,
            task.uuid,
            run.uuid,
            run_state.enum,
            run_state.display,
            task.json,
            task.cli,
            run.priority
        FROM
            run
            JOIN task on task.id = run.task
            JOIN run_state on run_state.id = run.state
        WHERE
            run.id IN (

                SELECT * FROM (
                    SELECT id FROM run
                    WHERE upper(run.times) < normalized_time
                    ORDER BY upper(run.times) DESC
                    LIMIT window_size
                ) past

                UNION ALL

                SELECT * FROM (
                    SELECT id FROM run
                    WHERE run.times @> normalized_time
                    ORDER BY run.times
                ) present

                UNION ALL

                SELECT * FROM (
                    SELECT id FROM run
                    WHERE
                        lower(run.times) > normalized_time
                        AND run.state IN (
			    run_state_pending(),
			    run_state_on_deck(),
			    run_state_nonstart()
			    )
                    ORDER BY lower(run.times)
                    LIMIT window_size
                ) future

            )
        ORDER BY ppf, times, task.added ASC
        ;

    RETURN;

END;
$$ LANGUAGE plpgsql;



--
-- API
--


-- Come up with a list of proposed times to run a task that fall
-- within a given time range.  If the start of the range is NULL, the
-- current time will be used.  If the end is NULL, the start plus the
-- length of the configured schedule time horizon will be used.  Under
-- no circumstances will any times in the past or beyond the time
-- horizon be proposed.

DO $$ BEGIN PERFORM drop_function_all('api_proposed_times'); END $$;

CREATE OR REPLACE FUNCTION api_proposed_times(
    task_uuid UUID,
    range_start TIMESTAMP WITH TIME ZONE = normalized_now(),
    range_end TIMESTAMP WITH TIME ZONE = tstz_infinity(),
    proposed_priority INTEGER = priority_min()
)
RETURNS TABLE (
    lower TIMESTAMP WITH TIME ZONE,
    upper TIMESTAMP WITH TIME ZONE
)
AS $$
DECLARE
    time_now TIMESTAMP WITH TIME ZONE;
    horizon_end TIMESTAMP WITH TIME ZONE;
    taskrec RECORD;
    time_range TSTZRANGE;
    last_end TIMESTAMP WITH TIME ZONE;
    run_record RECORD;
    use_priority INTEGER;
BEGIN

    -- Validate the input

    SELECT INTO taskrec
        task.*,
	test.scheduling_class,
        scheduling_class.anytime,
        scheduling_class.exclusive
    FROM
        task
        JOIN test ON test.id = task.test
        JOIN scheduling_class ON scheduling_class.id = test.scheduling_class
    WHERE
        uuid = task_uuid;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No task % exists', task_uuid;
    END IF;

    IF range_end < range_start THEN
        RAISE EXCEPTION 'Range start and end must be in the proper order';
    END IF;


    -- If the scheduling class for the task is background, the entire
    -- range is fair game and that's our final answer.
    IF taskrec.anytime THEN
        RETURN QUERY
            SELECT range_start AS lower, range_end AS upper;
        RETURN;
    END IF;


    -- Figure out the actual boundaries of where we can schedule and
    -- trim accordingly.

    time_now := normalized_now();
    SELECT INTO horizon_end time_now + schedule_horizon FROM configurables;

    -- Pass on ranges for which nothing can be scheduled
    IF 
        range_end <= time_now         -- Completely in the past
        OR range_start > horizon_end  -- Too far in the future
    THEN
        RETURN;
    END IF;


    -- Correct for the range start being earlier than now.  Don't
    -- bother proposing anything for a run_start_margin's worth of
    -- time, either.

    -- TODO: This might be more precicely accomplished by checking for
    -- tasks that would collide, but scheduling something so close to
    -- the present is relatively unlikely.

    range_start := greatest(range_start,
    		   	    time_now + (SELECT run_start_margin FROM configurables));
    range_start := normalized_time(range_start);

    -- Can't schedule past the end of the time horizon, either.
    range_end := LEAST(range_end, horizon_end);
    range_end := normalized_time(range_end);

    -- If the adjusted start overshoots the end, there's no time
    -- available.  Punt.
    IF range_start >= range_end THEN
        RETURN;
    END IF;

    time_range := tstzrange(range_start, range_end, '[)');

    last_end := range_start;


    -- Figure out what priority will be used.

    -- TODO: This and code in run.sql (~line 975) are almost close
    -- enough to merit writing a function to do this.

    use_priority := proposed_priority;
    IF use_priority IS NOT NULL
    THEN
        IF taskrec.priority IS NOT NULL
	THEN
	    -- No priority for the task means no priority for the run.
	    use_priority := NULL;
	ELSE	
	    -- Don't exceed the prioirity assigned to the task.
	    use_priority := LEAST(use_priority, taskrec.priority);
	END IF;
    END IF;


    -- Sift through everything on the timeline that overlaps with the
    -- time range and find the gaps.  Other than non-starters, the
    -- runs we care about avoiding are represented by this truth
    -- table:
    --
    -- Proposed  ||         Run on Timeline         |
    -- Run       || Background | Normal | Exclusive |
    -- ----------++------------+--------+-----------+
    -- Background|| Ignore     | Ignore |   Ignore  |
    -- Normal    || Ignore     | Ignore |   Avoid   |
    -- Exclusive || Ignore     | Avoid  |   Avoid   |

    -- TODO: Can this be selected out of run_conflictable?

    FOR run_record IN
        SELECT run.*
        FROM
            run
            JOIN task ON task.id = run.task
            JOIN test ON test.id = task.test
            JOIN scheduling_class
                 ON scheduling_class.id = test.scheduling_class
        WHERE
            -- Overlap
	    times && time_range
	    -- Higher priority than proposed or already running
	    AND ( run.priority >= use_priority
	          OR run.state = run_state_running() )
            -- Ignore non-starters
            AND state <> run_state_nonstart()
            -- Ignore background
            AND NOT scheduling_class.anytime
            AND (
                -- Always avoid exclusive runs
                (scheduling_class.exclusive)
                -- Avoid normal runs if the proposed run is exclusive
                OR (taskrec.exclusive AND NOT scheduling_class.exclusive)
            )
        ORDER BY times
    LOOP

        -- Clamp the end time to the horizon
        IF upper(run_record.times) > horizon_end
        THEN
            run_record.times = tstzrange( lower(run_record.times), horizon_end,
                '[)' );
        END IF;

        -- A run that starts beyond the last end implies a gap, but
        -- the gap must be longer than the duration of the task for it
        -- to one that can be proposed.
        IF lower(run_record.times) > last_end
           AND lower(run_record.times) - last_end >= taskrec.duration
        THEN
            RETURN QUERY
                SELECT last_end AS lower, lower(run_record.times) AS upper;
        END IF;

        last_end := upper(run_record.times);

    END LOOP;

    -- If the end of the last run is before the end of the range,
    -- that's also a gap.
    IF last_end < range_end
       AND range_end - last_end >= taskrec.duration
    THEN
        RETURN QUERY SELECT last_end, range_end;
    END IF;

    RETURN;

END;
$$ LANGUAGE plpgsql;



--
-- Maintenance
--

DO $$ BEGIN PERFORM drop_function_all('schedule_maint_minute'); END $$;

CREATE OR REPLACE FUNCTION schedule_maint_minute()
RETURNS VOID
AS $$
DECLARE
    older_than TIMESTAMP WITH TIME ZONE;
BEGIN

    SELECT INTO older_than normalized_now() - keep_runs_tasks
    FROM configurables;

    -- Get rid of tasks that no longer have runs and can be considered
    -- completed.  Note this this is done here and not task.sql
    -- because it depends on that table and run.

    DELETE FROM task
    WHERE
        NOT EXISTS (SELECT * FROM run where run.task = task.id)
        -- Use time added as a proxy for start time in non-repeaters
        AND COALESCE(start, added) < older_than
        AND (
            -- Complete based on runs
            (max_runs IS NOT NULL AND runs >= max_runs)
            -- One-shot
            OR repeat IS NULL
            )
    ;

END;
$$ LANGUAGE plpgsql;
