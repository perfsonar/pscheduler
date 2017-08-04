--
-- Functions for handling various kinds of boots
--


CREATE OR REPLACE FUNCTION warm_boot()
RETURNS VOID
AS $$
BEGIN
    -- These are nondestructive and load the lists.
    PERFORM test_boot();
    PERFORM tool_boot();
    PERFORM archiver_boot();
    PERFORM context_boot();
    NOTIFY warmboot;
END;
$$ LANGUAGE plpgsql;


-- This is invoked by the ticker when it starts
CREATE OR REPLACE FUNCTION cold_boot()
RETURNS VOID
AS $$
BEGIN
    PERFORM warm_boot();
END;
$$ LANGUAGE plpgsql;
