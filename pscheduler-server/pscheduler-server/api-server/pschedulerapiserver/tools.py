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
    else:
        log.debug("Looking for tools against filter %s", test_filter)
        cursor = dbcursor_query("SELECT api_tools_for_test(%s)",
                                [test_filter],
                                onerow=True)
        return ok_json( cursor.fetchone()[0] )


@application.route("/tools/<name>", methods=['GET'])
def tools_name(name):
    return json_query("SELECT json FROM tool"
                      " WHERE available AND name = %s",
                      [name], single=True)
