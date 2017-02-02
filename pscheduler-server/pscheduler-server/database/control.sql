--
-- Table with one row that holds control values
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

    t_name := 'control';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE control (

            -- End of run pause time
            pause_runs_until	TIMESTAMP WITH TIME ZONE

        );

        -- This table gets exactly one row that can only ever be updated.
        INSERT INTO control DEFAULT VALUES;

	t_version := t_version + 1;

    END IF;

    -- Version 1 to version 2
    -- IF t_version = 1
    -- THEN
    --     ,,,
    --     t_version := t_version + 1;
    -- END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS control_update ON control CASCADE;

CREATE OR REPLACE FUNCTION control_update()
RETURNS TRIGGER
AS $$
BEGIN
    NOTIFY control_changed;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER control_update
AFTER UPDATE
ON control
FOR EACH ROW
    EXECUTE PROCEDURE control_update();



DROP TRIGGER IF EXISTS control_alter ON control CASCADE;
DROP TRIGGER IF EXISTS control_truncate ON control CASCADE;

CREATE OR REPLACE FUNCTION control_noalter()
RETURNS TRIGGER
AS $$
BEGIN
	RAISE EXCEPTION 'This table can only be updated.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER control_alter
BEFORE INSERT OR DELETE
ON control
FOR EACH ROW
    EXECUTE PROCEDURE control_noalter();

CREATE TRIGGER control_truncate
BEFORE TRUNCATE
ON control
EXECUTE PROCEDURE control_noalter();


--
-- API for Individual Columns
--

--
-- pause_runs_until
--

CREATE OR REPLACE FUNCTION control_pause(
    duration INTERVAL DEFAULT NULL
)
RETURNS VOID
AS $$
DECLARE
    end_time TIMESTAMP WITH TIME ZONE;
BEGIN
    IF duration IS NOT NULL
    THEN
        end_time := now() + duration;
    ELSE
        end_time := tstz_infinity();
    END IF;

    UPDATE control SET pause_runs_until = end_time;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION control_is_paused()
RETURNS BOOLEAN
AS $$
DECLARE
    is_paused BOOLEAN;
BEGIN
    SELECT INTO is_paused EXISTS (
        SELECT * FROM control WHERE pause_runs_until > now()
    );

    RETURN is_paused;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION control_resume()
RETURNS VOID
AS $$
BEGIN
    UPDATE control SET pause_runs_until = NULL;
END;
$$ LANGUAGE plpgsql;
