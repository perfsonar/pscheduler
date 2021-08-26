#!/usr/bin/env python3
"""
Functions for finding and killing processes
"""

import os
import psutil
import signal
import time



def process_exists(pid):
    """
    Determine if process 'pid' exists.
    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False    # Doesn't exist
    except PermissionError:
        pass            # Exists but not ours

    return True



def kill_processes(first_args,
                   orphaned_only=False,
                   send_signal=signal.SIGINT,
                   wait=2.0,
                   retry=0.25
):
    """
    Find all processes whose arguments begin with the list 'first_args'
    and kill them off, first with 'send_signal' for up to 'wait' seconds
    and retrying every 'retry' seconds.  If, after that time, any
    processes are left, send them a SIGKILL.   If 'orphaned_only' is True,
    only kill processes with a PPID of 1.
    """

    if not isinstance(first_args,list):
        raise ValueError("Program arguments must be in a list")

    len_first_args = len(first_args)
    if len_first_args < 1:
        raise ValueError("Must have at least one argument to match.")


    pids = []

    for process_item in psutil.process_iter():
        process = process_item.as_dict()
        if (process["cmdline"][0:len_first_args] == first_args) \
           and ((not orphaned_only) or (process["ppid"] == 1)):
            pids.append(process["pid"])

    times = (wait / retry)

    while times:

        existing = 0

        # Do the kills in parallel to make things more predictable
        # time-wise.

        for pid in pids:
            if process_exists(pid):
                existing += 1
                os.kill(pid, send_signal)

        if existing == 0:
            return   # Awww.  Ran out of PIDdies.

        time.sleep(retry)

        times -= 1

    # Last resort

    for pid in pids:
        if process_exists(pid):
            os.kill(pid, signal.SIGKILL)
