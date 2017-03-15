#
# Logger Handle
#

import pscheduler
import sys

from pschedulerapiserver import application

from flask import Response
from flask import request

from .args import *

# This is thread-safe, so no need to do anything special with it.
log = pscheduler.Log(name='pscheduler-api',
                     signals=False)


# Don't use anything out of .response in this because it uses the
# logger.

@application.route("/debug", methods=['PUT'])
def debug():

    if request.method == 'PUT':

        try:
            new_state = arg_boolean('state')
        except ValueError:
            return Response("Invalid state", status=500)

        # Allow only from localhost
        if not request.remote_addr in ['127.0.0.1', '::1']:
            return Response("Not allowed", status=403)

        log.set_debug(new_state)
        return Response(status=200)
