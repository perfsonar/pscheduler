"""
JQ JSON Filter Class
"""

import re

import pyjq
from  _pyjq import ScriptRuntimeError


class JQRuntimeError(Exception):
    pass

_import_include = r"((import|include) [^;]+;)"

def _groom(script):
    """
    Groom a filter by moving all imports and includes to the top.  
    """

    # Pull and hold all imports
    lines = map(
        lambda x: x[0],
        re.findall(_import_include, script)
    )
    # Add the rest of the script without the imports and includes
    lines.append(re.sub(_import_include, "", script))
    return "\n".join(lines)



def issue_717_workaround(json):
    """
    As a workaround for the problem uncovered in #717, traverse
    everything in a blob of JSON and convert all floats which are
    larger than 31 bits and have nothing to the right of the decimal
    point into integers.

    TODO: Remove this after #717 is fixed.
    """

    if isinstance(json, dict):
        return { key: issue_717_workaround(value)
                 for key, value in json.iteritems() }

    elif isinstance(json, list):
        return [ issue_717_workaround(item) for item in json ]

    elif isinstance(json, float) \
         and json >= 2147483648.0 \
         and int(json) == json:
        return int(json)

    else:
        return json


class JQFilter(object):
    """
    JQ JSON filter
    """

    def __init__(
            self,
            filter_spec=".",
            args={},
            output_raw=False,
            groom=False,
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

        groom - Move all 'import' and 'include' statements to the
        top of the script before compiling.  This allows filters
        prepending functions to user-provided scripts that do
        imports to compile properly.
        """

        self.output_raw = output_raw

        if type(filter_spec) == dict:
            self.output_raw = filter_spec.get("output-raw", output_raw)
            filter_spec = filter_spec.get("script", ".")

        if isinstance(filter_spec, list):
            filter_spec = "\n".join([str(line) for line in filter_spec])

        if not isinstance(filter_spec, basestring):
            raise ValueError("Filter spec must be plain text, list or dict")

        if groom:
            filter_spec = _groom(filter_spec)

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

            result = issue_717_workaround(self.script.all(json))
            # TODO: Restore this after the issue behind #717 is fixed.
            #result = self.script.all(json)

            if isinstance(result, list) and self.output_raw:
                return "\n".join([str(item) for item in result])

            elif isinstance(result, dict) or isinstance(result, list):
                return result

            else:
                raise ValueError("No idea what to do with %s result", type(result))

        except ScriptRuntimeError as ex:
            raise JQRuntimeError(str(ex))




if __name__ == "__main__":

    # Check out grooming

    print "Groom Check:"
    print _groom("def xyz: 123 end; import x/y/z; xyz")
    print

    print "Filter:"
    filter = JQFilter(".")
    print filter('{ "foo": 123, "bar": 456 }')
    print

    # Note that this only works if pscheduler-jq-library is installed.
    print "Groomed Filter:"
    filter = JQFilter([
        'def x: 123;',
        'import "pscheduler/si" as si;',
        'si::as_integer("12ki"), x'
        ], groom=True)

    print filter('{ "foo": 123, "bar": 456 }')
    print
