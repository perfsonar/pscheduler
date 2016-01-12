--
-- Database creation
--

DROP DATABASE IF EXISTS pscheduler;
CREATE DATABASE pscheduler;

\c pscheduler


DROP ROLE IF EXISTS pscheduler;
CREATE ROLE pscheduler
WITH
    LOGIN
--    UNENCRYPTED PASSWORD 'pscheduler'  -- TODO: Find a secure way to deal with this.
    ;

GRANT ALL PRIVILEGES ON DATABASE pscheduler TO pscheduler;


CREATE OR REPLACE LANGUAGE plpythonu;
