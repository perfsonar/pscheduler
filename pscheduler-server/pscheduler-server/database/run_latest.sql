--
-- Table of latest-scheduled runs for each task.  This is used to make
-- the query behind the schedule_runs_to_schedule view run faster.
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

    t_name := 'run_latest';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE run_latest (

        	-- Task this run belongs to
        	task		BIGINT
        			UNIQUE
        			REFERENCES task(id)
        			ON DELETE CASCADE,

        	-- Range of times when this task will be run
        	latest		TIMESTAMP WITH TIME ZONE
        			NOT NULL
        );

        -- Populate the table from existing runs

        INSERT INTO run_latest
        SELECT run.task, max(upper(run.times))
        FROM
            run
            JOIN task ON task.id = run.task
        WHERE task.repeat IS NOT NULL
        GROUP BY run.task;

        CREATE INDEX run_latest_task_latest ON run_latest(task, latest);

	t_version := t_version + 1;

    END IF;


    -- Version 1 to version 2
    -- IF t_version = 1
    -- THEN
    --
    --    t_version := t_version + 1;
    --END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;


DO $$ BEGIN PERFORM drop_function_all('run_latest_update'); END $$;

CREATE OR REPLACE FUNCTION run_latest_update()
RETURNS TRIGGER
AS $$
DECLARE
    affected RECORD;
    latest TIMESTAMP WITH TIME ZONE;
BEGIN

    affected := CASE
            WHEN TG_OP = 'DELETE' THEN OLD
            ELSE NEW
        END;

    -- We only care about tasks that repeat
    IF NOT EXISTS (SELECT * FROM task WHERE id = affected.task AND repeat IS NOT NULL)
    THEN
        RETURN affected;
    END IF;


    SELECT INTO latest
        max(upper(times))
        FROM run
        WHERE task = affected.task
        GROUP BY task;

    IF NOT FOUND  -- No run records left
    THEN
        DELETE FROM run_latest WHERE task = affected.task;
        RETURN affected;
    END IF;    

    INSERT INTO run_latest
    VALUES (affected.task, latest)
    ON CONFLICT (task) DO UPDATE
    SET latest = EXCLUDED.latest;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- TODO: It would be nice if this didn't fire for every row during
-- mass deletes, but there doesn't appear to be a good way around it
-- because FOR EACH STATEMENT doesn't have a way to retrieve the rows
-- affected.

DROP TRIGGER IF EXISTS run_latest_update ON run;
CREATE TRIGGER run_latest_update AFTER INSERT OR UPDATE OR DELETE ON run
    FOR EACH ROW EXECUTE PROCEDURE run_latest_update();
