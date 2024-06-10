#
# Tool-Related Pages
#

import pscheduler

from pschedulerapiserver import application

from flask import request

from .dbcursor import dbcursor_query
from .json import *
from .log import log
from .response import *

#
# Tools
#

@application.route("/tools", methods=['GET'])
def tools():
    # Get only the tools that can run this test.
    test_filter = request.args.get('test', None)

    if test_filter is None:
        return json_query("SELECT json FROM tool WHERE available ORDER BY NAME")

    log.debug("Looking for tools against filter %s", test_filter)
    cursor = dbcursor_query("SELECT * FROM api_tools_for_test(%s)",
                            [test_filter],
                            onerow=False)

    if requested_api() < 6:
        # API 1-5: Return a lot of the tool enumerations that
        # accepted.
        result = [ row[1] for row in cursor if row[0]['can-run']]
    else:
        # API 6+: Return all tools that were asked and their responses
        result = [ { "can-run": row[0], "tool": row[1] } for row in cursor ]

    # Sanitized, even though there should be nothing special in these.
    return ok_json( result )


@application.route("/tools/<name>", methods=['GET'])
def tools_name(name):
    return json_query("SELECT json FROM tool"
                      " WHERE available AND name = %s",
                      [name], single=True)
