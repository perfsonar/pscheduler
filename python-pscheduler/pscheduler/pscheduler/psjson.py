"""
Functions for inhaling JSON in a pScheduler-normalized way
"""

from json import load, loads, dump, dumps
import sys
import pscheduler


def json_decomment(json, prefix='#', null=False):
    """
    Remove any JSON object emember whose name begins with 'prefix'
    (default '#') and return the result.  If 'null' is True, replace
    the prefixed items with a null value instead of deleting them.
    """
    if type(json) is dict:
        result = {}
        for item in json.keys():
            if item.startswith(prefix):
                if null:
                    result[item] = None
                else:
                    next
            else:
                result[item] = json_decomment(json[item], prefix=prefix,
                                              null=null)
        return result

    elif type(json) is list:
        result = []
        for item in json:
            result.append(json_decomment(item, prefix=prefix, null=null))
        return result

    else:
        return json


def json_substitute(json, value, replacement):
    """
    Substitute any pair whose value is 'value' with the replacement
    JSON 'replacement'.  Based on pscheduler.json_decomment().
    """
    if type(json) is dict:
        result = {}
        for item in json.keys():
            if json[item] == value:
                result[item] = replacement
            else:
                result[item] = json_substitute(json[item], value, replacement)
        return result

    elif type(json) is list:
        result = []
        for item in json:
            result.append(json_substitute(item, value, replacement))
        return result

    else:
        return json


def json_load(source=None, exit_on_error=False, strip=True):
    """
    Load a blob of JSON and exit with failure if it didn't read.

    Arguments:

    source - String or open file containing the JSON.  If not
    specified, sys.stdin will be used.

    exit_on_error - Use the pScheduler failure mechanism to complain and
    exit the program.  (Default False)

    strip - Remove all pairs whose names begin with '#'.  This is a
    low-budget way to support comments wthout requiring a parser that
    understands them.  (Default True)
    """
    if source is None:
        source = sys.stdin

    try:
        if type(source) is str or type(source) is unicode:
            json_in = loads(str(source))
        elif type(source) is file:
            json_in = load(source)
        else:
            raise Exception("Internal error: bad source type ", type(source))
    except ValueError as ex:
        # TODO: Make this consistent and fix scripts that use it.
        if type(source) is str or not exit_on_error:
            raise ValueError("Invalid JSON: " + str(ex))
        else:
            pscheduler.fail("Invalid JSON: " + str(ex))

    return json_decomment(json_in) if strip else json_in


def json_dump(obj, dest=None, pretty=False):
    """
    Write a blob of JSON contained in a hash to a file destination.
    If no destination is specified, it will be returned as a string.
    If the blob is None, a JSON 'null' will be returned.
    """

    # TODO: Make the use of dump/dumps less repetitive

    # Return a string
    if dest is None:
        if pretty:
            return dumps(obj,
                         sort_keys=True,
                         indent=4,
                         separators=(',', ': ')
                         )
        else:
            return dumps(obj)

    # Send to a file
    if pretty:
        dump(obj, dest,
             sort_keys=True,
             indent=4,
             separators=(',', ': ')
             )
    else:
        dump(obj, dest)
        print >> dest
