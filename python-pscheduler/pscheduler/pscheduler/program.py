"""
Functions for running external programs neatly
"""

import pscheduler
import subprocess32

# Note: Docs for the 3.x version of subprocess, the backport of which
# is used here, is at https://docs.python.org/3/library/subprocess.html

def run_program(argv,
                stdin=None,        # What to send to stdin
                timeout=None,      # Seconds
                timeout_ok=False,  # Treat timeouts as not being an error
                short=False,       # True to force timeout to 2 seconds
                fail_message=None  # Exit with this failure message
                ):
    """
    Run a program and return the results.

    Arguments:

    argv - Array containing arguments, including name of program
    stdin=s - String containing what should be sent to standard input
    timeout=n - Wait n seconds for the program to finish, otherwise kill it.
    timeout_ok - True to prevent timeouts from being treated as errors.
    short - True to force timeout to two seconds
    fail_message=s - Exit program and include string s if program fails.

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
        status = process.returncode

    except subprocess32.TimeoutExpired as ex:
        # Clean up after a timeout
        process.kill()
        process.communicate()

        status = 0 if timeout_ok else 2

        # TODO: See if the exception has the contents of stdout and
        # stderr available.
        stdout = ''
        stderr = "Process took too long to run."

    except Exception as ex:
        status = 2
        stdout = ''
        stderr = str(ex)

    if fail_message is not None and status != 0:
        pscheduler.fail("%s: %s" % (fail_message, stderr))

    return status, stdout, stderr
