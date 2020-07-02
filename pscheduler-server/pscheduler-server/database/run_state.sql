--
-- Run State
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

    t_name := 'run_state';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

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

	t_version := t_version + 1;

    END IF;

    -- Version 1 to version 2
    IF t_version = 1
    THEN

        -- This column indicates if there's nothing more to be done
        -- with this run, successful or not.
        ALTER TABLE run_state ADD COLUMN
        finished BOOLEAN DEFAULT FALSE;

        t_version := t_version + 1;
    END IF;


    -- Version 2 to version 3
    IF t_version = 2
    THEN

        -- Indicates whether the state indicates success (TRUE),
        -- failure (FALSE) or neither (NULL).
        ALTER TABLE run_state ADD COLUMN
        success BOOLEAN DEFAULT NULL;

        t_version := t_version + 1;
    END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;



--
-- Functions that encapsulate the numeric values for each state
--

-- NOTE: These use ALTER FUNCTION to set the IMMUTABLE attribute
-- because in some cases, replacement doesn't set it properly.

-- Run is waiting to execute (not time yet)

DO $$ BEGIN PERFORM drop_function_all('run_state_pending'); END $$;

CREATE OR REPLACE FUNCTION run_state_pending()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 1;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION run_state_pending() IMMUTABLE;


-- The runner is preparing to execute the run

DO $$ BEGIN PERFORM drop_function_all('run_state_on_deck'); END $$;

CREATE OR REPLACE FUNCTION run_state_on_deck()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 2;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION run_state_on_deck() IMMUTABLE;


-- Run is being executed

DO $$ BEGIN PERFORM drop_function_all('run_state_running'); END $$;

CREATE OR REPLACE FUNCTION run_state_running()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 3;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION run_state_running() IMMUTABLE;

-- Post-run cleanup

DO $$ BEGIN PERFORM drop_function_all('run_state_cleanup'); END $$;

CREATE OR REPLACE FUNCTION run_state_cleanup()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 4;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION run_state_cleanup() IMMUTABLE;


-- Run finished successfully

DO $$ BEGIN PERFORM drop_function_all('run_state_finished'); END $$;

CREATE OR REPLACE FUNCTION run_state_finished()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 5;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION run_state_finished() IMMUTABLE;


-- No idea of the outcome yet

DO $$ BEGIN PERFORM drop_function_all('run_state_overdue'); END $$;

CREATE OR REPLACE FUNCTION run_state_overdue()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 6;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION run_state_overdue() IMMUTABLE;


-- Run never happened

DO $$ BEGIN PERFORM drop_function_all('run_state_missed'); END $$;

CREATE OR REPLACE FUNCTION run_state_missed()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 7;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION run_state_missed() IMMUTABLE;


-- Run ran but was not a success

DO $$ BEGIN PERFORM drop_function_all('run_state_failed'); END $$;

CREATE OR REPLACE FUNCTION run_state_failed()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 8;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION run_state_failed() IMMUTABLE;


-- Run lost out to something with a higher priority

DO $$ BEGIN PERFORM drop_function_all('run_state_preempted'); END $$;

CREATE OR REPLACE FUNCTION run_state_preempted()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 9;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION run_state_preempted() IMMUTABLE;

-- Run was dead on arrival

DO $$ BEGIN PERFORM drop_function_all('run_state_nonstart'); END $$;

CREATE OR REPLACE FUNCTION run_state_nonstart()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 10;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION run_state_nonstart() IMMUTABLE;


-- Run was canceled

DO $$ BEGIN PERFORM drop_function_all('run_state_canceled'); END $$;

CREATE OR REPLACE FUNCTION run_state_canceled()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 11;
END;
$$ LANGUAGE plpgsql;
ALTER FUNCTION run_state_canceled() IMMUTABLE;



DROP TRIGGER IF EXISTS run_state_alter ON run_state CASCADE;

DO $$ BEGIN PERFORM drop_function_all('run_state_alter'); END $$;

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



-- Do this after trigger creation and with a DISABLE/ENABLE in case
-- the table was previously populated.

ALTER TABLE run_state DISABLE TRIGGER run_state_alter;
INSERT INTO run_state (id, display, enum, finished, success)
VALUES
    (run_state_pending(),   'Pending',     'pending',   FALSE, NULL),
    (run_state_on_deck(),   'On Deck',     'on-deck',   FALSE, NULL),
    (run_state_running(),   'Running',     'running',   FALSE, NULL),
    (run_state_cleanup(),   'Cleanup',     'cleanup',   TRUE,  NULL),
    (run_state_finished(),  'Finished',    'finished',  TRUE,  TRUE),
    (run_state_overdue(),   'Overdue',     'overdue',   TRUE,  FALSE),
    (run_state_missed(),    'Missed',      'missed',    TRUE,  FALSE),
    (run_state_failed(),    'Failed',      'failed',    TRUE,  FALSE),
    (run_state_preempted(), 'Preempted',   'preempted', TRUE,  FALSE),
    (run_state_nonstart(),  'Non-Starter', 'nonstart',  TRUE,  FALSE),
    (run_state_canceled(),  'Canceled',    'canceled',  TRUE,  NULL)
ON CONFLICT (id) DO UPDATE
SET
    display = EXCLUDED.display,
    enum = EXCLUDED.enum,
    finished = EXCLUDED.finished,
    success = EXCLUDED.success;
ALTER TABLE run_state ENABLE TRIGGER run_state_alter;


-- Determine if a transition between states is valid
DO $$ BEGIN PERFORM drop_function_all('run_state_transition_is_valid'); END $$;

CREATE OR REPLACE FUNCTION run_state_transition_is_valid(
    old INTEGER,
    new INTEGER
)
RETURNS BOOLEAN
AS $$
BEGIN
   -- TODO: This might be worth putting into a table.
   RETURN  new = old
           OR   ( old = run_state_pending()
	          AND new IN (run_state_on_deck(),
			      run_state_missed(),
			      run_state_failed(),
			      run_state_preempted(),
			      run_state_canceled(),
			      run_state_nonstart()) )
           OR   ( old = run_state_on_deck()
	          AND new IN (run_state_running(),
		              run_state_overdue(),
			      run_state_missed(),
			      run_state_failed(),
			      run_state_canceled(),
			      run_state_preempted()) )
           OR ( old = run_state_running()
	        AND new IN (run_state_cleanup(),
		            run_state_finished(),
		            run_state_overdue(),
			    run_state_missed(),
			    run_state_failed(),
			    run_state_preempted(),
			    run_state_canceled()) )
           OR ( old = run_state_cleanup()
	        AND new IN (run_state_finished(),
			    run_state_failed()) )
           OR ( old = run_state_finished()
	        AND new IN (run_state_failed()) )
	   OR ( old = run_state_overdue()
                AND new IN (run_state_finished(),
		            run_state_missed(),
		            run_state_failed(),
			    run_state_canceled(),
		            run_state_preempted()) )
           OR ( old = run_state_missed()
	        AND new IN (run_state_failed()) )
           OR   ( old = run_state_nonstart()
	          AND new IN (run_state_canceled()) )
           ;
END;
$$ LANGUAGE plpgsql;





-- Determine if a run state is one of the finished ones.

DO $$ BEGIN PERFORM drop_function_all('run_state_is_finished'); END $$;

CREATE OR REPLACE FUNCTION run_state_is_finished(
    state INTEGER
)
RETURNS BOOLEAN
AS $$
BEGIN
    RETURN EXISTS (SELECT * FROM run_state WHERE id = state AND finished);
END;
$$ LANGUAGE plpgsql
IMMUTABLE;
