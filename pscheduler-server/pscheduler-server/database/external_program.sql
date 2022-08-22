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
-- Run a pscheduler frontend command
--
-- TODO: Figure out what do do when DB is off-node.  Probably need an
-- external process like the task runner.
--
-- TODO: This doesn't fail if the program never returns.  Need to do
-- something about that, maybe along the lines of
-- http://stackoverflow.com/a/4825933.  (Uses threading... Ick.)
--

DO $$ BEGIN PERFORM drop_function_all('pscheduler_command'); END $$;

CREATE OR REPLACE FUNCTION pscheduler_command(
    argv TEXT[] DEFAULT '{}',  -- Arguments to pass to 'pscheduler'
    input TEXT DEFAULT '',     -- What goes to the standard input
    timeout INTEGER DEFAULT 15  -- How long to wait in seconds
)
RETURNS external_program_result
AS $$

import pscheduler

try:

    status, stdout, stderr = pscheduler.run_program(
        [ 'pscheduler' ] + argv,
	stdin = input,
	timeout = timeout
	)

except Exception as ex:
    plpy.error('Unable to run pscheduler front-end program: ' + str(ex))

return { 'status': status, 'stdout': stdout, 'stderr': stderr }

$$ LANGUAGE plpython3u;




-- Run a pScheduler plugin method.  This has all of the same pitfalls
-- as pscheduler_command().

DO $$ BEGIN PERFORM drop_function_all('pscheduler_plugin_invoke'); END $$;

CREATE OR REPLACE FUNCTION pscheduler_plugin_invoke(
    pltype TEXT,               -- Type of plugin
    which TEXT,                -- Instance of the type
    method TEXT,               -- Method within the instance
    input TEXT DEFAULT '',     -- What goes to the standard input
    timeout INTEGER DEFAULT 15  -- How long to wait in seconds
)
RETURNS external_program_result
AS $$

import pscheduler

try:

    status, stdout, stderr = pscheduler.plugin_invoke(
        pltype, which, method,
	stdin=input,
	timeout=timeout
	)

except Exception as ex:
    plpy.error('Unable to run pscheduler plugin method: ' + str(ex))

return { 'status': status, 'stdout': stdout, 'stderr': stderr }

$$ LANGUAGE plpython3u;
