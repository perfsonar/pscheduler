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
--
--
-- HACK: BWCTLBC -- Can probably leave this.
--
-- The env_add argument is an array of alternating pairs of variable
-- names and values that are to be added to the environment before the
-- program runs.  [ 'FOO', 'bar', 'BAZ', 'quux' ] would be turned into
-- the Python equivalent of {"FOO": "bar", "BAZ": "quux"}.
--

DO $$ BEGIN PERFORM drop_function_all('pscheduler_internal'); END $$;

CREATE OR REPLACE FUNCTION pscheduler_internal(
    argv TEXT[] DEFAULT '{}',  -- Arguments to pass to 'pscheduler internal'
    input TEXT DEFAULT NULL,   -- What goes to the standard input
    timeout INTEGER DEFAULT 5, -- How long to wait in seconds
    env_add TEXT[] DEFAULT ARRAY[]::TEXT[]  -- Environment additions.  See above.
)
RETURNS external_program_result
AS $$

import pscheduler


if env_add is None or len(env_add) == 0:
    env_add_hash = {}
else:
    if len(env_add) % 2 != 0:
        plpy.error('env_add must have an even number of elements.')
    env_add_hash = {}
    while env_add:
        env_add_hash[env_add.pop()] = env_add.pop()


try:

    status, stdout, stderr = pscheduler.run_program(
        [ 'pscheduler', 'internal' ] + argv,
	stdin = input,
	timeout = timeout,
	env_add = env_add_hash
	)

except Exception as ex:
    plpy.error('Unable to run pscheduler front-end program: ' + str(ex))

return { 'status': status, 'stdout': stdout, 'stderr': stderr }

$$ LANGUAGE plpythonu;
