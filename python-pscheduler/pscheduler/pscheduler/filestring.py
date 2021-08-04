"""
Functions for retrieving strings from files
"""

import os


def string_from_file(string, strip=True):
    """
    Return an unaltered string or the contents of a file if the string
    begins with @ and the rest of it points at a path.

    If 'strip' is True, remove leading and trailing whitespace
    (default behavior).
    """

    if not isinstance(string, str):
        raise ValueError("Argument must be a string")

    if not string:
        # Easy case.  No need to strip, either.
        return string

    if (string[0] != "@"):
        if string.startswith("\\@"):
            value = string[1:]
        else:
            value = string

    else:

        path = os.path.expanduser(string[1:])
        with open(path, 'r') as content:
            value = content.read()

    return value.strip() if strip else value
