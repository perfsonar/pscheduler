#
# Argument-Related Functions
#

import pscheduler
import uuid

from flask import request


def arg_boolean(name):
    """Determine if a boolean argument is part of a request.  The
    argument is considered true if it is 'true', 'yes' or '1' or if it
    is present but has no value.  Otherwise it is considered False."""
    argval = request.args.get(name)
    if argval is None:
        return False;
    argval = argval.lower()
    if argval in [ '', 'true', 'yes', '1' ]:
        return True
    return False


def arg_datetime(name):
    """Fetch and validate an argument as an ISO8601 date and time,
    returning a datetime if specificed, None if not and throwing a
    ValueError if invalid."""
    argval = request.args.get(name)
    if argval is None:
        return None
    timestamp = pscheduler.iso8601_as_datetime(argval)
    if timestamp is None:
        raise ValueError("Invalid timestamp; expecting ISO8601.")
    return timestamp


def arg_cardinal(name):
    """Fetch and validate an argument as a cardinal number."""
    argval = request.args.get(name)
    if argval is None:
        return None
    try:
        cardinal = int(argval)
        if cardinal < 1:
            raise ValueError
    except ValueError:
        raise ValueError("Invalid cardinal; expecting integer > 0")
    return cardinal

def arg_integer(name):
    """Fetch and validate an argument as an integer."""
    argval = request.args.get(name)
    if argval is None:
        return None
    try:
        integer = int(argval)
    except ValueError:
        raise ValueError("Invalid integer.")
    return integer



def arg_json(name):
    """Fetch and validate an argument as JSON"""
    argval = request.args.get(name)
    if argval is None:
        return None
    # This will throw a ValueError if something's wrong.
    return pscheduler.json_load(argval)


def arg_uuid(name):
    """Fetch and validate an argument as a UUID"""
    argval = request.args.get(name)
    if argval is None:
        return None
    # This will throw a ValueError if something's wrong.
    return str(uuid.UUID(argval))


def is_expanded():
    return arg_boolean('expanded')
