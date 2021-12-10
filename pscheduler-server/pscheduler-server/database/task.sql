--
-- Task Table
--

DO $$
DECLARE
    t_name TEXT;            -- Name of the table being worked on
    t_version INTEGER;      -- Current version of the table
    t_version_old INTEGER;  -- Version of the table at the start

    -- Used by version 1 to 2 upgrade
    v1_2_record RECORD;
    v1_2_run_result external_program_result;
BEGIN

    --
    -- Preparation
    --

    t_name := 'task';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

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
		-- NOTE: This column was remove in version 9.
        	randslip	NUMERIC
        			DEFAULT 0.0
        			CHECK (randslip BETWEEN 0.0 AND 1.0),

                -- How long the tool that runs the test says it will take
        	duration        INTERVAL,

        	-- How often the test should be repeated.
        	repeat		INTERVAL,

        	-- Time after which scheduling stops.
        	until		TIMESTAMP WITH TIME ZONE
        			DEFAULT 'infinity',

        	-- Number of times successfully executed before scheduling stops
        	max_runs	NUMERIC,

        	-- Number of times the task has been scheduled for a
        	-- run.  Note that this only ever increases, even if
        	-- runs are deleted because of cancellation.
        	runs	  	NUMERIC
        			DEFAULT 0,

        	--
        	-- TESTING
        	--

        	-- Tool that will be used to run this test
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
               	archives	JSONB,

        	--
        	-- MISCELLANEOUS
        	--

        	-- Whether or not the task should be scheduled
        	enabled	    	BOOLEAN
        			DEFAULT TRUE,

        	-- Hints used by the limit system
        	hints	    	JSONB
        );


        -- This should be used when someone looks up the external ID.  Bring
        -- the row ID a long so it can be pulled without having to consult the
        -- table.
        CREATE INDEX task_uuid
        ON task(uuid, id);

        -- This helps the 'json' query limiter in the REST API
        CREATE INDEX task_json
        ON task(json);

	t_version := t_version + 1;

    END IF;

    -- Version 1 to version 2
    IF t_version = 1
    THEN
	-- CLI equivalent to what's in the JSON task spec
        ALTER TABLE task ADD COLUMN
	cli JSON;

	-- Turn off triggers because the updates below bring out a bug
	-- in the old version.  Can't just turn off task_alter because
	-- it may not exist yet.

        ALTER TABLE task DISABLE TRIGGER USER;

	-- Calculate CLI for all existing tasks
	FOR v1_2_record IN (SELECT * FROM task)
	LOOP
	    v1_2_run_result := pscheduler_plugin_invoke(
                'test', v1_2_record.json #>> '{test, type}', 'spec-to-cli',
		v1_2_record.json #>> '{test, spec}' );
	    IF v1_2_run_result.status <> 0 THEN
	        RAISE NOTICE 'Unable to divine CLI from spec id %: %',
		  v1_2_run_result.status, v1_2_run_result.stderr;
		v1_2_run_result.stdout := '[ "(CLI Unavailable)" ]';
	    END IF;

	    UPDATE TASK SET cli = v1_2_run_result.stdout::JSON
            WHERE id = v1_2_record.id;
	END LOOP;

        ALTER TABLE task ENABLE TRIGGER USER;

	ALTER TABLE task
	ALTER COLUMN cli SET NOT NULL;

        t_version := t_version + 1;
    END IF;


    -- Version 2 to version 3
    -- Improve indexing on json field
    IF t_version = 2
    THEN

        DROP INDEX IF EXISTS task_json;

        -- This helps the 'json' query limiter in the REST API
        CREATE INDEX task_json
        ON task USING GIN (json);

        t_version := t_version + 1;
    END IF;


    -- Version 3 to version 4
    -- Adds indexes to aid cascading deletes
    IF t_version = 3
    THEN
        CREATE INDEX task_test ON task(test);
	CREATE INDEX task_tool ON task(tool);

        t_version := t_version + 1;
    END IF;

    -- Version 4 to version 5
    -- Adds 'post' column
    IF t_version = 4
    THEN
        -- Amount of time to wait before a result might be available
        ALTER TABLE task ADD COLUMN
        post INTERVAL DEFAULT 'P0';

        t_version := t_version + 1;
    END IF;

    -- Version 5 to version 6
    -- Add proper default to uuid column
    IF t_version = 5
    THEN
        ALTER TABLE task ALTER COLUMN uuid
        DROP NOT NULL;

        ALTER TABLE task ALTER COLUMN uuid
        SET DEFAULT gen_random_uuid();

        t_version := t_version + 1;
    END IF;

    -- Version 6 to version 7
    -- Add first_start column
    IF t_version = 6
    THEN
	-- When the first run of the task started
        ALTER TABLE task ADD COLUMN
	first_start TIMESTAMP WITH TIME ZONE;

        t_version := t_version + 1;
    END IF;

    -- Version 7 to version 8
    -- Add field to hold passed limits
    IF t_version = 7
    THEN
	ALTER TABLE task ADD COLUMN limits_passed JSON DEFAULT '[]'::JSON;

	UPDATE task SET limits_passed = DEFAULT WHERE limits_passed IS NULL;

        t_version := t_version + 1;
    END IF;


    -- Version 8 to version 9
    -- Remove deprecated randslip column
    IF t_version = 8
    THEN
	ALTER TABLE task DROP COLUMN randslip;

        t_version := t_version + 1;
    END IF;


    -- Version 9 to version 10
    -- Separate, queryable JSON column with details
    IF t_version = 9
    THEN
	ALTER TABLE task ADD COLUMN json_detail JSONB;

	-- Populate existing tasks
	UPDATE task SET json_detail = NULL;

        t_version := t_version + 1;
    END IF;


    -- Version 10 to version 11
    -- Add diagnostics column
    IF t_version = 10
    THEN
	ALTER TABLE task ADD COLUMN diags TEXT
	DEFAULT NULL;

	-- Add a placeholder for older tasks
	UPDATE task SET diags = '(None available)';

        t_version := t_version + 1;
    END IF;


    -- Version 11 to version 12
    -- Add runs_started column
    IF t_version = 11
    THEN
        -- Number of times a run has gone into the running state
	ALTER TABLE task ADD COLUMN runs_started NUMERIC
	DEFAULT 0;

        t_version := t_version + 1;
    END IF;

    -- Version 12 to version 13
    -- Add priority column.
    IF t_version = 12
    THEN
	ALTER TABLE task ADD COLUMN
	priority INTEGER;

        t_version := t_version + 1;
    END IF;

    -- Version 13 to version 14
    -- Adds cron_repeat column
    IF t_version = 13
    THEN
	-- How often the task should repeat, cron-style
	ALTER TABLE task ADD COLUMN
	repeat_cron TEXT;

        t_version := t_version + 1;
    END IF;


    -- Version 14 to version 15
    -- Adds participant_key column
    IF t_version = 14
    THEN

	-- Key to be used when tasking second participants when none
	-- was specified in the task.
	ALTER TABLE task ADD COLUMN
	participant_key TEXT;

        t_version := t_version + 1;
    END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;







DROP TRIGGER IF EXISTS task_alter ON task CASCADE;

DO $$ BEGIN PERFORM drop_function_all('task_alter'); END $$;

CREATE OR REPLACE FUNCTION task_alter()
RETURNS TRIGGER
AS $$
DECLARE
	key TEXT;
	test_type TEXT;
	tool_type TEXT;
	start TEXT;
	until TEXT;
	run_result external_program_result;
	temp_json JSONB;
	archive JSONB;
	json_result TEXT;
	context_participant JSONB;
	context JSONB;
        scheduling RECORD;
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


	-- Do this only if the JSON has changed
	IF TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND NEW.json <> OLD.json)
        THEN

	    -- Calculate CLI equivalent
	    run_result := pscheduler_plugin_invoke('test', test_type, 'spec-to-cli',
		          NEW.json #>> '{test, spec}' );
	    IF run_result.status <> 0 THEN
	        RAISE EXCEPTION 'Unable to divine CLI from spec: %', run_result.stderr;
	    END IF;
	    NEW.cli = run_result.stdout::JSON;

	    -- Count the participants
	    NEW.nparticipants := jsonb_array_length(NEW.participants);
	    IF NEW.nparticipants IS NULL OR NEW.nparticipants = 0
            THEN
                RAISE EXCEPTION 'INTERNAL ERROR: Test produced empty participant list from task.';
            END IF;

	    -- Set the priority
	    IF (NEW.json #> '{priority}') IS NOT NULL THEN
	        NEW.priority := NEW.json #>> '{priority}';
	    END IF;

        END IF;

	-- TODO: Should probably check that the list members are
	-- unique and that one of them includes the local system.

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
        -- Key for second and later participants.  Use the one
        -- provided in the task if that exists.
        --

	IF TG_OP = 'INSERT' AND NEW.nparticipants > 1 AND new.participant = 0 THEN
            -- Create a key only if one wasn't provided.
            IF NEW.json ? '_key' THEN
	      NEW.participant_key := NEW.json ->> '_key';
	    ELSE
	      NEW.participant_key := random_string(64, TRUE, TRUE);
	    END IF;
        ELSIF TG_OP = 'UPDATE' AND NEW.participant_key <> OLD.participant_key THEN
            RAISE EXCEPTION 'Participant key cannot be updated.';
        END IF;

	--
	-- TOOL
	--

	tool_type := NEW.json #>> '{tool}';
	IF tool_type IS NULL THEN
	   RAISE EXCEPTION 'Task package specifies no tool';
	END IF;

	SELECT INTO NEW.tool id FROM tool WHERE name = tool_type AND available;

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

	NEW.repeat := text_to_interval(NEW.json #>> '{schedule, repeat}');
	NEW.repeat_cron := NEW.json #>> '{schedule, repeat-cron}';
	IF NEW.repeat_cron IS NOT NULL AND NOT cron_spec_is_valid(NEW.repeat_cron) THEN
	    RAISE EXCEPTION 'Invalid cron repeat specification';
	END IF;

	-- TODO: Should we check that the repeat interval is greater
	-- than the duration (which we no longer have by default)?

	NEW.max_runs := text_to_numeric(NEW.json #>> '{schedule, max-runs}');
	IF (NEW.max_runs IS NOT NULL) AND (NEW.max_runs < 1) THEN
	   RAISE EXCEPTION 'Maximum runs must be positive.';
	END IF;


	-- REPEAT

	IF NEW.repeat IS NULL AND NEW.repeat_cron IS NULL THEN
	    -- Non-repeaters run once
	    NEW.until := NULL;
	    NEW.max_runs := 1;
	END IF;


	-- UNTIL

	until := NEW.json #>> '{schedule, until}';

	-- TODO: Make this compatible with TimestampAbsoluteRelative
	IF until IN ('forever', 'infinity', 'doomsday') THEN
	   NEW.until := 'infinity';
	ELSE
	   NEW.until := text_to_timestamp_with_time_zone(until);
	END IF;

	IF ( (TG_OP = 'INSERT')
             OR (TG_OP = 'UPDATE' AND NEW.until <> OLD.until) )
           AND NEW.until IS NOT NULL
	   AND NEW.until <= now() THEN
	    RAISE EXCEPTION 'Until must be in the future.';
        END IF;

        IF NEW.start IS NOT NULL AND NEW.until <= NEW.start THEN
	   RAISE EXCEPTION 'Until must be after the start.';
	END IF;


        -- See what the tool says about how long it should take.
	
	IF TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND NEW.json <> OLD.json)
        THEN
	    run_result := pscheduler_plugin_invoke('tool', tool_type, 'duration',
		          NEW.json #>> '{test, spec}' );
	    IF run_result.status <> 0 THEN
	        RAISE EXCEPTION 'Unable to determine duration of test: %', run_result.stderr;
	    END IF;
	    temp_json := run_result.stdout::JSONB;
	    NEW.duration := interval_round_up( (temp_json #>> '{duration}')::INTERVAL );
	    -- This will come up NULL if not provided.
	    NEW.post := interval_round_up( (temp_json #>> '{post}')::INTERVAL );
	    IF NEW.post IS NULL THEN
                NEW.post = 'P0'::INTERVAL;
            END IF;
        END IF;

	--
	-- ARCHIVES
	--

	IF (TG_OP = 'INSERT'
            OR (TG_OP = 'UPDATE' AND NEW.json <> OLD.json))
	   AND NEW.json ? 'archives'
        THEN
	    FOR archive IN (SELECT * FROM jsonb_array_elements_text(NEW.json -> 'archives'))
	    LOOP
	        PERFORM archiver_validate(archive);
	    END LOOP;
	END IF;


	--
	-- CONTEXTS
	--

	IF (TG_OP = 'INSERT'
            OR (TG_OP = 'UPDATE' AND NEW.json <> OLD.json))
	   AND NEW.json ? 'contexts'
        THEN

	    -- Make sure it looks sane
	    json_result := json_validate(NEW.json #> '{contexts}', '#/pScheduler/ContextSpecification');
            IF json_result IS NOT NULL
            THEN
		RAISE EXCEPTION 'Invalid context specification: %', json_result;
	    END IF;

	    -- Make sure there aren't more contexts than the task has participants.
	    IF jsonb_array_length(NEW.json #> '{contexts,contexts}') <> NEW.nparticipants
            THEN
		RAISE EXCEPTION 'Number of contexts for this task must be exactly %',
		    NEW.nparticipants;
	    END IF;

	    -- Check with all of the plugins to make sure the data is valid.
	    FOR context_participant IN ( SELECT * FROM jsonb_array_elements(NEW.json #> '{contexts, contexts}') )
	    LOOP
	        FOR context IN (SELECT * FROM jsonb_array_elements_text(context_participant))
		LOOP
		    PERFORM context_validate(context);
	        END LOOP;
	    END LOOP;
	END IF;

	--
	-- SEARCHABLE JSON WITH DETAILS
	--

	SELECT INTO scheduling
            scheduling_class.*
        FROM
	    test
            JOIN scheduling_class ON scheduling_class.id = test.scheduling_class
        WHERE
            test.id = NEW.test
        ;


	NEW.json_detail := jsonb_set(NEW.json, '{detail}', '{}'::JSONB);

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,added}',
            to_jsonb(timestamp_with_time_zone_to_iso8601(NEW.added)));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,anytime}',
            to_jsonb(scheduling.anytime));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,cli}',
            to_jsonb(NEW.cli));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,diags}',
            to_jsonb(NEW.diags));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,duration}',
            to_jsonb(interval_to_iso8601(NEW.duration)));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,enabled}',
	    to_jsonb(NEW.enabled));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,exclusive}',
            to_jsonb(scheduling.exclusive));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,hints}',
            to_jsonb(NEW.hints));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,multi-result}',
            to_jsonb(scheduling.multi_result));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,participant}',
	    to_jsonb(NEW.participant));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,participants}',
	    to_jsonb(NEW.participants));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,post}',
            to_jsonb(interval_to_iso8601(NEW.post)));

	-- TODO: runs and runs_started change often enough that it
	-- might be worth hitting those in separate triggers.

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,runs}',
	    to_jsonb(NEW.runs));

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,runs-started}',
	    to_jsonb(NEW.runs_started));

        IF NEW.slip IS NOT NULL
        THEN
	    NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,slip}',
                to_jsonb(interval_to_iso8601(NEW.slip)));
        ELSE
            NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,slip}',
                'null'::JSONB);
        END IF;

	NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,spec-limits-passed}',
	    to_jsonb(NEW.limits_passed));

        IF NEW.start IS NOT NULL
        THEN
	    NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,start}',
                to_jsonb(timestamp_with_time_zone_to_iso8601(NEW.start)));
        ELSE
            NEW.json_detail := jsonb_set(NEW.json_detail, '{detail,start}',
                'null'::JSONB);
        END IF;




	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER task_alter BEFORE INSERT OR UPDATE ON task
    FOR EACH ROW EXECUTE PROCEDURE task_alter();




DROP TRIGGER IF EXISTS task_alter_notify ON task CASCADE;

DO $$ BEGIN PERFORM drop_function_all('task_alter_notify'); END $$;

CREATE OR REPLACE FUNCTION task_alter_notify()
RETURNS TRIGGER
AS $$
BEGIN
    NOTIFY task_change;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER task_alter_notify AFTER INSERT ON task
    -- Doesn't matter how many inserts happened
    FOR EACH STATEMENT
    EXECUTE PROCEDURE task_alter_notify();

CREATE TRIGGER task_alter_notify_update AFTER UPDATE ON task
    -- One of these per row since changes may be different.
    FOR EACH ROW
    -- Don't trigger scheduling if it's just a run count update.
    WHEN ((NEW.runs = OLD.runs) AND (NEW.runs_started = OLD.runs_started))
    EXECUTE PROCEDURE task_alter_notify();




-- Calculate when the next iteration of a task should take place after
-- a given time.  This isn't actually a task-specific function, but
-- tasks are the only context where it will be used.

DO $$ BEGIN PERFORM drop_function_all('task_next_run'); END $$;

CREATE OR REPLACE FUNCTION task_next_run(
       start TIMESTAMP WITH TIME ZONE,   -- Task's start (first run) time
       after TIMESTAMP WITH TIME ZONE,   -- Base for "next" time
       repeat INTERVAL,                  -- Time between runs
       repeat_cron TEXT                  -- Cron-style repeat spec
)
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
DECLARE
    intervals NUMERIC;
    next_interval TIMESTAMP WITH TIME ZONE;
    next_cron TIMESTAMP WITH TIME ZONE;
BEGIN

    IF repeat IS NULL AND repeat_cron IS NULL THEN
        RAISE EXCEPTION 'Must have either an interval or a cron spec';
    END IF;

    -- Standard, every-x repeat

    IF repeat IS NULL THEN
        next_interval := tstz_infinity();
    ELSIF repeat = 'P0' THEN
        RAISE EXCEPTION 'Cannot divide by a zero interval';
    ELSE 
        -- Number of runs that should have happened between the task
        -- start and the after time.
	intervals := 
        	  TRUNC( (EXTRACT(EPOCH FROM after) - EXTRACT(EPOCH FROM start))
		  / EXTRACT(EPOCH FROM repeat) ) + 1;
	next_interval := start + (repeat * intervals);
    END IF;

    -- Cron-style repeat

    IF repeat_cron IS NULL THEN
        next_cron = tstz_infinity();
    ELSE
        next_cron = cron_next(repeat_cron, after);
    END IF;

    -- The behavior in the presence of both is to use the earlier
    RETURN least(next_interval, next_cron);

END;
$$ LANGUAGE plpgsql;





---
--- Maintenance
---

DO $$ BEGIN PERFORM drop_function_all('task_purge'); END $$;

CREATE OR REPLACE FUNCTION task_purge()
RETURNS VOID
AS $$
DECLARE
    older_than TIMESTAMP WITH TIME ZONE;
BEGIN

    SELECT INTO older_than normalized_now() - keep_runs_tasks
    FROM configurables;

    -- Get rid of tasks that no longer have runs and can be considered
    -- completed.

    DELETE FROM task
    WHERE
        NOT EXISTS (SELECT * FROM run where run.task = task.id)
        -- The first of these will be the latest known time.
        AND COALESCE(until, start, added) < older_than
        AND (
            -- Complete based on runs
            (max_runs IS NOT NULL AND runs >= max_runs)
            -- One-shot
            OR (repeat IS NULL AND repeat_cron IS NULL)
            -- Until time has passed
            OR until < older_than
            )
    ;

END;
$$ LANGUAGE plpgsql;



-- Maintenance that happens four times a minute.

DO $$ BEGIN PERFORM drop_function_all('task_maint_fifteen'); END $$;

CREATE OR REPLACE FUNCTION task_maint_fifteen()
RETURNS VOID
AS $$
BEGIN
    PERFORM task_purge();
END;
$$ LANGUAGE plpgsql;



---
--- API
---


-- Put a task on the timeline and return its UUID

DO $$ BEGIN PERFORM drop_function_all('api_task_post'); END $$;

CREATE OR REPLACE FUNCTION api_task_post(
    task_package JSONB,
    participant_list TEXT[],
    hints JSONB,
    limits_passed JSON = '[]',
    participant INTEGER DEFAULT 0,
    priority INTEGER DEFAULT NULL,
    task_uuid UUID = NULL,
    enabled BOOLEAN = TRUE,
    diags TEXT = '(None)'
)
RETURNS TABLE(
  uuid UUID,
  participant_key TEXT
)
AS $$
DECLARE
    inserted RECORD;
BEGIN

   IF EXISTS (SELECT * FROM task WHERE task.uuid = task_uuid)
   THEN
       RAISE EXCEPTION 'Task already exists.  All participants must be on separate systems.';
   END IF;

   WITH inserted_row AS (
        INSERT INTO task(json, participants, limits_passed, participant,
	                 priority, uuid, hints, enabled, diags)
        VALUES (task_package, array_to_json(participant_list), limits_passed,
	        participant, priority, task_uuid, hints, enabled, diags)
        RETURNING *
    ) SELECT INTO inserted * from inserted_row;

    uuid := inserted.uuid;
    participant_key := inserted.participant_key;

    RETURN NEXT;

END;
$$ LANGUAGE plpgsql;



-- This function enables a task by its UUID.  This is used by the REST
-- API to keep the scheduler from trying to ask the other participants
-- for runtimes when they don't have it yet.  (Other participants'
-- schedulers won't touch their copies because they're not leading.)

DO $$ BEGIN PERFORM drop_function_all('api_task_enable'); END $$;

CREATE OR REPLACE FUNCTION api_task_enable(
    task_uuid UUID        -- UUID of task to enable
)
RETURNS VOID
AS $$
DECLARE
    taskrec RECORD;
BEGIN

    SELECT INTO taskrec * FROM task WHERE uuid = task_uuid;
    IF NOT FOUND
    THEN
        RAISE EXCEPTION 'Task not found while enabling task %', task_uuid;
    END IF;

    IF taskrec.enabled
    THEN
        -- Don't so anything redundant redundant.
        RETURN;
    END IF;

    UPDATE task SET enabled = TRUE WHERE id = taskrec.id;

END;
$$ LANGUAGE plpgsql;


-- This function disables a task and does the corresponding DELETE on
-- the other participants.  The task_url_format argument is the URL of
-- the task with the hostname replaced with %s, which will be filled
-- in with the hostname of each participant.

DO $$ BEGIN PERFORM drop_function_all('api_task_disable'); END $$;

CREATE OR REPLACE FUNCTION api_task_disable(
    task_uuid UUID,       -- UUID of task to disable
    task_url_format TEXT  -- URL template.  See above.
)
RETURNS VOID
AS $$
DECLARE
    taskrec RECORD;
    host TEXT;
    ip INET;
    ip_family INTEGER;
    bind TEXT;
    task_url_append TEXT;
BEGIN

    SELECT INTO taskrec * FROM task WHERE uuid = task_uuid;
    IF NOT FOUND
    THEN
        RAISE EXCEPTION 'Task not found while disabling task %', task_uuid;
    END IF;

    IF NOT taskrec.enabled
    THEN
        -- Don't so anything redundant redundant.
        RETURN;
    END IF;

    UPDATE task SET enabled = FALSE WHERE uuid = task_uuid;

    -- Sling a DELETE at the non-lead participants if there are any
    -- and we're the lead.

    IF taskrec.participant = 0
    THEN

        -- If the task has a lead-bind, use it.
	IF taskrec.json ? 'lead-bind'
	THEN
	    bind := taskrec.json #>> '{"lead-bind"}';
	ELSE
	    bind := NULL;
	END IF;

	-- If this task has a key, use that for the participant key or
	-- generate one.

        IF taskrec.participant_key IS NOT NULL
	THEN
	    task_url_append := '?key=' || uri_encode(taskrec.participant_key);
	ELSE
	    task_url_append := '';
	END IF;


        FOR host IN (SELECT jsonb_array_elements_text(taskrec.participants)
                     FROM task WHERE uuid = task_uuid OFFSET 1)
        LOOP

            -- IPv6 adresses get special treatment
            BEGIN
		IF family(host::INET) = 6
                THEN
                    host := format('[%s]', host);
                END IF;
            EXCEPTION WHEN OTHERS THEN
                NULL;  -- Don't care
            END;

            INSERT INTO http_queue (operation, uri, bind)
                VALUES ('DELETE',
		    format(task_url_format, host) || task_url_append,
		    bind);
        END LOOP;
    END IF;   

END;
$$ LANGUAGE plpgsql;
