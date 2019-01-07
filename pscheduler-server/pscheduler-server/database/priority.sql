--
-- Priority
--


DO $$ BEGIN PERFORM drop_function_all('priority_default'); END $$;

CREATE OR REPLACE FUNCTION 
priority_default()
RETURNS INTEGER
AS $$
BEGIN
    RETURN 0;
END;
$$ LANGUAGE plpgsql
IMMUTABLE;


DO $$ BEGIN PERFORM drop_function_all('priority_min'); END $$;

CREATE OR REPLACE FUNCTION 
priority_min()
RETURNS INTEGER
AS $$
BEGIN
    RETURN -2147483648;
END;
$$ LANGUAGE plpgsql
IMMUTABLE;


DO $$ BEGIN PERFORM drop_function_all('priority_max'); END $$;

CREATE OR REPLACE FUNCTION 
priority_max()
RETURNS INTEGER
AS $$
BEGIN
    RETURN 2147483647;
END;
$$ LANGUAGE plpgsql
IMMUTABLE;

