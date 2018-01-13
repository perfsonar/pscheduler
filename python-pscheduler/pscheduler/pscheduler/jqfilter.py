"""
JQ JSON Filter Class
"""

import pyjq
from  _pyjq import ScriptRuntimeError

from .psjson import *


class JQRuntimeError(Exception):
    pass


class JQFilter(object):
    """
    JQ JSON filter
    """

    def __init__(
            self,
            filter_spec=".",
            args={},
            output_raw=False
            ):
        """
        Construct a filter.  Arguments:

        filter_spec - The JQ script to be used for this filter.  This
        may be any subclass of basestring, a list or a dict.  Strings
        are interpreted directly, lists are stringified and joined
        with newlines (to make multi-line scripts readable in JSON)
        and dicts give their "script" and "output-raw" elements
        extracted and used as if they were either of the other types.

        args - A dictionary of variables to be pre-set in the script.

        output_raw - True to produce raw output instead of JSON.
        """

        self.output_raw = output_raw

        if type(filter_spec) == dict:
            self.output_raw = filter_spec.get("output-raw", output_raw)
            filter_spec = filter_spec.get("script", ".")

        if isinstance(filter_spec, list):
            filter_spec = "\n".join([str(line) for line in filter_spec])

        if not isinstance(filter_spec, basestring):
            raise ValueError("Filter spec must be plain text, list or dict")

        self.script = pyjq.compile(filter_spec, args)


    def __call__(
            self,
            json={}
    ):
        """
        Filter 'json' according to the script.  If output_raw is True,
        join everything that comes out of the filter into a a single
        string and return that.
        """

        try:

            result = self.script.all(json)

            if isinstance(result, list) and self.output_raw:
                return "\n".join([str(item) for item in result])

            elif isinstance(result, dict) or isinstance(result, list):
                return result

            else:
                raise ValueError("No idea what to do with %s result", type(result))

        except ScriptRuntimeError as ex:
            raise JQRuntimeError(str(ex))




if __name__ == "__main__":

    # TODO:  Write a few examples.

    filter = JQFilter(".")
    print filter('{ "foo": 123, "bar": 456 }')

    pass
