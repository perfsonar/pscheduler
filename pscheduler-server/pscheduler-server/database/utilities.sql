--
-- UTILITIES
-- 
--


-- ----------------------------------------------------------------------------

--
-- CONVERSIONS
--

-- Most of these functions take a TEXT value and attempt to convert it
-- into the return type.  If the 'picky' argument is TRUE, the
-- function will raise an exception if the conversion fails, otherwise
-- it will return NULL.

-- TODO: In all of these, need to look at whether we should narrow the
-- exception down to something more specific than 'OTHERS'.

DO $$ BEGIN PERFORM drop_function_all('text_to_timestamp_with_time_zone'); END $$;

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



DO $$ BEGIN PERFORM drop_function_all('timestamp_with_time_zone_to_iso8601'); END $$;

CREATE OR REPLACE FUNCTION 
timestamp_with_time_zone_to_iso8601(
	value TIMESTAMP WITH TIME ZONE
)
RETURNS TEXT
AS $$
BEGIN

    IF value IS NULL
    THEN
        RETURN NULL;
    END IF;

    return to_json(date_trunc('seconds', value)) #>> '{}';

END;
$$ LANGUAGE plpgsql;


DO $$ BEGIN PERFORM drop_function_all('interval_to_iso8601'); END $$;

CREATE OR REPLACE FUNCTION interval_to_iso8601(period INTERVAL)
RETURNS TEXT
AS $$
DECLARE
    extracted NUMERIC;
    days NUMERIC;
    weeks NUMERIC;
    use_t BOOLEAN;
    iso TEXT;
BEGIN

    iso = '';
    use_t = FALSE;

    extracted = EXTRACT('SECONDS' FROM period);
    IF extracted > 0
    THEN
        iso := to_char(extracted, 'FM999999999') || 'S' || iso;
        use_t := TRUE;
    END IF;

    extracted = EXTRACT('MINUTES' FROM period);
    IF extracted > 0
    THEN
        iso := to_char(extracted, 'FM999999999') || 'M' || iso;
        use_t := TRUE;
    END IF;

    extracted = EXTRACT('HOURS' FROM period);
    IF extracted > 0
    THEN
        iso := to_char(extracted, 'FM999999999') || 'H' || iso;
        use_t := TRUE;
    END IF;

    IF use_t
    THEN
        iso := 'T' || iso;
    END IF;

    extracted = EXTRACT('DAYS' FROM period);
    IF extracted > 0
    THEN

        days := extracted % 7;
	IF days > 0
        THEN
            iso := to_char(days, 'FM999999999') || 'D' || iso;
        END IF;

        extracted := extracted - days;
        IF extracted > 0
        THEN
            iso := to_char(extracted / 7, 'FM999999999') || 'W' || iso;
        END IF;

    END IF;

    IF ISO = ''
    THEN
        RETURN 'P0D';
    END IF;

    RETURN 'P' || iso;
END;
$$ LANGUAGE plpgsql;




DO $$ BEGIN PERFORM drop_function_all('text_to_interval'); END $$;

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



DO $$ BEGIN PERFORM drop_function_all('text_to_numeric'); END $$;

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


DO $$ BEGIN PERFORM drop_function_all('text_to_jsonb'); END $$;

CREATE OR REPLACE FUNCTION 
text_to_jsonb(
	value TEXT,
	picky BOOL DEFAULT TRUE
)
RETURNS JSONB
AS $$
DECLARE
	converted JSONB DEFAULT NULL;
BEGIN
    BEGIN
	converted := value::JSONB;
    EXCEPTION WHEN OTHERS THEN
        IF picky THEN
	    RAISE EXCEPTION 'Invalid JSON "%"', value;
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

DO $$ BEGIN PERFORM drop_function_all('normalized_time'); END $$;

CREATE OR REPLACE FUNCTION normalized_time(value TIMESTAMP WITH TIME ZONE)
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
BEGIN
	RETURN date_trunc('seconds', value);
END;
$$LANGUAGE plpgsql;


-- Return the normalized current (transaction start) time

DO $$ BEGIN PERFORM drop_function_all('normalized_now'); END $$;

CREATE OR REPLACE FUNCTION normalized_now()
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
BEGIN
	RETURN normalized_time(now());
END;
$$LANGUAGE plpgsql;


-- Return the normalized wall clock time

DO $$ BEGIN PERFORM drop_function_all('normalized_wall_clock'); END $$;

CREATE OR REPLACE FUNCTION normalized_wall_clock()
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
BEGIN
	RETURN normalized_time(clock_timestamp());
END;
$$LANGUAGE plpgsql;




-- Practical alternatives to infinite timestamps for use with intervals.
--
-- These exist because PostgreSQL does not yet support infinite
-- intervals (been in the plans since before 2008, apparently).  As a
-- substitute, the minimum/maximum dates supported by the TIMESTAMP
-- WITH TIME ZONE type are provided here.
--
-- See:
--   https://wiki.postgresql.org/wiki/Todo#Dates_and_Times
--   http://www.postgresql.org/docs/9.5/static/datatype-datetime.html


DO $$ BEGIN PERFORM drop_function_all('tstz_negative_infinity'); END $$;

CREATE OR REPLACE FUNCTION tstz_negative_infinity()
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
BEGIN
	RETURN '4713-01-01 BC'::TIMESTAMP WITH TIME ZONE;
END;
$$LANGUAGE plpgsql;


DO $$ BEGIN PERFORM drop_function_all('tstz_infinity'); END $$;

CREATE OR REPLACE FUNCTION tstz_infinity()
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
BEGIN
	RETURN '294276-12-31'::TIMESTAMP WITH TIME ZONE;
END;
$$LANGUAGE plpgsql;





-- Find the next even occurence of a specified interval, truncating
-- fractional seconds from both.  For example, '2016-02-02
-- 11:27:36-05' and 'PT1H' would yield '2016-02-02 12:00:00-05'

DO $$ BEGIN PERFORM drop_function_all('time_next_interval'); END $$;

CREATE OR REPLACE FUNCTION time_next_interval(
    start TIMESTAMP WITH TIME ZONE,
    round_to INTERVAL
)
RETURNS TIMESTAMP WITH TIME ZONE
AS $$
DECLARE
    start_epoch NUMERIC;
    round_to_epoch NUMERIC;
BEGIN
    -- Convert times to epoch with fractional seconds

    start_epoch := EXTRACT(EPOCH FROM start);
    round_to_epoch := EXTRACT(EPOCH FROM round_to);

    RETURN to_timestamp(
        (TRUNC(start_epoch / round_to_epoch)::NUMERIC + 1)
	* round_to_epoch
	);
END;
$$ LANGUAGE plpgsql;


-- Round an interval up to the next whole second if there are any
-- fractional seconds.

DO $$ BEGIN PERFORM drop_function_all('interval_round_up'); END $$;

CREATE OR REPLACE function interval_round_up(candidate INTERVAL)
RETURNS INTERVAL
AS $$
DECLARE
    microseconds INTEGER;
BEGIN
    microseconds := EXTRACT(MICROSECONDS FROM candidate)::INTEGER % 1000000;
    IF microseconds > 0 THEN
        microseconds := 1000000 - microseconds;
	candidate = candidate + make_interval(0, 0, 0, 0, 0, 0, microseconds / 1000000.0);
    END IF;

    return CANDIDATE;
END;
$$ LANGUAGE plpgsql;



-- ----------------------------------------------------------------------------

--
-- STRING AND URL
--

-- Source: https://stackoverflow.com/a/33616365/180674

DO $$ BEGIN PERFORM drop_function_all('url_encode'); END $$;

CREATE OR REPLACE FUNCTION uri_encode(input text)
  RETURNS text
  LANGUAGE plpgsql
  IMMUTABLE STRICT
AS $$
DECLARE
  parsed text;
  safePattern text;
BEGIN
  safePattern = 'a-zA-Z0-9_~/\-\.';
  IF input ~ ('[^' || safePattern || ']') THEN
    SELECT STRING_AGG(fragment, '')
    INTO parsed
    FROM (
      SELECT prefix || encoded AS fragment
      FROM (
        SELECT COALESCE(match[1], '') AS prefix,
               COALESCE('%' || encode(match[2]::bytea, 'hex'), '') AS encoded
        FROM (
          SELECT regexp_matches(
            input,
            '([' || safePattern || ']*)([^' || safePattern || '])?',
            'g') AS match
        ) matches
      ) parsed
    ) fragments;
    RETURN parsed;
  ELSE
    RETURN input;
  END IF;
END;
$$
;



-- Generate a random string

DO $$ BEGIN PERFORM drop_function_all('random_string'); END $$;

CREATE OR REPLACE FUNCTION random_string(
  len INTEGER,                         -- String length
  alphanumeric BOOLEAN DEFAULT FALSE,  -- Alphanumeric only
  random_len BOOLEAN DEFAULT FALSE     -- Make length random between len/2 and len
)
  RETURNS text
  LANGUAGE plpgsql
  IMMUTABLE STRICT
AS $$
DECLARE
  charset TEXT;
BEGIN

  charset := 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  IF NOT alphanumeric THEN
    charset := CONCAT(charset, '!"#$%&''()*+,-./:;<=>?@[\]^_`{|}~');
  END IF;

  IF random_len THEN
     -- Chop off up to half of the length
     len := (len - (random() * (len / 2)))::integer;
  END IF;

  RETURN array_to_string(array(
    SELECT SUBSTR(charset, ((random()*(LENGTH(charset)-1)+1)::integer), 1)
    FROM generate_series(1,len)), '');

END;
$$
;


-- ----------------------------------------------------------------------------

--
-- DEBUGGING TOOLS
--

DROP VIEW IF EXISTS queries;
CREATE OR REPLACE VIEW queries
AS
    SELECT
        application_name,
        state,
        CASE state
            WHEN 'active' THEN (now() - query_start)::TEXT
            ELSE 'FINISHED'
            END
            AS run_time,
            regexp_replace(query, '[ \t]+', ' ', 'g') AS query
FROM pg_stat_activity
ORDER BY run_time desc
;
