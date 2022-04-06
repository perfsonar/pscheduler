--
-- Scheduling Class
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

    t_name := 'scheduling_class';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE scheduling_class (

        	-- Row identifier
        	id		INTEGER
        			PRIMARY KEY,

        	-- Display name
        	display		TEXT
        			UNIQUE NOT NULL,

        	-- Enumeration for use by programs
        	enum		TEXT
        			UNIQUE NOT NULL,

        	-- Whether or not tests in the class should be scheduled at
        	-- any time, regardless of exclusivity.  This is intended for
        	-- long-running jobs like powstream.
        	anytime         BOOLEAN,

        	-- Whether or not tests in the class get exclusive schedule
        	-- time
        	exclusive       BOOLEAN,

        	-- Whether or not tests in the class generate multiple
        	-- results.  For now, this is actually identical to the value
        	-- of 'anytime'.
        	multi_result    BOOLEAN
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




--
-- Functions that encapsulate the numeric values for each state
--

DO $$ BEGIN PERFORM drop_function_all('scheduling_class_background_multi'); END $$;

CREATE OR REPLACE FUNCTION scheduling_class_background_multi()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 1;
END;
$$ LANGUAGE plpgsql;


DO $$ BEGIN PERFORM drop_function_all('scheduling_class_exclusive'); END $$;

CREATE OR REPLACE FUNCTION scheduling_class_exclusive()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 2;
END;
$$ LANGUAGE plpgsql;


DO $$ BEGIN PERFORM drop_function_all('scheduling_class_normal'); END $$;

CREATE OR REPLACE FUNCTION scheduling_class_normal()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 3;
END;
$$ LANGUAGE plpgsql;


DO $$ BEGIN PERFORM drop_function_all('scheduling_class_background'); END $$;

CREATE OR REPLACE FUNCTION scheduling_class_background()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 4;
END;
$$ LANGUAGE plpgsql;



DROP TRIGGER IF EXISTS scheduling_class_alter ON scheduling_class CASCADE;

DO $$ BEGIN PERFORM drop_function_all('scheduling_class_alter'); END $$;

CREATE OR REPLACE FUNCTION scheduling_class_alter()
RETURNS TRIGGER
AS $$
BEGIN
	RAISE EXCEPTION 'This table may not be altered';
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER scheduling_class_alter
BEFORE INSERT OR UPDATE OR DELETE
ON scheduling_class
       FOR EACH ROW EXECUTE PROCEDURE scheduling_class_alter();


-- Do this after trigger creation and with a DISABLE/ENABLE in case
-- the table was previously populated.

ALTER TABLE scheduling_class DISABLE TRIGGER scheduling_class_alter;
INSERT INTO scheduling_class (id, display, enum, anytime, exclusive, multi_result)
VALUES
    (scheduling_class_background_multi(), 'Background Multi-Result',  'background-multi', TRUE,  FALSE, TRUE ),
    (scheduling_class_background(),       'Background Single-Result', 'background',       TRUE,  FALSE, FALSE),
    (scheduling_class_exclusive(),        'Exclusive',                'exclusive',        FALSE, TRUE,  FALSE),
    (scheduling_class_normal(),           'Normal',                   'normal',           FALSE, FALSE, FALSE)
ON CONFLICT (id) DO UPDATE
SET
    display = EXCLUDED.display,
    enum = EXCLUDED.enum,
    anytime = EXCLUDED.anytime,
    exclusive = EXCLUDED.exclusive,
    multi_result = EXCLUDED.multi_result;
ALTER TABLE scheduling_class ENABLE TRIGGER scheduling_class_alter;


-- Find the ID for a class by its enumeration

DO $$ BEGIN PERFORM drop_function_all('scheduling_class_find'); END $$;

CREATE OR REPLACE FUNCTION scheduling_class_find(
    candidate TEXT
)
RETURNS INTEGER
AS $$
BEGIN
    RETURN (SELECT id FROM scheduling_class WHERE enum = candidate);
END;
$$ LANGUAGE plpgsql;
