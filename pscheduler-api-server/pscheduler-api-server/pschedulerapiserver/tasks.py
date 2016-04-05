#
# Task-Related Pages
#

import pscheduler

from pschedulerapiserver import application

from flask import request

from .dbcursor import dbcursor
from .json import *
from .response import *

def task_exists(task):
    """Determine if a task exists by its UUID"""
    dbcursor().execute("SELECT EXISTS (SELECT * FROM task WHERE uuid = %s)", [task])
    # TODO: Assert that rowcount is 1
    return dbcursor().fetchone()[0]
    


@application.route("/tasks", methods=['GET', 'POST', 'DELETE'])
def tasks():

    if request.method == 'GET':

        expanded = is_expanded()
        # TODO: Handle failure
        dbcursor().execute("SELECT json, uuid FROM task")
        result = []
        for row in dbcursor():
            url = base_url(row[1])
            if not expanded:
                result.append(url)
                continue
            row[0]['href'] = url
            result.append(row[0])
        return json_response(json_dump(result))

    elif request.method == 'POST':

        try:
            task = pscheduler.json_load(request.data)
        except ValueError:
            return bad_request("Invalid JSON:" + request.data)

        # Find the participants

        returncode, stdout, stderr = pscheduler.run_program(
            [ "pscheduler", "internal", "invoke", "test",
              task['test']['type'], "participants" ],
            stdin = pscheduler.json_dump(task['test']['spec'])
            )

        try:
            participants = [ host if host is not None
                             else pscheduler.api_this_host()
                             for host in pscheduler.json_load(stdout) ]
        except Exception as ex:
            # TODO: Return a 500?
            return error("Unable to load returned participant list: " + str(ex) + stderr)
        nparticipants = len(participants)

        # The host in the requested URL should match participant 0.

        netloc = urlparse.urlparse(request.url)[1].split(':')[0]
        if netloc != participants[0]:
            return bad_request("Wrong host %s; should be asking %s."
                               % (netloc, participants[0]))

        # TODO: Pick tools and add to task package

        return error("Not finished.")

        # TODO: Handle failure.
        dbcursor().execute("SELECT * FROM api_task_post( %s, 0)", [request.data])
        # TODO: Assert that rowcount is 1
        return ok(request.url + '/' + dbcursor().fetchone()[0])


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

        dbcursor().execute("""
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
        row = dbcursor().fetchone()
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
        # TODO: This should probably a PUT and not a POST.

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
        dbcursor().execute("SELECT * FROM api_task_post(%s, %s, %s)",
                       [request.data, participant, uuid])
        # TODO: Assert that rowcount is 1
        return ok(base_url())

    elif request.method == 'DELETE':

        # TODO: This should just disable the task.
        return not_implemented()

    else:

        return not_allowed()
