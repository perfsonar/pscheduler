#
# Archiver-Related Pages
#

import pscheduler

from pschedulerapiserver import application

from flask import request

from .dbcursor import dbcursor_query
from .json import *
from .response import *

#
# Archivers
#

# All archivers
@application.route("/archivers", methods=['GET'])
def archivers():
    return json_query("SELECT json FROM archiver", [])


# Archiver <name>
@application.route("/archivers/<name>", methods=['GET'])
def archivers_name(name):
    return json_query("SELECT json FROM archiver WHERE name = %s",
                      [name], single=True)
