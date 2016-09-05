#
# HTTP Response Functions
#

import pscheduler
import requests

from flask import Response
from flask import request

from .args import arg_boolean


# TODO: Duplicative, but easier than the cross-module imports. :-@
def response_json_dump(dump):
    return pscheduler.json_dump(dump,
                                pretty=arg_boolean('pretty')
                                )


# Responses

def json_response(data):
    return Response(response_json_dump(data) + '\n',
                    mimetype='application/json')

def ok(message="OK", mimetype=None):
    return Response(message + '\n',
                    status=200,
                    mimetype=mimetype)

def ok_json(data=None):
    return Response(response_json_dump(data) + '\n',
                    mimetype='application/json')

def bad_request(message="Bad request"):
    return Response(message + '\n', status=400)

def forbidden(text="Not allowed."):
    return Response(text, status=403)

def not_found():
    return Response("Resource not found\n", status=404)

def not_allowed(text=None):
    return Response("%s not allowed on this resource\n" % request.method, status=405)

def no_can_do(message=None):
    return Response("Unable to complete request" \
                        + ((": " + message ) \
                        if message is not None \
                        else ".") \
                        + '\n',
                    status=422)

def error(message=None):
    if message is None:
        message = "Unknown internal error"
    return Response(message + '\n', 500)

def not_implemented():
    return Response("Not implemented yet\n", 501)
