--
-- Run Table
--

DROP TABLE IF EXISTS run CASCADE;
CREATE TABLE run (

	-- Row identifier
	-- TODO: Make this a UUID in the future?
	id		BIGSERIAL
			PRIMARY KEY,

	-- External-use identifier
	uuid		UUID
			UNIQUE
			DEFAULT gen_random_uuid(),

	-- Task this run belongs to
	task		BIGINT
			REFERENCES task(id)
			ON DELETE CASCADE,

	-- Range of times when this task will be run
	times		TSTZRANGE
			NOT NULL,

	-- State of this run (see run_state table)
	state	    	 INTEGER DEFAULT run_state_pending()
			 REFERENCES run_state(id),


	-- How it went locally
	status	    	 INTEGER
);


-- This should be used when someone looks up the external ID.  Bring
-- the row ID a long so it can be pulled without having to consult the
-- table.
CREATE INDEX run_uuid
ON task(uuid, id);


-- GIST accelerates range-specific operators like &&
CREATE INDEX run_times ON run USING GIST (times);
CREATE INDEX run_times_lower ON run(lower(times), state);



CREATE OR REPLACE FUNCTION run_alter()
RETURNS TRIGGER
AS $$
BEGIN

    -- Disallow overlap
    -- TODO: Remove this when the scheduler can decide which run runs

    IF ( (TG_OP = 'INSERT')
         AND (EXISTS (SELECT * FROM run WHERE run.times && NEW.times)) )
       OR ( (TG_OP = 'UPDATE')
            AND (NEW.times != OLD.times)
            AND (EXISTS (SELECT * FROM run WHERE id != NEW.id AND run.times && NEW.times)) )
    THEN
       RAISE EXCEPTION 'Runs may not overlap.';
    END IF;

    -- Change the state automatically if the status from the run
    -- changes.

    IF (TG_OP = 'UPDATE') THEN

        IF (NEW.status IS NOT NULL) THEN

            IF lower(NEW.times) > normalized_now() THEN
  	        RAISE EXCEPTION 'Cannot set status on future tasks.';
	    END IF;

            NEW.state := CASE NEW.status
    	        WHEN 0 THEN run_state_finished()
	        ELSE        run_state_failed()
	        END;
        END IF;

	IF NOT run_state_transition_is_valid(OLD.state, NEW.state) THEN
            RAISE EXCEPTION 'Invalid transition between states.';
        END IF;

    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER run_alter BEFORE INSERT OR UPDATE ON run
       FOR EACH ROW EXECUTE PROCEDURE run_alter();


-- TODO: Should do a trigger after any change to run that calls
-- run_main_minute() to update any run statues.


-- Calculate the number of runs for a task that start within a range
-- of specified times.
-- TODO: Need to test this carefully; no rows yet.
CREATE OR REPLACE FUNCTION run_runs_between(
       task_id BIGINT,
       beginning TIMESTAMP WITH TIME ZONE DEFAULT '-infinity',
       ending TIMESTAMP WITH TIME ZONE DEFAULT 'infinity'
       )
RETURNS NUMERIC
AS $$
DECLARE
	range TSTZRANGE;
	result NUMERIC;
BEGIN
	IF beginning = ending THEN
	   SELECT COUNT(*) INTO result
	   FROM run
	   WHERE
		task = task_id
		AND lower(times) = beginning;
	ELSE
	   range := tstzrange(beginning, ending, '[]');
	   SELECT COUNT(*) INTO result
	   FROM run
	   WHERE
		task = task_id
		AND range @> lower(times);
	END IF;

	RETURN result;
END;
$$ LANGUAGE plpgsql;



-- Maintenance functions

CREATE OR REPLACE FUNCTION run_maint_minute()
RETURNS VOID
AS $$
BEGIN

    -- Runs that are still pending after their completion
    -- times as having been missed.

    UPDATE run
    SET state = run_state_missed()
    WHERE
        state = run_state_pending()
	-- TODO: This interval should probably be a tunable.
	AND upper(times) < normalized_now() - 'PT5S'::interval;

    -- Runs still running well after their expected completion times
    -- are treated as having failed.

    UPDATE run
    SET
        state = run_state_missed()
    WHERE
        state = run_state_running()
	-- TODO: This interval should probably be a tunable.
	AND upper(times) < normalized_now() - 'PT1M'::interval;


END;
$$ LANGUAGE plpgsql;



-- Convenient ways to see the goings on

CREATE OR REPLACE VIEW run_status
AS
    SELECT
        run.id,
	run.task,
	run.id AS run,
	run.times,
	run_state.display AS state
    FROM
        run
	JOIN run_state ON run_state.id = run.state
    WHERE
        state != run_state_pending()
    ORDER BY times;


CREATE VIEW run_status_short
AS
    SELECT id, task, times, state
    FROM  run_status
;
