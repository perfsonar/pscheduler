#
# Logger Handle
#

import os
import pscheduler
import sys
import time

from pschedulerapiserver import application

from flask import Response
from flask import request

from .args import *
from .debug import *

class APILog(pscheduler.Log):

    def __init__(self, *args, **kwargs):
        self.__last_state = debug_state()
        pscheduler.Log.__init__(self, *args, **kwargs)
        self.set_debug(self.__last_state)

    def debug(self, format, *args):
        current_state = debug_state()
        if current_state != self.__last_state:
            self.__last_state = current_state
            self.set_debug(current_state)
        pscheduler.Log.debug(self, format, *args)


# This is thread-safe, so no need to do anything special with it.
log = APILog(name='pscheduler-api[%d]' % (os.getpid()), signals=False, propagate=True)
