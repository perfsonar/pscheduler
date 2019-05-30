#
# Run-Related Pages
#

import copy
import pscheduler
import time

from pschedulerapiserver import application

from flask import request

from .access import *
from .args import arg_integer
from .dbcursor import dbcursor_query
from .json import *
from .limitproc import *
from .log import log
from .response import *
from .tasks import task_exists
from .util import *


# Proposed times for a task
@application.route("/tasks/<task>/runtimes", methods=['GET'])
def task_uuid_runtimes(task):

    if not uuid_is_valid(task):
        return not_found()

    try:
        range_start = arg_datetime('start')
        range_end   = arg_datetime('end')
    except ValueError:
        return bad_request('Invalid start or end time')
    if not task_exists(task):
        return not_found()

    # TODO: At some point, we will likely have to consider making the
    # proposals fall within the limits, which is going to be complex.

    proposed_priority = arg_integer('priority')

    if proposed_priority is None:
        return json_query_simple(
            """SELECT row_to_json(apt.*)
            FROM  api_proposed_times(%s, %s, %s) apt""",
            [task, range_start, range_end], empty_ok=True)
    else:
        return json_query_simple(
            """SELECT row_to_json(apt.*)
            FROM  api_proposed_times(%s, %s, %s, %s) apt""",
            [task, range_start, range_end, proposed_priority], empty_ok=True)



def __evaluate_limits(
    task,       # Task UUID
    start_time  # When the task should start
    ):

    """Evaluate the limits for a run."""

    log.debug("Applying limits")
    # Let this throw what it may; callers have to catch it.
    cursor = dbcursor_query(
        "SELECT json, duration, hints FROM task where uuid = %s", [task])
    if cursor.rowcount == 0:
        # TODO: This or bad_request when the task isn't there?
        return False, None, not_found()
    task_spec, duration, hints = cursor.fetchone()
    cursor.close()
    log.debug("Task is %s, duration is %s" % (task_spec, duration))

    limit_input = copy.copy(task_spec)
    limit_input['run_schedule'] = {
        'start': pscheduler.datetime_as_iso8601(start_time),
        'duration': pscheduler.timedelta_as_iso8601(duration)
    }

    log.debug("Checking limits against %s" % str(limit_input))

    processor, whynot = limitprocessor()
    if processor is None:
        log.debug("Limit processor is not initialized. %s", whynot)
        return False, None, no_can_do("Limit processor is not initialized: %s" % whynot)

    # Don't pass hints since that would have been covered when the
    # task was submitted and only the scheduler will be submitting
    # runs.
    passed, limits_passed, diags, _new_task, priority \
        = processor.process(limit_input, hints, rewrite=False, prioritize=True)

    log.debug("Passed: %s.  Diags: %s" % (passed, diags))

    return passed, diags, None, priority



# Established runs for a task
@application.route("/tasks/<task>/runs", methods=['GET', 'POST'])
def tasks_uuid_runs(task):

    if not uuid_is_valid(task):
        return not_found()

    if request.method == 'GET':

        query = "SELECT '" + base_url() + """/' || run.uuid
             FROM
                 run
                 JOIN task ON task.id = run.task
             WHERE
                task.uuid = %s"""
        args = [task]

        try:

            start_time = arg_datetime('start')
            if start_time is not None:
                query += " AND lower(times) >= %s"
                args.append(start_time)

            end_time = arg_datetime('end')
            if end_time is not None:
                query += " AND upper(times) <= %s"
                args.append(end_time)

            if arg_boolean('upcoming'):
                query += " AND (times @> normalized_now() OR lower(times) > normalized_now())"
                query += " AND state IN (run_state_pending(), run_state_on_deck(), run_state_running(), run_state_nonstart())"

            query += " ORDER BY times"

            limit = arg_cardinal('limit')
            if limit is not None:
                query += " LIMIT " + str(limit)

            # TODO: This should be exapandable

        except ValueError as ex:

            return bad_request(str(ex))


        return json_query_simple(query, args, empty_ok=True)

    elif request.method == 'POST':

        log.debug("Run POST: %s --> %s", request.url, request.data)

        requester, key = task_requester_key(task)
        if requester is None:
            return not_found()

        if not access_write_task(requester, key):
            return forbidden()


        try:
            data = pscheduler.json_load(request.data, max_schema=1)
            start_time = pscheduler.iso8601_as_datetime(data['start-time'])
        except KeyError:
            return bad_request("Missing start time")
        except ValueError as ex:
            return bad_request("Invalid JSON: %s" % (str(ex)))

        try:
            passed, diags, response, priority \
                = __evaluate_limits(task, start_time)
        except Exception as ex:
            log.exception()
            return error(str(ex))
        if response is not None:
            return response

        try:
            log.debug("Posting run for task %s starting %s, priority %s"
                      % (task, start_time, priority))

            if passed:
                diag_message = None
            else:
                diag_message = "Run forbidden by limits:\n%s" % (diags)

            cursor = dbcursor_query(
                "SELECT * FROM api_run_post(%s, %s, NULL, %s, %s, %s)",
                [task, start_time, diag_message, priority, diags],
                onerow=True)
            succeeded, uuid, conflicts, error_message = cursor.fetchone()
            cursor.close()
            if conflicts:
                return conflict(error_message)
            if error_message:
                return error(error_message)
        except Exception as ex:
            log.exception()
            return error(str(ex))

        url = base_url() + '/' + uuid
        log.debug("New run posted to %s", url)
        return ok_json(url)

    else:

        return not_allowed()



def __runs_first_run(
    task,         # UUID of task
    future=False  # Get first future run instead of first-ever
    ):
    """
    Find the UUID of the first run of the specified task, returning
    None if none exists.
    """

    # Let this throw what it may; callers are responsible for handling
    # exceptions.
    cursor = dbcursor_query("""
                SELECT run.uuid
                FROM
                  task
                  JOIN run ON run.task = task.id
                WHERE
                  task.uuid = %s
                  AND (%s OR lower(run.times) >= normalized_now())
                ORDER BY run.times
                LIMIT 1
                """, [task, not future])

    if cursor.rowcount == 0:
        cursor.close()
        return None
    else:
        value = cursor.fetchone()[0]
        cursor.close()
        return value



@application.route("/tasks/<task>/runs/<run>", methods=['GET', 'PUT', 'DELETE'])
def tasks_uuid_runs_run(task, run):

    if not uuid_is_valid(task):
        return not_found()

    if (
            (request.method in ['PUT', 'DELETE']
             and not uuid_is_valid(run))
            or
            (run not in ['first', 'next']
             and not uuid_is_valid(run))
    ):
        return not_found()


    if request.method == 'GET':

        # Wait for there to be a local result
        wait_local = arg_boolean('wait-local')

        # Wait for there to be a merged result
        wait_merged = arg_boolean('wait-merged')

        if wait_local and wait_merged:
            return bad_request("Cannot wait on local and merged results")

        # Figure out how long to wait in seconds.  Zero means don't
        # wait.

        wait_time = arg_integer('wait')
        if wait_time is None:
            wait_time = 30
        if wait_time < 0:
            return bad_request("Wait time must be >= 0")

        # If asked for 'first', dig up the first run and use its UUID.

        if run in ['next', 'first']:
            future = run == 'next'
            wait_interval = 0.5
            tries = int(wait_time / wait_interval) if wait_time > 0 \
                    else 1
            while tries > 0:
                run = __runs_first_run(task, future)
                if run is not None:
                    break
                if wait_time > 0:
                    time.sleep(1.0)
                tries -= 1

            if run is None:
                return not_found()


        # Obey the wait time with tries at 0.5s intervals
        tries = wait_time * 2 if (wait_local or wait_merged) else 1
        result = {}

        while tries:

            try:
                cursor = dbcursor_query(
                    """
                    SELECT
                        run_json(run.id),
                        run_state.finished
                    FROM
                        task
                        JOIN run ON task.id = run.task
                        JOIN run_state ON run_state.id = run.state
                    WHERE 
                        task.uuid = %s
                        AND run.uuid = %s
                    """, [task, run])
            except Exception as ex:
                log.exception()
                return error(str(ex))

            if cursor.rowcount == 0:
                cursor.close()
                return not_found()

            result, finished = cursor.fetchone()
            cursor.close()

            if not (wait_local or wait_merged):
                break
            else:
                if (wait_local and result['result'] is None) \
                   or (wait_merged \
                       and ( (result['result-full'] is None) or (not finished) ) ):
                    log.debug("Waiting (%d left) for merged: %s %s", tries, result['result-full'], finished)
                    time.sleep(0.5)
                    tries -= 1
                else:
                    log.debug("Got the requested result.")
                    break


        # Even if we timed out waiting, return the last result we saw
        # and let the client sort it out.


        # This strips any query parameters and replaces the last item
        # with the run, which might be needed if the 'first' option
        # was used.

        href_path_parts = urlparse.urlparse(request.url).path.split('/')
        href_path_parts[-1] = run
        href_path = '/'.join(href_path_parts)
        href = urlparse.urljoin( request.url, href_path )

        result['href'] = href
        result['task-href'] = root_url('tasks/' + task)
        result['result-href'] = href + '/result'

        # For a NULL first participant, fill in the netloc.

        try:
            if result['participants'][0] is None:
                result['participants'][0] = server_netloc()
        except KeyError:
            pass  # Not there?  Don't care.


        return json_response(result)

    elif request.method == 'PUT':

        log.debug("Run PUT %s", request.url)

        requester, key = task_requester_key(task)

        if requester is None:
            return not_found()

        if not access_write_task(requester, key):
            return forbidden()

        # Get the JSON from the body
        try:
            run_data = pscheduler.json_load(request.data, max_schema=1)
        except ValueError:
            log.exception()
            log.debug("Run data was %s", request.data)
            return bad_request("Invalid or missing run data")

        # If the run doesn't exist, take the whole thing as if it were
        # a POST.

        cursor = dbcursor_query(
            "SELECT EXISTS (SELECT * FROM run WHERE uuid = %s)",
            [run], onerow=True)

        fetched = cursor.fetchone()[0]
        cursor.close()
        if not fetched:

            log.debug("Record does not exist; full PUT.")

            try:
                start_time = \
                    pscheduler.iso8601_as_datetime(run_data['start-time'])
            except KeyError:
                return bad_request("Missing start time")
            except ValueError:
                return bad_request("Invalid start time")


            try:

                passed, diags, response, priority \
                    = __evaluate_limits(task, start_time)
                if response is not None:
                    return response

                if passed:
                    diag_message = None
                else:
                    diag_message = "Run forbidden by limits:\n%s" % (diags)

                cursor = dbcursor_query(
                    "SELECT * FROM api_run_post(%s, %s, %s, %s, %s, %s)",
                    [task, start_time, run, diag_message, priority, diags],
                    onerow=True)
                succeeded, uuid, conflicts, error_message = cursor.fetchone()
                cursor.close()
                if conflicts:
                    return conflict(error_message)
                if not succeeded:
                    return error(error_message)
                log.debug("Full put of %s, got back %s", run, uuid)
            except Exception as ex:
                log.exception()
                return error(str(ex))

            return ok()

        # For anything else, only one thing can be udated at a time,
        # and even that is a select subset.

        log.debug("Record exists; partial PUT.")

        if 'part-data-full' in run_data:

            log.debug("Updating part-data-full from %s", run_data)

            try:
                part_data_full = \
                    pscheduler.json_dump(run_data['part-data-full'])
            except KeyError:
                return bad_request("Missing part-data-full")
            except ValueError:
                return bad_request("Invalid part-data-full")

            log.debug("Full data is: %s", part_data_full)

            cursor = dbcursor_query("""
                          UPDATE
                              run
                          SET
                              part_data_full = %s
                          WHERE
                              uuid = %s
                              AND EXISTS (SELECT * FROM task WHERE UUID = %s)
                          """,
                       [ part_data_full, run, task])

            rowcount = cursor.rowcount
            cursor.close()
            if rowcount != 1:
                return not_found()

            log.debug("Full data updated")

            return ok()

        elif 'result-full' in run_data:

            log.debug("Updating result-full from %s", run_data)

            try:
                result_full = \
                    pscheduler.json_dump(run_data['result-full'])
            except KeyError:
                return bad_request("Missing result-full")
            except ValueError:
                return bad_request("Invalid result-full")

            try:
                succeeded = bool(run_data['succeeded'])
            except KeyError:
                return bad_request("Missing success value")
            except ValueError:
                return bad_request("Invalid success value")

            log.debug("Updating result-full: JSON %s", result_full)
            log.debug("Updating result-full: Run  %s", run)
            log.debug("Updating result-full: Task %s", task)
            cursor = dbcursor_query("""
                          UPDATE
                              run
                          SET
                              result_full = %s,
                              state = CASE %s
                                  WHEN TRUE THEN run_state_finished()
                                  ELSE run_state_failed()
                                  END
                          WHERE
                              uuid = %s
                              AND EXISTS (SELECT * FROM task WHERE UUID = %s)
                          """,
                           [ result_full, succeeded, run, task ])

            rowcount = cursor.rowcount
            cursor.close()
            if rowcount != 1:
                return not_found()

            return ok()



    elif request.method == 'DELETE':

        # TODO: If this is the lead, the run's counterparts on the
        # other participating nodes need to be removed as well.

        requester, key = task_requester_key(task)
        if requester is None:
            return not_found()

        if not access_write_task(requester, key):
            return forbidden()


        cursor = dbcursor_query("""
        DELETE FROM run
        WHERE
            task in (SELECT id FROM task WHERE uuid = %s)
            AND uuid = %s 
        """, [task, run])

        rowcount = cursor.rowcount
        cursor.close()

        return ok() if rowcount == 1 else not_found()

    else:

        return not_allowed()





#
# Merged results, optionally formatted.
#

@application.route("/tasks/<task>/runs/<run>/result", methods=['GET'])
def tasks_uuid_runs_run_result(task, run):

    if not uuid_is_valid(task) or not uuid_is_valid(run):
        return not_found()

    wait = arg_boolean('wait')

    format = request.args.get('format')

    if format is None:
        format = 'application/json'

    if format not in [ 'application/json', 'text/html', 'text/plain' ]:
        return bad_request("Unsupported format " + format)

    # If asked for 'first', dig up the first run and use its UUID.
    # This is more for debug convenience than anything else.
    if run == 'first':
        run = __runs_first_run(task)
        if run is None:
            return not_found()



    #
    # Camp on the run for a result
    #

    # 40 tries at 0.25s intervals == 10 sec.
    tries = 40 if wait else 1

    while tries:

        cursor = dbcursor_query("""
            SELECT
                test.name,
                run.result_merged,
                task.json #> '{test, spec}'
            FROM
                run
                JOIN task ON task.id = run.task
                JOIN test ON test.id = task.test
            WHERE
                task.uuid = %s
                AND run.uuid = %s
            """, [task, run])

        if cursor.rowcount == 0:
            cursor.close()
            return not_found()

        # TODO: Make sure we got back one row with two columns.
        row = cursor.fetchone()
        cursor.close()

        if not wait and row[1] is None:
            time.sleep(0.25)
            tries -= 1
        else:
            break

    if tries == 0:
        return not_found()


    test_type, merged_result, test_spec = row


    # JSON requires no formatting.
    if format == 'application/json':
        return ok_json(merged_result)

    if not merged_result['succeeded']:
        if format == 'text/plain':
            return ok("Run failed.", mimetype=format)
        elif format == 'text/html':
            return ok("<p>Run failed.</p>", mimetype=format)
        return bad_request("Unsupported format " + format)

    formatter_input = {
        "spec": test_spec,
        "result": merged_result
        }

    returncode, stdout, stderr = pscheduler.run_program(
        [ "pscheduler", "internal", "invoke", "test", test_type,
          "result-format", format ],
        stdin = pscheduler.json_dump(formatter_input)
        )

    if returncode != 0:
        return error("Failed to format result: " + stderr)

    return ok(stdout.rstrip(), mimetype=format)
