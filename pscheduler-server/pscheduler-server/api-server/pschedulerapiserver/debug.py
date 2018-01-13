#
# Debug Switch
#

# Because there's no easy way to share state among Apache processes,
# this module uses a temporary file as a global signal debug is in
# effect.  Storing it in the database would have been hairy because
# the database code uses the logging facilities.

import os
import pscheduler
import sys
import time

from pschedulerapiserver import application

from flask import request
from flask import Response

from .args import *



module = sys.modules[__name__]

module.DEBUG_FILE = "%s/pscheduler-api-debug" \
                    % (os.environ.get("TMPDIR", "/tmp"))
module.CHECK_INTERVAL = 5
module.state = False
module.last_check = 0

def debug_state():

    # If it's been awhile since we last checked the debug state,
    # get an update.
    now = time.time()
    if now - module.last_check > module.CHECK_INTERVAL:
        module.state = os.path.isfile(module.DEBUG_FILE)
        module.last_check = now

    return module.state


@application.route("/debug", methods=['PUT'])
def debug():

    if request.method == 'PUT':

        # Allow only from localhost
        if not request.remote_addr in ['127.0.0.1', '::1']:
            return Response("Forbidden", status=403)

        try:
            new_state = arg_boolean('state')
        except ValueError:
            return Response("Invalid state", status=400)

        if os.path.isfile(module.DEBUG_FILE):
            try:
                os.remove(module.DEBUG_FILE)
            except OSError as ex:
                return Response("Unable to remove debug file: %s" % (ex),
                                status=500)

        if new_state:
            try:
                with open(module.DEBUG_FILE, 'w'):
                    pass
                os.chmod(module.DEBUG_FILE, 000)
            except OSError as ex:
                return Response("Unable to create debug file: %s" % (ex),
                                status=500)


        # Spare a refresh.
        module.state = new_state
        module.last_check = time.time()

        return Response("OK", status=200)
