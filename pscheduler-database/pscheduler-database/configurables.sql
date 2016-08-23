--
-- Table with one row that holds configurable values
--


DROP TABLE IF EXISTS configurables;
CREATE TABLE configurables (

    -- How far in advance we should schedule runs
    schedule_horizon    INTERVAL
			DEFAULT 'P1D',

    -- How long we should keep old runs and tasks
    keep_runs_tasks	INTERVAL
			DEFAULT 'P7D',

    -- Maximum runs in parallel
    max_parallel_runs	INTEGER
			DEFAULT 50
);


-- This table gets exactly one row that can only ever be updated.
INSERT INTO configurables DEFAULT VALUES;


CREATE OR REPLACE FUNCTION configurables_update()
RETURNS TRIGGER
AS $$
BEGIN
    IF NEW.max_parallel_runs < 1
    THEN
        RAISE EXCEPTION 'Maximum parallel runs must be positive.';
    END IF;

    NOTIFY configurables_changed;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER configurables_update
AFTER UPDATE
ON configurables
FOR EACH ROW
    EXECUTE PROCEDURE configurables_update();




CREATE OR REPLACE FUNCTION configurables_noalter()
RETURNS TRIGGER
AS $$
BEGIN
	RAISE EXCEPTION 'This table can only be updated.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER configurables_alter
BEFORE INSERT OR DELETE
ON configurables
FOR EACH ROW
    EXECUTE PROCEDURE configurables_noalter();

CREATE TRIGGER configurables_truncate
BEFORE TRUNCATE
ON configurables
EXECUTE PROCEDURE configurables_noalter();
