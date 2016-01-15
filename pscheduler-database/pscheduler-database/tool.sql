--
-- Tables of tools and the tests they run.
--

-- NOTE: Rows in this table should only be maintained (i.e., inserted
-- or updated) using the tool_upsert() function.
-- TODO: Use native upserting when Pg is upgraded to 9.5


DROP TABLE IF EXISTS tool CASCADE;
CREATE TABLE tool (

	-- Row identifier
	id		SERIAL
			PRIMARY KEY,

	-- Original JSON
	json		JSONB
			NOT NULL,

	-- Tool Name
	name		TEXT
			UNIQUE NOT NULL,

	-- Verbose description
	description	TEXT,

	-- Version
	version		NUMERIC
			NOT NULL,

	-- Preference value
	preference      INTEGER
			DEFAULT 0,

	-- When this record was last updated
	updated		TIMESTAMP WITH TIME ZONE,

	-- Whether or not the tool is currently available
	available	BOOLEAN
			DEFAULT TRUE
);


CREATE INDEX tool_name ON tool(name);


DROP TABLE IF EXISTS tool_test CASCADE;
CREATE TABLE tool_test (

	-- Tool which says it can handle a test
	tool		INTEGER
			REFERENCES tool(id)
			ON DELETE CASCADE,

	-- The test the tool says it can handle
	test		INTEGER
			REFERENCES test(id)
			ON DELETE CASCADE
);



CREATE OR REPLACE FUNCTION tool_json_is_valid(json JSONB)
RETURNS BOOLEAN
AS $$
BEGIN
    RETURN (json ->> 'name') IS NOT NULL
      AND (text_to_numeric(json ->> 'version', false) IS NOT NULL)
      AND (text_to_numeric(json ->> 'preference', false) IS NOT NULL);
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION tool_alter()
RETURNS TRIGGER
AS $$
BEGIN
    IF NOT tool_json_is_valid(NEW.json) THEN
        RAISE EXCEPTION 'Tool JSON is invalid.';
    END IF;

    NEW.name := NEW.json ->> 'name';
    NEW.description := NEW.json ->> 'description';
    NEW.version := text_to_numeric(NEW.json ->> 'version');
    NEW.preference := text_to_numeric(NEW.json ->> 'preference');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tool_alter
BEFORE INSERT OR UPDATE
ON tool
FOR EACH ROW
    EXECUTE PROCEDURE tool_alter();



CREATE OR REPLACE FUNCTION tool_alter_post()
RETURNS TRIGGER
AS $$
DECLARE
    test_name TEXT;
    test_id INTEGER;
BEGIN

    -- Update the breaker table between this and test.

    DELETE FROM tool_test WHERE tool = NEW.id;

    FOR test_name IN
        (SELECT * FROM jsonb_array_elements_text(NEW.json -> 'tests'))
    LOOP
        -- Only insert records for tests that are installed on the system.
        SELECT id INTO test_id FROM test WHERE name = test_name;
	IF FOUND THEN
	    INSERT INTO tool_test (tool, test)
	        VALUES (NEW.id, test_id);
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tool_alter_post
AFTER INSERT OR UPDATE
ON tool
FOR EACH ROW
    EXECUTE PROCEDURE tool_alter_post();



CREATE OR REPLACE FUNCTION tool_delete()
RETURNS TRIGGER
AS $$
BEGIN
    DELETE FROM tool_test where tool = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tool_delete
BEFORE DELETE
ON tool
FOR EACH ROW
    EXECUTE PROCEDURE tool_delete();






-- Insert a new tool or update an existing one by name
CREATE OR REPLACE FUNCTION tool_upsert(new_json JSONB)
RETURNS VOID
AS $$
DECLARE
    existing_id INTEGER;
    new_name TEXT;
BEGIN

   new_name := (new_json ->> 'name')::TEXT;

   SELECT id from tool into existing_id WHERE name = new_name;

   IF NOT FOUND THEN

      -- Legitimately-new row.
      INSERT INTO tool (json, updated, available)
      VALUES (new_json, now(), true);

   ELSE

     -- Update of existing row.
     UPDATE tool
     SET
       json = new_json,
       updated = now(),
       available = true
     WHERE id = existing_id;

   END IF;

END;
$$ LANGUAGE plpgsql;




-- Function to run at startup.
CREATE OR REPLACE FUNCTION tool_boot()
RETURNS VOID
AS $$
DECLARE
    run_result external_program_result;
    tool_list JSONB;
    tool_name TEXT;
    tool_enumeration JSONB;
BEGIN
    run_result := pscheduler_internal(ARRAY['list', 'tool']);
    IF run_result.status != 0 THEN
       RAISE EXCEPTION 'Unable to list installed tools: %', run_result.stderr;
    END IF;

    tool_list := run_result.stdout::JSONB;

    FOR tool_name IN (select * from jsonb_array_elements_text(tool_list))
    LOOP

	run_result := pscheduler_internal(ARRAY['invoke', 'tool', tool_name, 'enumerate']);
        IF run_result.status != 0 THEN
         RAISE EXCEPTION 'Tool "%" failed to enumerate: %',
	       tool_name, run_result.stderr;
        END IF;

	tool_enumeration := run_result.stdout::JSONB;

	IF NOT tool_json_is_valid(tool_enumeration) THEN
	    RAISE WARNING 'Tool "%" enumeration is invalid', tool_name;
	    CONTINUE;
	END IF;

	PERFORM tool_upsert(tool_enumeration);

    END LOOP;

    -- TODO: Disable, but don't remove, tools that aren't installed.
    UPDATE tool SET available = FALSE WHERE updated < now();
    -- TODO: Should also can anything on the schedule.  (Do that elsewhere.)
END;
$$ LANGUAGE plpgsql;



-- Determine whether or not a tool is willing to run a specific test

CREATE OR REPLACE FUNCTION tool_can_run_task(tool_name TEXT, task JSONB)
RETURNS BOOLEAN
AS $$
DECLARE
    run_result external_program_result;
BEGIN
    IF NOT EXISTS (SELECT * FROM tool where name = tool_name) THEN
        RAISE EXCEPTION 'Tool "%" is not installed.', tool_name;
    END IF;

    run_result := pscheduler_internal(ARRAY['invoke', 'tool', tool_name, 'can-run'], task::TEXT);

    IF run_result.status = 0 THEN
        RETURN TRUE;
    END IF;

    IF run_result.status <> 1 THEN
        -- TODO: Log something
        NULL;
    END IF;

    RETURN FALSE;

END;
$$ LANGUAGE plpgsql;


-- TODO: For multi-participant, will need a function that will return
-- a list of the tools in order of preference.
