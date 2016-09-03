--
-- Preamble for non-privileged portion of database
--


\c pscheduler

-- TODO: This should be taken care of by postgresql-load but isn't.
SET ROLE pscheduler;
