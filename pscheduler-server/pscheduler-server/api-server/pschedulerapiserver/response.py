#
# HTTP Response Functions
#

import pscheduler
import requests

from flask import Response
from flask import request

from .args import arg_boolean
from .log import log


# TODO: Duplicative, but easier than the cross-module imports. :-@
def response_json_dump(dump):
    sanitized = pscheduler.json_decomment(dump, prefix="_", null=True)
    return pscheduler.json_dump(sanitized, pretty=arg_boolean('pretty'))

# Responses

def json_response(data):
    text = response_json_dump(data)
    log.debug("Response 200+JSON: %s", text)
    return Response(text + '\n',
                    mimetype='application/json')

def ok(message="OK", mimetype=None):
    log.debug("Response 200")
    return Response(message + '\n',
                    status=200,
                    mimetype=mimetype)

def ok_json(data=None):
    text = response_json_dump(data)
    log.debug("Response 200+JSON: %s", text)
    return Response(text + '\n',
                    mimetype='application/json')

def bad_request(message="Bad request"):
    log.debug("Response 400: %s", message)
    return Response(message + '\n', status=400)

def forbidden(message="Not allowed."):
    log.debug("Response 403: %s", message)
    return Response(message, status=403)

def not_found(message="Resource Not found."):
    log.debug("Response 404: %s", message)
    return Response(message + "\n", status=404)

def not_allowed():
    log.debug("Response 405: %s not allowed.", request.method)
    return Response("%s not allowed on this resource\n" % request.method, status=405)

def conflict(message="Request would create a conflict."):
    log.debug("Response 409: Conflict")
    return Response(message + '\n', status=409)

def no_can_do(message=None):
    log.debug("Response 422: %s", message)
    return Response("Unable to complete request" \
                        + ((": " + message ) \
                        if message is not None \
                        else ".") \
                        + '\n',
                    status=422)

def error(message=None):
    log.debug("Response 500: %s", message)
    if message is None:
        message = "Unknown internal error"
    return Response(message + '\n', 500)

def not_implemented(message="Not implemented.\n"):
    log.debug("Response 501: %s", message)
    return Response(message, 501)
