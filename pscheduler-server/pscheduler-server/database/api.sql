--
-- API for the Outside World
--

-- Get a list of the tools that can run a task in
-- most-to-least-preferred order.

CREATE OR REPLACE FUNCTION api_tools_for_task(
    task_package JSONB
)
RETURNS TABLE (
    tool TEXT,
    description TEXT,
    version NUMERIC,
    preference INTEGER
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        tool.name,
	tool.description,
	tool.version,
	tool.preference
    FROM
        test
        JOIN tool_test ON tool_test.test = test.id
        JOIN tool ON tool.id = tool_test.tool
    WHERE
        test.name = 'idle'
        AND test.available
        AND tool.available
        AND tool_can_run_task( tool.name, task_package )
    ORDER BY
      tool.preference DESC,
      tool.name ASC
    ;
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
