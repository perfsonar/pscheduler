--
-- Scheduling Class
--


DROP TABLE IF EXISTS scheduling_class CASCADE;
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



--
-- Functions that encapsulate the numeric values for each state
--

CREATE OR REPLACE FUNCTION scheduling_class_background()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 1;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION scheduling_class_exclusive()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 2;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION scheduling_class_normal()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 3;
END;
$$ LANGUAGE plpgsql;



INSERT INTO scheduling_class (id, display, enum, anytime, exclusive, multi_result)
VALUES
    (scheduling_class_background(), 'Background', 'background', TRUE,  FALSE, TRUE),
    (scheduling_class_exclusive(),  'Exclusive',  'exclusive',  FALSE, TRUE,  FALSE),
    (scheduling_class_normal(),     'Normal',     'normal',     FALSE, FALSE, FALSE)
	;



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


-- Find the ID for a class by its enumeration
CREATE OR REPLACE FUNCTION scheduling_class_find(
    candidate TEXT
)
RETURNS INTEGER
AS $$
BEGIN
    RETURN (SELECT id FROM scheduling_class WHERE enum = candidate);
END;
$$ LANGUAGE plpgsql;
