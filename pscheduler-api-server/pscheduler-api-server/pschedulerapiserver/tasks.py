#
# Task-Related Pages
#

import pscheduler

from pschedulerapiserver import application

from flask import request

from .dbcursor import dbcursor
from .json import *
from .log import log
from .response import *

def task_exists(task):
    """Determine if a task exists by its UUID"""
    dbcursor().execute("SELECT EXISTS (SELECT * FROM task WHERE uuid = %s)", [task])
    # TODO: Assert that rowcount is 1
    return dbcursor().fetchone()[0]
    


def pick_tool(lists):
    """Count and score the number of times each tool appears in a list
    of lists retrieved from servers, then return the name of the tool
    that was preferred or None if there were none in common.  (Not to
    be used outside this module.)"""

    participants = len(lists)

    # The count is used to determine whether or not a tool is supported
    # by all participants.

    # The score is the sum of each tool's position in each list and is
    # used to determine its overall preference.  Like golf, the tool
    # with the smallest score has the highest preference.

    # TODO: At some point, we'll have to account for minimum schema
    # version supported, too.  (Or will hosts that don't support it just
    # bow out?)

    count = {}
    score = {}

    for tool_list in lists:

        if tool_list is None:
            continue

        for position in range(len(tool_list)):

            tool = tool_list[position]['name']

            try:
                count[tool] += 1
            except KeyError:
                count[tool] = 1

            try:
                score[tool] += position
            except KeyError:
                score[tool] = position

    # Pick out the tools all lists have in common and their scores.

    common = {}
    for tool in count:
        if count[tool] == participants:
            common[tool] = score[tool]

    # Nothing in common means no thing can be picked.

    if not len(common):
        return None

    # Pick out the common tool with the lowest score.
    ordered = sorted(common.items(), key=lambda value: value[1])
    return ordered[0][0]



@application.route("/tasks", methods=['GET', 'POST', 'DELETE'])
def tasks():

    if request.method == 'GET':

        expanded = is_expanded()
        # TODO: Handle failure
        dbcursor().execute("""
            SELECT json, uuid
            FROM task ORDER BY added
            """)
        result = []
        for row in dbcursor():
            url = base_url(row[1])
            if not expanded:
                result.append(url)
                continue
            row[0]['href'] = url
            result.append(row[0])
        return json_response(result)

    elif request.method == 'POST':

        try:
            task = pscheduler.json_load(request.data)
        except ValueError:
            return bad_request("Invalid JSON:" + request.data)

        # See if the task spec is valid

        try:
            returncode, stdout, stderr = pscheduler.run_program(
                [ "pscheduler", "internal", "invoke", "test",
                  task['test']['type'], "spec-is-valid" ],
                stdin = pscheduler.json_dump(task['test']['spec'])
                )

            if returncode != 0:
                return error(stderr)
        except Exception as ex:
            return error("Unable to validate test spec: " + str(ex))


        # Find the participants

        try:
            returncode, stdout, stderr = pscheduler.run_program(
                [ "pscheduler", "internal", "invoke", "test",
                  task['test']['type'], "participants" ],
                stdin = pscheduler.json_dump(task['test']['spec'])
                )

            if returncode != 0:
                return error(stderr)

            participants = [ host if host is not None
                             else pscheduler.api_this_host()
                             for host in pscheduler.json_load(stdout) ]
        except Exception as ex:
            return error("Unable to determine participants: " + str(ex))
        nparticipants = len(participants)

        # The host in the requested URL should match participant 0.

        netloc = urlparse.urlparse(request.url)[1].split(':')[0]
        if netloc != participants[0]:
            return bad_request("Wrong host %s; should be asking %s."
                               % (netloc, participants[0]))

        #
        # TOOL SELECTION
        #

        # TODO: Need to provide for tool being specified by the task
        # package.

        tools = []

        # TODO: Get the local tool list out of the database instead of
        # doing a HTTP round trip.
        for participant in participants:

            try:
                r = requests.get(pscheduler.api_url(participant, "tools"),
                                 params={ 'test': pscheduler.json_dump(task['test']) })
                if r.status_code != 200:
                    raise Exception("%d: %s" % (r.status_code, r.text))
                tools.append( pscheduler.json_load(str(r.text)) )
            except Exception as ex:
                return error("Error getting tools from %s: %s" \
                                     % (participant, str(ex)))
            log.debug("Participant %s offers tools %s", participant, tools)

        if len(tools) != nparticipants:
            return error("Didn't get a full set of tool responses")

        tool = pick_tool(tools)
        if tool is None:
            # TODO: This could stand some additional diagnostics.
            return no_can_do("Couldn't find a tool in common")

        task['tool'] = tool

        #
        # TASK CREATION
        #

        task_data = pscheduler.json_dump(task)

        tasks_posted = []

        # Post the lead with the local database, which also assigns
        # its UUID.

        # TODO: Handle failure.
        dbcursor().execute("SELECT * FROM api_task_post(%s, 0)", [task_data])
        # TODO: Assert that rowcount is 1 and has one column

        task_uuid = dbcursor().fetchone()[0]

        # Other participants get the UUID forced upon them.

        for participant in range(1,nparticipants):
            part_name = participants[participant]
            try:
                r = requests.post(pscheduler.api_url(part_name,
                                                     'tasks/' + task_uuid),
                                  params={ 'participant': participant },
                                  data=task_data)
                if r.status_code != 200:
                    raise Exception("%d: %s" % (r.status_code, r.text))
                tasks_posted.append(r.text)

            except Exception as ex:

                for url in tasks_posted:
                    r = requests.delete(url)
                
                # TODO: Handle failure?
                dbcursor().execute("SELECT api_task_delete(%s)", [task_uuid])

                return error("Error while tasking %d: %s" % (participant, ex))

        return ok_json(pscheduler.api_url(path='/tasks/' + task_uuid))



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
        if row is None:
            return not_found()
        json = row[0]

        # Add details if we were asked for them.
        if arg_boolean('detail'):

            json['detail'] = {
                'added': None if row[1] is None \
                    else pscheduler.datetime_as_iso8601(row[1]),
                'start': None if row[2] is None \
                    else pscheduler.datetime_as_iso8601(row[2]),
                'start': None if row[3] is None \
                    else pscheduler.timedelta_as_iso8601(row[3]),
                'duration': None if row[4] is None \
                    else pscheduler.timedelta_as_iso8601(row[4]),
                'runs': None if row[5] is None \
                    else int(row[5]),
                'participants': None if row[6] is None \
                    else row[6]
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
