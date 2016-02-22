"""
Functions for inhaling JSON in a pScheduler-normalized way
"""

from json import load, loads, dump, dumps
import sys
import pscheduler

# Recursively remove all items that are construed as comments (begin
# with an underscore)
#
# TODO: This doesn't play nicely with arrays.
#
def _json_scrub_comments(dict):
    for key, value in dict.items():
        if type(value) is dict:
            _json_scrub_comments(dict)
        elif key.startswith('_'):
            del dict[key]



def json_load(source=None):
    """
    Load a blob of JSON and exit with failure if it didn't read.

    Arguments:

    source - String or open file containing the JSON.  If not
    specified, sys.stdin will be used.
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
    except ValueError:
        # TODO: Make this consistent and fix scripts that use it.
        if type(source) is str:
            raise Exception("Invalid JSON")
        else:
            pscheduler.fail("Invalid JSON")

    # TODO: This doesn' work, so don't bother with it.
    # _json_scrub_comments(json_in)
    return json_in


def json_dump(obj=None, dest=None):
    """
    Write a blob of JSON contained in a hash to a file destination.
    If none is specified, it will be returned as a string.
    """

    # Return a string
    if dest is None:
        return '' if obj is None else dumps(obj) 

    # Send to a file
    if obj is not None:
        dump(obj, dest)
        print >> dest
    return None
