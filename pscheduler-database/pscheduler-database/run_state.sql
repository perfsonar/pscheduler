--
-- Run State
--


DROP TABLE IF EXISTS run_state CASCADE;
CREATE TABLE run_state (

	-- Row identifier
	id		INTEGER
			PRIMARY KEY,

	-- Display name
	display		TEXT
			UNIQUE NOT NULL
);


INSERT INTO run_state (id, display)
VALUES
	(1, 'Pending'),   -- Waiting to be run
	(2, 'Running'),   -- Being executed
	(3, 'Finished'),  -- Ran successfully
	(4, 'Overdue'),   -- No idea of outcome yet
	(5, 'Missed'),    -- Didn't run
	(6, 'Failed'),    -- Ran but didn't succeed
	(7, 'Trumped')    -- Lost out to higher-priority run
	;



CREATE OR REPLACE FUNCTION run_state_alter()
RETURNS TRIGGER
AS $$
BEGIN
	RAISE EXCEPTION 'This table may not be altered';
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER run_state_alter
BEFORE INSERT OR UPDATE OR DELETE
ON run_state
       FOR EACH ROW EXECUTE PROCEDURE run_state_alter();



-- Determine if a transition between states is valid
CREATE OR REPLACE FUNCTION run_state_transition_is_valid(
    old INTEGER,
    new INTEGER
)
RETURNS BOOLEAN
AS $$
BEGIN
   RETURN  new = old
           OR   ( old = 1 AND new IN (2, 4, 5, 7)   )
           OR ( old = 2 AND new IN (3, 4, 5, 6, 7) )
           OR ( old = 4 AND new IN (3, 5, 6, 7)    );
END;
$$ LANGUAGE plpgsql;



--
-- Functions that encapsulate the hard-wired values above for use
-- outside this file
--

CREATE OR REPLACE FUNCTION run_state_pending()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 1;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION run_state_running()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 2;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION run_state_finished()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 3;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION run_state_overdue()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 4;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION run_state_missed()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 5;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION run_state_failed()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 6;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION run_state_trumped()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 7;
END;
$$ LANGUAGE plpgsql;
