--
-- Table of archives to be used with every run
--


DROP TABLE IF EXISTS archive_default;
CREATE TABLE archive_default (

    -- Archive specification
    archive             JSONB,

    -- When the record was inserted (for debug only)
    inserted            TIMESTAMP WITH TIME ZONE
                        DEFAULT now()

);



CREATE OR REPLACE FUNCTION archive_default_insert()
RETURNS TRIGGER
AS $$
BEGIN
    PERFORM archiver_validate(NEW.archive);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archive_default_insert
AFTER INSERT
ON archive_default
FOR EACH ROW
    EXECUTE PROCEDURE archive_default_insert();



-- Rows in this can't be updated, only inserted and deleted.  (And
-- usually the whole table at once.)

CREATE OR REPLACE FUNCTION archive_default_update()
RETURNS TRIGGER
AS $$
BEGIN
    RAISE EXCEPTION 'Rows in this table cannot be updated.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archive_default_update
AFTER UPDATE
ON archive_default
FOR EACH ROW
    EXECUTE PROCEDURE archive_default_update();
