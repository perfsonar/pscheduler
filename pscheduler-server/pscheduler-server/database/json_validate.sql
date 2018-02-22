--
-- Stored procedure that validates JSON using the pScheduler library
--

-- NOTE: This uses an untrusted language and therefore must be
-- installed as the superuser

--
-- Validate JSON
--
--

DO $$ BEGIN PERFORM drop_function_all('json_validate'); END $$;

CREATE OR REPLACE FUNCTION json_validate(
    candidate JSONB,                               -- JSON to be validated
    json_ref TEXT DEFAULT '#/pScheduler/AnyJSON'   -- What object to validate
)
RETURNS TEXT  -- NULL if okay, error text otherwise.
AS $$

import pscheduler

if not isinstance(candidate, basestring):
    plpy.error("No idea what to do with type %s" % (type(candidate)))

json = pscheduler.json_load(candidate)

valid, message = pscheduler.json_validate(
    {"": json},
    {    
        "type": "object",
        "properties": {
            "": { "$ref": json_ref }
        },
        "required": [ "" ]
    })

return None if valid else message

$$ LANGUAGE plpythonu;
