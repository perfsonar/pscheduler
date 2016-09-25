--
-- Stored procedures for HTTP(S) Operations
--

-- NOTE: This uses an untrusted language and therefore must be
-- installed as the superuser

-- TODO: It would be nice to use PgCURL
-- (https://github.com/Ormod/pgcurl) or something like it instead of
-- dragging this through Python.  This'll do for now.

DROP TYPE IF EXISTS http_result CASCADE;
CREATE TYPE http_result AS (
       status INTEGER,
       returned TEXT
);


CREATE OR REPLACE FUNCTION http_get(
    url TEXT DEFAULT NULL
)
RETURNS http_result
AS $$

import pscheduler

try:
    status, returned = pscheduler.url_get(url, json=False, throw=False)
except Exception as ex:
    plpy.error("Failed to GET %s: %s" % (url, str(ex)))

return { "status": status, "returned": returned }

$$ LANGUAGE plpythonu;



CREATE OR REPLACE FUNCTION http_put(
    url TEXT DEFAULT NULL,
    payload TEXT DEFAULT NULL
)
RETURNS http_result
AS $$

import pscheduler

try:
    status, returned = pscheduler.url_put(url, data=payload,
                                          json=False, throw=False)
except Exception as ex:
    plpy.error("Failed to PUT %s: %s" % (url, str(ex)))

return { "status": status, "returned": returned }

$$ LANGUAGE plpythonu;



CREATE OR REPLACE FUNCTION http_post(
    url TEXT DEFAULT NULL,
    payload TEXT DEFAULT NULL
)
RETURNS http_result
AS $$

import pscheduler

try:
    status, returned = pscheduler.url_post(url, data=payload,
                                           json=False, throw=False)
except Exception as ex:
    plpy.error("Failed to POST %s: %s" % (url, str(ex)))

return { "status": status, "returned": returned }

$$ LANGUAGE plpythonu;



CREATE OR REPLACE FUNCTION http_delete(
    url TEXT DEFAULT NULL
)
RETURNS http_result
AS $$

import pscheduler

try:
    status, returned = pscheduler.url_delete(url, throw=False)
except Exception as ex:
    plpy.error("Failed to DELETE %s: %s" % (url, str(ex)))

return { "status": status, "returned": returned }

$$ LANGUAGE plpythonu;
