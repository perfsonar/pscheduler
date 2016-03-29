"""
Functions for use in spec-to-cli methods
"""

import pscheduler

def speccli_build_args(json, strings=[], bools=[]):
    """
    Build an array of command-line switches from a flat JSON object
    and lists of key/parameter tuples.

    Each key/parameter tuple consists of a key and an option name.
    For example, to turn the JSON { "foo": "blatz" } into a switch
    called "--foo", the tuple to pass would be ( 'foo', 'foo' ).

    Tuples supplied to the 'strings' list will append the switch and
    the value of the JSON pair if the first item in the tuple is
    present.  The example above would produce [ '--foo', 'blatz' ].

    Tuples supplied to the 'boolean' argument will append the switch
    if it is present in the JSON, either in a --xxx format if true or
    a --no-xxx format if false.  For the JSON { "bar": true, "baz":
    false }, the tuple ('bar', bar') would produce [ '--bar' ] and the
    tuple ('baz', 'baz') would produce [ '--no-bar' ].
    """

    result = []

    for arg in strings:
        item, option = arg
        try:
            value = json[item]
            result.append('--' + option)
            result.append(str(value))
        except KeyError:
            pass  # Missing key is okay.

    for arg in bools:
        item, option = arg
        try:
            value = json[item]
            if value:
                result.append('--' + option)
            else:
                result.append('--no-' + option)
        except KeyError:
            pass  # Missing key is okay.     

    return result
