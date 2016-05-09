#
# Run-Related Pages
#

import pscheduler
import time

from pschedulerapiserver import application

from flask import request

from .dbcursor import dbcursor
from .json import *
from .log import log
from .response import *
from .tasks import task_exists


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

            query += " ORDER BY times"

            limit = arg_cardinal('limit')
            if limit is not None:
                query += " LIMIT " + str(limit)

            # TODO: This should be exapandable

        except ValueError as ex:

            return bad_request(str(ex))


        return json_query_simple(dbcursor(), query, args, empty_ok=True)

    elif request.method == 'POST':

        log.debug("Run POST: %s --> %s", request.url, request.data)

        try:
            data = pscheduler.json_load(request.data)
            start_time = pscheduler.iso8601_as_datetime(data['start-time'])
        except KeyError:
            return bad_request("Missing start time")
        except ValueError:
            return bad_request("Invalid JSON:" + request.data)

        try:
            dbcursor().execute("SELECT api_run_post(%s, %s)", [task, start_time])
            uuid = dbcursor().fetchone()[0]
        except:
            log.exception()
            return error("Database query failed")

        # TODO: Assert that rowcount is 1
        url = base_url() + '/' + uuid
        log.debug("New run posted to %s", url)
        return ok_json(url)

    else:

        return not_allowed()



def __runs_first_run(
    task   # UUID of task
    ):
    """
    Find the UUID of the first run of the specified task, returning
    None if none exists.
    """
    dbcursor().execute("""
                SELECT run.uuid
                FROM
                  task
                  JOIN run ON run.task = task.id
                WHERE
                  task.uuid = %s
                ORDER BY run.times
                LIMIT 1
                """, [task])
    # TODO: Handle failure.

    return None if dbcursor().rowcount == 0 \
        else dbcursor().fetchone()[0]



@application.route("/tasks/<task>/runs/<run>", methods=['GET', 'PUT', 'DELETE'])
def tasks_uuid_runs_run(task, run):

    if task is None:
        return bad_request("Missing or invalid task")

    if run is None:
        return bad_request("Missing or invalid run")

    if request.method == 'GET':

        wait_local = arg_boolean('wait-local')
        wait_merged = arg_boolean('wait-merged')

        if wait_local and wait_merged:
            return error("Cannot wait on local and merged results")

        # If asked for 'first', dig up the first run and use its UUID.

        if run == 'first':
            # 40 tries at 0.25s intervals == 10 sec.
            tries = 40 if (wait_local or wait_merged) else 1
            while tries:
                run = __runs_first_run(task)
                if run is not None:
                    break
                time.sleep(0.25)
                tries -= 1

            if run is None:
                return not_found()



        # 40 tries at 0.25s intervals == 10 sec.
        tries = 40 if (wait_local or wait_merged) else 1

        while tries:

            dbcursor().execute("""
                SELECT
                    lower(run.times),
                    upper(run.times),
                    upper(run.times) - lower(run.times),
                    task.participant,
                    task.nparticipants,
                    task.participants,
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

            row = dbcursor().fetchone()

            if not (wait_local or wait_merged):
                break
            else:
                if (wait_local and row[7] is None) \
                        or (wait_merged and row[9] is None):
                    time.sleep(0.25)
                    tries -= 1
                else:
                    break

        # Return a result Whether or not we timed out and let the
        # client sort it out.

        result = {}

        # This strips any query parameters and replaces the last item
        # with the run, which might be needed if the 'first' option
        # was used.

        href_path_parts = urlparse.urlparse(request.url).path.split('/')
        href_path_parts[-1] = run
        href_path = '/'.join(href_path_parts)
        href = urlparse.urljoin( request.url, href_path )

        result['href'] = href
        result['start-time'] = pscheduler.datetime_as_iso8601(row[0])
        result['end-time'] = pscheduler.datetime_as_iso8601(row[1])
        result['duration'] = pscheduler.timedelta_as_iso8601(row[2])
        result['participant'] = row[3]
        result['participants'] = [
            participant if participant is not None
            else pscheduler.api_this_host()
            for participant in row[5]
            ]
        result['participant-data'] = row[6]
        result['participant-data-full'] = row[7]
        result['result'] = row[8]
        result['result-full'] = row[9]
        result['result-merged'] = row[10]
        result['state'] = row[11]
        result['state-display'] = row[12]
        result['task-href'] = root_url('tasks/' + task)
        result['result-href'] = href + '/result'

        return json_response(result)

    elif request.method == 'PUT':

        log.debug("Run PUT %s", request.url)

        # This expects one argument called 'run'
        try:
            log.debug("ARG run %s", request.args.get('run'))
            run_data = arg_json('run')
        except ValueError:
            log.exception()
            log.debug("Run data was %s", request.args.get('run'))
            return error("Invalid or missing run data")

        # If the run doesn't exist, take the whole thing as if it were
        # a POST.

        dbcursor().execute("SELECT EXISTS (SELECT * FROM run WHERE uuid = %s)", [run])
        # TODO: Handle Failure
        # TODO: Assert that rowcount is 1
        if not dbcursor().fetchone()[0]:

            log.debug("Record does not exist; full PUT.")

            try:
                start_time = \
                    pscheduler.iso8601_as_datetime(run_data['start-time'])
            except KeyError:
                return bad_request("Missing start time")
            except ValueError:
                return bad_request("Invalid start time")

            try:
                dbcursor().execute("SELECT api_run_post(%s, %s, %s)", [task, start_time, run])
                # TODO: Assert that rowcount is 1
                log.debug("Full put of %s, got back %s", run, dbcursor().fetchone()[0])
            except:
                log.exception()
                return error("Database query failed")

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

            dbcursor().execute("""UPDATE
                                  run
                              SET
                                  part_data_full = %s
                              WHERE
                                  uuid = %s
                                  AND EXISTS (SELECT * FROM task WHERE UUID = %s)
                              """,
                           [ part_data_full, run, task])
            if dbcursor().rowcount != 1:
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

            log.debug("Updating result-full: %s", result_full)


            dbcursor().execute("""UPDATE
                                  run
                              SET
                                  result_full = %s
                              WHERE
                                  uuid = %s
                                  AND EXISTS (SELECT * FROM task WHERE UUID = %s)
                              """,
                           [ result_full, run, task])
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





#
# Merged results, optionally formatted.
#

@application.route("/tasks/<task>/runs/<run>/result", methods=['GET'])
def tasks_uuid_runs_run_result(task, run):

    if task is None:
        return bad_request("Missing or invalid task")

    if run is None:
        return bad_request("Missing or invalid run")

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

            dbcursor().execute("""
                SELECT
                    test.name,
                    run.result_merged
                FROM
                    run
                    JOIN task ON task.id = run.task
                    JOIN test ON test.id = task.test
                WHERE
                    task.uuid = %s
                    AND run.uuid = %s
                """, [task, run])

            if dbcursor().rowcount == 0:
                return not_found()

            # TODO: Make sure we got back one row with two columns.
            row = dbcursor().fetchone()

            if not wait and row[1] is None:
                time.sleep(0.25)
                tries -= 1
            else:
                break

    if tries == 0:
        return not_found()


    test_type, merged_result = row


    # JSON requires no formatting.
    if format == 'application/json':

        return ok_json(merged_result)


    returncode, stdout, stderr = pscheduler.run_program(
        [ "pscheduler", "internal", "invoke", "test", test_type,
          "result-format", format ],
        stdin = pscheduler.json_dump(merged_result)
        )

    if returncode != 0:
        return error("Failed to format result: " + stderr)

    return ok(stdout.rstrip(), mimetype=format)
