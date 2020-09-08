"""
Functions for exiting scripts in a standard way.
"""

import json
import os
import sys


def fail(*args):
    """
    Exit with failure with optional commentary to stderr.
    """
    message = ''
    for arg in args:
        message += arg
    if message != '':
        sys.stderr.write(message.strip() + '\n')
    exit(1)


def fail_other(status, *args):
    """
    Exit with a specific failure code with optional commentary to stderr.
    """
    # TODO: Find out how to pass args so this doesn't have to be rubberstamped.
    message = ''
    for arg in args:
        message += arg
    if message != '':
        sys.stderr.write(message.strip() + '\n')
    exit(status)


def succeed(text=None):
    """
    Exit with success and an optional messsage to stdout.
    """
    if text is not None:
        print(text.strip())
    exit(0)


def succeed_json(result=None):
    """
    Exit with success, dumping JSON to stdout.
    """
    json.dump(result, sys.stdout)
    print()
    exit(0)



def beta_feature(example=None):
    """
    Require that the environment be set for a beta feature and fail if
    it isn't.
    """

    if example is None:
        example = "pscheduler %s ..." % (os.path.basename(sys.argv[0]))

    if "BETA" not in os.environ:
        fail(
            "This program is a beta feature and must be run with the\n"
            "BETA environment variable set.\n"
            "\n"
            "For example:\n"
            "$ BETA=1 %s\n"
            "\n"
            "This requirement will be removed in a future release."
            % (example)
        )
