--
-- Table of authorization identifiers
--

-- Types

-- IP Block Set
CREATE OR REPLACE FUNCTION auth_identifier_type_ip()
RETURNS INTEGER
AS $$
BEGIN
	RETURN 1;
END;
$$ LANGUAGE plpgsql;



DROP TABLE IF EXISTS auth_identifier CASCADE;
CREATE TABLE auth_identifier (

	-- Row identifier
	id		BIGSERIAL
			PRIMARY KEY,

	-- External-use identifier
	uuid		UUID
			UNIQUE
			DEFAULT gen_random_uuid(),

	-- Type (See functions below)
	itype		INTEGER
                        NOT NULL
                        CHECK (itype IN (auth_identifier_type_ip())),

	-- Name
	name            TEXT
                        UNIQUE
                        NOT NULL

);



-- This should be used when someone looks up the external ID.  Bring
-- the row ID a long so it can be pulled without having to consult the
-- table.

CREATE INDEX auth_identifiers
  ON auth_identifier(uuid, id);



