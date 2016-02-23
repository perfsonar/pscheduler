--
-- Functions that manage the schedule of runs
--



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
    task RECORD;
    time_range TSTZRANGE;
    last_end TIMESTAMP WITH TIME ZONE;
    run_record RECORD;
BEGIN

    -- Validate the input

    SELECT INTO task * FROM task WHERE uuid = task_uuid;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'No task % exists', task_uuid;
    END IF;

    IF range_end < range_start THEN
        RAISE EXCEPTION 'Range start and end must be in the proper order';
    END IF;


    -- Figure out the actual boundaries of where we can schedule and
    -- trim accordingly.

    time_now := normalized_now();
    horizon_end := time_now + schedule_time_horizon();

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

    FOR run_record IN
        SELECT * FROM run
        WHERE times && time_range
        ORDER BY times
    LOOP

        -- A run that starts beyond the last end implies a gap, but
        -- the gap must be longer than the duration of the task for it
        -- to one that can be proposed.
        IF lower(run_record.times) > last_end
           AND lower(run_record.times) - last_end >= task.duration
        THEN
            RETURN QUERY
                SELECT last_end AS lower, lower(run_record.times) AS UPPER;
        END IF;

        last_end := upper(run_record.times);

    END LOOP;

    -- If the end of the last run is before the end of the range,
    -- that's also a gap.
    IF last_end < range_end
       AND range_end - last_end >= task.duration
    THEN
        RETURN QUERY SELECT last_end, range_end;
    END IF;

    RETURN;

END;
$$ LANGUAGE plpgsql;
