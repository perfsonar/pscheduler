--
-- Tables of tools and the tests they run.
--

-- NOTE: Rows in this table should only be maintained (i.e., inserted
-- or updated) using the tool_upsert() function.
-- TODO: Use native upserting when Pg is upgraded to 9.5

DO $$
DECLARE
    t_name TEXT;            -- Name of the table being worked on
    t_version INTEGER;      -- Current version of the table
    t_version_old INTEGER;  -- Version of the table at the start
BEGIN

    --
    -- Preparation
    --

    t_name := 'tool';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE tool (

        	-- Row identifier
        	id		BIGSERIAL
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


--
-- Breaker table that maps tools to the tests they can run
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

    t_name := 'tool_test';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

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



CREATE OR REPLACE FUNCTION tool_json_is_valid(json JSONB)
RETURNS BOOLEAN
AS $$
BEGIN
    RETURN (json ->> 'name') IS NOT NULL
      AND (text_to_numeric(json ->> 'version', false) IS NOT NULL)
      AND (text_to_numeric(json ->> 'preference', false) IS NOT NULL);
END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS tool_alter ON tool CASCADE;

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



DROP TRIGGER IF EXISTS tool_alter_post ON tool CASCADE;

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



DROP TRIGGER IF EXISTS tool_delete ON tool CASCADE;

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
    sschema NUMERIC;  -- Name dodges a reserved word
BEGIN
    run_result := pscheduler_internal(ARRAY['list', 'tool']);
    IF run_result.status <> 0 THEN
       RAISE EXCEPTION 'Unable to list installed tools: %', run_result.stderr;
    END IF;

    tool_list := run_result.stdout::JSONB;

    FOR tool_name IN (select * from jsonb_array_elements_text(tool_list))
    LOOP

	run_result := pscheduler_internal(ARRAY['invoke', 'tool', tool_name, 'enumerate']);
        IF run_result.status <> 0 THEN
            RAISE WARNING 'Tool "%" failed to enumerate: %',
	        tool_name, run_result.stderr;
            CONTINUE;
        END IF;

	tool_enumeration := run_result.stdout::JSONB;

        sschema := text_to_numeric(tool_enumeration ->> 'schema');
        IF sschema IS NOT NULL AND sschema > 1 THEN
            RAISE WARNING 'Tool "%": schema % is not supported',
                tool_name, sschema;
            CONTINUE;
        END IF;

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



-- Determine whether or not a tool is willing to run a specific test.


-- TODO: Drop this after the first release
DROP FUNCTION IF EXISTS tool_can_run_test(tool_id BIGINT, test JSONB);

CREATE OR REPLACE FUNCTION tool_can_run_test(
    tool_id BIGINT,
    test JSONB,
    lead_bind TEXT DEFAULT NULL  -- HACK: BWCTLBC
)
RETURNS BOOLEAN
AS $$
DECLARE
    tool_name TEXT;
    run_result external_program_result;
    result_json JSONB;
    lead_bind_array TEXT[];  -- HACK: BWTCLBC
BEGIN

    SELECT INTO tool_name name FROM tool WHERE id = tool_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tool ID % is invalid', tool_id;
    END IF;

    -- HACK: BWCTLBC
    IF lead_bind IS NOT NULL THEN
        lead_bind_array := ARRAY['PSCHEDULER_LEAD_BIND_HACK', lead_bind];
    ELSE
        lead_bind_array := ARRAY[]::TEXT[];
    END IF;

    run_result := pscheduler_internal(
        ARRAY['invoke', 'tool', tool_name, 'can-run'], test::TEXT, 5,
        lead_bind_array  -- HACK: BWCTLBC
        );

    -- Any result other than 1 indicates a problem that shouldn't be
    -- allowed to gum up the works.  Log it and assume the tool said
    -- no dice.
    IF run_result.status <> 0 THEN
        RAISE WARNING 'Tool "%" failed can-run: %', tool_name, run_result.stderr;
        RETURN FALSE;
    END IF;

    result_json = text_to_jsonb(run_result.stdout);
    IF result_json IS NULL THEN
        RAISE WARNING 'Tool "%" returned invalid JSON "%"', tool_name, run_result.stdout;
        RETURN FALSE;
    END IF;

    RETURN result_json #> '{can-run}';

END;
$$ LANGUAGE plpgsql;



--
-- API
--

-- Get a JSON array of the enumerations of all tools that can run a
-- test, returned in order of highest to lowest preference.

-- TODO: Remove this after release
DROP FUNCTION IF EXISTS api_tools_for_test(JSONB);

CREATE OR REPLACE FUNCTION api_tools_for_test(
    test_json JSONB,
    lead_bind TEXT DEFAULT NULL  -- HACK: BWCTLBC
)
RETURNS JSON
AS $$
DECLARE
    test_type TEXT;
    return_json JSON;
BEGIN

    test_type := test_json ->> 'type';
    IF test_type IS NULL THEN
        RAISE EXCEPTION 'No test type found in JSON';
    END IF;

    SELECT INTO return_json
        array_to_json(array_agg(tools.tool_json))
    FROM (
        SELECT
            tool.json AS tool_json
        FROM
	    test
            JOIN tool_test ON tool_test.test = test.id
	    JOIN tool ON tool.id = tool_test.tool
        WHERE
	    test.name = test_type
            AND test.available
            AND tool.available
            AND tool_can_run_test( tool.id, test_json, lead_bind ) -- HACK: BWCTLBC
        ORDER BY
            tool.preference DESC,
            tool.name ASC
    ) tools;

    RETURN return_json;
END;
$$ LANGUAGE plpgsql;
