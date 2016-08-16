"""
Functions for running external programs neatly
"""

import atexit
import pscheduler
import select
import subprocess32
import sys
import traceback

# Note: Docs for the 3.x version of subprocess, the backport of which
# is used here, is at https://docs.python.org/3/library/subprocess.html


# Keep a hash of what processes are running so they can be killed off
# when the program exits.  Note that it would behoove any callers to
# make sure they exit cleanly on most signals so this gets called.

__running = {}

def __terminate_running():
    for process in __running:
        process.terminate()

atexit.register(__terminate_running)


def run_program(argv,              # Program name and args
                stdin=None,        # What to send to stdin
                line_call=None,    # Lambda to call when a line arrives
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
    line_call=l - Call lambda l with one argument containing a line which
        arrived on stdout each time that happens.  If provided, the
        'stdout' return value will be None.
    timeout=n - Wait n seconds for the program to finish, otherwise kill it.
    timeout_ok - True to prevent timeouts from being treated as errors.
    short - True to force timeout to two seconds
    fail_message=s - Exit program and include string s if program fails.

    Return Values:

    status - Status code returned by the program
    stdout - Contents of standard output as a single string
    stderr - Contents of standard erroras a single string
    """

    process = None

    if filter(lambda v: v is None, argv):
        raise Exception("Can't run with null arguments.")

    try:
        process = subprocess32.Popen(argv,
                                     stdin=subprocess32.PIPE,
                                     stdout=subprocess32.PIPE,
                                     stderr=subprocess32.PIPE,
                                     )

        __running[process] = 1

        if line_call is None:

            # Single-shot I/O with optional timeout

            try:
                stdout, stderr = process.communicate(stdin, timeout=timeout)
                status = process.returncode

            except subprocess32.TimeoutExpired:
                # Clean up after a timeout
                try:
                    process.kill()
                except OSError:
                    pass  # Can't kill things that change UID
                process.communicate()

                status = 0 if timeout_ok else 2

                # TODO: See if the exception has the contents of stdout and
                # stderr available.
                stdout = ''
                stderr = "Process took too long to run."

        else:

            # Read one line at a time, passing each to the line_call lambda

            if not isinstance(line_call, type(lambda:0)):
                raise ValueError("Function provided is not a lambda.")

            if stdin is not None:
                process.stdin.write(stdin)
            process.stdin.close()

            stderr = ''

            stdout_fileno = process.stdout.fileno()
            stderr_fileno = process.stderr.fileno()

            fds = [ stdout_fileno, stderr_fileno ]

            end_time = pscheduler.time_now() \
                + pscheduler.seconds_as_timedelta(timeout)

            while True:

                time_left = pscheduler.timedelta_as_seconds(
                    end_time - pscheduler.time_now() )

                reads, writes, specials = select.select(fds, [], [], time_left)

                if len(reads) == 0:
                    del __running[process]
                    return 2, None, "Process took too long to run."

                for fd in reads:
                    if fd == stdout_fileno:
                        line = process.stdout.readline()
                        if line != '':
                            line_call(line[:-1])
                    elif fd == stderr_fileno:
                        line = process.stderr.readline()
                        if line != '':
                            stderr += line

                if process.poll() != None:
                    break

            process.wait()

            status = process.returncode
            stdout = None

    except Exception as ex:
        extype, ex_dummy, tb = sys.exc_info()
        status = 2
        stdout = ''
        stderr = ''.join(traceback.format_exception_only(extype, ex)) \
            + ''.join(traceback.format_exception(extype, ex, tb)).strip()


    if process is not None:
        del __running[process]

    if fail_message is not None and status != 0:
        pscheduler.fail("%s: %s" % (fail_message, stderr))

    return status, stdout, stderr



if __name__ == "__main__":

    status, out, err = run_program(["cat", "/etc/issue", "-"],
                                   stdin="Hello, world.",
                                   short=True
                                   )
    print "Status:", status
    print "Out:   ", out
    print "Err:   ", err
