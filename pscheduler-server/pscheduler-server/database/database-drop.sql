--
-- Database drop
--

-- Force disconnection of any clients using the database.

DO $$
BEGIN
    PERFORM pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE
        pg_stat_activity.datname = 'pscheduler'
        AND pid <> pg_backend_pid();
END;
$$ LANGUAGE plpgsql;


DROP DATABASE IF EXISTS pscheduler;
DROP ROLE IF EXISTS pscheduler;
