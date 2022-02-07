--
-- Table of Test Types
--

DO $$
DECLARE
    t_name TEXT;            -- Name of the table being worked on
    t_version INTEGER;      -- Current version of the table
    t_version_old INTEGER;  -- Version of the table at the start
BEGIN

    --
    -- Preparation
    --

    t_name := 'test';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE test (

        	-- Row identifier
        	id		BIGSERIAL
        			PRIMARY KEY,

        	-- Original JSON
        	json		JSONB
        			NOT NULL,

        	-- Test Name
        	name		TEXT
        			UNIQUE NOT NULL,

        	-- Verbose description
        	description	TEXT,

        	-- Version
        	version		NUMERIC
        			NOT NULL,

        	-- When this record was last updated
        	updated		TIMESTAMP WITH TIME ZONE,

        	-- Whether or not the test is currently available
        	available	BOOLEAN
        			DEFAULT TRUE,

                -- Scheduling class for this type of test
        	scheduling_class INTEGER
                                NOT NULL
        			REFERENCES scheduling_class(id)
        			-- Deletes should never happen but for consistency...
        			ON DELETE CASCADE
        );

	t_version := t_version + 1;

    END IF;

    -- Version 1 to version 2
    -- Remove unused and trouble-causing version column
    IF t_version = 1
    THEN
        ALTER TABLE test DROP COLUMN version;

        t_version := t_version + 1;
    END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS test_alter ON test CASCADE;

DO $$ BEGIN PERFORM drop_function_all('test_alter'); END $$;

CREATE OR REPLACE FUNCTION test_alter()
RETURNS TRIGGER
AS $$
DECLARE
    json_result TEXT;
BEGIN

    json_result := json_validate(NEW.json, '#/pScheduler/PluginEnumeration/Test');
    IF json_result IS NOT NULL
    THEN
        RAISE EXCEPTION 'Invalid enumeration: %', json_result;
    END IF;

    NEW.name := NEW.json ->> 'name';
    NEW.description := NEW.json ->> 'description';
    NEW.scheduling_class := scheduling_class_find(NEW.json ->> 'scheduling-class');

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER test_alter
BEFORE INSERT OR UPDATE
ON test
FOR EACH ROW
    EXECUTE PROCEDURE test_alter();



-- Function to run at startup.

DO $$ BEGIN PERFORM drop_function_all('test_boot'); END $$;

CREATE OR REPLACE FUNCTION test_boot()
RETURNS VOID
AS $$
DECLARE
    run_result external_program_result;
    test_list JSONB;
    test_name TEXT;
    test_enumeration JSONB;
    json_result TEXT;
    sschema NUMERIC;  -- Name dodges a reserved word
BEGIN
    run_result := pscheduler_command(ARRAY['internal', 'list', 'test']);
    IF run_result.status <> 0 THEN
       RAISE EXCEPTION 'Unable to list installed tests: %', run_result.stderr;
    END IF;

    test_list := run_result.stdout::JSONB;

    FOR test_name IN (select * from jsonb_array_elements_text(test_list))
    LOOP
	run_result := pscheduler_plugin_invoke('test', test_name, 'enumerate');
        IF run_result.status <> 0 THEN
            RAISE WARNING 'Test "%" failed to enumerate: %',
	        test_name, run_result.stderr;
            CONTINUE;
        END IF;

	test_enumeration := run_result.stdout::JSONB;

        sschema := text_to_numeric(test_enumeration ->> 'schema');
        IF sschema IS NOT NULL AND sschema > 1 THEN
            RAISE WARNING 'Test "%": schema % is not supported',
                test_name, sschema;
            CONTINUE;
        END IF;

        json_result := json_validate(test_enumeration,
	    '#/pScheduler/PluginEnumeration/Test');
        IF json_result IS NOT NULL
        THEN
            RAISE WARNING 'Invalid enumeration for test "%": %', test_name, json_result;
	    CONTINUE;
        END IF;

	INSERT INTO test (json, updated, available)
	VALUES (test_enumeration, now(), TRUE)
	ON CONFLICT (name) DO UPDATE
        SET json = test_enumeration, updated = now(), available = TRUE;

    END LOOP;

    -- Disable, but don't remove, tests that aren't installed.
    UPDATE test SET available = FALSE WHERE updated < now();
    -- TODO: Should also can anything on the schedule.  (Do that elsewhere.)
END;
$$ LANGUAGE plpgsql;
