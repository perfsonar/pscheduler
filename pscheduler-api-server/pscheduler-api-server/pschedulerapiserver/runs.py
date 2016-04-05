#
# Run-Related Pages
#

import pscheduler

from pschedulerapiserver import application

from flask import request

from .dbcursor import dbcursor
from .json import *
from .response import *


# Proposed times for a task
@application.route("/tasks/<task>/runtimes", methods=['GET'])
def task_uuid_runtimes(task):
    try:
        range_start = arg_datetime('start')
        range_end   = arg_datetime('end')
    except ValueError:
        return bad_request('Invalid start or end time')
    if not task_exists(task):
        return not_found()

    return json_query_simple(dbcursor(), """
        SELECT row_to_json(apt.*)
        FROM  api_proposed_times(%s, %s, %s) apt
        """, [task, range_start, range_end], empty_ok=True)



# Established runs for a task
@application.route("/tasks/<task>/runs", methods=['GET', 'POST'])
def tasks_uuid_runs(task):
    if request.method == 'GET':
        # TODO: This should be exapandable and filterable by time, status,
        # limit numbers, etc.
        return json_query_simple(dbcursor(),
            "SELECT '" + base_url() + """/' || run.uuid
             FROM
                 run
                 JOIN task ON task.id = run.task
             WHERE
                task.uuid = %s""", [task])

    elif request.method == 'POST':

        start_time = arg_datetime('start')
        if start_time is None:
            return bad_request("Missing or invalid start time")

        dbcursor().execute("SELECT api_run_post(%s, %s)", [task, start_time])
        # TODO: Handle failure
        # TODO: Assert that rowcount is 1
        return ok('"' + base_url(dbcursor().fetchone()[0]) + '"')

    else:

        return not_allowed()



@application.route("/tasks/<task>/runs/<run>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def tasks_uuid_runs_run(task, run):

    if request.method == 'GET':

        # TODO: Should handle POST, PUT of full participant data and DELETE
        dbcursor().execute("""
            SELECT
                lower(run.times),
                upper(run.times),
                upper(run.times) - lower(run.times),
                task.participant,
                task.nparticipants,
                run.part_data,
                run.part_data_full,
                run.result,
                run.result_full,
                run.result_merged,
                run_state.enum,
                run_state.display
            FROM
                run
                JOIN task ON task.id = run.task
                JOIN run_state ON run_state.id = run.state
            WHERE
                task.uuid = %s
                AND run.uuid = %s
            """, [task, run])

        if dbcursor().rowcount == 0:
            return not_found()

        result = {}
        row = dbcursor().fetchone()
        result['href'] = request.url
        result['start-time'] = pscheduler.datetime_as_iso8601(row[0])
        result['end-time'] = pscheduler.datetime_as_iso8601(row[1])
        result['duration'] = pscheduler.timedelta_as_iso8601(row[2])
        result['participant'] = row[3]
        result['participants'] = row[4]
        result['participant-data'] = row[5]
        result['participant-data-full'] = row[6]
        result['result'] = row[7]
        result['result-full'] = row[8]
        result['result-merged'] = row[9]
        result['state'] = row[10]
        result['state-display'] = row[11]
        result['task-href'] = root_url('tasks/' + task)

        return json_response(json_dump(result))

    elif request.method == 'POST':

        start_time = arg_datetime('start')
        if start_time is None:
            return bad_request("Missing or invalid start time")

        dbcursor().execute("SELECT api_run_post(%s, %s, %s)", [task, start_time, run])
        # TODO: Handle failure
        # TODO: Assert that rowcount is 1
        return ok('"' + base_url() + '"')

    elif request.method == 'PUT':

        try:
            json_in = pscheduler.json_load(request.args.get('run'))
        except ValueError:
            return bad_request("Invalid JSON")

        # Only one thing can be udated at a time, and even that is a select subset.
        if len(json_in) != 1:
            return bad_request("Can only update one thing at a time.")

        if 'part-data-full' in json_in:

            dbcursor().execute("""UPDATE
                                  run
                              SET
                                  part_data_full = %s
                              WHERE
                                  uuid = %s
                                  AND EXISTS (SELECT * FROM task WHERE UUID = %s)
                              """,
                           [ pscheduler.json_dump(json_in['part-data-full']),
                             run, task])
            if dbcursor().rowcount != 1:
                return not_found()

        elif 'result-full' in json_in:

            dbcursor().execute("""UPDATE
                                  run
                              SET
                                  result_full = %s
                              WHERE
                                  uuid = %s
                                  AND EXISTS (SELECT * FROM task WHERE UUID = %s)
                              """,
                           [ pscheduler.json_dump(json_in['result-full']),
                             run, task])
            if dbcursor().rowcount != 1:
                return not_found()

        return ok()

    elif request.method == 'DELETE':

        # TODO: If this is the lead, the run's counterparts on the
        # other participating nodes need to be removed as well.

        dbcursor().execute("""
            DELETE FROM run
            WHERE
                task in (SELECT id FROM task WHERE uuid = %s)
                AND uuid = %s 
            """, [task, run])

        return ok() if dbcursor().rowcount == 1 else not_found()

    else:

        return not_allowed()


# TODO: This is probably OBE.  Or is it?
@application.route("/tasks/<task>/runs/<run>/part-data-full", methods=['GET', 'PUT'])
def tasks_uuid_runs_run_part_data_full(task, run):

    if request.method == 'GET':

        dbcursor().execute("""
            SELECT part_data_full
            FROM
                run
                JOIN task ON task.id = run.task
            WHERE
                task.uuid = %s
                AND run.uuid = %s
            """, [task, run])
        if dbcursor().rowcount == 0:
            return not_found();
        # TODO: Assert that rowcount should be 1 or just LIMIT the query?
        row = dbcursor().fetchone()
        return json_response(json_dump(row[0]))

    elif request.method == 'PUT':

        # TODO: Can't Flask validate JSON?
        try:
            json_in = json.loads(request.data)
        except ValueError:
            return bad_request("Invalid JSON")



        # Need to make sure the run exists.
        dbcursor().execute("""
            SELECT
              run.id
            FROM
                run
                JOIN task ON task.id = run.task
            WHERE
                task.uuid = %s
                AND run.uuid = %s
            """, [task, run])
        if dbcursor().rowcount == 0:
            return not_found();

        # TODO: Assert that rowcount should be 1 or just LIMIT the query?
        run_id = dbcursor().fetchone()[0]

        dbcursor().execute("""
            UPDATE run
            SET part_data_full = %s
            WHERE id = %s
            """, [request.data, run_id])

        return ok();

    else:

        assert False, "Should not be reached."
