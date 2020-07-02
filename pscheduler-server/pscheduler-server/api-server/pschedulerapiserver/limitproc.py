#
# Limit Processor
#

import os
import sys
import time

from pscheduler.limitprocessor.limitprocessor import LimitProcessor

from .log import log



# TODO: Don't like the global nature of this.  Do a better job
# encapsulating it.

this = sys.modules[__name__]

# How often we check the file for an update, in seconds
this.update_interval = 15

# The limit processor; the default being one that does nothing.
this.processor = LimitProcessor()

this.limit_file = None   # Path to limit file
this.file_exists = False # Whether or not the file exists
this.last_check = None   # Last time the file's time was checked
this.modified = None     # File's mtime last we saw it
this.whynot = None       # Reason for last load failure

def __limitproc_update():

    now = time.time()

    # If we're within the update time, don't bother.
    if this.last_check is not None \
       and now - this.last_check < this.update_interval:
        return
    this.last_check = now

    log.debug("Checking for new limit configuration")
    exists = os.path.isfile(this.limit_file)

    # No file means no limits
    if not exists:
        log.debug("No limit file present.")
        # Transition from existing to not existing means a new, empty processor
        if this.file_exists:
            log.info("Limit file has been removed.  Disabling limits.")
            this.processor = LimitProcessor()
            this.file_exists = False
            this.timestamp = None
        return


    modified = os.path.getmtime(this.limit_file)

    # If we have a limit configuration and the file hasn't changed,
    # maintain the status quo.

    file_unchanged = this.modified is not None and modified <= this.modified

    if this.processor is not None and file_unchanged:
        log.debug("Limit file has not changed.")
        return

    try:
        this.processor = LimitProcessor(this.limit_file)
        this.whynot = None
        log.info("Limits %s from %s" % (
            "reloaded" if this.file_exists else "loaded",
            this.limit_file))
    except Exception as ex:
        this.processor = None
        this.whynot = str(ex)
        # Only complain if the file changed so the logs don't get
        # flooded.
        if not file_unchanged:
            log.critical("Failed to load limit file: %s", this.whynot)

    this.file_exists = True
    this.modified = modified

    # Make the last check time the actual time in case the check took
    # awhile.  This will prevent continuous attempts at re-loading the
    # file if this attempt took awhile.
    this.last_check = time.time()



def limitproc_init(limit_file):
    """Initialize the limit processor"""

    this.limit_file = limit_file
    __limitproc_update()




def limitprocessor():
    __limitproc_update()
    if this.processor is None:
        return (None, "Limit processor is not initialized.  See system logs.")
    else:
        return (this.processor, None)
