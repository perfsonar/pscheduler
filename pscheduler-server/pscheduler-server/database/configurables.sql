--
-- Table with one row that holds configurable values
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

    t_name := 'configurables';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE configurables (

            -- How far in advance we should schedule runs
            schedule_horizon    INTERVAL
        			DEFAULT 'P1D',

            -- How long we should keep old runs and tasks
            keep_runs_tasks	INTERVAL
        			DEFAULT 'P7D',

            -- Maximum runs in parallel
            max_parallel_runs	INTEGER
        			DEFAULT 50
        );

        -- This table gets exactly one row that can only ever be updated.
        INSERT INTO configurables DEFAULT VALUES;

	t_version := t_version + 1;

    END IF;

    -- Version 1 to version 2
    IF t_version = 1
    THEN
        ALTER TABLE configurables ADD COLUMN
        -- How long runs should be late before being considered stragglers
        run_straggle INTERVAL DEFAULT 'PT10S';

        t_version := t_version + 1;
    END IF;

    -- Version 2 to version 3
    IF t_version = 2
    THEN
        -- Do this update only if the old default is in place.
        UPDATE configurables SET run_straggle = 'PT30S'
        WHERE run_straggle = 'PT10S';

        t_version := t_version + 1;
    END IF;

    -- Version 3 to version 4
    -- Drops unused max_parallel_runs column
    IF t_version = 3
    THEN
        ALTER TABLE configurables DROP COLUMN max_parallel_runs;

        t_version := t_version + 1;
    END IF;

    -- Version 4 to version 5
    -- Changes default keep time to two days.
    IF t_version = 4
    THEN
        -- Make sure pre-version-4 triggers don't fire.
        ALTER TABLE configurables DISABLE TRIGGER USER;

        ALTER TABLE configurables
        ALTER COLUMN keep_runs_tasks
        SET DEFAULT 'P2D';

        UPDATE configurables SET keep_runs_tasks = DEFAULT;

        ALTER TABLE configurables ENABLE TRIGGER USER;

        t_version := t_version + 1;
    END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS configurables_update ON configurables CASCADE;

CREATE OR REPLACE FUNCTION configurables_update()
RETURNS TRIGGER
AS $$
BEGIN
    NOTIFY configurables_changed;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER configurables_update
AFTER UPDATE
ON configurables
FOR EACH ROW
    EXECUTE PROCEDURE configurables_update();



DROP TRIGGER IF EXISTS configurables_alter ON configurables CASCADE;
DROP TRIGGER IF EXISTS configurables_truncate ON configurables CASCADE;

CREATE OR REPLACE FUNCTION configurables_noalter()
RETURNS TRIGGER
AS $$
BEGIN
	RAISE EXCEPTION 'This table can only be updated.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER configurables_alter
BEFORE INSERT OR DELETE
ON configurables
FOR EACH ROW
    EXECUTE PROCEDURE configurables_noalter();

CREATE TRIGGER configurables_truncate
BEFORE TRUNCATE
ON configurables
EXECUTE PROCEDURE configurables_noalter();


--
-- Maintenance
--

-- Maintenance functions


CREATE OR REPLACE FUNCTION configurables_maint_minute()
RETURNS VOID
AS $$
DECLARE
    command_result external_program_result;
    config_json JSONB;
BEGIN

    -- Re-read the configuration

    command_result := pscheduler_command(ARRAY['validate-configurables', '--dump']);
    IF command_result.status <> 0 THEN
        -- TODO: Decide whether we want to log this once a minute.
        -- RAISE NOTICE 'Unable to read configurables: %', command_result.stderr;
        RETURN;
    END IF;

    config_json := command_result.stdout::JSONB;
    IF config_json IS NULL THEN
        RETURN;
    END IF;

    -- Update the database

    IF config_json->'keep-runs-tasks' IS NOT NULL THEN
        UPDATE configurables SET keep_runs_tasks = (config_json ->> 'keep-runs-tasks')::INTERVAL;
    END IF;

    IF config_json->'run-straggle' IS NOT NULL THEN
        UPDATE configurables SET run_straggle = (config_json ->> 'run-straggle')::INTERVAL;
    END IF;

END;
$$ LANGUAGE plpgsql;
