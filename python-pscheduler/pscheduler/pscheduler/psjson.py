"""
Functions for inhaling JSON in a pScheduler-normalized way
"""

from json import load, loads

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
        if type(source) is str:
            json_in = loads(source)
        elif type(source) is file:
            json_in = load(source)
        else:
            pscheduler.fail('Internal error: bad source type ', type(source))
    except ValueError:
        pscheduler.fail('Invalid JSON')

    _json_scrub_comments(json_in)
    return json_in
