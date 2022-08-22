--
-- Table of archivers
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

    t_name := 'archiver';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE archiver (

        	-- Row identifier
        	id		BIGSERIAL
        			PRIMARY KEY,

        	-- Original JSON
        	json		JSONB
        			NOT NULL,

        	-- Archiver Name
        	name		TEXT
        			UNIQUE NOT NULL,

        	-- Verbose description
        	description	TEXT,

        	-- Version
        	version		NUMERIC
        			NOT NULL,

        	-- When this record was last updated
        	updated		TIMESTAMP WITH TIME ZONE,

        	-- Whether or not the archiver is currently available
        	available	BOOLEAN
        			DEFAULT TRUE
        );


        CREATE INDEX archiver_name ON archiver(name);

	t_version := t_version + 1;

    END IF;

    -- Version 1 to version 2
    -- Remove unused and trouble-causing version column
    IF t_version = 1
    THEN
        ALTER TABLE archiver DROP COLUMN version;

        t_version := t_version + 1;
    END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;


--
-- Breaker table that maps archivers to the tests they can run
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

    t_name := 'archiver_test';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE archiver_test (

        	-- Archiver which says it can handle a test
        	archiver	BIGINT
        			REFERENCES archiver(id)
        			ON DELETE CASCADE,

        	-- The test the archiver says it can handle
        	test		BIGINT
        			REFERENCES test(id)
        			ON DELETE CASCADE
        );

	t_version := t_version + 1;

    END IF;

    -- Version 1 to version 2
    --IF t_version = 1
    --THEN
    --    ALTER TABLE ...
    --    t_version := t_version + 1;
    --END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS archiver_alter ON archiver CASCADE;

DO $$ BEGIN PERFORM drop_function_all('archiver_alter'); END $$;

CREATE OR REPLACE FUNCTION archiver_alter()
RETURNS TRIGGER
AS $$
DECLARE
    json_result TEXT;
BEGIN
    json_result := json_validate(NEW.json, '#/pScheduler/PluginEnumeration/Archiver');
    IF json_result IS NOT NULL
    THEN
        RAISE EXCEPTION 'Invalid enumeration: %', json_result;
    END IF;

    NEW.name := NEW.json ->> 'name';
    NEW.description := NEW.json ->> 'description';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archiver_alter
BEFORE INSERT OR UPDATE
ON archiver
FOR EACH ROW
    EXECUTE PROCEDURE archiver_alter();



DROP TRIGGER IF EXISTS archiver_alter_post ON archiver CASCADE;

DO $$ BEGIN PERFORM drop_function_all('archiver_alter_post'); END $$;

CREATE OR REPLACE FUNCTION archiver_alter_post()
RETURNS TRIGGER
AS $$
DECLARE
    test_name TEXT;
    test_id BIGINT;
BEGIN

    -- Update the breaker table between this and test.

    DELETE FROM archiver_test WHERE archiver = NEW.id;

    FOR test_name IN
        (SELECT * FROM jsonb_array_elements_text(NEW.json -> 'tests'))
    LOOP
        -- Only insert records for tests that are installed on the system.
        SELECT id INTO test_id FROM test WHERE name = test_name;
	IF FOUND THEN
	    INSERT INTO archiver_test (archiver, test)
	        VALUES (NEW.id, test_id);
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archiver_alter_post
AFTER INSERT OR UPDATE
ON archiver
FOR EACH ROW
    EXECUTE PROCEDURE archiver_alter_post();


DROP TRIGGER IF EXISTS archiver_delete ON archiver CASCADE;

DO $$ BEGIN PERFORM drop_function_all('archiver_delete'); END $$;

CREATE OR REPLACE FUNCTION archiver_delete()
RETURNS TRIGGER
AS $$
BEGIN
    DELETE FROM archiver_test where archiver = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archiver_delete
BEFORE DELETE
ON archiver
FOR EACH ROW
    EXECUTE PROCEDURE archiver_delete();



-- Function to run at startup.

DO $$ BEGIN PERFORM drop_function_all('archiver_boot'); END $$;

CREATE OR REPLACE FUNCTION archiver_boot()
RETURNS VOID
AS $$
DECLARE
    run_result external_program_result;
    archiver_list JSONB;
    archiver_name TEXT;
    archiver_enumeration JSONB;
    json_result TEXT;
    sschema NUMERIC;  -- Name dodges a reserved word
BEGIN
    run_result := pscheduler_command(ARRAY['internal', 'list', 'archiver']);
    IF run_result.status <> 0 THEN
       RAISE EXCEPTION 'Unable to list installed archivers: %', run_result.stderr;
    END IF;

    archiver_list := run_result.stdout::JSONB;

    FOR archiver_name IN (select * from jsonb_array_elements_text(archiver_list))
    LOOP

	run_result := pscheduler_plugin_invoke('archiver', archiver_name, 'enumerate');
        IF run_result.status <> 0 THEN
            RAISE WARNING 'Archiver "%" failed to enumerate: %',
	        archiver_name, run_result.stderr;
            CONTINUE;
        END IF;

	archiver_enumeration := run_result.stdout::JSONB;

        sschema := text_to_numeric(archiver_enumeration ->> 'schema');
        IF sschema IS NOT NULL AND sschema > 1 THEN
            RAISE WARNING 'Archiver "%": schema % is not supported',
                archiver_name, sschema;
            CONTINUE;
        END IF;

        json_result := json_validate(archiver_enumeration,
	    '#/pScheduler/PluginEnumeration/Archiver');
        IF json_result IS NOT NULL
        THEN
            RAISE WARNING 'Invalid enumeration for archiver "%": %', archiver_name, json_result;
	    CONTINUE;
        END IF;

	INSERT INTO archiver (json, updated, available)
	VALUES (archiver_enumeration, now(), TRUE)
	ON CONFLICT (name) DO UPDATE
        SET json = archiver_enumeration, updated = now(), available = TRUE;

    END LOOP;

    -- TODO: Disable, but don't remove, archivers that aren't installed.
    UPDATE archiver SET available = FALSE WHERE updated < now();
    -- TODO: Should also can anything on the schedule that used this archiver.  (Do that elsewhere.)
END;
$$ LANGUAGE plpgsql;



-- Validate an archiver entry and raise an error if invalid.

DO $$ BEGIN PERFORM drop_function_all('archiver_validate'); END $$;

CREATE OR REPLACE FUNCTION archiver_validate(
    candidate JSONB
)
RETURNS VOID
AS $$
DECLARE
    archiver_name TEXT;
    candidate_data JSONB;
    run_result external_program_result;
    validate_result JSONB;
BEGIN
    IF NOT candidate ? 'archiver' THEN
        RAISE EXCEPTION 'No archiver name specified in archiver.';
    END IF;

    archiver_name := candidate ->> 'archiver';

    IF NOT EXISTS (SELECT * FROM archiver WHERE name = archiver_name) THEN
        RAISE EXCEPTION 'No archiver "%" is avaiable.', archiver_name;
    END IF;

    IF candidate ? 'data' THEN
        candidate_data := candidate -> 'data';
    ELSE
        candidate_data := 'null'::JSONB;
    END IF;

    run_result := pscheduler_plugin_invoke('archiver', archiver_name, 'data-is-valid',
        candidate_data::TEXT );
    IF run_result.status <> 0 THEN
        RAISE EXCEPTION 'Archiver "%" failed to validate: %', archiver_name, run_result.stderr;
    END IF;

    validate_result := run_result.stdout::JSONB;

    IF NOT (validate_result ->> 'valid')::BOOLEAN THEN
        IF validate_result ? 'error' THEN
            RAISE EXCEPTION 'Invalid data for archiver "%": %', archiver_name, validate_result ->> 'error';
        ELSE
            RAISE EXCEPTION 'Invalid data for archiver "%": No error provided by plugin.', archiver_name;
        END IF;
    END IF;

END;
$$ LANGUAGE plpgsql;



-- Quick summary

CREATE OR REPLACE VIEW archiver_summary
AS
    SELECT
        archiver.name AS archiver,
        test.name AS test
    FROM
        archiver_test
	JOIN archiver ON archiver.id = archiver
	JOIN test ON test.id = test
;
