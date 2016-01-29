--
-- Task Table
--


DROP TABLE IF EXISTS task CASCADE;
CREATE TABLE task (

	-- Row identifier
	id		BIGSERIAL
			PRIMARY KEY,

	-- External-use identifier
	uuid		UUID
			UNIQUE
			DEFAULT gen_random_uuid(),

	-- JSON representation of the task.  This should be the only
	-- column specified when inserting a row; all of the others
	-- are derived and will be overwritten.
	json		JSONB
			NOT NULL,
	

	--
	-- TEST
	--

	test		BIGINT
			REFERENCES test(id)
			ON DELETE CASCADE,

	--
	-- SCHEDULING
	--

	-- When this task was first added to the schedule.  This is
	-- used for breaking ties on equal-priority tasks.
	added		TIMESTAMP WITH TIME ZONE,


	-- When the first iteration of the test should start
	start		TIMESTAMP WITH TIME ZONE,

	-- How long the test should last
	duration	INTERVAL
			NOT NULL,

	-- Amount of slip permissible in start time without
	-- sacrificing duration.
	slip		INTERVAL,

	-- How much of the slip is randomly applied to the start time.
	randslip	NUMERIC
			DEFAULT 0.0
			CHECK (randslip BETWEEN 0.0 AND 1.0),

	-- How often the test should be repeated.

	-- TODO: This needs to handle CRON-style and streaming.  Might
	-- be helped by https://pypi.python.org/pypi/croniter or a C
	-- counterpart.

	repeat		INTERVAL,

	-- Time after which scheduling stops.
	until		TIMESTAMP WITH TIME ZONE
			DEFAULT 'infinity',

	-- Number of times successfully executed before scheduling stops
	max_runs	NUMERIC,

	-- Number of iterations that have been executed
	repeats	  	NUMERIC
			DEFAULT 0,

	-- When this task should be removed.  This is used to do temporary holds.
	-- TODO: Need something to enforce this.  Could probably do it when the scheduler runs.
	expires	  	TIMESTAMP WITH TIME ZONE
			DEFAULT NULL,

	--
	-- TESTING
	--

	-- Tool that will be used to run this test
	-- TODO: Need to noodle through tool selection
	tool	  	INTEGER
			NOT NULL
			REFERENCES tool(id)
			ON DELETE CASCADE,

	-- List of URIs for nodes participating in the test.
	participants	JSONB,

	-- Number of participants involved in the test, derived from
	-- the participants field.
	nparticipants	INTEGER,

	-- This system's participant number
	participant	INTEGER,


	-- List of archives where the results are sent.
	-- TODO: Validate this with a trigger
	-- TODO: If NULL, the archiver will need to pull the system
	-- defaults effective... when?  When scheduled?  When run?
	archives	JSONB,


	--
	-- MISCELLANEOUS
	--

	-- Whether or not the task should be scheduled
	enabled	    	BOOLEAN
			DEFAULT(TRUE)
);


-- This should be used when someone looks up the external ID.  Bring
-- the row ID a long so it can be pulled without having to consult the
-- table.
CREATE INDEX task_uuid
ON task(uuid, id);





CREATE OR REPLACE FUNCTION task_alter()
RETURNS TRIGGER
AS $$
DECLARE
	key TEXT;
	test_type TEXT;
	start TEXT;
	until TEXT;
	run_result external_program_result;
BEGIN

	--
	-- Pull columns from the JSON
	-- TODO: Only if changed?  (Probably a good idea.)
	--

	FOR key IN (SELECT jsonb_object_keys(NEW.json))
	LOOP
	   IF (left(key, 1) != '_')
	      AND (key NOT IN ('schema', 'schedule', 'test', 'archives', 'passthrough')) THEN
	      RAISE EXCEPTION 'Unrecognized section "%" in task package.', key;
	   END IF;
	END LOOP;

	test_type := (NEW.json #>> '{test, type}');
	SELECT INTO NEW.test test.id FROM test WHERE test.name = test_type;
	IF NOT FOUND THEN
            RAISE EXCEPTION 'Unknown test type "%"', test_type;
	END IF;


	run_result := pscheduler_internal(ARRAY['invoke', 'test', (NEW.json #>> '{test, type}'), 'spec-is-valid'],
		      NEW.json #>> '{test, spec}' );
	IF run_result.status != 0 THEN
	   RAISE EXCEPTION 'Unusable task package: %', run_result.stderr;
	END IF;

	IF (NEW.json #> '{schedule}') IS NULL THEN
	   RAISE EXCEPTION 'Task package has no schedule section.';
	END IF;

	IF TG_OP = 'INSERT' THEN
	      NEW.added := now();
	ELSIF NEW.added <> OLD.added THEN
	      RAISE EXCEPTION 'Insertion time cannot be updated.';
	END IF;

	-- Need this first because a 'soonest' start depends on it.
	NEW.duration := text_to_interval(NEW.json #>> '{schedule, duration}');

	start := NEW.json #>> '{schedule, start}';
	IF start IS NULL THEN
	   NEW.start := now();
	ELSIF start = 'soonest' THEN
	   -- Earliest spot in the schedule where this task
	   NEW.start := schedule_soonest_available(NEW.duration);
	ELSIF start LIKE '<P%' THEN
	   -- TODO: Soonest within specified interval
	   RAISE EXCEPTION 'Soonest-within scheduling is not yet supported';
	ELSIF start LIKE '>P%' THEN
	   -- Soonest after specified interval
	   NEW.start := schedule_soonest_available(NEW.duration,
				now() + text_to_interval(substring(start FROM 2)));
	ELSIF start LIKE 'P%' THEN
	   -- ISO Interval
	   NEW.start := normalized_time(now() + text_to_interval(start));
	ELSE
	   -- Full timestamp
	   NEW.start := normalized_time(text_to_timestamp_with_time_zone(start));
	END IF;
	IF NEW.start is NULL THEN
	   RAISE EXCEPTION 'Unable to find a time to schedule the task.';
	END IF;

	NEW.slip := text_to_interval(NEW.json #>> '{schedule, slip}');
	NEW.randslip := text_to_numeric(NEW.json #>> '{schedule, randslip}');

	NEW.repeat := text_to_interval(NEW.json #>> '{schedule, repeat}');

	until := NEW.json #>> '{schedule, until}';
	IF until LIKE 'P%' THEN
	   NEW.until := now() + text_to_interval(until);
	-- TODO: 'infinity' and 'doomsday' are not officially supported.
	ELSIF until IN ('forever', 'infinity', 'doomsday') THEN
	   NEW.until := 'infinity';
	ELSE
	   NEW.until := text_to_timestamp_with_time_zone(until);
	END IF;

	NEW.max_runs := text_to_numeric(NEW.json #>> '{schedule, max_runs}');

	IF (NEW.json #> '{test}') IS NULL THEN
	   RAISE EXCEPTION 'Task package has no test section';
	END IF;

	-- TODO: Validate test type once we have a table of those.
	-- TODO: Validate test spec once we have test type classes

	-- Extract participant list
	run_result := pscheduler_internal(ARRAY['invoke', 'test', (NEW.json #>> '{test, type}'), 'participants'],
		      NEW.json #>> '{test, spec}' );
	IF run_result.status != 0 THEN
	   RAISE EXCEPTION 'Unable to determine participants: %', run_result.stderr;
	END IF;
        NEW.participants := run_result.stdout;
	-- TODO: Should probably check that the list members are
	-- unique and that one of them includes the local system.

	NEW.nparticipants := jsonb_array_length(NEW.participants);

	-- Validate the participant number
	IF NEW.participant IS NULL THEN
	    RAISE EXCEPTION 'A participant number must be provided.';
	END IF;
	IF (NEW.participant < 0)
	    OR (NEW.participant > (NEW.nparticipants - 1)) THEN
	    RAISE EXCEPTION 'Participant number is invalid for this test';
	END IF;

	-- TODO: Validate archives section once we have a way to do that.


	--
	-- Apply Defaults and corrections
	--

	IF NEW.start IS NULL THEN
	   NEW.start := now();
	END IF;

	-- This prevents fractional gaps in the schedule
	NEW.start := normalized_time(NEW.start);

	-- TODO: Get the tool to set the duration?

	IF NEW.slip IS NULL THEN
	   -- TODO: Should this default be something greater than 0?
	   NEW.slip := 'P0';
	END IF;

	IF (NEW.randslip < 0.0) OR (NEW.randslip > 1.0)
	THEN
		RAISE EXCEPTION 'Slip fraction must be in [0.0 .. 1.0]';
	END IF;

	IF (NEW.repeat IS NOT NULL) AND (NEW.repeat <= NEW.duration) THEN
	   RAISE EXCEPTION 'Repeat must be longer than the duration. %', NEW.repeat;
	END IF;

	IF NEW.repeat IS NULL THEN
	   NEW.until := NULL;
	   NEW.max_runs := 1;
	END IF;

	IF (NEW.until IS NULL) AND (NEW.repeat IS NOT NULL) THEN
	   -- Repeaters go forever by default
	   NEW.until := 'infinity';
	END IF;

	IF NEW.until <= NEW.start THEN
	   RAISE EXCEPTION 'Until must be after the start.';
	END IF;

	IF (NEW.max_runs IS NOT NULL) AND (NEW.max_runs < 1) THEN
	   RAISE EXCEPTION 'Maximum runs must be positive.';
	END IF;


	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER task_alter BEFORE INSERT OR UPDATE ON task
       FOR EACH ROW EXECUTE PROCEDURE task_alter();


-- TODO: This trigger should probably be part of schedule.sql
-- TODO: It should go entirely when we do multi-participant
CREATE OR REPLACE FUNCTION task_alter_post()
RETURNS TRIGGER AS $$
BEGIN
	PERFORM schedule_reschedule(NEW.id);
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER task_alter_post AFTER INSERT OR UPDATE ON task
       FOR EACH ROW EXECUTE PROCEDURE task_alter_post();
