--
-- API for the Outside World
--

-- Get a JSON array of the enumerations of all tools that can run a
-- test, returned in order of highest to lowest preference.

CREATE OR REPLACE FUNCTION api_tools_for_test(
    test_json JSONB
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
            AND tool_can_run_test( tool.id, test_json )
        ORDER BY
            tool.preference DESC,
            tool.name ASC
    ) tools;

    RETURN return_json;
END;
$$ LANGUAGE plpgsql;



-- Put a task on the timeline and return its ID

CREATE OR REPLACE FUNCTION api_task_add(
    task_package JSONB,
    tool_name TEXT,
    participant INTEGER DEFAULT 0
)
RETURNS TABLE (
    id BIGINT,      -- New task's ID
    slip INTERVAL  -- How much more the task could slip
)
AS $$
DECLARE
    tool_id INTEGER;
    new_id BIGINT;
    inserted RECORD;
    result RECORD;
BEGIN

    SELECT INTO tool_id tool.id FROM tool
      WHERE name = tool_name;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown tool "%"', tool_name;
    END IF;

    WITH inserted_row AS (
        INSERT INTO task(json, tool, participant)
        VALUES (task_package, tool_id, participant )
           RETURNING *
    ) SELECT INTO inserted * from inserted_row;

    RETURN QUERY SELECT
        inserted.id,
        'P0'::INTERVAL
        ;

END;
$$ LANGUAGE plpgsql;
