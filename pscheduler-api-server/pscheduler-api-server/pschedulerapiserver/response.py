#
# HTTP Response Functions
#

import pscheduler
import requests

from flask import Response

# Responses

def json_response(data):
    if type(data) in [ dict, list ]:
        return Response(pscheduler.json_dump(data),
                        mimetype='application/json')
    else:
        return Response(data, mimetype='application/json')

def ok(message="OK"):
    return Response(message, status=200)

def ok_json(data=''):
    # TODO: This used to be...
    # return json_response(json_dump(data)), 200
    # ...which Python can't seem to see.
    if type(data) in [ dict, list ]:
        return Response(pscheduler.json_dump(data),
                        mimetype='application/json')
    else:
        return Response(data, mimetype='application/json')


def bad_request(message="Bad request"):
    return Response(message, status=400)

def not_found():
    return Response("Resource not found", status=404)

def not_allowed():
    return Response("%s not allowed on this resource\n" % request.method,
                    status=405)

def error(message=None):
    if message is None:
        message = "Unknown internal error"
    else:
        message = "Internal error: " + message
    return Response(message, 500)

def not_implemented():
    return Response("Not implemented yet", 501)
