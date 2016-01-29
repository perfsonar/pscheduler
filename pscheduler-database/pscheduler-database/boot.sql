--
-- Stored Procedure Run When the ticker starts
--


-- Things that get done a one-minute intervals
CREATE OR REPLACE FUNCTION boot()
RETURNS VOID
AS $$
BEGIN
    PERFORM test_boot();
    PERFORM tool_boot();
    PERFORM archiver_boot();
END;
$$ LANGUAGE plpgsql;
