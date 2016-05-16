"""
Functions for running external programs neatly
"""

import pscheduler
import select
import subprocess32

# Note: Docs for the 3.x version of subprocess, the backport of which
# is used here, is at https://docs.python.org/3/library/subprocess.html

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

    try:
        process = subprocess32.Popen(argv,
                                     stdin=subprocess32.PIPE,
                                     stdout=subprocess32.PIPE,
                                     stderr=subprocess32.PIPE
                                     )

        if line_call is None:

            # Single-shot I/O with optional timeout

            try:
                stdout, stderr = process.communicate(stdin, timeout=timeout)
                status = process.returncode

            except subprocess32.TimeoutExpired:
                # Clean up after a timeout
                process.kill()
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
        status = 2
        stdout = ''
        stderr = str(ex)

    if fail_message is not None and status != 0:
        pscheduler.fail("%s: %s" % (fail_message, stderr))

    return status, stdout, stderr
