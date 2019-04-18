#
# HTTP Response Functions
#

import pscheduler

from werkzeug.datastructures import Headers
from flask import Response
from flask import request

from .args import arg_boolean
from .log import log


# TODO: Duplicative, but easier than the cross-module imports. :-@
def response_json_dump(dump, sanitize=True):
    if sanitize:
        sanitized = pscheduler.json_decomment(dump, prefix="_", null=True)
        return pscheduler.json_dump(sanitized, pretty=arg_boolean('pretty'))
    else:
        return pscheduler.json_dump(dump, pretty=arg_boolean('pretty'))

# Responses

def json_response(data):
    text = response_json_dump(data)
    log.debug("Response 200+JSON: %s", text)
    return Response(text + '\n',
                    mimetype='application/json')

def ok(message="OK", mimetype=None):
    log.debug("Response 200: %s", message)
    return Response(message + '\n',
                    status=200,
                    mimetype=mimetype)

def ok_json(data=None, sanitize=True):
    text = response_json_dump(data, sanitize=sanitize)
    log.debug("Response 200+JSON: %s", text)
    return Response(text + '\n',
                    mimetype='application/json')

def bad_request(message="Bad request"):
    log.debug("Response 400: %s", message)
    return Response(message + '\n', status=400, mimetype="text/plain")

def forbidden(message="Forbidden."):
    log.debug("Response 403: %s", message)
    log.info("Forbade %s %s %s: %s", request.remote_addr, request.method, request.base_url, message)
    return Response(message + "\n", status=403, mimetype="text/plain")

def not_found(message="Resource Not found.", mimetype="text/plain"):
    log.debug("Response 404: %s", message)
    return Response(message + "\n", status=404, mimetype="text/plain")

def not_allowed():
    log.debug("Response 405: %s not allowed.", request.method)
    log.info("Disallowed %s %s %s", request.remote_addr, request.method, request.base_url)
    return Response("%s not allowed on this resource\n" % (request.method),
                    status=405, mimetype="text/plain")

def conflict(message="Request would create a conflict."):
    log.debug("Response 409: Conflict")
    return Response(message + '\n', status=409, mimetype="text/plain")

def no_can_do(message=None):
    log.debug("Response 422: %s", message)
    return Response("Unable to complete request" \
                        + ((": " + message ) \
                        if message is not None \
                        else ".") \
                        + '\n',
                    status=422, mimetype="text/plain")

def error(message="Unknown internal error"):
    log.debug("Response 500: %s", message)
    log.error("Internal error %s %s %s: %s", request.remote_addr, request.method, request.base_url, message)
    return Response(message + '\n', status=500, mimetype="text/plain")

def not_implemented(message="Not implemented."):
    log.debug("Response 501: %s", message)
    log.warning("Not implemented %s %s %s: %s", request.remote_addr, request.method, request.base_url, message)
    return Response(message + "\n", status=501, mimetype="text/plain")

def see_other(url):
    log.debug("Response 303: Redirect to %s", url)
    return Response(url + "\n", status=303,
                    headers=Headers([("Location", url)]))
