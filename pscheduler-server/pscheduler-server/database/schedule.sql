--
-- Functions that manage the schedule of runs
--


-- Schedule, for use by the REST API

DROP VIEW IF EXISTS schedule;
CREATE OR REPLACE VIEW schedule
AS
    SELECT
        run.times,
        task.uuid AS task,
        run.uuid AS run,
        run_state.enum AS state_enum,
        run_state.display AS state_display,
        -- TODO: Pull full JSON with details when that's available.  See #95.
        task.json AS task_json,
	FALSE AS remove_this
    FROM
        run
        JOIN run_state ON run_state.id = run.state
        JOIN task ON task.id = run.task
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

    WITH interim AS (

        -- Non-repeating tasks with no runs scheduled

        SELECT
            task.id AS task,
	    task.uuid,
            task.enabled,
            task.added,
            task.start,
            task.duration,
            now() AS after,
            task.repeat,
            task.max_runs,
	    0 AS scheduled,
            task.runs,
            task.until,
            greatest(normalized_now(), task.start) AS trynext,
	    task.participant,
            test.scheduling_class
        FROM
            task
            JOIN test ON test.id = task.test
        WHERE
	    repeat IS NULL
	    AND NOT EXISTS (SELECT * FROM run WHERE run.task = task.id)

        UNION

        -- Repeating tasks without runs

        SELECT
            task.id AS task,
            task.uuid,
            task.enabled,
            task.added,
            task.start,
            task.duration,
            greatest(task.start, now()) AS after,
	    task.repeat,
            task.max_runs,
	    0 AS scheduled,
            task.runs,
            task.until,
            greatest(task.start, normalized_now()) AS trynext,
            task.participant,
            test.scheduling_class
        FROM
            task
            JOIN test on test.id = task.test
        WHERE
	    repeat IS NOT NULL
            AND NOT EXISTS (SELECT * FROM run WHERE run.task = task.id)

	UNION
    
        -- Repeating tasks with runs

        SELECT
            task.id AS task,
	    task.uuid,
            task.enabled,
            task.added,
            task.start,
            duration,
            greatest(now(), task.start, max(upper(run.times))) AS after,
            task.repeat,
            max_runs,
	    (SELECT COUNT(*)
             FROM
                 run
                 JOIN test ON test.id = task.test
             WHERE
                 run.task = task.id
                 AND upper(times) > normalized_now()) AS scheduled,
            runs,
            task.until,
 	    task_next_run(coalesce(start, normalized_now()), 
                          greatest(normalized_now(), task.start, max(upper(run.times))),
                          repeat) AS trynext,
	    task.participant,
	    test.scheduling_class
        FROM
            run
            JOIN task ON task.id = run.task
            JOIN test ON test.id = task.test
	WHERE
	    task.repeat IS NOT NULL
        GROUP BY task.id, test.scheduling_class

    )
    SELECT
        task,
	uuid,
	runs,
        trynext
    FROM
        interim, 
        configurables
    WHERE
        enabled
	AND participant = 0
        AND ( (max_runs IS NULL)
              OR (runs + scheduled) < max_runs )
        AND ( (until IS NULL) OR (trynext < until) )
	-- Anything that fits the scheduling horizon or is a backgrounder
        AND (
            trynext + duration < (normalized_now() + schedule_horizon)
            OR scheduling_class = scheduling_class_background()
        )
    ORDER BY added
;






--
-- API
--


-- Come up with a list of proposed times to run a task that fall
-- within a given time range.  If the start of the range is NULL, the
-- current time will be used.  If the end is NULL, the start plus the
-- length of the configured schedule time horizon will be used.  Under
-- no circumstances will any times in the past or beyond the time
-- horizon be proposed.

CREATE OR REPLACE FUNCTION api_proposed_times(
    task_uuid UUID,
    range_start TIMESTAMP WITH TIME ZONE = normalized_now(),
    range_end TIMESTAMP WITH TIME ZONE = tstz_infinity()
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
    -- range is fair game.
    IF taskrec.anytime THEN
        RETURN QUERY
            SELECT range_start AS lower, range_end AS upper;
    END IF;


    -- Figure out the actual boundaries of where we can schedule and
    -- trim accordingly.

    time_now := normalized_now();
    SELECT INTO horizon_end time_now + schedule_horizon FROM configurables;

    IF range_end < time_now THEN
        -- Completely in the past means nothing schedulable at all.
        RETURN;
    END IF;

    -- This is partially correctable
    range_start := greatest(range_start, time_now);
    range_start := normalized_time(range_start);

    -- Can't schedule past the end of the time horizon, either.
    range_end := LEAST(range_end, horizon_end);
    range_end := normalized_time(range_end);


    -- Can't propose anything for ranges in the past or beyond the
    -- scheduling horizon.
    IF range_start > horizon_end OR range_end <= normalized_now() THEN
	RETURN;
    END IF;

    time_range := tstzrange(range_start, range_end, '[)');

    last_end := range_start;



    -- Sift through everything on the timeline that overlaps with the
    -- time range and find the gaps.  Other than non-starters, the
    -- runs we care about avoiding are represented by this truth
    -- table:
    --
    -- Proposed  ||   Run on Timeline  |
    -- Run       || Normal | Exclusive |
    -- ----------++--------+-----------+
    -- Normal    || Ignore |   Avoid   |
    -- Exclusive || Avoid  |   Avoid   |

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
            -- Ignore non-starters
            AND state <> run_state_nonstart()
            AND (
                -- Always avoid exclusive runs
                (scheduling_class.exclusive)
                -- Avoid normal runs if the proposed run is exclusive
                OR (taskrec.exclusive AND NOT scheduling_class.exclusive)
            )
        ORDER BY times
    LOOP

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

CREATE OR REPLACE FUNCTION schedule_maint_minute()
RETURNS VOID
AS $$
DECLARE
    older_than TIMESTAMP WITH TIME ZONE;
BEGIN

    SELECT INTO older_than normalized_now() - keep_runs_tasks
    FROM configurables;

    -- Get rid of runs that finished
    DELETE FROM run
    WHERE upper(times) < older_than
    ;


    -- Get rid of tasks that no longer have runs and can be considered
    -- completed.

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
