--
-- Run Table
--

DROP TABLE IF EXISTS run CASCADE;
CREATE TABLE run (

	-- Row identifier
	-- TODO: Make this a UUID in the future?
	id		BIGSERIAL
			PRIMARY KEY,

	-- Task this run belongs to
	task		BIGINT
			REFERENCES task(id),

	-- Range of times when this task will be run
	times		TSTZRANGE
			NOT NULL,

	-- State of this run (see run_states table)
	state	    	 INTEGER DEFAULT run_state_pending()
			 REFERENCES run_state(id),

	-- How it went
	status	    	 INTEGER,

	-- What the test burped out (a.k.a., what showed on stdout)
	-- TODO: Should we require that this be JSON?
	result	    	 TEXT,

	-- Errors (a.k.a., what showed on stderr)
	errors	    	 TEXT
);

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



-- Accept the results of a run
CREATE OR REPLACE FUNCTION run_results(
       run_id BIGINT,
       status INTEGER,
       result TEXT DEFAULT '{ }',
       errors TEXT DEFAULT ''
       )
RETURNS NUMERIC
AS $$
BEGIN
	RAISE EXCEPTION 'Not implemented yet';
	-- TODO: Update 
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
        state = run_state_missed(),
	errors = 'Started but never finished'
    WHERE
        state = run_state_running()
	-- TODO: This interval should probably be a tunable.
	AND upper(times) < normalized_now() - 'PT1M'::interval;


END;
$$ LANGUAGE plpgsql;



-- Convenient ways to see the goings on

CREATE VIEW run_status
AS
    SELECT
        run.id,
	run.task,
	run.times,
	run_state.display AS state,
	COALESCE(run.result, run.errors) AS output
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
