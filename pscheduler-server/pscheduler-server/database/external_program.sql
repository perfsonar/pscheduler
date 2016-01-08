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
CREATE OR REPLACE FUNCTION pscheduler_internal(
    argv TEXT[] DEFAULT '{}',  -- Arguments to pass to 'pscheduler internal'
    input TEXT DEFAULT NULL    -- What goes to the standard input
)
RETURNS external_program_result
AS $$

import subprocess

try:

    process = subprocess.Popen(
        [ 'pscheduler', 'internal' ] + argv,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE )

    stdout, stderr = process.communicate(input)
except:
    plpy.error('Unable to run pscheduler front-end program')

return { 'status': process.returncode, 'stdout': stdout, 'stderr': stderr }

$$ LANGUAGE plpythonu;
