--
-- UTILITIES
-- 
--

-- ----------------------------------------------------------------------------

--
-- CONVERSIONS
--

-- All of these functions take a TEXT value and attempt to convert it
-- into the return type.  If the 'picky' argument is TRUE, the
-- function will raise an exception if the conversion fails, otherwise
-- it will return NULL.

-- TODO: In all of these, need to look at whether we should narrow the
-- exception down to something more specific than 'OTHERS'.

CREATE OR REPLACE FUNCTION 
text_to_timestamp_with_time_zone(
	value TEXT,
	picky BOOL DEFAULT TRUE
)
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
DECLARE
	converted TIMESTAMP WITH TIME ZONE DEFAULT NULL;
BEGIN

    -- Special case: "forever" and "infinity" map to Pg's infinity.
    -- Regular SQL would have to use the largest value.
    IF value = 'forever' THEN
       RETURN 'infinity';
    END IF;

    BEGIN
	converted := value::TIMESTAMP WITH TIME ZONE;
    EXCEPTION WHEN OTHERS THEN
        IF picky THEN
	    RAISE EXCEPTION 'Invalid timestamp "%"', value;
	ELSE
	    RETURN NULL;
	END IF;	
    END;
RETURN converted;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION 
text_to_interval(
	value TEXT,
	picky BOOL DEFAULT TRUE
)
RETURNS INTERVAL
AS $$
DECLARE
	converted INTERVAL DEFAULT NULL;
BEGIN
    BEGIN
	converted := value::INTERVAL;
    EXCEPTION WHEN OTHERS THEN
        IF picky THEN
	    RAISE EXCEPTION 'Invalid interval "%"', value;
	ELSE
	    RETURN NULL;
	END IF;	
    END;
RETURN converted;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION 
text_to_numeric(
	value TEXT,
	picky BOOL DEFAULT TRUE
)
RETURNS NUMERIC
AS $$
DECLARE
	converted NUMERIC DEFAULT NULL;
BEGIN
    BEGIN
	converted := value::NUMERIC;
    EXCEPTION WHEN OTHERS THEN
        IF picky THEN
	    RAISE EXCEPTION 'Invalid numeric "%"', value;
	ELSE
	    RETURN NULL;
	END IF;	
    END;
RETURN converted;
END;
$$ LANGUAGE plpgsql;


-- ----------------------------------------------------------------------------

--
-- DATE AND TIME
--

-- Truncate a timestamp to our scheduling increment (seconds)
CREATE OR REPLACE FUNCTION normalized_time(value TIMESTAMP WITH TIME ZONE)
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
BEGIN
	RETURN date_trunc('seconds', value);
END;
$$LANGUAGE plpgsql;


-- Return the normalized current (transaction start) time
CREATE OR REPLACE FUNCTION normalized_now()
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
BEGIN
	RETURN normalized_time(now());
END;
$$LANGUAGE plpgsql;


-- Return the normalized wall clock time
CREATE OR REPLACE FUNCTION normalized_wall_clock()
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
BEGIN
	RETURN normalized_time(clock_timestamp());
END;
$$LANGUAGE plpgsql;
