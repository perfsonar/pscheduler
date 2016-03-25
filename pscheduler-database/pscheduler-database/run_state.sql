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
			UNIQUE NOT NULL,

	-- Enumeration for use by programs
	enum		TEXT
			UNIQUE NOT NULL
);



--
-- Functions that encapsulate the numeric values for each state
--

-- Run is waiting to execute (not time yet)
CREATE OR REPLACE FUNCTION run_state_pending()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 1;
END;
$$ LANGUAGE plpgsql;

-- The runner is preparing to execute the run
CREATE OR REPLACE FUNCTION run_state_on_deck()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 2;
END;
$$ LANGUAGE plpgsql;

-- Run is being executed
CREATE OR REPLACE FUNCTION run_state_running()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 3;
END;
$$ LANGUAGE plpgsql;

-- Run finished successfully
CREATE OR REPLACE FUNCTION run_state_finished()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 4;
END;
$$ LANGUAGE plpgsql;

-- No idea of the outcome yet
CREATE OR REPLACE FUNCTION run_state_overdue()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 5;
END;
$$ LANGUAGE plpgsql;

-- Run never happened
CREATE OR REPLACE FUNCTION run_state_missed()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 6;
END;
$$ LANGUAGE plpgsql;

-- Run ran but was not a success
CREATE OR REPLACE FUNCTION run_state_failed()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 7;
END;
$$ LANGUAGE plpgsql;

-- Run lost out to something with a higher priority
CREATE OR REPLACE FUNCTION run_state_trumped()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 8;
END;
$$ LANGUAGE plpgsql;



INSERT INTO run_state (id, display, enum)
VALUES
	(run_state_pending(),  'Pending',  'pending'),
	(run_state_on_deck(),  'On Deck',  'on-deck'),
	(run_state_running(),  'Running',  'running'),
	(run_state_finished(), 'Finished', 'finished'),
	(run_state_overdue(),  'Overdue',  'overdue'),
	(run_state_missed(),   'Missed',   'missed'),
	(run_state_failed(),   'Failed',   'failed'),
	(run_state_trumped(),  'Trumped',  'trumped')
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
           OR   ( old = run_state_pending()
	          AND new IN (run_state_on_deck(),
			      run_state_missed(),
			      run_state_trumped()) )
           OR   ( old = run_state_on_deck()
	          AND new IN (run_state_running(),
		              run_state_overdue(),
			      run_state_missed(),
			      run_state_trumped()) )
           OR ( old = run_state_running()
	        AND new IN (run_state_finished(),
		            run_state_overdue(),
			    run_state_missed(),
			    run_state_failed(),
			    run_state_trumped()) )
	   OR ( old = run_state_overdue()
                AND new IN (run_state_finished(),
		            run_state_missed(),
		            run_state_failed(),
		            run_state_trumped()) )
           ;
END;
$$ LANGUAGE plpgsql;



