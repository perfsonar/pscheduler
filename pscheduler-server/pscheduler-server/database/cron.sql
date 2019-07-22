--
-- Functions related to Cron specifications
--

-- TODO: These should be replaced with C


-- Use conventional DROPs here because drop_function_all() doesn't
-- exist in the superuser stage of the build.

DROP FUNCTION IF EXISTS cron_spec_is_valid(TEXT);

CREATE OR REPLACE FUNCTION cron_spec_is_valid(
    spec TEXT
)
RETURNS BOOLEAN
AS $$

import crontab

try:
    cron = crontab.CronTab(spec)
except (AttributeError, ValueError):
    return False

return True

$$ LANGUAGE plpythonu;




DROP FUNCTION IF EXISTS cron_next(TEXT, TIMESTAMP WITH TIME ZONE);

CREATE OR REPLACE FUNCTION cron_next(
    spec TEXT,   -- Cron spec
    after_time TIMESTAMP WITH TIME ZONE DEFAULT now()
)
RETURNS TIMESTAMP WITH TIME ZONE
AS $$

import crontab
import datetime
import dateutil.parser

# This is one of the types not converted, so it becomes text.

if after_time is None:
    plpy.error('Invalid time')
after = dateutil.parser.parse(after_time)

try:
    cron = crontab.CronTab(spec)
except (AttributeError, ValueError):
    plpy.error('Invalid cron spec')

# The return is properly converted.
return after + datetime.timedelta(seconds=cron.next(now=after, default_utc=False))

$$ LANGUAGE plpythonu;
