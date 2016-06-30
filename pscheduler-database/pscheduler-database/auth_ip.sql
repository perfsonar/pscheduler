--
-- Table of IP blocks
--

DROP TABLE IF EXISTS auth_ip CASCADE;
CREATE TABLE auth_ip (

	-- Row identifier
	id		BIGSERIAL
			PRIMARY KEY,

	-- The identifier to which this block belongs
	identifier	BIGINT
			REFERENCES auth_identifier(id)
			ON DELETE CASCADE,

	-- IP address or CIDR block
	block		INET
);


-- The ususal lookup with the block_set ID brought along so it can be
-- pulled without having to consult the table.
CREATE INDEX auth_ips
  ON auth_ip(block, identifier);


-- Remove duplicates

CREATE OR REPLACE FUNCTION auth_ip_alter()
RETURNS TRIGGER
AS $$
BEGIN

    -- Skip INSERTs that are already covered
    IF (TG_OP = 'INSERT')
       AND EXISTS (SELECT * FROM auth_ip
                   WHERE
                       identifier = NEW.identifier
                       AND block = NEW.block) THEN
        RETURN NULL;
    END IF;

    -- Delete rows that are updated to match others
    IF (TG_OP = 'UPDATE')
       AND NEW.block <> OLD.block
       AND EXISTS (SELECT * FROM auth_ip
                   WHERE
                       id <> NEW.id
                       AND identifier = NEW.identifier
                       AND block = NEW.block) THEN
        DELETE FROM auth_ip WHERE id = NEW.id;
        RETURN NULL;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER run_alter BEFORE INSERT OR UPDATE ON auth_ip
       FOR EACH ROW EXECUTE PROCEDURE auth_ip_alter();



-- Replace a full set of IPs by identifier name

CREATE OR REPLACE FUNCTION api_auth_ip_post(
    identifier_name TEXT,
    blocks INET[]
)
RETURNS VOID
AS $$
DECLARE
    ident_id BIGINT;
    block INET;
BEGIN

    -- TODO: This needs to work only on IP-type identifiers to prevent
    -- having multiple types of "things" under the same identifier.

    SELECT INTO ident_id id FROM auth_identifier WHERE name = identifier_name;
    IF FOUND THEN
        DELETE FROM auth_ip WHERE identifier = ident_id;
    ELSE
        WITH inserted AS (
            INSERT INTO auth_identifier (itype, name)
	      VALUES (auth_identifier_type_ip(), identifier_name)
            RETURNING *
        ) SELECT INTO ident_id * FROM inserted;
    END IF;

    FOREACH block IN ARRAY blocks
    LOOP
        INSERT INTO auth_ip (identifier, block) VALUES (ident_id, block);
    END LOOP;

    RETURN;

END;
$$ LANGUAGE plpgsql;



-- Find the identifiers that an IP matches

CREATE OR REPLACE FUNCTION api_auth_ip_identifiers(
    ip INET
)
RETURNS TABLE (
    id BIGINT,
    name TEXT
)
AS $$
BEGIN

    RETURN QUERY
    SELECT DISTINCT auth_identifier.id, auth_identifier.name
    FROM
        auth_ip
        JOIN auth_identifier ON auth_identifier.id = auth_ip.identifier
    WHERE
        auth_ip.block && ip;

    RETURN;

END;
$$ LANGUAGE plpgsql;


