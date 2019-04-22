--
-- Table that keeps track of the version numbers of other tables and
-- supporting utility functions.
--

-- See the README file in this directory for details.


-- Find the installed version of a table and check for consistency
-- between the database and the versions table.
--
-- Returns 0 if the table does not exist.

DO $$ BEGIN PERFORM drop_function_all('table_version_find'); END $$;

CREATE OR REPLACE FUNCTION table_version_find(
    table_name   TEXT,
    table_schema TEXT DEFAULT 'public'
)
RETURNS INTEGER
AS $$
DECLARE
    table_exists BOOLEAN;
    table_version INTEGER;
BEGIN

    table_exists := EXISTS (
        SELECT *
        FROM pg_catalog.pg_tables
        WHERE
            schemaname = table_schema
            AND tablename = table_name
    );

    -- The table_version table is a special case, because if it
    -- doesn't exist, there's no way it can have a row saying it
    -- exists.

    IF NOT table_exists AND table_name = 'table_version'
    THEN
        RETURN 0;
    END IF;

    -- Find the version of the table.

    SELECT INTO table_version version FROM table_version WHERE name = table_name;
    IF NOT FOUND
    THEN
        table_version := 0;
    END IF;

    -- This is an untenable situation because we would have no idea
    -- what version of the table is installed and couldn't do upgrades
    -- to it.

    IF table_exists AND table_version = 0
    THEN
        RAISE EXCEPTION 'Table "%" exists but is not in the versions table.',
	    table_name;
    END IF;


    RETURN table_version;

END;
$$ LANGUAGE plpgsql;


DO $$ BEGIN PERFORM drop_function_all('table_version_set'); END $$;

CREATE OR REPLACE FUNCTION table_version_set(
    t_name TEXT,
    t_version INTEGER,
    t_version_old INTEGER
)
RETURNS VOID
AS $$
BEGIN

    IF t_version < t_version_old
    THEN
        RAISE EXCEPTION '%s: Cannot upgrade from version % to %',
            t_name, t_version, t_version_old;
     END IF;

    -- Don't do an upsert here, because the trigger depends on seeing
    -- an UPDATE to vary the messages it produces.

    IF t_version_old = 0
    THEN
        INSERT INTO table_version (name, version)
            VALUES (t_name, t_version);
    ELSE
        UPDATE table_version
        SET version = t_version
        WHERE name = t_name;
    END IF;

END;
$$ LANGUAGE plpgsql;




DO $$
DECLARE
    t_name TEXT;            -- Name of the table being worked on
    t_version INTEGER;      -- Current version of the table
    t_version_old INTEGER;  -- Prior version of the table
BEGIN

    -- WARNING: Please see the README file before modifying this code.

    --
    -- Preparation
    --

    t_name := 'table_version';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    IF t_version = 0
    THEN

        CREATE TABLE table_version (
	    -- Name of the table
            name     		   TEXT
	    			   UNIQUE
				   NOT NULL,

	    -- Version of the table
            version    		   INTEGER
	    			   NOT NULL
                                   CHECK (version > 0),

	    -- Last attempt at an upgrade
            attempted              TIMESTAMP WITH TIME ZONE
	    			   DEFAULT now(),

	    -- Last time the table was modified
            modified               TIMESTAMP WITH TIME ZONE
	    			   DEFAULT now()

        );

	t_version := t_version + 1;

    END IF;

    -- -- 1 to 2
    -- IF t_version = 1
    -- THEN
    --     -- ALTER TABLE ...
    --     t_version := t_version + 1;
    -- END IF;

    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS table_version_alter ON table_version CASCADE;

DO $$ BEGIN PERFORM drop_function_all('table_version_alter'); END $$;

CREATE OR REPLACE FUNCTION table_version_alter()
RETURNS TRIGGER
AS $$
BEGIN

    NEW.attempted = now();

    IF TG_OP = 'UPDATE'
    THEN

        -- Downgrades are not acceptable.
        IF NEW.version < OLD.version
        THEN
            RAISE EXCEPTION 'Table %s: Cannot be downgraded (%s to %s)',
    	    NEW.name, OLD.version, NEW.version;
        END IF;

        IF NEW.version > OLD.version
        THEN
            NEW.modified = now();
        END IF;

        IF NEW.version <> OLD.version
        THEN
            RAISE NOTICE 'Table %: Upgraded from version % to %',
                NEW.name, OLD.version, NEW.version;
        END IF;

    ELSIF TG_OP = 'INSERT'
    THEN

        RAISE NOTICE 'Table %: Created at version %', NEW.name, NEW.version;

    END IF;


    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER table_version_alter
BEFORE INSERT OR UPDATE
ON table_version
FOR EACH ROW
    EXECUTE PROCEDURE table_version_alter();



DROP TRIGGER IF EXISTS table_version_alter_after ON table_version CASCADE;

DO $$ BEGIN PERFORM drop_function_all('table_version_alter_after'); END $$;

CREATE OR REPLACE FUNCTION table_version_alter_after()
RETURNS TRIGGER
AS $$
BEGIN

    -- Remove tables that have been dropped from the database.

    DELETE FROM table_version 
    WHERE NOT EXISTS (
        SELECT *
        FROM pg_catalog.pg_tables
        WHERE tablename = table_version.name
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER table_version_alter_after
AFTER INSERT OR UPDATE
ON table_version
FOR EACH STATEMENT
    EXECUTE PROCEDURE table_version_alter_after();
