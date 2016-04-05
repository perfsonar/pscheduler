#
# Tool-Related Pages
#

import pscheduler

from pschedulerapiserver import application

from flask import request

from .dbcursor import dbcursor
from .json import *
from .response import *

#
# Tests
#

# All tests
@application.route("/tests", methods=['GET'])
def tests():
    return json_query(dbcursor(), "SELECT json FROM test", [])


# Test <name>
@application.route("/tests/<name>", methods=['GET'])
def tests_name(name):
    return json_query(dbcursor(), "SELECT json FROM test WHERE name = %s",
                      [name], single=True)


# Tools that can carry out test <name>
@application.route("/tests/<name>/tools", methods=['GET'])
def tests_name_tools(name):
    expanded = is_expanded()
    # TODO: Handle failure
    dbcursor().execute("""
        SELECT
            tool.name,
            tool.json
        FROM
            tool
            JOIN tool_test ON tool_test.tool = tool.id
            JOIN test ON test.id = tool_test.test
        """)
    result = []
    for row in dbcursor():
        url = root_url('tools/' + row[0])
        if not expanded:
            result.append(url)
            continue
        row[1]['href'] = url
        result.append(row[1])
    return json_response(json_dump(result))



# Participants in a test spec
@application.route("/tests/<name>/lead", methods=['GET'])
def tests_name_lead(name):

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

    part_list = pscheduler.json_load(stdout)
    lead = part_list[0]

    if lead is None:
        lead = pscheduler.api_this_host()

    return json_response('"%s"' % lead)
