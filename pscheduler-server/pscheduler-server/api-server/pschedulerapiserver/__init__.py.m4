#
# Initialization for pschedulerapiserver
#

import pscheduler

from flask import Flask

# This must happen before the other imports.
application = Flask(__name__)
application.config["APPLICATION_ROOT"] = pscheduler.api_root()

application.config["DEBUG"] = False

from .log import *
from .response import *

from .admin import *
from .args import *
from .dbcursor import *
from .json import *
from .limitproc import *
from .limits import *
from .archivers import *
from .runs import *
from .schedule import *
from .tasks import *
from .tests import *
from .tools import *
from .url import *


# These values are not hard-wired; they were filled in during the
# build.

dsn = "@__DSN_FILE__"
dbcursor_init(dsn)


limit_file = "__LIMITS_FILE__"
limitproc_init(limit_file)
