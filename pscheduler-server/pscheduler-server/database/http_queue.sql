--
-- Queue of Pending HTTP Operations
--

-- This table holds a list of HTTP operations to be carried out until
-- successful.  One attempt to process each row after INSERT so the
-- query is handled immediately.  Failing queries will remain in the
-- table and retried at their specified interval until they expire.

DO $$
DECLARE
    t_name TEXT;            -- Name of the table being worked on
    t_version INTEGER;      -- Current version of the table
    t_version_old INTEGER;  -- Version of the table at the start
BEGIN

    --
    -- Preparation
    --

    t_name := 'http_queue';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE http_queue (

        	-- Row identifier
        	id		BIGSERIAL
        			PRIMARY KEY,

		operation	TEXT
        			CHECK (operation IN ('GET', 'PUT',
				                     'POST', 'DELETE')),

        	-- URI to fetch
        	uri		TEXT
        			NOT NULL,

        	-- Payload for GET and PUT
        	payload		TEXT
        			CHECK (NULL OR operation IN ('GET', 'PUT')),

        	-- How often to try after the first attempt
        	try_interval	INTERVAL
        			DEFAULT 'PT5M',

        	-- How long to keep trying.  This will be defaulted on INSERT.
        	try_for	     	INTERVAL,

        	-- When added
        	added		TIMESTAMP WITH TIME ZONE
        			DEFAULT now(),

        	-- When to stop trying
        	expires		TIMESTAMP WITH TIME ZONE,

        	-- Last time an attempt was made
        	last_attempt	TIMESTAMP WITH TIME ZONE,

        	-- Last status returned
        	last_status	INTEGER,

        	-- Last result returned
        	last_returned	TEXT,

        	-- Last time an attempt was made
        	next_attempt	TIMESTAMP WITH TIME ZONE
        			DEFAULT now(),

        	-- Attempts so far (really just for information)
        	attempts	INTEGER
        			DEFAULT 0

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



-- Process one item in the table by its row ID

CREATE OR REPLACE FUNCTION http_queue_process(
    row_id BIGINT
)
RETURNS VOID
AS $$
DECLARE
    entry RECORD;
    status http_result;
    status_family INTEGER;
BEGIN

    SELECT INTO entry * from http_queue WHERE id = row_id;
    IF NOT FOUND
    THEN
        RETURN;
    END IF;

    -- TODO: Try the fetch/post/whatever

    IF entry.operation = 'DELETE'
    THEN
	status := http_delete(entry.uri);
    ELSEIF entry.operation = 'GET'
    THEN
	status := http_get(entry.uri);
    ELSEIF entry.operation = 'POST'
    THEN
	status := http_post(entry.uri, entry.payload);
    ELSEIF entry.operation = 'PUT'
    THEN
	status := http_put(entry.uri, entry.payload);
    ELSE
        RAISE EXCEPTION 'Unsupported operation %', entry.operation;
    END IF;

    status_family := (status.status/100)::INTEGER;

    IF status_family IN (1, 2, 3) -- Successful results
        OR now() + entry.try_interval > entry.expires
    THEN
        -- No need to keep succeeded or expired records around
        DELETE FROM http_queue WHERE id = entry.id;
    ELSE
        -- Set up the next attempt
        UPDATE http_queue
        SET
            attempts = attempts + 1,
	    last_status = status.status,
	    last_returned = status.returned,
            last_attempt = now(),
            next_attempt = now() + entry.try_interval
        WHERE id = row_id;
    END IF;

END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS http_queue_insert ON http_queue CASCADE;

CREATE OR REPLACE FUNCTION http_queue_insert()
RETURNS TRIGGER
AS $$
BEGIN

    IF NEW.try_for IS NULL
    THEN
        SELECT INTO NEW.try_for keep_runs_tasks FROM configurables;
    END IF;
    NEW.expires = NEW.added + NEW.try_for;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER http_queue_insert
BEFORE INSERT ON http_queue
FOR EACH ROW EXECUTE PROCEDURE http_queue_insert();




DROP TRIGGER IF EXISTS http_queue_insert_after ON http_queue CASCADE;

CREATE OR REPLACE FUNCTION http_queue_insert_after()
RETURNS TRIGGER
AS $$
BEGIN
    PERFORM http_queue_process(NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER http_queue_insert_after
AFTER INSERT ON http_queue
FOR EACH ROW EXECUTE PROCEDURE http_queue_insert_after();



-- Maintenance functions

-- Maintenance that happens once per minute

CREATE OR REPLACE FUNCTION http_queue_maint_minute()
RETURNS VOID
AS $$
BEGIN
    PERFORM http_queue_process(id) FROM http_queue WHERE next_attempt < now();
END;
$$ LANGUAGE plpgsql;
