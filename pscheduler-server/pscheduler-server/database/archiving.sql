--
-- Table of archiving records for a run
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

    t_name := 'archiving';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE archiving (

        	-- Row identifier
        	id		BIGSERIAL
        			PRIMARY KEY,

        	-- Run this archiving is part of
        	run		BIGINT
        			NOT NULL
        			REFERENCES run(id)
        			ON DELETE CASCADE,

                -- Archiver to be used
        	archiver        BIGINT
        			NOT NULL
        			REFERENCES archiver(id)
        			ON DELETE CASCADE,

                -- Data for the archiver
        	archiver_data   JSONB,

        	-- How many times we've tried to archive the result
        	attempts    	INTEGER
        			DEFAULT 0
        			CHECK(attempts >= 0),

        	-- How many times we've tried to archive
        	last_attempt   	TIMESTAMP WITH TIME ZONE,

        	-- Whether or not this archiving has been completed,
        	-- successfully or not.
        	archived   	BOOLEAN
        			DEFAULT FALSE,

        	-- When we should try again if not successful
        	next_attempt  	TIMESTAMP WITH TIME ZONE
        			DEFAULT '-infinity'::TIMESTAMP WITH TIME ZONE,

        	-- Array of results from each attempt
        	diags	   	JSONB
                			DEFAULT '[]'::JSONB
        );

	t_version := t_version + 1;

    END IF;

    -- Version 1 to version 2
    -- Adds indexes for run and archiver to aid cascading deletes
    IF t_version = 1
    THEN
        CREATE INDEX archiving_run ON archiving(run);
        CREATE INDEX archiving_archiver ON archiving(archiver);

        t_version := t_version + 1;
    END IF;

    -- Version 2 to version 3
    -- Adds indexes to make archiving_eligible go faster
    IF t_version = 2
    THEN
        CREATE INDEX archiving_candidates
        ON archiving(archived, next_attempt)
	WHERE NOT archived;

        t_version := t_version + 1;
    END IF;

    -- Version 3 to version 4
    -- Improvement to archiving_candidates index
    IF t_version = 3
    THEN
        DROP INDEX IF EXISTS archiving_candidates;
        CREATE INDEX archiving_candidates
        ON archiving(archived, next_attempt)
        WHERE NOT archived AND next_attempt IS NOT NULL;

        t_version := t_version + 1;
    END IF;

    -- Version 4 to version 5
    -- Adds expiration time
    IF t_version = 4
    THEN
        -- Calculated by archiving_run_afer from the 'ttl' value in the JSON
        ALTER TABLE archiving ADD COLUMN
        ttl_expires TIMESTAMP WITH TIME ZONE;

        t_version := t_version + 1;
    END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS archiving_run_after ON archiving CASCADE;

CREATE OR REPLACE FUNCTION archiving_run_after()
RETURNS TRIGGER
AS $$
DECLARE
    inserted BOOLEAN;
    archive JSONB;
    expires TIMESTAMP WITH TIME ZONE;
BEGIN

    -- Start an archive if conditions are right

    IF ( -- Non-Background-multi run
         TG_OP = 'UPDATE'
         AND OLD.result_merged IS NULL 
         AND NEW.result_merged IS NOT NULL )
       OR ( -- Background-multi Run
            TG_OP = 'INSERT'
            AND NEW.state = run_state_finished()
            AND NEW.result_merged IS NOT NULL
            AND EXISTS (SELECT *
                        FROM
                            task
                            JOIN test ON test.id = task.test
                        WHERE
                            task.id = NEW.task
                            AND test.scheduling_class = scheduling_class_background_multi())
          )
   THEN

       inserted := FALSE;

        -- Insert rows into the archiving table.
        FOR archive IN (
                        -- Task-provided archivers
                        SELECT
                            jsonb_array_elements(task.json #> '{archives}')
                        FROM
                            run
                            JOIN task on run.task = task.id
                        WHERE
                            run.id = NEW.id
			    AND task.participant = 0

                        UNION ALL

                        -- System-wide default archivers
                        SELECT archive_default.archive FROM archive_default
                       )
        LOOP
            IF archive ? 'ttl'
            THEN
                expires := now() + text_to_interval(archive #>> '{ttl}');
            ELSE
                expires := NULL;
	    END IF;

	    INSERT INTO archiving (run, archiver, archiver_data, ttl_expires)
    	    VALUES (
    	        NEW.id,
    	        (SELECT id from archiver WHERE name = archive #>> '{archiver}'),
	        (archive #> '{data}')::JSONB,
	        expires
    	    );
            inserted := TRUE;
        END LOOP;

        IF inserted THEN
            NOTIFY archiving_change;
        END IF;

    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS archiving_run_after ON run;
CREATE TRIGGER archiving_run_after AFTER INSERT OR UPDATE ON run
       FOR EACH ROW EXECUTE PROCEDURE archiving_run_after();





DROP TRIGGER IF EXISTS archiving_update ON archiving CASCADE;

CREATE OR REPLACE FUNCTION archiving_update()
RETURNS TRIGGER
AS $$
BEGIN

    -- Notify on things the archiver will want to know about:

    IF
        -- Completions
        (NEW.archived AND NEW.archived <> OLD.archived)
        -- Reschedules
        OR (NEW.next_attempt IS NOT NULL
                AND NEW.next_attempt <> OLD.next_attempt)
    THEN
        NOTIFY archiving_change;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS archiving_update ON archiving;
CREATE TRIGGER archiving_update AFTER UPDATE ON archiving
       FOR EACH ROW EXECUTE PROCEDURE archiving_update();





-- TODO: These can go away after GA.

DROP TRIGGER IF EXISTS archiving_alter ON archiving CASCADE;
DROP FUNCTION IF EXISTS archiving_alter();



-- Return the first max_return items eligible for archiving

-- TODO: Can remove this after GA release.
DROP FUNCTION IF EXISTS archiving_next(INTEGER);

CREATE OR REPLACE FUNCTION archiving_next(
    max_return INTEGER
)
RETURNS TABLE (
    id BIGINT,
    task_uuid UUID,
    run_uuid UUID,
    archiver TEXT,
    archiver_data JSONB,
    start TIMESTAMP WITH TIME ZONE,
    duration INTERVAL,
    test JSONB,
    tool JSONB,
    participants JSONB,
    result JSONB,
    attempts INTEGER,
    last_attempt TIMESTAMP WITH TIME ZONE
)
AS $$
BEGIN

    RETURN QUERY

    SELECT
        archiving.id AS id,
        task.uuid AS task_uuid,
        run.uuid AS run_uuid,
        archiver.name AS archiver,
        archiving.archiver_data,
        lower(run.times) AS start,
        task.duration AS duration,
        task.json #> '{test}' AS test,
        tool.json AS tool,
        task.participants AS participants,
        run.result_merged AS result,
        archiving.attempts AS attempts,
        archiving.last_attempt AS last_attempt
    FROM
        archiving
        JOIN archiver ON archiver.id = archiving.archiver
        JOIN run ON run.id = archiving.run
        JOIN task ON task.id = run.task
        JOIN tool ON tool.id = task.tool
    WHERE
        archiving.id IN (
            SELECT archiving.id FROM archiving
            WHERE
                NOT archived
                AND next_attempt IS NOT NULL
                AND next_attempt < now()
                AND (ttl_expires IS NULL OR ttl_expires > now())
            ORDER BY archiving.attempts, next_attempt
            LIMIT max_return
        )
    ORDER BY attempts, next_attempt;

    RETURN;

END;
$$ LANGUAGE plpgsql;


-- A handy view for the archiver to use

-- TODO: Remove this after GA release
DROP VIEW IF EXISTS archiving_eligible;
CREATE OR REPLACE VIEW archiving_eligible
AS
    SELECT
        archiving.id,
        run.uuid,
	archiver.name AS archiver,
	archiving.archiver_data,
	lower(run.times) AS start,
	task.duration,
	task.json #> '{test}' AS test,
	tool.json AS tool,
	task.participants,
	run.result_full AS result_full,
	run.result_merged AS result,
	archiving.attempts,
	archiving.last_attempt
    FROM
        archiving
	JOIN archiver ON archiver.id = archiving.archiver
	JOIN run ON run.id = archiving.run
	JOIN task ON task.id = run.task
	JOIN tool ON tool.id = task.tool
    WHERE
        NOT archived
        AND next_attempt < now()
    ORDER BY next_attempt
;


--
-- Maintenance
--

-- Maintenance functions


CREATE OR REPLACE FUNCTION archiving_maint_minute()
RETURNS VOID
AS $$
DECLARE
    diag JSONB;
    default_next_attempt TIMESTAMP WITH TIME ZONE;
BEGIN

    -- Force archivings that have seen no attempts by their TTL into a
    -- failed state.

    diag := '{ "return-code": 1,
               "stdout": "",
               "stderr": "Time to live expired before first attempt"}';
    diag := jsonb_set(diag, '{"time"}',
        to_jsonb(timestamp_with_time_zone_to_iso8601(normalized_now())), TRUE);

    UPDATE archiving
    SET
        archived = TRUE,     -- Not really, but gets the attempt off the table.
        next_attempt = NULL,
        diags = diags || diag::JSONB
    WHERE
        NOT archived
	-- Note that this must be the same as the default in the table.
        AND next_attempt = '-infinity'
        AND attempts = 0
        AND ttl_expires < now();

END;
$$ LANGUAGE plpgsql;
