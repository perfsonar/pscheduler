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

        if isinstance(filter_spec, basestring):
            self.script = pyjq.compile(filter_spec, args)
            self.output_raw = output_raw

        elif type(filter_spec) == dict:
            self.script = pyjq.compile(filter_spec.get("script", "."), args)
            self.output_raw = filter_spec.get("output-raw", output_raw)

        else:
            raise ValueError("Filter spec must be plain text or dict")


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
