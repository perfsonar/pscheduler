#
# Access-Related Functions
#

import pscheduler

from .args import *

from flask import request

local_ips = pscheduler.LocalIPList()

def access_write_task(original_requester, key=None):
    """
    Determine whether a requester can write to a task or its runs.
    """

    requester = request.remote_addr

    # Local interfaces are always okay.
    if requester in local_ips:
        return True

    # Tasks without keys are limited to the original requester only
    if key is None:
        return requester == original_requester

    # Beyond here, the task has a key.  

    request_key = arg_string("key")

    return (request_key is not None) and (request_key == key)



def access_read_sensitive():
    """
    Determine if a requester can read sensitive information in a task
    or its runs.
    """

    return False  # TODO:
