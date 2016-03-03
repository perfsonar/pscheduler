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



def json_load(source=None, exit_on_error=False):
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
    except ValueError as ex:
        # TODO: Make this consistent and fix scripts that use it.
        if type(source) is str or not exit_on_error:
            raise ValueError("Invalid JSON: " + str(ex))
        else:
            pscheduler.fail("Invalid JSON: " + str(ex))

    # TODO: This doesn' work, so don't bother with it.
    # _json_scrub_comments(json_in)
    return json_in


def json_dump(obj=None, dest=None, pretty=False):
    """
    Write a blob of JSON contained in a hash to a file destination.
    If none is specified, it will be returned as a string.
    """

    # TODO: Make the use of dump/dumps less repetitive

    # Return a string
    if dest is None:
        if obj is None:
            return ''

        if pretty:
            return dumps(obj, 
                         sort_keys=True,
                         indent=4,
                         separators=(',', ': ')
                         )
        else:
            return dumps(obj)

    # Send to a file
    if obj is not None:
        if pretty:
            dump(obj, dest,
                 sort_keys=True,
                 indent=4,
                 separators=(',', ': ')
                 )
        else:
            dump(obj, dest)
        print >> dest
    return None


    if always_pretty or arg_boolean('pretty'):
        return json.dumps(dump, \
                              sort_keys=True, \
                              indent=4, \
                              separators=(',', ': ') \
                              ) + '\n'
    else:
        return json.dumps(dump) + '\n'

