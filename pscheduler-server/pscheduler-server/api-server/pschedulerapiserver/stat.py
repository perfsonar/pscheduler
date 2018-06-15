#
# Statistics-Related Pages
#

import pscheduler

from pschedulerapiserver import application

from flask import request

from .dbcursor import dbcursor_query
from .json import *
from .response import *


def single_numeric_query(query, query_args = []):

    cursor = dbcursor_query(query, query_args)

    if cursor.rowcount == 0:
        return not_found()

    row = cursor.fetchone()
    cursor.close()

    return ok(str(row[0]))


#
# System Controls
#
@application.route("/stat/control/pause", methods=['GET'])
def stat_control_pause():
    cursor = dbcursor_query("""
        SELECT
            control_is_paused(),
            date_trunc('second', pause_runs_until - now()),
            pause_runs_until = tstz_infinity()
        FROM control""")
    if cursor.rowcount != 1:
        pscheduler.fail("Got back more data than expected.")
    (is_paused, left, infinite) = cursor.fetchone()
    cursor.close()

    result = { "is_paused": is_paused }
    if is_paused:
        result["infinite"] = infinite
        if not infinite:
            result["remaining"] = pscheduler.timedelta_as_iso8601(left)

    return ok_json(result)



#
# Archiving
#

@application.route("/stat/archiving/backlog", methods=['GET'])
def stat_archive_backlog():
    return single_numeric_query("""SELECT COUNT(*) FROM archiving
                                   WHERE NOT archived AND next_attempt < now()""")

@application.route("/stat/archiving/upcoming", methods=['GET'])
def stat_archive_upcoming():
    return single_numeric_query("""SELECT COUNT(*) FROM archiving
                                   WHERE NOT archived AND next_attempt >= now()""")


#
# HTTP Queue
#

@application.route("/stat/http-queue/backlog", methods=['GET'])
def stat_http_queue_backlog():
    return single_numeric_query("""SELECT COUNT(*) FROM http_queue
                                   WHERE attempts = 0""")

@application.route("/stat/http-queue/length", methods=['GET'])
def stat_http_queue_length():
    return single_numeric_query("""SELECT COUNT(*) FROM http_queue""")



#
# Runs
#


@application.route("/stat/runs/pending", methods=['GET'])
def stat_runs_pending():
    return single_numeric_query("""SELECT COUNT(*) FROM run 
                                   WHERE STATE = run_state_pending()""")

@application.route("/stat/runs/on-deck", methods=['GET'])
def stat_runs_on_deck():
    return single_numeric_query("""SELECT COUNT(*) FROM run 
                                   WHERE STATE = run_state_on_deck()""")

@application.route("/stat/runs/running", methods=['GET'])
def stat_runs_running():
    return single_numeric_query("""SELECT COUNT(*) FROM run 
                                   WHERE STATE = run_state_running()""")

@application.route("/stat/runs/cleanup", methods=['GET'])
def stat_runs_cleanup():
    return single_numeric_query("""SELECT COUNT(*) FROM run 
                                   WHERE STATE = run_state_cleanup()""")

@application.route("/stat/runs/finished", methods=['GET'])
def stat_runs_finished():
    return single_numeric_query("""SELECT COUNT(*) FROM run 
                                   WHERE STATE = run_state_finished()""")

@application.route("/stat/runs/overdue", methods=['GET'])
def stat_runs_overdue():
    return single_numeric_query("""SELECT COUNT(*) FROM run 
                                   WHERE STATE = run_state_overdue()""")

@application.route("/stat/runs/missed", methods=['GET'])
def stat_runs_missed():
    return single_numeric_query("""SELECT COUNT(*) FROM run 
                                   WHERE STATE = run_state_missed()""")

@application.route("/stat/runs/failed", methods=['GET'])
def stat_runs_failed():
    return single_numeric_query("""SELECT COUNT(*) FROM run 
                                   WHERE STATE = run_state_failed()""")

@application.route("/stat/runs/preempted", methods=['GET'])
def stat_runs_preempted():
    return single_numeric_query("""SELECT COUNT(*) FROM run 
                                   WHERE STATE = run_state_preempted()""")

@application.route("/stat/runs/nonstart", methods=['GET'])
def stat_runs_nonstart():
    return single_numeric_query("""SELECT COUNT(*) FROM run 
                                   WHERE STATE = run_state_nonstart()""")
