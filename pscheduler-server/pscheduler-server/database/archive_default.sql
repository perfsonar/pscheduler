--
-- Table of archives to be used with every run
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

    t_name := 'archive_default';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE archive_default (

            -- Archive specification
            archive             JSONB,

            -- When the record was inserted (for debug only)
            inserted            TIMESTAMP WITH TIME ZONE
                                DEFAULT now()
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


DROP TRIGGER IF EXISTS archive_default_insert ON archive_default CASCADE;

DO $$ BEGIN PERFORM drop_function_all('archive_default_insert'); END $$;

CREATE OR REPLACE FUNCTION archive_default_insert()
RETURNS TRIGGER
AS $$
BEGIN
    PERFORM archiver_validate(NEW.archive);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archive_default_insert
AFTER INSERT
ON archive_default
FOR EACH ROW
    EXECUTE PROCEDURE archive_default_insert();



-- Rows in this can't be updated, only inserted and deleted.  (And
-- usually the whole table at once.)

DROP TRIGGER IF EXISTS archive_default_update ON archive_default CASCADE;

DO $$ BEGIN PERFORM drop_function_all('archive_default_update'); END $$;

CREATE OR REPLACE FUNCTION archive_default_update()
RETURNS TRIGGER
AS $$
BEGIN
    RAISE EXCEPTION 'Rows in this table cannot be updated.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archive_default_update
AFTER UPDATE
ON archive_default
FOR EACH ROW
    EXECUTE PROCEDURE archive_default_update();
