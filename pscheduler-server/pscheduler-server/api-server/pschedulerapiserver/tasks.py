#
# Task-Related Pages
#

import crontab
import pscheduler
import urllib.request, urllib.parse, urllib.error

from pschedulerapiserver import application

from flask import request

from .access import *
from .dbcursor import dbcursor_query
from .json import *
from .limitproc import *
from .log import log
from .response import *
from .util import *


class TaskPostingException(Exception):
    """This is used internally when some phase of task posting fails."""
    pass


def task_exists(task):
    """Determine if a task exists by its UUID"""

    cursor = dbcursor_query("SELECT EXISTS (SELECT * FROM task WHERE uuid = %s)",
                            [task], onerow=True)

    return cursor.fetchone()[0]
    


def pick_tool(lists, pick_from=None):
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

    if pick_from is None:

        # Take the tool with the lowest score.
        ordered = sorted(list(common.items()), key=lambda value: value[1])
        return ordered[0][0]

    else:

        # Find the first tool in the pick list that matches
        for candidate in pick_from:
            if candidate in common:
                return candidate

    # If we got here, nothing matched.
    return None


def __tasks_get_filtered(uri_base,
                         where_clause='TRUE',
                         args=[],
                         expanded=False,
                         detail=False,
                         single=True,
                         part_key_field=None
):

    """Get one or more tasks from a table using a WHERE clause."""

    # Let this throw; callers are responsible for catching.

    cursor = dbcursor_query(
        """SELECT json_detail, uuid, participant_key FROM task WHERE %s""" % (where_clause),
        args)

    tasks_returned = []

    for row in cursor:

        uri = uri_base if single else "%s/%s" % (uri_base, row[1])

        if not expanded:
            tasks_returned.append(uri)
            continue

        json = row[0]
        assert json is not None, "Database did not return details."

        # This is always added.
        json['href'] = uri

        # The lead participant passes the participant list to the
        # others within the JSON, but that shouldn't come out when
        # querying it.

        try:
            del json["participants"]
        except KeyError:
            pass


        # Add URI-specific details if we were asked for them,
        # otherwise ditch the details entirely.

        if detail:

            json['detail']['href'] = uri
            json['detail']['runs-href'] = "%s/runs" % (uri)
            json['detail']['first-run-href'] = "%s/runs/first" % (uri)
            json['detail']['next-run-href'] = "%s/runs/next" % (uri)

        else:

            try:
                del json['detail']
            except KeyError:
                pass

        if part_key_field is not None:
            json[part_key_field] = row[2]

        tasks_returned.append(json)

    return tasks_returned



@application.route("/tasks", methods=['GET', 'POST'])
def tasks():

    if request.method == 'GET':

        where_clause = "TRUE"
        args=[]

        try:
            json_query = arg_json("json")
        except ValueError as ex:
            return bad_request(str(ex))

        if json_query is not None:
            where_clause += " AND task.json_detail @> %s"
            args.append(request.args.get("json"))

        where_clause += " ORDER BY added"

        tasks = __tasks_get_filtered(
            request.base_url,
            where_clause=where_clause,
            args=args,
            expanded=is_expanded(),
            detail=arg_boolean("detail"),
            single=False
        )

        # Returns multiple tasks, must be sanitized
        return ok_json(tasks, sanitize=True)

    elif request.method == 'POST':

        data = request.data.decode("ascii")

        try:
            task = pscheduler.json_load(data, max_schema=4)
        except ValueError as ex:
            return bad_request("Invalid task specification: %s" % (str(ex)))

        # Validate the JSON against a TaskSpecification
        # TODO: Figure out how to do this without the intermediate object

        valid, message = pscheduler.json_validate({"": task}, {
            "type": "object",
            "properties": {
                "": {"$ref": "#/pScheduler/TaskSpecification"}
            },
            "required": [""]
        })

        if not valid:
            return bad_request("Invalid task specification: %s" % (message))

        # See if the test spec is valid

        try:
            returncode, stdout, stderr = pscheduler.plugin_invoke(
                "test", task['test']['type'], "spec-is-valid",
                stdin=pscheduler.json_dump(task['test']['spec'])
                )

            if returncode != 0:
                return error("Unable to validate test spec: %s" % (stderr))
            validate_json = pscheduler.json_load(stdout, max_schema=1)
            if not validate_json["valid"]:
                return bad_request("Invalid test specification: %s" %
                                   (validate_json.get("error", "Unspecified error")))
        except Exception as ex:
            return error("Unable to validate test spec: " + str(ex))

        log.debug("Validated test: %s", pscheduler.json_dump(task['test']))


        # Validate the schedule

        try:
            cron = crontab.CronTab(task["schedule"]["repeat-cron"])
        except (AttributeError, ValueError):
                return error("Cron repeat specification is invalid.")
        except KeyError:
            pass



        # Validate the archives

        for archive in task.get("archives", []):

            # Data

            try:
                returncode, stdout, stderr = pscheduler.plugin_invoke(
                    "archiver", archive["archiver"], "data-is-valid",
                    stdin=pscheduler.json_dump(archive["data"]),
                )
                if returncode != 0:
                    return error("Unable to validate archive spec: %s" % (stderr))
            except Exception as ex:
                return error("Unable to validate test spec: " + str(ex))

            try:
                returned_json = pscheduler.json_load(stdout)
                if not returned_json["valid"]:
                    return bad_request("Invalid archiver data: %s" % (returned_json["error"]))
            except Exception as ex:
                return error("Internal probelm validating archiver data: %s" % (str(ex)))

            # Transform, if there was one.

            if "transform" in archive:
                transform = archive["transform"]
                try:
                    _ = pscheduler.JQFilter(
                        filter_spec=transform["script"],
                        args=transform.get("args", {} )
                    )

                except ValueError as ex:
                    return error("Invalid transform: %s" % (str(ex)))


        # Validate the lead binding if there was one.

        lead_bind = task.get("lead-bind", None)
        if lead_bind is not None \
           and (pscheduler.address_interface(lead_bind) is None):
            return bad_request("Lead bind '%s' is not  on this host"
                              % (lead_bind))


        # Evaluate the task against the limits and reject the request
        # if it doesn't pass.  We do this early so anything else in
        # the process gets any rewrites.

        log.debug("Checking limits on %s", task)

        (processor, whynot) = limitprocessor()
        if processor is None:
            log.debug("Limit processor is not initialized. %s", whynot)
            return no_can_do("Limit processor is not initialized: %s" % whynot)

        hints, error_response = request_hints();
        if hints is None:
            log.debug("Can't come up with valid hints for lead task limits.")
            return error_response

        hints_data = pscheduler.json_dump(hints)

        log.debug("Processor = %s" % processor)
        passed, limits_passed, diags, new_task, _priority \
            = processor.process(task, hints)

        if not passed:
            return forbidden("Task forbidden by limits:\n" + diags)

        if new_task is not None:
            try:
                task = new_task
                returncode, stdout, stderr = pscheduler.plugin_invoke(
                    "test", task['test']['type'], "spec-is-valid",
                    stdin=pscheduler.json_dump(task["test"]["spec"])
                )

                if returncode != 0:
                    return error("Failed to validate rewritten test specification: %s" % (stderr))
                validate_json = pscheduler.json_load(stdout, max_schema=1)
                if not validate_json["valid"]:
                    return bad_request("Rewritten test specification is invalid: %s" %
                                   (validate_json.get("error", "Unspecified error")))
            except Exception as ex:
                return error("Unable to validate rewritten test specification: " + str(ex))



        # Find the participants

        try:

            returncode, stdout, stderr = pscheduler.plugin_invoke(
                "test", task['test']['type'], "participants",
                stdin=pscheduler.json_dump(task['test']['spec']),
                timeout=5
                )

            if returncode != 0:
                return error("Unable to determine participants: " + stderr)

            participants = [ host if host is not None else
                             server_netloc() for host in
                             pscheduler.json_load(stdout,
                                                  max_schema=1)["participants"] ]
        except Exception as ex:
            return error("Exception while determining participants: " + str(ex))
        nparticipants = len(participants)

        # TODO: The participants must be unique.  This should be
        # verified by fetching the host name from each one.

        #
        # TOOL SELECTION
        #

        # TODO: Need to provide for tool being specified by the task
        # package.

        tools = []

        tool_params={ "test": pscheduler.json_dump(task["test"]) }

        tool_offers = {}

        for participant_no in range(0, len(participants)):

            participant = participants[participant_no]

            try:

                # Make sure the other participants are running pScheduler

                participant_api = pscheduler.api_url_hostport(participant)

                log.debug("Pinging %s" % (participant))
                status, result = pscheduler.url_get(
                    participant_api, throw=False, timeout=10,
                    bind=lead_bind)

                if status == 400:
                    raise TaskPostingException(result)
                elif status in [ 202, 204, 205, 206, 207, 208, 226,
                                 300, 301, 302, 303, 304, 205, 306, 307, 308 ] \
                    or ( (status >= 400) and (status <=499) ):
                    raise TaskPostingException("Host is not running pScheduler")
                elif status != 200:
                    raise TaskPostingException("returned status %d: %s"
                                               % (status, result))


                # TODO: This will fail with a very large test spec.
                status, result = pscheduler.url_get(
                    "%s/tools" % (participant_api),
                    params=tool_params,
                    throw=False,
                    bind=lead_bind
                    )
                if status != 200:
                    raise TaskPostingException("%d: %s" % (status, result))
                tools.append(result)
            except TaskPostingException as ex:
                return error("Error getting tools from %s: %s" \
                                     % (participant, str(ex)))
            log.debug("Participant %s offers tools %s", participant, result)
            tool_offers[participant] = result

        if len(tools) != nparticipants:
            return error("Didn't get a full set of tool responses")

        if "tools" in task:
            tool = pick_tool(tools, pick_from=task['tools'])
        else:
            tool = pick_tool(tools)

        # Complain if no usable tool was found

        if tool is None:

            offers = []
            for participant in participants:
                participant_offers = tool_offers.get(participant, [{"name": "nothing"}])
                if participant_offers is not None:
                    offer_set = [ offer["name"] for offer in participant_offers ]
                else:
                    offer_set = [ "nothing" ]
                offers.append("%s offered %s" % (
                    participant,
                    ", ".join(offer_set)
                ))

            return no_can_do(
                "No tool in common among the participants:  %s." % (
                    ";  ".join(offers)) )


        task['tool'] = tool



        #
        # TASK CREATION
        #

        tasks_posted = []



        # Post the lead with the local database, which also assigns
        # its UUID.  Make it disabled so the scheduler doesn't try to
        # do anything with it until the task has been submitted to all
        # of the other participants.

        cursor = dbcursor_query(
            "SELECT uuid, participant_key FROM api_task_post(%s, %s, %s, %s, 0, %s, NULL, FALSE, %s)",
            [pscheduler.json_dump(task), participants, hints_data,
             pscheduler.json_dump(limits_passed),
             task.get("priority", None), diags], onerow=True)

        if cursor.rowcount == 0:
            return error("Task post failed; poster returned nothing.")

        (task_uuid, task_participant_key) = cursor.fetchone()

        log.debug("Tasked lead, UUID %s", task_uuid)

        # Other participants get the UUID and participant list forced upon them.

        task["participants"] = participants


        # If there's a participant key, add that to the task for other
        # participants.

        if task_participant_key is not None and "_key" not in task:
            log.debug("Adding participant key %s", task_participant_key)
            task["_key"] = task_participant_key


        for participant in range(1,nparticipants):

            part_name = participants[participant]
            log.debug("Tasking participant %s", part_name)
            try:

                # Post the task

                log.debug("Tasking %d@%s: %s", participant, part_name, task)
                post_url = pscheduler.api_url_hostport(part_name,
                                                       'tasks/' + task_uuid)

                log.debug("Posting task to %s", post_url)
                status, result = pscheduler.url_post(
                    post_url,
                    params={ "participant": participant },
                    data=task,
                    bind=lead_bind,
                    json=False,
                    throw=False)
                log.debug("Remote returned %d: %s", status, result)
                if status != 200:
                    raise TaskPostingException("Unable to post task to %s: %s"
                                               % (part_name, result))
                tasks_posted.append(result)

                # Fetch the task's details and add the list of limits
                # passed to our own.

                status, result = pscheduler.url_get(post_url,
                                                    params={ "detail": True },
                                                    bind=lead_bind,
                                                    throw=False)
                if status != 200:
                    raise TaskPostingException(
                        "Unable to fetch posted task from %s: %s"
                        % (part_name, result))
                log.debug("Fetched %s", result)
                try:
                    details = result["detail"]["spec-limits-passed"]
                    log.debug("Details from %s: %s", post_url, details)
                    limits_passed.extend(details)
                except KeyError:
                    pass

            except TaskPostingException as ex:

                # Disable the task locally and let it get rid of the
                # other participants.

                posted_to = "%s/%s" % (request.url, task_uuid)
                parsed = list(urllib.parse.urlsplit(posted_to))
                parsed[1] = "%s"
                template = urllib.parse.urlunsplit(parsed)

                try:
                    dbcursor_query("SELECT api_task_disable(%s, %s)",
                                   [task_uuid, template])
                except Exception:
                    log.exception()

                return error("Error while tasking %s: %s" % (part_name, ex))


        # Update the list of limits passed in the local database
        # TODO: How do the other participants know about this?
        log.debug("Limits passed: %s", limits_passed)
        cursor = dbcursor_query(
            "UPDATE task SET limits_passed = %s::JSON WHERE uuid = %s",
            [pscheduler.json_dump(limits_passed), task_uuid])

        # Enable the task so the scheduler will schedule it.
        try:
            dbcursor_query("SELECT api_task_enable(%s)", [task_uuid])
        except Exception:
            log.exception()
            return error("Failed to enable task %s.  See system logs." % task_uuid)
        log.debug("Task enabled for scheduling.")

        task_url = "%s/%s" % (request.base_url, task_uuid)

        # Non-expanded gets just the URL; no need tgo sanitize it.
        if not arg_boolean("expanded"):
            return ok_json(task_url, sanitize=False)

        # Expanded gets a redirect to GET+expanded

        params = []
        for arg in [ "detail", "pretty" ]:
            if arg_boolean(arg):
                params.append(arg)

        if params:
            task_url += "?%s" % ("&".join(params))

        return see_other(task_url)

    else:

        return not_allowed()





PART_KEY_FIELD = "__participant_key"

@application.route("/tasks/<uuid>", methods=['GET', 'POST', 'DELETE'])
def tasks_uuid(uuid):

    if not uuid_is_valid(uuid):
        return not_found()

    if request.method == 'GET':

        tasks = __tasks_get_filtered(
            request.base_url,
            where_clause="task.uuid = %s",
            args=[uuid],
            expanded=True,
            detail=arg_boolean("detail"),
            single=True,
            part_key_field=PART_KEY_FIELD
        )

        if not tasks:
            return not_found()

        task = tasks[0]

        log.debug("GOT TASK %s", task)
        participant_key = task.get(PART_KEY_FIELD)
        del task[PART_KEY_FIELD]

        log.debug("LOOKING FOR %s", participant_key)

        return ok_json_sanitize_checked(task, participant_key)

    elif request.method == 'POST':

        data = request.data.decode("ascii")

        log.debug("Posting to %s", uuid)
        log.debug("Data is %s", data)

        # TODO: This is only for participant 1+
        # TODO: This should probably a PUT and not a POST.

        try:
            json_in = pscheduler.json_load(data, max_schema=4)
        except ValueError as ex:
            return bad_request("Invalid JSON: %s" % str(ex))
        log.debug("JSON is %s", json_in)

        try:
            participant = arg_cardinal('participant')
        except ValueError as ex:
            return bad_request("Invalid participant: " + str(ex))
        log.debug("Participant %d", participant)

        # Evaluate the task against the limits and reject the request
        # if it doesn't pass.

        log.debug("Checking limits on task")

        processor, whynot = limitprocessor()
        if processor is None:
            message = "Limit processor is not initialized: %s" % whynot
            log.debug(message)
            return no_can_do(message)

        hints, error_response = request_hints();
        if hints is None:
            log.debug("Can't come up with valid hints for subordinate limits.")
            return error_response

        hints_data = pscheduler.json_dump(hints)

        # Only the lead rewrites tasks; everyone else just applies
        # limits.
        passed, limits_passed, diags, _new_task, priority \
            = processor.process(json_in, hints, rewrite=False)

        if not passed:
            return forbidden("Task forbidden by limits:\n" + diags)
        log.debug("Limits passed")

        # TODO: Pluck UUID from URI
        uuid = url_last_in_path(request.url)

        log.debug("Posting task %s", uuid)

        try:

            try:
                participants = pscheduler.json_load(data,
                                                    max_schema=4)["participants"]
            except Exception as ex:
                return bad_request("Task error: %s" % str(ex))
            cursor = dbcursor_query(
                "SELECT * FROM api_task_post(%s, %s, %s, %s, %s, %s, %s, TRUE, %s)",
                [data, participants, hints_data,
                 pscheduler.json_dump(limits_passed), participant,
                 json_in.get("priority", None),
                 uuid,
                 "\n".join(diags)])

        except Exception as ex:
            return bad_request("Task error: %s" % str(ex))

        if cursor.rowcount == 0:
            return error("Task post failed; poster returned nothing.")
        # TODO: Assert that rowcount is 1
        log.debug("All done: %s", base_url())
        return ok(base_url())

    elif request.method == 'DELETE':

        requester, key = task_requester_key(uuid)
        if requester is None:
            return not_found()

        if not access_write_task(requester, key):
            return forbidden()

        parsed = list(urllib.parse.urlsplit(request.url))
        parsed[1] = "%s"
        template = urllib.parse.urlunsplit(parsed)

        log.debug("Disabling")

        cursor = dbcursor_query(
            "SELECT api_task_disable(%s, %s)", [uuid, template])
        cursor.close()

        return ok()

    else:

        return not_allowed()





@application.route("/tasks/<uuid>/cli", methods=['GET'])
def tasks_uuid_cli(uuid):

    if not uuid_is_valid(uuid):
        return not_found()

    # Get a task, adding server-derived details if a 'detail'
    # argument is present.

    cursor = dbcursor_query(
        """SELECT
               task.json #>> '{test, spec}',
               test.name
           FROM
               task
               JOIN test on test.id = task.test
           WHERE task.uuid = %s""", [uuid])

    if cursor.rowcount == 0:
        return not_found()

    row = cursor.fetchone()
    if row is None:
        return not_found()
    json, test = row

    try:
        returncode, stdout, stderr = pscheduler.plugin_invoke(
            "test", test, "spec-to-cli", stdin=json )
        if returncode != 0:
            return error("Unable to convert test spec: " + stderr)
    except Exception as ex:
        return error("Unable to convert test spec: " + str(ex))

    returned = pscheduler.json_load(stdout)
    returned.insert(0, test)

    return ok(pscheduler.json_dump(returned))
