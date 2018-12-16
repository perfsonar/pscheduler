--
-- Stored procedure that runs external programs
--

-- NOTE: This uses an untrusted language and therefore must be
-- installed as the superuser

DROP TYPE IF EXISTS external_program_result CASCADE;
CREATE TYPE external_program_result AS (
       status INTEGER,
       stdout TEXT,
       stderr TEXT
);


--
-- Run the pscheduler frontend's "internal" command
--
-- TODO: Figure out what do do when DB is off-node.  Probably need an
-- external process like the task runner.
--
-- TODO: This doesn't fail if the program never returns.  Need to do
-- something about that, maybe along the lines of
-- http://stackoverflow.com/a/4825933.  (Uses threading... Ick.)
--

DO $$ BEGIN PERFORM drop_function_all('pscheduler_internal'); END $$;

CREATE OR REPLACE FUNCTION pscheduler_internal(
    argv TEXT[] DEFAULT '{}',  -- Arguments to pass to 'pscheduler internal'
    input TEXT DEFAULT NULL,   -- What goes to the standard input
    timeout INTEGER DEFAULT 5  -- How long to wait in seconds
)
RETURNS external_program_result
AS $$

import pscheduler

try:

    status, stdout, stderr = pscheduler.run_program(
        [ 'pscheduler', 'internal' ] + argv,
	stdin = input,
	timeout = timeout
	)

except Exception as ex:
    plpy.error('Unable to run pscheduler front-end program: ' + str(ex))

return { 'status': status, 'stdout': stdout, 'stderr': stderr }

$$ LANGUAGE plpythonu;
