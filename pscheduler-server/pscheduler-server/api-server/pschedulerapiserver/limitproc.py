#
# Limit Processor
#

import os
import pscheduler
import sys
import time

from pscheduler.limitprocessor import LimitProcessor

from .log import log



# TODO: Don't like the global nature of this.  Do a better job
# encapsulating it.

this = sys.modules[__name__]

# How often we check the file for an update, in seconds
this.update_interval = 10

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
       and now - last_check < this.update_interval:
        return
    this.last_check = now

    log.debug("Checking for new limit configuration")

    exists = os.path.isfile(this.limit_file) \
             and os.access(this.limit_file, os.R_OK)

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

    # If the file hasn't changed, maintain the status quo.
    if this.modified is not None and modified <= this.modified:
        log.debug("Limit file has not changed.")
        return

    log.debug("Loading limits from %s" % this.limit_file)
    try:
        processor = LimitProcessor(this.limit_file)
        log.info("New limits loaded")
    except Exception as ex:
        processor = None
        this.whynot = str(ex)
        log.critical("Failed to load limit file %s: %s",
                     limit_file, this.whynot)

    this.file_exists = True
    this.modified = modified
    this.processor = processor



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
