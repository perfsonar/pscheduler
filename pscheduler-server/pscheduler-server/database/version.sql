--
-- Table that holds the database version
--


DROP TABLE IF EXISTS version;
CREATE TABLE version (

    version  	     	INTEGER
			NOT NULL
);


-- This table gets exactly one row that can only ever be updated.
INSERT INTO version (version) VALUES (1);



DROP TRIGGER IF EXISTS version_alter ON version CASCADE;
DROP TRIGGER IF EXISTS version_truncate ON version CASCADE;

CREATE OR REPLACE FUNCTION version_noalter()
RETURNS TRIGGER
AS $$
BEGIN
	RAISE EXCEPTION 'This table cannot be altered';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER version_alter
BEFORE INSERT OR UPDATE OR DELETE
ON version
FOR EACH ROW
    EXECUTE PROCEDURE version_noalter();

CREATE TRIGGER version_truncate
BEFORE TRUNCATE
ON version
EXECUTE PROCEDURE version_noalter();
