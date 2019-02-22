--
-- Table of daemon heartbeat records
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

    t_name := 'heartbeat';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE heartbeat (

        	-- Row identifier
        	name		TEXT
        			PRIMARY KEY,

        	-- Update count
        	updates		BIGINT DEFAULT 0,


        	-- When this record was last updated
        	last		TIMESTAMP WITH TIME ZONE
				DEFAULT now(),

        	-- How long until the next heartbeat is expected, NULL if we don't know.
        	next_time	INTERVAL
        );

	t_version := t_version + 1;

    END IF;

    -- Version 1 to version 2
    -- ...Description...
    -- IF t_version = 1
    -- THEN
    --     ALTER TABLE tool DROP COLUMN version;
    --
    --     t_version := t_version + 1;
    -- END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;




DROP TRIGGER IF EXISTS heartbeat_alter ON heartbeat CASCADE;

CREATE OR REPLACE FUNCTION heartbeat_alter()
RETURNS TRIGGER
AS $$
DECLARE
    json_result TEXT;
BEGIN
    NEW.last = now();
    NEW.updates = NEW.updates + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER heartbeat_alter
BEFORE INSERT OR UPDATE
ON heartbeat
FOR EACH ROW
    EXECUTE PROCEDURE heartbeat_alter();



-- Insert a new heartbeat or update an existing one by name

DO $$ BEGIN PERFORM drop_function_all('heartbeat'); END $$;

CREATE OR REPLACE FUNCTION heartbeat(new_name TEXT, new_next_time INTERVAL DEFAULT NULL)
RETURNS VOID
AS $$
BEGIN

    INSERT INTO heartbeat (name, next_time)
    VALUES (new_name, new_next_time)
    ON CONFLICT (name) DO UPDATE
    SET
        next_time = new_next_time
    ;

END;
$$ LANGUAGE plpgsql;



-- Function to run at startup.

DO $$ BEGIN PERFORM drop_function_all('heartbeat_cold_boot'); END $$;

CREATE OR REPLACE FUNCTION heartbeat_cold_boot()
RETURNS VOID
AS $$
BEGIN
    DELETE FROM heartbeat;
END;
$$ LANGUAGE plpgsql;



-- Full-content view

DROP VIEW IF EXISTS heartbeat_full CASCADE;

CREATE OR REPLACE VIEW heartbeat_full
AS
    SELECT
        name,
	updates,
        timestamp_with_time_zone_to_iso8601(last) AS last,
	CASE
	    WHEN next_time IS NOT NULL
	        THEN interval_to_iso8601(next_time)
	    ELSE NULL
	END AS next_time,
	CASE
	    WHEN next_time IS NOT NULL
	        THEN timestamp_with_time_zone_to_iso8601(last + next_time)
	    ELSE NULL
	END AS expected,
        CASE
            WHEN (last + next_time) < now()
	        THEN interval_to_iso8601(now() - (last + next_time))
            ELSE NULL
        END AS overdue
    FROM heartbeat
    ORDER BY NAME
;


-- JSON for the API to pass along

CREATE OR REPLACE VIEW heartbeat_json
AS
    select json_agg(tbl) FROM (SELECT * FROM heartbeat_full) tbl;
;
