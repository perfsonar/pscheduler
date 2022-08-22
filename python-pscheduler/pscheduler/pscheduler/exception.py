"""
Functions for dealing with exceptions
"""

import sys
import traceback

class NoExceptionError(Exception):
    pass


def formatted_exception(ex=None):
    """
    Format an exception *ex* into a string.

    If *ex* is None, get the current exception being processed.  If
    there is none, a NoExceptionError will be raised.
    """

    if ex is None:
        _extype, ex, _tb = sys.exc_info()

    if ex is None:
        raise NoExceptionError("No exception is being processed.")

    assert isinstance(ex, Exception)
    return ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__)).strip()
