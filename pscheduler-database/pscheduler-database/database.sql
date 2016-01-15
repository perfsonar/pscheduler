--
-- Database creation
--
DROP DATABASE IF EXISTS pscheduler;
DROP ROLE IF EXISTS pscheduler;

CREATE ROLE pscheduler
WITH
    LOGIN
    ;

CREATE DATABASE pscheduler
WITH
    OWNER=pscheduler
    ;

GRANT ALL ON DATABASE pscheduler TO pscheduler;

\c pscheduler

CREATE OR REPLACE LANGUAGE plpythonu;

-- Needed for generating UUIDs
CREATE EXTENSION pgcrypto;
