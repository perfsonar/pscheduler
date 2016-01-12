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
    ;

GRANT ALL PRIVILEGES ON DATABASE pscheduler TO pscheduler;


CREATE OR REPLACE LANGUAGE plpythonu;
