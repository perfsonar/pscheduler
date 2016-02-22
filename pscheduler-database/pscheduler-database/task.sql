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
                        NOT NULL,

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


	-- When the first run of the test should start.  If NULL, the
	-- scheduler should find the first available time for the
	-- first iteration and use that.
	start		TIMESTAMP WITH TIME ZONE
			DEFAULT NULL,

	-- Amount of slip permissible in start time
	slip		INTERVAL,

	-- How much of the slip is randomly applied to the start time.
	randslip	NUMERIC
			DEFAULT 0.0
			CHECK (randslip BETWEEN 0.0 AND 1.0),

        -- How long the tool that runs the test says it will take
	duration        INTERVAL,

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

	-- Number of times the task has been run
	runs	  	NUMERIC
			DEFAULT 0,

	-- Last time the task was run
	last_run  	TIMESTAMP WITH TIME ZONE,

	--
	-- TESTING
	--

	-- Tool that will be used to run this test
	-- TODO: Do we want to determine this per run or just once?
	tool	  	INTEGER
			NOT NULL
			REFERENCES tool(id)
			ON DELETE CASCADE,

	-- List of URIs for nodes participating in the test.
	participants	JSONB,

	-- Number of participants involved in the test, derived from
	-- the participants field.
	nparticipants	INTEGER,

	-- This node's participant number
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
	tool_type TEXT;
	start TEXT;
	randslip TEXT;
	until TEXT;
	run_result external_program_result;
BEGIN

	--
	-- BASIC VALIDATION
	--

	-- TODO: Should probably only allow updates to the columns
	-- that we don't want changing, which is the task package.

	IF TG_OP = 'INSERT' THEN
	    NEW.added := now();
	ELSIF NEW.added <> OLD.added THEN
	    RAISE EXCEPTION 'Insertion time cannot be updated.';
	END IF;

	FOR key IN (SELECT jsonb_object_keys(NEW.json))
	LOOP
	   IF (left(key, 1) != '_')
              -- TODO: How was passthrough going to be used?
	      AND (key NOT IN ('schema', 'test', 'tool', 'schedule', 'archives', 'passthrough')) THEN
	      RAISE EXCEPTION 'Unrecognized section "%" in task package.', key;
	   END IF;
	END LOOP;


	--
	-- TEST
	--

	IF (NEW.json #> '{test}') IS NULL THEN
	   RAISE EXCEPTION 'Task package has no test section';
	END IF;


	test_type := (NEW.json #>> '{test, type}');

	IF test_type IS NULL THEN
	   RAISE EXCEPTION 'Task contains no test type';
	END IF;

	SELECT INTO NEW.test id FROM test WHERE name = test_type;
	IF NOT FOUND THEN
            RAISE EXCEPTION 'Test type "%" is not available', test_type;
	END IF;


	run_result := pscheduler_internal(ARRAY['invoke', 'test', test_type, 'spec-is-valid'],
		      NEW.json #>> '{test, spec}' );
	IF run_result.status != 0 THEN
	    RAISE EXCEPTION 'Task package contains unusable test: %', run_result.stderr;
	END IF;


	-- Extract participant list
	run_result := pscheduler_internal(ARRAY['invoke', 'test', test_type, 'participants'],
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

        --
        -- UUID
        --

	IF TG_OP = 'INSERT' THEN
            IF NEW.participant = 0 THEN
                IF NEW.uuid IS NOT NULL THEN
                    RAISE EXCEPTION 'Lead participant should not be given a UUID.';
                END IF;
                NEW.uuid = gen_random_uuid();
            ELSIF NEW.uuid IS NULL THEN
                RAISE EXCEPTION 'Non-lead participants must have a UUID.';
            END IF;
        END IF;

	--
	-- TOOL
	--

	-- TODO: Validate tool name

	tool_type := NEW.json #>> '{tool}';
	IF tool_type IS NULL THEN
	   RAISE EXCEPTION 'Task package specifies no tool';
	END IF;

	SELECT INTO NEW.tool id FROM tool WHERE name = tool_type;

	IF NOT FOUND THEN
            RAISE EXCEPTION 'Tool "%" is not available', tool_type;
	END IF;



	--
	-- SCHEDULE
	--

	IF (NEW.json #> '{schedule}') IS NULL THEN
	    RAISE EXCEPTION 'Task package has no schedule section.';
	END IF;

	start := NEW.json #>> '{schedule, start}';
	IF start IS NULL or start = 'soonest' THEN
	    NEW.start := NULL;
        ELSIF start LIKE '@P%' THEN
            -- Start at the next increment of the specified interval,
            -- e.g., @PT1H means to start at the top of the next hour.
            -- Any interval not containing fractional seconds will
            -- work.
	    NEW.start := time_next_interval(now(),
                text_to_interval(substring(start FROM 2)));
	ELSIF start LIKE 'P%' THEN
	    -- ISO Interval, from right now.
	    NEW.start := normalized_time(now() + text_to_interval(start));
	ELSE
	    -- Full timestamp
	    NEW.start := normalized_time(text_to_timestamp_with_time_zone(start));
	END IF;


	NEW.slip := text_to_interval(NEW.json #>> '{schedule, slip}');
	IF NEW.slip IS NULL THEN
	   NEW.slip := 'P0';
	END IF;

	randslip := NEW.json #>> '{schedule, randslip}';
	IF randslip IS NOT NULL THEN
	    NEW.randslip := text_to_numeric(randslip);
	    IF (NEW.randslip < 0.0) OR (NEW.randslip > 1.0) THEN
	        RAISE EXCEPTION 'Slip fraction must be in [0.0 .. 1.0]';
	    END IF;
	END IF;


	NEW.repeat := text_to_interval(NEW.json #>> '{schedule, repeat}');

	-- TODO: Should we check that the repeat interval is greater
	-- than the duration (which we no longer have by default)?

	IF NEW.repeat IS NULL THEN
	   NEW.until := NULL;
	   NEW.max_runs := 1;
	END IF;

	IF (NEW.until IS NULL) AND (NEW.repeat IS NOT NULL) THEN
	   -- Repeaters go forever by default
	   NEW.until := 'infinity';
	END IF;


	until := NEW.json #>> '{schedule, until}';

	IF until LIKE 'P%' THEN
	   NEW.until := now() + text_to_interval(until);
	-- TODO: 'infinity' and 'doomsday' are not officially supported.
	ELSIF until IN ('forever', 'infinity', 'doomsday') THEN
	   NEW.until := 'infinity';
	ELSE
	   NEW.until := text_to_timestamp_with_time_zone(until);
	END IF;

	IF NEW.start IS NULL THEN
            IF NEW.until <= now() THEN
	        RAISE EXCEPTION 'Until must be in the future.';
            END IF;
        ELSIF NEW.until <= NEW.start THEN
	   RAISE EXCEPTION 'Until must be after the start.';
	END IF;


	NEW.max_runs := text_to_numeric(NEW.json #>> '{schedule, max_runs}');

	IF (NEW.max_runs IS NOT NULL) AND (NEW.max_runs < 1) THEN
	   RAISE EXCEPTION 'Maximum runs must be positive.';
	END IF;

        -- See what the tool says about how long it should take.

	run_result := pscheduler_internal(ARRAY['invoke', 'tool', tool_type, 'duration'],
		      NEW.json #>> '{test, spec}' );
	IF run_result.status != 0 THEN
	    RAISE EXCEPTION 'Unable to determine duration of test: %', run_result.stderr;
	END IF;
	-- TODO: Pre-validate the output?
	NEW.duration := interval_round_up(regexp_replace(run_result.stdout, '\s+$', '')::INTERVAL);


	--
	-- ARCHIVES
	--

	-- TODO: Validate archives section once we have a way to do that.


	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER task_alter BEFORE INSERT OR UPDATE ON task
       FOR EACH ROW EXECUTE PROCEDURE task_alter();



-- Register a run having taken place on a task
CREATE OR REPLACE FUNCTION task_register_run(task_id BIGINT)
RETURNS VOID
AS $$
BEGIN
    UPDATE task
    SET
        runs = runs + 1,
        last_run = now()
    WHERE id = task_id;
END;
$$ LANGUAGE plpgsql;



-- TODO: Will need a ticker job to hunt down and kill tasks that no
-- longer need to be in the database.

---
--- API
---


-- Put a task on the timeline and return its UUID

CREATE OR REPLACE FUNCTION api_task_post(
    task_package JSONB,
    participant INTEGER DEFAULT 0,
    task_uuid UUID = NULL
)
RETURNS UUID
AS $$
DECLARE
    inserted RECORD;
BEGIN

   WITH inserted_row AS (
        INSERT INTO task(json, participant, uuid)
        VALUES (task_package, participant, task_uuid)
        RETURNING *
    ) SELECT INTO inserted * from inserted_row;

    RETURN inserted.uuid;

END;
$$ LANGUAGE plpgsql;


-- TODO: Need an api_task_get()
-- TODO: Need an api_task_delete()


