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
    return json_query("SELECT json FROM archiver"
                      " WHERE available ORDER BY NAME")


# Archiver <name>
@application.route("/archivers/<name>", methods=['GET'])
def archivers_name(name):
    return json_query("SELECT json FROM archiver"
                      " WHERE available AND name = %s",
                      [name], single=True)


# Archiver spec validation
@application.route("/archivers/<name>/data-is-valid", methods=['GET'])
def archivers_name_data_is_valid(name):

    cursor = dbcursor_query("SELECT EXISTS"
                            " (SELECT * FROM archiver WHERE NAME = %s)",
                            [name])

    exists = cursor.fetchone()[0]
    cursor.close()
    if not exists:
        return not_found()

    data = request.args.get('data')
    if data is None:
        return bad_request("No archive data provided")

    try:
        returncode, stdout, stderr = pscheduler.run_program(
            ["pscheduler", "internal", "invoke", "archiver",
             name, "data-is-valid"],
            stdin=data)

        if returncode != 0:
            return error("Unable to validate archiver data: %s" % (stderr))

        validate_json = pscheduler.json_load(stdout, max_schema=1)
        return ok_json(validate_json)

    except Exception as ex:
        return error("Unable to validate archiver data: %s" % (str(ex)))
