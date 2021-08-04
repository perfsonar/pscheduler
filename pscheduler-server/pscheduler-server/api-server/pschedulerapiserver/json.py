#
# JSON-Related Functions
#

import pscheduler

from flask import request

from .args import *
from .dbcursor import dbcursor_query
from .response import *
from .util import *

def json_dump(dump):
    return pscheduler.json_dump(dump,
                                pretty=arg_boolean('pretty')
                                )


def json_query_simple(query, query_args=[], empty_ok=False, key=None):
    """Do a SQL query that selects one column and dump those values as
    a JSON array"""

    if request.method != 'GET':
        return not_allowed()

    cursor = dbcursor_query(query, query_args)

    if cursor.rowcount == 0:
        cursor.close()
        if empty_ok:
            # This is safe to return unsanitized
            return ok_json([], sanitize=False)
        else:
            return not_found()

    result = []
    for row in cursor:
        result.append(row[0])
    cursor.close()
    return ok_json_sanitize_checked(result, key)



def json_query(query, query_args=[], name='name', single=False, key=None):
    """Do a SQL query that selects one column containing JSON and dump
    the results, honoring the 'expanded' and 'pretty' arguments.  If
    the 'single' argument is True, the first-returned row will be
    returned as a single item instead of an array."""

    if request.method != 'GET':
        return not_allowed()

    cursor = dbcursor_query(query, query_args)

    if single and cursor.rowcount == 0:
        cursor.close()
        return not_found()
    result = []
    for row in cursor:
        this = base_url(None if single else row[0][name])
        row[0]['href'] = this
        result.append( row[0] if single or is_expanded() else this)
    cursor.close()
    return ok_json_sanitize_checked((result[0] if single else result), key)
