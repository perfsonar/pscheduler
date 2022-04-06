#
# Limit-Related Pages
#

import pscheduler

from pschedulerapiserver import application

from flask import request

from .args import *
from .limitproc import *
from .response import *
from .util import *

@application.route("/limits", methods=['GET'])
def limits():

    try:
        proposal = arg_json('proposal')
    except ValueError as ex:
        return bad_request(str(ex))

    if proposal is None:
        return bad_request("No proposal provided")

    (processor, whynot) = limitprocessor()
    if processor is None:
        return no_can_do("Limit processor is not initialized: {0}".format(whynot))

    hints, error_response = request_hints();
    if hints is None:
        return error_response

    passed, diags, _new_task, _priority \
        = processor.process(proposal, hints)

    return ok_json({
        "passed": passed,
        "diags": diags
    })

