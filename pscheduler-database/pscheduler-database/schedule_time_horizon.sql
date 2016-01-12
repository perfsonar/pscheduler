--
-- Table with one row that sets the time horizon for scheduleing
--


DROP TABLE IF EXISTS schedule_time_horizon;
CREATE TABLE schedule_time_horizon (

	-- How far ahead tests should be scheduled
	duration	INTERVAL
			NOT NULL

);


-- This table gets exactly one row that can only ever be updated.
INSERT INTO schedule_time_horizon(duration)
VALUES ('P1D');


CREATE OR REPLACE FUNCTION schedule_time_horizon_update()
RETURNS TRIGGER
AS $$
BEGIN
	IF NEW.duration = OLD.duration THEN
	   -- No change; don't care.
	   RETURN NEW;
	ELSIF NEW.duration > OLD.duration THEN
	   NULL; -- TODO: Reschedule all beyond old duration
	ELSE
	   NULL; -- TODO: Reschedule all beyond present time
	END IF;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER schedule_time_horizon_update
AFTER UPDATE
ON schedule_time_horizon
FOR EACH ROW
    EXECUTE PROCEDURE schedule_time_horizon_update();



CREATE OR REPLACE FUNCTION schedule_time_horizon_noalter()
RETURNS TRIGGER
AS $$
BEGIN
	RAISE EXCEPTION 'This table can only be updated.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER schedule_time_horizon_alter
BEFORE INSERT OR DELETE
ON schedule_time_horizon
FOR EACH ROW
    EXECUTE PROCEDURE schedule_time_horizon_noalter();

CREATE TRIGGER schedule_time_horizon_truncate
BEFORE TRUNCATE
ON schedule_time_horizon
EXECUTE PROCEDURE schedule_time_horizon_noalter();


-- Get the current time horizon
CREATE OR REPLACE FUNCTION
schedule_time_horizon()
RETURNS INTERVAL
AS $$
DECLARE
	result INTERVAL;
BEGIN
	SELECT duration INTO result from schedule_time_horizon;
	RETURN result;
END;
$$ LANGUAGE plpgsql;


-- Change the time horizon
CREATE OR REPLACE FUNCTION
schedule_time_horizon_set(horizon INTERVAL)
RETURNS VOID
AS $$
BEGIN
	UPDATE schedule_time_horizon SET duration = horizon;
END;
$$ LANGUAGE plpgsql;
