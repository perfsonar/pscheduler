--
-- Database creation
--

CREATE EXTENSION IF NOT EXISTS dblink;

DO $$
DECLARE
    db_name TEXT;
BEGIN

    db_name := 'pscheduler';

    IF NOT EXISTS (SELECT * FROM pg_roles WHERE rolname = db_name)
    THEN
        PERFORM dblink_exec('dbname=' || current_database(),
                            'CREATE ROLE ' || db_name || ' WITH LOGIN');
        RAISE NOTICE 'Created role %', db_name;
    END IF;

    IF NOT EXISTS (SELECT * FROM pg_database WHERE datname = db_name)
    THEN
        PERFORM dblink_exec('dbname=' || current_database(),
                            'CREATE DATABASE ' || db_name
                              || ' WITH OWNER=' || db_name);
        PERFORM dblink_exec('dbname=' || current_database(),
                            'GRANT ALL ON DATABASE ' || db_name
			      || ' TO ' || db_name);
        RAISE NOTICE 'Created database %', db_name;
    END IF;

END;
$$ LANGUAGE plpgsql;


\c pscheduler

CREATE OR REPLACE LANGUAGE plpythonu;

-- Needed for generating UUIDs
CREATE EXTENSION IF NOT EXISTS pgcrypto;
