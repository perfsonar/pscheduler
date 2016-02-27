"""
Functions for running external programs neatly
"""

import subprocess32

# Note: Docs for the 3.x version of subprocess, the backport of which
# is used here, is at https://docs.python.org/3/library/subprocess.html

def run_program(argv,
                stdin=None,   # What to send to stdin
                timeout=None  # Seconds
                ):
    """
    Run a program and return the results.

    Arguments:

    argv - Array containing arguments, including name of program
    stdin=s - String containing what should be sent to standard input
    timeout=n - Wait n seconds for the program to finish, otherwise kill it.

    Return Values:

    status - Status code returned by the program
    stdout - Contents of standard output as a single string
    stderr - Contents of standard erroras a single string
    """

    try:
        process = subprocess32.Popen(argv,
                                     stdin=subprocess32.PIPE,
                                     stdout=subprocess32.PIPE,
                                     stderr=subprocess32.PIPE
                                     )

        stdout, stderr = process.communicate(stdin, timeout=timeout)
        return process.returncode, stdout, stderr
    except subprocess32.TimeoutExpired as ex:
        # TODO: Pick a better exit status
        return 2, '', "Process took too long to run."
    except Exception as ex:
        # TODO: Pick a better exit status
        return 2, '', str(ex)


def run_program_short(args,
                      stdin=None,   # What to send to stdin
                      ):
    """
    Run a program that should not run very long using a timeout of 2
    seconds.
    """
    return run_program(args, stdin=stdin, timeout=2)
