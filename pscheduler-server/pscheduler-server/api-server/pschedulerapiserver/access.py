#
# Access-Related Functions
#

import pscheduler

from flask import request

local_ips = pscheduler.LocalIPList()

def access_write_ok(original_requester):
    """
    Determine whether the remote requester can write to a task.

    The rules for this are (currently) that the request must come from
    the same IP that submitted the task or from an IP bound to one of
    the interfaces on the local system.
    """
    requester = request.remote_addr
    return ((requester == original_requester)
            or (requester in local_ips))
