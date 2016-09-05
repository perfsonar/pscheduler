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
    return pscheduler.json_dump(dump,
                                pretty=arg_boolean('pretty')
                                )


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

def forbidden(text="Not allowed."):
    log.debug("Response 403: %s", message)
    return Response(text, status=403)

def not_found():
    log.debug("Response 404: %s", message)
    return Response("Resource not found\n", status=404)

def not_allowed(text=None):
    log.debug("Response 405: Not allowed")
    return Response("%s not allowed on this resource\n" % request.method, status=405)

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

def not_implemented():
    log.debug("Response 501: Not implemented")
    return Response("Not implemented yet\n", 501)
