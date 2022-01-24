"""
Limit Class for test-type
"""

# TODO: #824: Remove this file in 5.1

from ...jsonval import *
from ...plugins import *
from ...psjson import *


class LimitTest(object):

    """Limit that passes or fails based on whether or not a test says it
    does.

    NO LONGER SUPPORTED.  THIS IS A TRANSITIONAL STUB.

    TODO: Remove this after 5.1.
    """

    def __init__(self, _data):
        raise ValueError("The 'test' limit is no longer supported.  Use 'jq' instead.")


    def checks_schedule(self):
        return False


    def evaluate(self, proposal):
        assert False, "This limit cannot be evaluated."
