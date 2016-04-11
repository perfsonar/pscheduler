#
# Initialization for pschedulerapiserver
#

import pscheduler

from flask import Flask

# This must happen before the other imports.
application = Flask(__name__)
application.config["APPLICATION_ROOT"] = pscheduler.api_root()

# TODO: Turn this off after development.  Or leave it on?
application.config["DEBUG"] = True

from .admin import *
from .args import *
from .dbcursor import *
from .json import *
from .log import *
from .response import *
from .runs import *
from .tasks import *
from .tests import *
from .tools import *
from .url import *


# TODO: Find something better than a hard-wired default.
dsn = "@/etc/pscheduler/database-dsn"
dbcursor_init(dsn)
