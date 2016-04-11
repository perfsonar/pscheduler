#
# Logger Handle
#

import pscheduler
import sys

from pschedulerapiserver import application

from flask import request

from .args import *
from .response import *

log = pscheduler.Log(name='pscheduler-api',
                     signals=False)

@application.route("/debug", methods=['PUT'])
def debug():

    if request.method == 'PUT':

        try:
            new_state = arg_boolean('state')
        except ValueError:
            return error("Invalid state")

        # TODO: Allow only from localhost
        if not request.remote_addr in ['127.0.0.1', '::1']:
            return forbidden()

        log.set_debug(new_state)
        return ok()
