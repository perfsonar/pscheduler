"""
Functions for exiting scripts in a standard way.
"""

import sys


def fail(*args):
    """
    Exit with failure with optional commentary to stderr.
    """
    for arg in args:
        sys.stderr.write(arg)
    if len(args) > 0:
        sys.stderr.write('\n')
    exit(1)


def fail_other(status, *args):
    """
    Exit with a specific failure code with optional commentary to stderr.
    """
    # TODO: Find out how to pass args so this doesn't have to be rubberstamped.
    for arg in args:
        sys.stderr.write(arg)
    if len(args) > 0:
        sys.stderr.write('\n')
    exit(status)


def succeed():
    """
    Exit with success.
    """
    exit(0)
