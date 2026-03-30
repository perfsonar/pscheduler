'''
Functions for invoking or carrying out plugin methods
'''

import jsonschema
import os
import sys

from .exitstatus import succeed_json
from .psjson import json_load
from .program import run_program

# The absolute here path was filled in by the build process.
__CLASSES = os.path.abspath("__CLASSES__")


def plugin_method_path(pltype, which, method):
    """
    Find the path for a plugin method.  Throws ValueError if there are
    problems.
    """
    type_dir = os.path.join(__CLASSES, pltype)
    if not os.path.isdir(type_dir):
        raise ValueError("Unknown plugin type '%s'" % pltype)

    plugin_dir = os.path.join(type_dir, which)
    if not os.path.isdir(plugin_dir):
        raise ValueError("Unknown %s plugin '%s'" % (pltype, which))

    method_exec = os.path.join(plugin_dir, method)
    if not os.access(method_exec, os.X_OK):
        raise ValueError("%s plugin %s has no '%s' method." % (pltype, which, method))

    return method_exec



def plugin_invoke(pltype, which, method, argv=[], **kwargs):
    """
    Run a plugin method.

    Keyword args get passed through to run_program().
    """

    return run_program([ plugin_method_path(pltype, which, method) ] + argv, **kwargs)



# Run the local enumerate

def _enumerated_spec_is_valid(proposed, plugin_type, plugin=None):
    '''
    This private function is the meat of plugin_spec_is_valid().
    See comments for how it works.
    '''

    # The structure of plugins requires that the {spec,data}-is-valid
    # method be in the same directory as the enumerator.  Run it from
    # wherever we are.

    whereami = os.path.realpath(os.path.dirname(sys.argv[0]))

    # Run the enumerator and see if the contents look sane.

    # Don't use plugin_invoke() here.  It assumes the installed
    # location, and running from the same directory where the program
    # was invoked wil allow it to operate in dev and production.
    status, stdout, stderr = run_program(f'{whereami}/enumerate')
    if status != 0:
        return (False, f'INTERNAL ERROR: Could not get enumeration: {stderr}')
    
    enumeration = json_load(stdout)
    try:
        versions = enumeration['spec']['jsonschema']['versions']
        if not isinstance(versions, list):
            raise KeyError()
    except KeyError:
        return (False, f'INTERNAL ERROR: Enumerator is malformed.')

    # Find and validate the schema

    schema = proposed.get('schema', 1)
    if schema < 1 or schema > len(versions):
        return(False, f'Schema {schema} is not supported.')

    # Validate the proposed spec against the specified schema version.

    validator = versions[schema]

    jsonschema.Draft7Validator.check_schema(validator)

    try:
        jsonschema.validate(proposed, validator,
                            format_checker=jsonschema.draft7_format_checker
        )
    except jsonschema.exceptions.ValidationError as ex:
        try:
            message = ex.schema["x-invalid-message"].replace("%s", ex.instance)
        except (KeyError, TypeError):
            message = ex.message

        path = "/".join([str(x) for x in ex.absolute_path])
        return (False, "At /%s: %s" % (path, message))

    return (True, 'OK')



def plugin_spec_is_valid(plugin_type, plugin=None):
    '''
    This is a fully-fleshed-out {spec,data}-is-valid method for
    plugins that reads a proposed JSON spec from stdin, runs the
    corresponding 'enumerate' method to get the validator, validates
    the proposed spec or data and does the standard exit for these
    methods.

    See _enumerated_spec_is_valid(), above, for additional deatails.
    '''

    try:
        proposed = json_load()
    except ValueError as ex:
        succeed_json({
            "valid": False,
            "error": str(ex)
        })

    valid, message = _enumerated_spec_is_valid(proposed, plugin_type, plugin)

    result = {
        "valid": valid
    }

    if not valid:
        result["error"] = message

    succeed_json(result)
