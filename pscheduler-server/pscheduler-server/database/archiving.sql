--
-- Table of archiving records for a run
--

DROP TABLE IF EXISTS archiving CASCADE;
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

	-- Whether or not this archiving has been completed
	archived   	BOOLEAN
			DEFAULT FALSE,

	-- When we should try again if not successful
	next_attempt  	TIMESTAMP WITH TIME ZONE
			DEFAULT '-infinity'::TIMESTAMP WITH TIME ZONE,

	-- Array of results from each attempt
	diags	   	JSONB
			DEFAULT '[]'::JSONB
);



DROP TRIGGER IF EXISTS archiving_run_after ON archiving CASCADE;

CREATE OR REPLACE FUNCTION archiving_run_after()
RETURNS TRIGGER
AS $$
DECLARE
    inserted BOOLEAN;
    archive JSONB;
BEGIN

    -- Start an archive if conditions are right

    IF ( -- Non-Background run
         TG_OP = 'UPDATE'
         AND OLD.result_merged IS NULL 
         AND NEW.result_merged IS NOT NULL )
       OR ( -- Background Run
            TG_OP = 'INSERT'
            AND NEW.state = run_state_finished()
            AND NEW.result_merged IS NOT NULL
            AND EXISTS (SELECT *
                        FROM
                            task
                            JOIN test ON test.id = task.test
                        WHERE
                            task.id = NEW.task
                            AND test.scheduling_class = scheduling_class_background())
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

                        UNION

                        -- System-wide default archivers
                        SELECT archive_default.archive FROM archive_default
                       )
        LOOP
	    INSERT INTO archiving (run, archiver, archiver_data)
    	    VALUES (
    	        NEW.id,
    	        (SELECT id from archiver WHERE name = archive #>> '{archiver}'),
	        (archive #> '{data}')::JSONB
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



DROP TRIGGER IF EXISTS archiving_alter ON archiving CASCADE;

CREATE OR REPLACE FUNCTION archiving_alter()
RETURNS TRIGGER
AS $$
BEGIN

    -- TODO: If there's an update to diags, append it instead of replacing it.

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archiving_alter BEFORE INSERT OR UPDATE ON archiving
       FOR EACH ROW EXECUTE PROCEDURE archiving_alter();



-- A handy view for the archiver to use

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
;
