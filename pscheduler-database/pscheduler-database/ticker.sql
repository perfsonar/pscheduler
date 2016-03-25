--
-- Ticker Stored Procedure
--


-- Things that get done a fifteen-second intervals
CREATE OR REPLACE FUNCTION ticker_fifteen()
RETURNS VOID
AS $$
BEGIN
    PERFORM task_maint_fifteen();
    PERFORM run_maint_fifteen();
END;
$$ LANGUAGE plpgsql;


-- Things that get done a one-minute intervals
CREATE OR REPLACE FUNCTION ticker_minute()
RETURNS VOID
AS $$
BEGIN
    NULL;
END;
$$ LANGUAGE plpgsql;


-- Things that get done on the hour
CREATE OR REPLACE FUNCTION ticker_hour()
RETURNS VOID
AS $$
BEGIN
    NULL;
END;
$$ LANGUAGE plpgsql;


-- Things that get done daily, but not necessarily at midnight
CREATE OR REPLACE FUNCTION ticker_day()
RETURNS VOID
AS $$
BEGIN
    NULL;
END;
$$ LANGUAGE plpgsql;


-- Things that get done at midnight
CREATE OR REPLACE FUNCTION ticker_midnight()
RETURNS VOID
AS $$
BEGIN
    NULL;
END;
$$ LANGUAGE plpgsql;



-- Cron on a budget.  This should be called once per minute,
-- preferably as close to the minute boundary as possible.  This
-- should be called repeatedly from outside to prevent having a
-- long-running transaction.

CREATE OR REPLACE FUNCTION ticker()
RETURNS INTERVAL
AS $$
DECLARE
    this_minute TIMESTAMP WITH TIME ZONE;
    clock_time TIMESTAMP WITH TIME ZONE;
BEGIN

    PERFORM ticker_fifteen();

    -- Allow a small amount of slop for minute intervals.
    IF EXTRACT(SECOND FROM now()) BETWEEN 0 and 5 THEN
        PERFORM ticker_minute();
    END IF;

    this_minute := date_trunc('minute', now());

    IF this_minute = date_trunc('hour', now()) THEN
        PERFORM ticker_hour();
    END IF;

    IF this_minute = date_trunc('day', now()) THEN
        PERFORM ticker_midnight();
    END IF;

    -- Use the actual wall clock time to determine how long until the
    -- next call (0/15/30/45 seconds within each minute).  This will
    -- compensate for any time consumed running the periodic
    -- functions.

    clock_time := clock_timestamp();  -- Note:  Not standard SQL
    RETURN
        date_trunc('minute', clock_time)
        + (TRUNC(EXTRACT(SECONDS FROM clock_time) / 15) + 1)
           * 'PT15S'::interval
        - (clock_time - 'PT1S'::interval);

END;
$$ LANGUAGE plpgsql;
