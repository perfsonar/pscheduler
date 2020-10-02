"""
Functions for invoking plugin methods
"""

import os

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
