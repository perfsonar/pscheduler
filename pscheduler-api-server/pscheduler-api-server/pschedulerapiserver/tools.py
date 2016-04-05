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
# Tools
#

@application.route("/tools", methods=['GET'])
def tools():
    # Get only the tools that can run this test.
    test_filter = request.args.get('test', None)
    if test_filter is None:
        return json_query(dbcursor(), "SELECT json FROM tool", [])
    else:
        dbcursor().execute("SELECT api_tools_for_test(%s)", [test_filter])
        # TODO: Assert that there's one row.
        return ok_json( dbcursor().fetchone()[0] )


@application.route("/tools/<name>", methods=['GET'])
def tools_name(name):
    return json_query(dbcursor(), "SELECT json FROM tool WHERE name = %s", [name], single=True)

