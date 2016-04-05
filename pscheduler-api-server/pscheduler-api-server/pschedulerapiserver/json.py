#
# JSON-Related Functions
#

import pscheduler

from flask import request

from .args import *
from .response import *
from .url import *

def json_dump(dump):
    return pscheduler.json_dump(dump,
                                pretty=arg_boolean('pretty')
                                )


def json_query_simple(cursor, query, query_args=[], empty_ok=False):
    """Do a SQL query that selects one column and dump those values as
    a JSON array"""

    if request.method != 'GET':
        return not_allowed()

    # TODO: Handle failure
    cursor.execute(query, query_args)
    if cursor.rowcount == 0 and not empty_ok:
        return not_found()
    result = []
    for row in cursor:
        result.append(row[0])
    return json_response(json_dump(result))



def json_query(cursor, query, query_args=[], name = 'name', single = False):
    """Do a SQL query that selects one column containing JSON and dump
    the results, honoring the 'expanded' and 'pretty' arguments.  If
    the 'single' argument is True, the first-returned row will be
    returned as a single item instead of an array."""

    if request.method != 'GET':
        return not_allowed()

    # TODO: Handle failure
    cursor.execute(query, query_args)
    if single and cursor.rowcount == 0:
        return not_found()
    result = []
    for row in cursor:
        this = base_url(None if single else row[0][name])
        row[0]['href'] = this
        result.append( row[0] if single or is_expanded() else this)
    return json_response(json_dump(result[0] if single else result))

