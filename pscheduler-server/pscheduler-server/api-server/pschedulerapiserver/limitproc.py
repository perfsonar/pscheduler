#
# Limit Processor
#

import os
import sys

from pscheduler.limitprocessor import LimitProcessor

from .log import log



# TODO: Don't like the global nature of this.  Do a better job
# encapsulating it.

this = sys.modules[__name__]

this.processor = None
this.whynot = None

def limitproc_init(limit_file):
    """Initialize the limit processor"""

    if os.path.isfile(limit_file) and os.access(limit_file, os.R_OK):

        try:
            this.processor = LimitProcessor(limit_file)
        except Exception as ex:
            this.whynot = str(ex)
            log.critical("Failed to load limit file %s: %s",
                         limit_file, this.whynot)
            this.processor = None

    else:

        # If the limit file doesn't exist, create an inert processor that
        # passes anything.
        this.processor = LimitProcessor()



def limitprocessor():
    if this.processor is None:
        return (None, "Limit processor is not initialized: %s" % this.whynot)
    else:
        return (this.processor, None)
