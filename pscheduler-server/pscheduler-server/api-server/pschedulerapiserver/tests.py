#
# Test-Related Pages
#

import pscheduler

from pschedulerapiserver import application

from flask import request

from .dbcursor import dbcursor_query
from .json import *
from .response import *

#
# Tests
#

# All tests
@application.route("/tests", methods=['GET'])
def tests():
    return json_query("SELECT json FROM test ORDER BY name", [])


# Test <name>
@application.route("/tests/<name>", methods=['GET'])
def tests_name(name):
    return json_query("SELECT json FROM test WHERE name = %s",
                      [name], single=True)


# Derive a spec from command line arguments in 'arg'
@application.route("/tests/<name>/spec", methods=['GET'])
def tests_name_spec(name):

    try:
        cursor = dbcursor_query("SELECT EXISTS (SELECT * FROM test WHERE NAME = %s)",
                                [ name ])
    except Exception as ex:
        return error(str(ex))

    exists = cursor.fetchone()[0]
    cursor.close()
    if not exists:
        return not_found()

    try:
        args = arg_json('args')
    except ValueError:
        return error("Invalid JSON passed to 'args'")
    
    status, stdout, stderr = pscheduler.run_program(
        [ 'pscheduler', 'internal', 'invoke', 'test', name, 'cli-to-spec' ],
        stdin = pscheduler.json_dump(args),
        timeout=5
        )

    if status != 0:
        return bad_request(stderr)

    # The extra parse here makes 'pretty' work.
    returned_json = pscheduler.json_load(stdout)
    return ok_json(returned_json)




# Tools that can carry out test <name>
@application.route("/tests/<name>/tools", methods=['GET'])
def tests_name_tools(name):

    # TODO: Should probably 404 if the test doesn't exist.
    # TODO: Is this used anywhere?

    expanded = is_expanded()
    try:
        cursor = dbcursor_query("""
        SELECT
            tool.name,
            tool.json
        FROM
            tool
            JOIN tool_test ON tool_test.tool = tool.id
            JOIN test ON test.id = tool_test.test
        WHERE
            test.name = %s
        """, [name])
    except Exception as ex:
        return error(str(ex))

    result = []
    for row in cursor:
        url = root_url('tools/' + row[0])
        if not expanded:
            result.append(url)
            continue
        row[1]['href'] = url
        result.append(row[1])
    cursor.close()
    return json_response(result)



# Participants in a test spec
@application.route("/tests/<name>/participants", methods=['GET'])
def tests_name_participants(name):

    spec = request.args.get('spec')
    if spec is None:
        return bad_request("No test spec provided")

    try:
        returncode, stdout, stderr = pscheduler.run_program(
            [ "pscheduler", "internal", "invoke", "test", name,
              "participants"],
            stdin = spec
            )
    except KeyError:
        return bad_request("Invalid spec")
    except Exception as ex:
        return bad_request(ex)

    if returncode != 0:
        return bad_request(stderr)

    # If this fails because of bad JSON, an exception will be thrown,
    # caught and logged.
    return json_response(pscheduler.json_load(stdout))
