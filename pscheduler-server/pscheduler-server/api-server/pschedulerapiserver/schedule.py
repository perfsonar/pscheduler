#
# Schedule-Related Pages
#

import pscheduler
import time

from pschedulerapiserver import application

from flask import request

from .dbcursor import dbcursor_query
from .json import *
from .limitproc import *
from .log import log
from .response import *
from .tasks import task_exists


# Schedule
@application.route("/schedule", methods=['GET'])
def schedule():

    try:
        range_start = arg_datetime('start')
        range_end   = arg_datetime('end')
    except ValueError:
        return bad_request('Invalid start or end time')

    try:
        cursor = dbcursor_query("""
            SELECT
                lower(times),
                upper(times),
                task,
                run,
                state_enum,
                state_display,
                task_json,
                task_cli
            FROM schedule
            WHERE times && tstzrange(%s, %s, '[)');
            """, [range_start, range_end])
    except Exception as ex:
        log.exception()
        return error(str(ex))

    result = []

    for row in cursor:

        task_href = pscheduler.api_url(path="tasks/%s" % row[2])
        run_href = "%s/runs/%s" % (task_href, row[3])

        run = {
            "start-time": pscheduler.datetime_as_iso8601(row[0]),
            "end-time": pscheduler.datetime_as_iso8601(row[1]),
            "href": run_href,
            "result-href": "%s/result" % run_href,
            "state": row[4],
            "state-display": row[5],
            "task": row[6],
            "cli": row[7]
            }

        run["task"]["href"] = task_href

        result.append(run)

    return ok_json(result)
