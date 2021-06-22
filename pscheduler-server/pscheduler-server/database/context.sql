--
-- Table of contexts
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

    t_name := 'context';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE context (

        	-- Row identifier
        	id		BIGSERIAL
        			PRIMARY KEY,

        	-- Original JSON
        	json		JSONB
        			NOT NULL,

        	-- Context Name
        	name		TEXT
        			UNIQUE NOT NULL,

        	-- Verbose description
        	description	TEXT,

        	-- When this record was last updated
        	updated		TIMESTAMP WITH TIME ZONE,

        	-- Whether or not the context is currently available
        	available	BOOLEAN
        			DEFAULT TRUE
        );


        CREATE INDEX context_name ON context(name);

	t_version := t_version + 1;

    END IF;

    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS context_alter ON context CASCADE;

DO $$ BEGIN PERFORM drop_function_all('context_alter'); END $$;

CREATE OR REPLACE FUNCTION context_alter()
RETURNS TRIGGER
AS $$
DECLARE
    json_result TEXT;
BEGIN
    -- TODO: Need to add this to the dictionary
    json_result := json_validate(NEW.json, '#/pScheduler/PluginEnumeration/Context');
    IF json_result IS NOT NULL
    THEN
        RAISE EXCEPTION 'Invalid enumeration: %', json_result;
    END IF;

    NEW.name := NEW.json ->> 'name';
    NEW.description := NEW.json ->> 'description';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER context_alter
BEFORE INSERT OR UPDATE
ON context
FOR EACH ROW
    EXECUTE PROCEDURE context_alter();



DROP TRIGGER IF EXISTS context_alter_post ON context CASCADE;


-- Function to run at startup.

DO $$ BEGIN PERFORM drop_function_all('context_boot'); END $$;

CREATE OR REPLACE FUNCTION context_boot()
RETURNS VOID
AS $$
DECLARE
    run_result external_program_result;
    context_list JSONB;
    context_name TEXT;
    context_enumeration JSONB;
    json_result TEXT;
    sschema NUMERIC;  -- Name dodges a reserved word
BEGIN
    run_result := pscheduler_command(ARRAY['internal', 'list', 'context']);
    IF run_result.status <> 0 THEN
       RAISE EXCEPTION 'Unable to list installed contexts: %', run_result.stderr;
    END IF;

    context_list := run_result.stdout::JSONB;

    FOR context_name IN (select * from jsonb_array_elements_text(context_list))
    LOOP

	run_result := pscheduler_plugin_invoke('context', context_name, 'enumerate');
        IF run_result.status <> 0 THEN
            RAISE WARNING 'Context "%" failed to enumerate: %',
	        context_name, run_result.stderr;
            CONTINUE;
        END IF;

	context_enumeration := run_result.stdout::JSONB;

        sschema := text_to_numeric(context_enumeration ->> 'schema');
        IF sschema IS NOT NULL AND sschema > 1 THEN
            RAISE WARNING 'Context "%": schema % is not supported',
                context_name, sschema;
            CONTINUE;
        END IF;

        json_result := json_validate(context_enumeration,
	    '#/pScheduler/PluginEnumeration/Context');
        IF json_result IS NOT NULL
        THEN
            RAISE WARNING 'Invalid enumeration for context "%": %', context_name, json_result;
	    CONTINUE;
        END IF;

	INSERT INTO context (json, updated, available)
        VALUES (context_enumeration, now(), true)
        ON CONFLICT (name) DO UPDATE
        SET json = context_enumeration, updated = now(), available = TRUE;

    END LOOP;

    -- TODO: Disable, but don't remove, contexts that aren't installed.
    UPDATE context SET available = FALSE WHERE updated < now();
    -- TODO: Should also can anything on the schedule that used this context.  (Do that elsewhere.)
END;
$$ LANGUAGE plpgsql;



-- Validate a context entry and raise an error if invalid.

DO $$ BEGIN PERFORM drop_function_all('context_validate'); END $$;

CREATE OR REPLACE FUNCTION context_validate(
    candidate JSONB
)
RETURNS VOID
AS $$
DECLARE
    json_result TEXT;
    context_name TEXT;
    run_result external_program_result;
    validate_result JSONB;
BEGIN

    json_result := json_validate(candidate, '#/pScheduler/ContextSpecificationSingle');
    IF json_result IS NOT NULL
    THEN
        RAISE EXCEPTION 'Invalid context specification: %', json_result;
    END IF;

    context_name := (candidate ->> 'context')::TEXT;

    IF NOT EXISTS (SELECT * FROM context WHERE name = context_name)
    THEN
        RAISE EXCEPTION 'Unknown context "%"', context_name;
    END IF;

    run_result := pscheduler_plugin_invoke('context', context_name, 'data-is-valid',
        (candidate ->> 'data')::TEXT );
    IF run_result.status <> 0 THEN
        RAISE EXCEPTION 'Context %/% failed to validate: %',
	    context_name, (candidate ->> 'data')::TEXT, run_result.stderr;
    END IF;

    validate_result := run_result.stdout::JSONB;

    IF NOT (validate_result ->> 'valid')::BOOLEAN THEN
        IF validate_result ? 'error' THEN
            RAISE EXCEPTION 'Invalid data for context "%": %',
	        context_name, validate_result ->> 'error';
        ELSE
            RAISE EXCEPTION 'Invalid data for context "%": No error provided by plugin.',
	        context_name;
        END IF;
    END IF;

END;
$$ LANGUAGE plpgsql;
