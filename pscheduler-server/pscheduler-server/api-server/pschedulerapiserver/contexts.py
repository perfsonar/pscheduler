#
# Context-Related Pages
#

import pscheduler

from pschedulerapiserver import application

from flask import request

from .dbcursor import dbcursor_query
from .json import *
from .response import *

#
# Contexts
#

# All contexts
@application.route("/contexts", methods=['GET'])
def contexts():
    return json_query("SELECT json FROM context ORDER BY NAME")


# Context <name>
@application.route("/contexts/<name>", methods=['GET'])
def contexts_name(name):
    return json_query("SELECT json FROM context WHERE name = %s",
                      [name], single=True)


# Context spec validation
@application.route("/contexts/<name>/data-is-valid", methods=['GET'])
def contexts_name_data_is_valid(name):

    try:
        cursor = dbcursor_query(
            "SELECT EXISTS (SELECT * FROM context WHERE NAME = %s)",
            [name])
    except Exception as ex:
        return error(str(ex))

    exists = cursor.fetchone()[0]
    cursor.close()
    if not exists:
        return not_found()

    data = request.args.get('data')
    if data is None:
        return bad_request("No archive data provided")

    try:
        returncode, stdout, stderr = pscheduler.run_program(
            ["pscheduler", "internal", "invoke", "context",
             name, "data-is-valid"],
            stdin=data)

        if returncode != 0:
            return error("Unable to validate context data: %s" % (stderr))

        validate_json = pscheduler.json_load(stdout, max_schema=1)
        return ok_json(validate_json)

    except Exception as ex:
        return error("Unable to validate context data: %s" % (str(ex)))
