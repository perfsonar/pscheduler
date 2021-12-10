--
-- Table of Authorization Key Types
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

    t_name := 'auth_key_type';

    t_version := table_version_find(t_name);
    t_version_old := t_version;


    --
    -- Upgrade Blocks
    --

    -- Version 0 (nonexistant) to version 1
    IF t_version = 0
    THEN

        CREATE TABLE auth_key_type (

        	-- Row identifier
        	id		BIGSERIAL
        			PRIMARY KEY,

        	-- Type Name
        	name		TEXT
        			UNIQUE NOT NULL
        );

	t_version := t_version + 1;

    END IF;

    -- Version 1 to version 2
    -- IF t_version = 1
    -- THEN
    --     ,,,
    -- 
    --     t_version := t_version + 1;
    -- END IF;


    --
    -- Cleanup
    --

    PERFORM table_version_set(t_name, t_version, t_version_old);

END;
$$ LANGUAGE plpgsql;
