#!/usr/bin/python
#
# pScheduler REST API Server
#


# TODO: Should break this up into parts using Flask blueprints or
# something similar.  See http://stackoverflow.com/a/15231623 and
# http://flask.pocoo.org/docs/0.10/patterns/packages.

# TODO: Need to add code to validate incoming UUIDs so the database
# doesn't barf on them and leave a cryptic error message.

import json
import optparse
import pscheduler
import socket
import urlparse


from flask import Flask
from flask import request
from flask import Response
from flask import url_for

application = Flask(__name__)
application.config["APPLICATION_ROOT"] = pscheduler.api_root()


# TODO: For now, these are is hard-wired defaults.  At some point we
# should be pulling this from a config file.

dsn = "@/etc/pscheduler/database-dsn"
opt_debug = False
always_pretty = False

# Connect to the database.
cursor = pscheduler.pg_cursor(dsn)

# TODO: What happens if the connection goes south?



#
# Utility Functions and Declarations
#


# Responses

def json_response(data):
    return Response(data, mimetype='application/json')

def ok(message="OK"):
    return Response(message, status=200)

def ok_json(value=''):
    return json_response(json_dump(value)), 200

def bad_request(message="Bad request"):
    return Response(message, status=400)

def not_found():
    return Response("Resource not found", status=404)

def not_allowed():
    return Response("%s not allowed on this resource\n" % request.method,
                    status=405)

def not_implemented():
    return Response("Not implemented yet", 501)



# URLs

def internal_url(path):
    return request.url_root + path

def root_url(path = None):
    return request.url_root + ("" if path is None else path)

def base_url(path = None):
    return request.base_url + ("" if path is None else "/" + path)

def url_last_in_path(url):
    result = urlparse.urlparse(url)
    return result.path.split('/')[-1]


# Arguments

def arg_boolean(name):
    """Determine if a boolean argument is part of a request.  The
    argument is considered true if it is 'true', 'yes' or '1' or if it
    is present but has no value.  Otherwise it is considered False."""
    argval = request.args.get(name)
    if argval is None:
        return False;
    argval = argval.lower()
    if argval in [ '', 'true', 'yes', '1' ]:
        return True
    return False

def arg_datetime(name):
    """Fetch and validate an argument as an ISO8601 date and time,
    returning a datetime if specificed, None if not and throwing a
    ValueError if invalid."""
    argval = request.args.get(name)
    if argval is None:
        return None
    timestamp = pscheduler.iso8601_as_datetime(argval)
    if timestamp is None:
        raise ValueError("Invalid timestamp; expecting ISO8601.")
    return timestamp

def arg_cardinal(name):
    """Fetch and validate an argument as a cardinal number."""
    argval = request.args.get(name)
    if argval is None:
        return None
    try:
        cardinal = int(argval)
        if cardinal < 1:
            raise ValueError
    except ValueError:
        raise ValueError("Invalid cardinal; expecting integer > 0")
    return cardinal


def is_expanded():
    return arg_boolean('expanded')





# JSON

def json_dump(dump):
    return pscheduler.json_dump(dump,
                                pretty=(always_pretty or arg_boolean('pretty'))
                                )


def json_query_simple(query, query_args=[], empty_ok=False):
    """Do a SQL query that selects one column and dump those values as
    a JSON array"""

    if request.method != 'GET':
        return not_allowed()

    # TODO: Handle failure
    cursor.execute(query, query_args)
    if cursor.rowcount == 0 and not empty_ok:
        return not_found()
    result = []
    for row in cursor:
        result.append(row[0])
    return json_response(json_dump(result))



def json_query(query, query_args=[], name = 'name', single = False):
    """Do a SQL query that selects one column containing JSON and dump
    the results, honoring the 'expanded' and 'pretty' arguments.  If
    the 'single' argument is True, the first-returned row will be
    returned as a single item instead of an array."""

    if request.method != 'GET':
        return not_allowed()

    # TODO: Handle failure
    cursor.execute(query, query_args)
    if single and cursor.rowcount == 0:
        return not_found()
    result = []
    for row in cursor:
        this = base_url(None if single else row[0][name])
        row[0]['href'] = this
        result.append( row[0] if single or is_expanded() else this)
    return json_response(json_dump(result[0] if single else result))



#
# The Root
#

@application.route("/", methods=['GET'])
def root():
    return ok("This is the pScheduler API server on %s.\n"
              % socket.gethostname())


# TODO: Remove after development.
@application.route("/s", methods=['GET', 'PUT'])
def sandbox():
    return ok("Sandbox")



#
# Administrative Information
#

@application.route("/schedule-horizon", methods=['GET'])
def schedule_horizon():
    """Get the length of the server's scheduling horizon"""
    cursor.execute("SELECT schedule_time_horizon()")
    # TODO: Assert that rowcount is 1
    return ok_json(pscheduler.timedelta_as_iso8601(cursor.fetchone()[0]))





#
# Tests
#

# All tests
@application.route("/tests", methods=['GET'])
def tests():
    return json_query("SELECT json FROM test", [])


# Test <name>
@application.route("/tests/<name>", methods=['GET'])
def tests_name(name):
    return json_query("SELECT json FROM test WHERE name = %s",
                      [name], single=True)


# Tools that can carry out test <name>
@application.route("/tests/<name>/tools", methods=['GET'])
def tests_name_tools(name):
    expanded = is_expanded()
    # TODO: Handle failure
    cursor.execute("""
        SELECT
            tool.name,
            tool.json
        FROM
            tool
            JOIN tool_test ON tool_test.tool = tool.id
            JOIN test ON test.id = tool_test.test
        """)
    result = []
    for row in cursor:
        url = root_url('tools/' + row[0])
        if not expanded:
            result.append(url)
            continue
        row[1]['href'] = url
        result.append(row[1])
    return json_response(json_dump(result))



#
# Tools
#

@application.route("/tools", methods=['GET'])
def tools():
    # Get only the tools that can run this test.
    test_filter = request.args.get('test', None)
    if test_filter is None:
        return json_query("SELECT json FROM tool", [])
    else:
        cursor.execute("SELECT api_tools_for_test(%s)", [test_filter])
        # TODO: Assert that there's one row.
        return ok_json( cursor.fetchone()[0] )


@application.route("/tools/<name>", methods=['GET'])
def tools_name(name):
    return json_query("SELECT json FROM tool WHERE name = %s", [name], single=True)



#
# Tasks
#


def task_exists(task):
    """Determine if a task exists by its UUID"""
    cursor.execute("SELECT EXISTS (SELECT * FROM task WHERE uuid = %s)", [task])
    # TODO: Assert that rowcount is 1
    return cursor.fetchone()[0]
    


@application.route("/tasks", methods=['GET', 'POST', 'DELETE'])
def tasks():

    if request.method == 'GET':

        expanded = is_expanded()
        # TODO: Handle failure
        cursor.execute("SELECT json, uuid FROM task")
        result = []
        for row in cursor:
            url = base_url(row[1])
            if not expanded:
                result.append(url)
                continue
            row[0]['href'] = url
            result.append(row[0])
        return json_response(json_dump(result))

    elif request.method == 'POST':

        # TODO: This is only for participant 0.

        try:
            json_in = pscheduler.json_load(request.data)
        except ValueError:
            return bad_request("Invalid JSON")

        # TODO: Handle failure.
        cursor.execute("SELECT * FROM api_task_post( %s, 0)", [request.data])
        # TODO: Assert that rowcount is 1
        return ok(request.url + '/' + cursor.fetchone()[0])


    elif request.method == 'DELETE':

        # TODO: This should just disable the task.
        return not_implemented()

    else:

        return not_allowed()



@application.route("/tasks/<uuid>", methods=['GET', 'POST', 'DELETE'])
def tasks_uuid(uuid):
    if request.method == 'GET':

        # Get a task, adding server-derived details if a 'detail'
        # argument is present.

        cursor.execute("""
            SELECT
                json,
                added,
                start,
                slip,
                duration,
                runs,
                participants
            FROM task WHERE uuid = %s
        """, [uuid])

        # TODO: Assert that we got one row
        row = cursor.fetchone()
        json = row[0]

        # Add details if we were asked for them.
        if arg_boolean('detail'):
            json['detail'] = {
                'added': pscheduler.datetime_as_iso8601(row[1]),
                'start': pscheduler.datetime_as_iso8601(row[2]),
                'slip': pscheduler.timedelta_as_iso8601(row[3]),
                'duration': pscheduler.timedelta_as_iso8601(row[4]),
                'runs': int(row[5]),
                'participants': row[6]
                }

        return ok_json(json)

    elif request.method == 'POST':

        # TODO: This is only for participant 1+

        try:
            json_in = pscheduler.json_load(request.data)
        except ValueError:
            return bad_request("Invalid JSON")

        try:
            participant = arg_cardinal('participant')
        except ValueError as ex:
            return bad_request("Invalid participant: " + str(ex))

        # TODO: Pluck UUID from URI
        uuid = url_last_in_path(request.url)

        # TODO: Handle failure.
        cursor.execute("SELECT * FROM api_task_post(%s, %s, %s)",
                       [request.data, participant, uuid])
        # TODO: Assert that rowcount is 1
        return ok(base_url())

    elif request.method == 'DELETE':

        # TODO: This should just disable the task.
        return not_implemented()

    else:

        return not_allowed()






#
# Runs
#


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

    return json_query_simple("""
        SELECT row_to_json(apt.*)
        FROM  api_proposed_times(%s, %s, %s) apt
        """, [task, range_start, range_end], empty_ok=True)



# Established runs for a task
@application.route("/tasks/<task>/runs", methods=['GET', 'POST'])
def tasks_uuid_runs(task):
    if request.method == 'GET':
        # TODO: This should be exapandable and filterable by time, status,
        # limit numbers, etc.
        return json_query_simple(
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

        cursor.execute("SELECT api_run_post(%s, %s)", [task, start_time])
        # TODO: Handle failure
        # TODO: Assert that rowcount is 1
        return ok('"' + base_url(cursor.fetchone()[0]) + '"')

    else:

        return not_allowed()



@application.route("/tasks/<task>/runs/<run>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def tasks_uuid_runs_run(task, run):

    if request.method == 'GET':

        # TODO: Should handle POST, PUT of full participant data and DELETE
        cursor.execute("""
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

        if cursor.rowcount == 0:
            return not_found()

        result = {}
        row = cursor.fetchone()
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

        cursor.execute("SELECT api_run_post(%s, %s, %s)", [task, start_time, run])
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

            cursor.execute("""UPDATE
                                  run
                              SET
                                  part_data_full = %s
                              WHERE
                                  uuid = %s
                                  AND EXISTS (SELECT * FROM task WHERE UUID = %s)
                              """,
                           [ pscheduler.json_dump(json_in['part-data-full']),
                             run, task])
            if cursor.rowcount != 1:
                return not_found()

        elif 'result-full' in json_in:

            cursor.execute("""UPDATE
                                  run
                              SET
                                  result_full = %s
                              WHERE
                                  uuid = %s
                                  AND EXISTS (SELECT * FROM task WHERE UUID = %s)
                              """,
                           [ pscheduler.json_dump(json_in['result-full']),
                             run, task])
            if cursor.rowcount != 1:
                return not_found()

        return ok()

    elif request.method == 'DELETE':

        # TODO: If this is the lead, the run's counterparts on the
        # other participating nodes need to be removed as well.

        cursor.execute("""
            DELETE FROM run
            WHERE
                task in (SELECT id FROM task WHERE uuid = %s)
                AND uuid = %s 
            """, [task, run])

        return ok() if cursor.rowcount == 1 else not_found()

    else:

        return not_allowed()


# TODO: This is probably OBE.
@application.route("/tasks/<task>/runs/<run>/part-data-full", methods=['GET', 'PUT'])
def tasks_uuid_runs_run_part_data_full(task, run):

    if request.method == 'GET':

        cursor.execute("""
            SELECT part_data_full
            FROM
                run
                JOIN task ON task.id = run.task
            WHERE
                task.uuid = %s
                AND run.uuid = %s
            """, [task, run])
        if cursor.rowcount == 0:
            return not_found();
        # TODO: Assert that rowcount should be 1 or just LIMIT the query?
        row = cursor.fetchone()
        return json_response(json_dump(row[0]))

    elif request.method == 'PUT':

        # TODO: Can't Flask validate JSON?
        try:
            json_in = json.loads(request.data)
        except ValueError:
            return bad_request("Invalid JSON")



        # Need to make sure the run exists.
        cursor.execute("""
            SELECT
              run.id
            FROM
                run
                JOIN task ON task.id = run.task
            WHERE
                task.uuid = %s
                AND run.uuid = %s
            """, [task, run])
        if cursor.rowcount == 0:
            return not_found();

        # TODO: Assert that rowcount should be 1 or just LIMIT the query?
        run_id = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE run
            SET part_data_full = %s
            WHERE id = %s
            """, [request.data, run_id])

        return ok();

    else:

        assert False, "Should not be reached."
                    


# TODO: Need a catch-all to do 404s.




if __name__ == "__main__":
    application.run(
        host='0.0.0.0',
        port=29285,  # Spell out "BWCTL" on a phone and this is what you get.
        debug=opt_debug
        )
