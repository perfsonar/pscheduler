--
-- Table of Authorization Keys
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

    t_name := 'auth_key';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE auth_key (

        	-- Row identifier
        	id		BIGSERIAL
        			PRIMARY KEY,

        	-- Key type
        	type		BIGINT
        			REFERENCES auth_key_type(id)
        			ON DELETE CASCADE,

        	-- User name
        	name		TEXT
        			NOT NULL,

        	-- Hashed password
        	password	TEXT
        			NOT NULL,

        	-- When this record was last updated
        	updated		TIMESTAMP WITH TIME ZONE
        			DEFAULT now(),

        	UNIQUE		(type, name)

        );


	-- There's no sense in indexing the password because the salt
	-- forces a computation against it.  This should get it down
	-- to one row.

        CREATE INDEX auth_key_type_name ON auth_key(type, name);

	t_version := t_version + 1;

    END IF;

    -- Version 1 to version 2
    -- Remove unused and trouble-causing version column
    -- IF t_version = 1
    -- THEN
    --     ...
    -- 
    --     t_version := t_version + 1;
    -- END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;



-- Insert a new key or update an existing one by name

DO $$ BEGIN PERFORM drop_function_all('auth_key_add_update'); END $$;

CREATE OR REPLACE FUNCTION auth_key_add_update(type TEXT, key_name TEXT, password TEXT)
RETURNS VOID
AS $$
DECLARE
    type_id BIGINT;
    crypted TEXT;
BEGIN

    SELECT INTO type_id id FROM auth_key_type WHERE auth_key_type.name = type;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown key type "%"', type;
    END IF;

    -- Note that this uses MD5 because it takes infinitely-long passwords
    -- TODO: Consider truncating to 72 and using bf?
    crypted := crypt(password, gen_salt('md5'));

    -- This can't be done with ON CONFLICT because multiple columns
    -- cause problems.  Use an old-fashioned UPSERT.

    IF EXISTS (SELECT * FROM auth_key WHERE auth_key.type = type_id AND name = key_name)
    THEN
        UPDATE auth_key
        SET password = crypted
	WHERE auth_key.type = type_id AND name = key_name;
    ELSE
        INSERT INTO auth_key (type, name, password)
        VALUES (type_id, key_name, crypted);
    END IF;

END;
$$ LANGUAGE plpgsql;



-- See if a provided type/name/password are valid

DO $$ BEGIN PERFORM drop_function_all('auth_key_is_valid'); END $$;

CREATE OR REPLACE FUNCTION auth_key_is_valid(type TEXT, key_name TEXT, pass TEXT)
RETURNS BOOLEAN
AS $$
DECLARE
    type_id BIGINT;
BEGIN

    SELECT INTO type_id id FROM auth_key_type WHERE auth_key_type.name = type;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown key type "%"', type;
    END IF;

    RETURN EXISTS (
        SELECT * FROM auth_key
        WHERE
	    auth_key.type = type_id
	    AND name = key_name
	    AND password = crypt(pass, password)
	);

END;
$$ LANGUAGE plpgsql;



-- Delete a key

DO $$ BEGIN PERFORM drop_function_all('auth_key_delete'); END $$;

CREATE OR REPLACE FUNCTION auth_key_delete(type TEXT, key_name TEXT)
RETURNS VOID
AS $$
DECLARE
    type_id BIGINT;
    crypted TEXT;
BEGIN

    SELECT INTO type_id id FROM auth_key_type WHERE auth_key_type.name = type;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Unknown key type "%"', type;
    END IF;

    DELETE FROM auth_key WHERE auth_key.type = type_id AND name = key_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No such % key "%"', type, key_name;
    END IF;

END;
$$ LANGUAGE plpgsql;
