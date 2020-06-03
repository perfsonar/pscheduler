#!/usr/bin/env python3
"""
Functions for running external programs neatly
"""

import atexit
import copy
import errno
import os
import select
import stat
import subprocess
import sys
import tempfile
import threading
import traceback
import os

from shlex import quote

from .exit import on_graceful_exit
from .exitstatus import *
from .psjson import *
from .psselect import polled_select
from .pstime import *



# Keep a hash of what processes are running so they can be killed off
# when the program exits.  Note that it would behoove any callers to
# make sure they exit cleanly on most signals so this gets called.

this = sys.modules[__name__]
this.lock = threading.Lock()
this.terminating = False
this.running = None


def __init_running():
    """Internal use:  Initialize the running hash if it isn't."""
    with this.lock:
        if this.running is None:
            this.running = {}
            on_graceful_exit(__terminate_running)


def __terminate_running():
    """Internal use:  Terminate a running process."""
    __init_running()
    while len(this.running) > 0:
        with this.lock:
            process = list(this.running.keys())[0]
        try:
            process.terminate()
            process.wait()
        except Exception:
            pass  # This is a best-effort effort.
        with this.lock:
            try:
                del this.running[process]
            except KeyError:
                pass  # Best effort.

    # Sometimes this gets called twice, so clean the list.
    this.running.clear()


def __running_add(process):
    """Internal use:  Add a running process."""
    __init_running()
    this.running[process] = 1


def __running_drop(process):
    """Internal use:  Drop a running process."""
    __init_running()
    try:
        del this.running[process]
    except KeyError:
        pass


# This gets a single underscore because use in a class makes Python
# mangle it.  See
# https://docs.python.org/2/tutorial/classes.html#private-variables-and-class-local-references
def _end_process(process):
    """End a process gently or, if necessary, forcibly."""
    try:
        process.terminate()
        process.wait(timeout=0.5)
    except OSError:
        pass  # Can't kill things that have changed UID.
    except subprocess.TimeoutExpired:
        process.kill()



def run_program(argv,              # Program name and args
                stdin="",          # What to send to stdin
                line_call=None,    # Lambda to call when a line arrives
                timeout=None,      # Seconds
                timeout_ok=False,  # Treat timeouts as not being an error
                fail_message=None, # Exit with this failure message
                env=None,          # Environment for new process, None=existing
                env_add=None,      # Add hash to existing environment
                attempts=10):      # Max attempts to start the process
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
    fail_message=s - Exit program and include string s if program fails.
    env=h - Pass environment hash 'h' to the child process, using the
        existing environment if the value is None.
    env_add=h - Add contents of hash 'h' to environment.


    Return Values:

    status - Status code returned by the program
    stdout - Contents of standard output as a single string
    stderr - Contents of standard erroras a single string

    NOTE: This function is only intended to process strings.  It will
    throw an exception if handed binary data by the caller or the
    program it runs.
    """

    process = None

    if [arg for arg in argv if arg is None]:
        raise Exception("Can't run with null arguments.")


    # Build up a new, incorruptable copy of the environment for the
    # child process to use.

    if env_add is None:
        env_add = {}

    if env is None and len(env_add) == 0:
        new_env = None
    else:
        new_env = (os.environ if env is None else env).copy()
        new_env.update(env_add)


    def __get_process(argv, new_env, attempts):
        """Try to start a process, handling EAGAINs."""
        while attempts > 0:
            attempts -= 1
            try:
                return subprocess.Popen(argv,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        env=new_env,
                                        universal_newlines=True
                                    )
            except OSError as ex:
                # Non-EAGAIN or last attempt gets re-raised.
                if ex.errno != errno.EAGAIN or attempts == 0:
                    raise ex
                # TODO: Should we sleep a bit here?


        assert False, "This code should not be reached."


    try:
        process = __get_process(argv, new_env, attempts)

        __running_add(process)

        if line_call is None:

            # Single-shot I/O with optional timeout

            try:
                stdout, stderr = process.communicate(stdin, timeout=timeout)
                status = process.returncode

            except subprocess.TimeoutExpired:
                _end_process(process)
                status = 0 if timeout_ok else 2
                stdout = ''
                stderr = "Process took too long to run."

        else:

            # Read one line at a time, passing each to the line_call lambda

            if not isinstance(line_call, type(lambda: 0)):
                raise ValueError("Function provided is not a lambda.")

            if stdin is not None:
                process.stdin.write(stdin)
            process.stdin.close()

            stderr = ''

            stdout_fileno = process.stdout.fileno()
            stderr_fileno = process.stderr.fileno()

            fds = [stdout_fileno, stderr_fileno]

            if timeout is not None:
                end_time = time_now() \
                    + seconds_as_timedelta(timeout)
            else:
                time_left = None

            while True:

                if timeout is not None:
                    time_left = timedelta_as_seconds(
                        end_time - time_now())

                reads, _, _ = polled_select(fds, [], [], time_left)

                if len(reads) == 0:
                    __running_drop(process)
                    _end_process(process)
                    return 2, None, "Process took too long to run."

                for readfd in reads:
                    if readfd == stdout_fileno:
                        got_line = process.stdout.readline()
                        if got_line != '':
                            line_call(got_line[:-1])
                    elif readfd == stderr_fileno:
                        got_line = process.stderr.readline()
                        if got_line != '':
                            stderr += got_line

                if process.poll() != None:
                    break

            # Siphon off anything left on stdout
            while True:
                got_line = process.stdout.readline()
                if got_line == '':
                    break
                line_call(got_line[:-1])

            process.wait()

            status = process.returncode
            stdout = None

    except Exception as ex:
        extype, _, trace = sys.exc_info()
        status = 2
        stdout = ''
        stderr = ''.join(traceback.format_exception_only(extype, ex)) \
            + ''.join(traceback.format_exception(extype, ex, trace)).strip()

    if process is not None:
        __running_drop(process)
        _end_process(process)


    if fail_message is not None and status != 0:
        fail("%s: %s" % (fail_message, stderr))

    return status, stdout, stderr

class ChainedExecRunner(object):

    """Run a series of programs that maintain the same PID and context by
    using exec to call each other.
    """


    def __init__(self, calls, argv=[], stdin=None):

        """The 'calls' argument is an array of dictionaries.  Each dictionary
        contains an entry called "call," a string that names the program
        to be run, and another called "input" which is an arbitrary blob
        of data (usually a dictionary) that can be converted into JSON and
        passed through to the program's standard input.

        The format for the program's input is that for a pScheduler
        context plugin's "change" method.  It consists of two items:
        "data", which is an arbitrary blob of (JSON) data for the
        program to use and "exec," a string indicating the path to the
        program that should be exec'd when the program completes
        successfully.

        For example:

        {
            "program": "/run/this/program",
            "input": {
                "data": { "foo": "bar", "baz": 31415 },
                "exec": "/run/that/program"
            }
        }

        The "argv" and "stdin" are program parameters and standard
        input with the same semantics as the same arguments to
        run_program().
        """

        if not isinstance(calls, list):
            raise ValueError("Calls must be a list.")

        self.stages = []

        if not calls:
            return


        # Create the temporary files that will hold the scripts.


        try:

            # Create a list of temporary files ahead of time so the
            # stage n script can refer to the one for stage n+1.  The
            # extra added on is the "final" stage where the program to
            # be run is actually run.

            for _ in range(0, len(calls)+1):

                (fileno, path) = tempfile.mkstemp(prefix="ContextedRunner-")
                os.close(fileno)
                os.chmod(path, stat.S_IRWXU)
                self.stages.append(path)

            # Write the scripts

            for stage in range(0, len(calls)):

                stage_script = "#!/bin/sh -e\n" \
                               "exec %s <<'EOF'\n" \
                               "%s\n" \
                               "EOF\n" % (
                                   " ".join([quote(arg) for arg in calls[stage]["program"]]),
                                   json_dump({
                                       "data": calls[stage]["input"],
                                       "exec": self.stages[stage+1]
                                   }))

                with open(self.stages[stage], "w") as output:
                    output.write(stage_script)

            # Write the "final" stage

            with open(self.stages[-1], "w") as output:
                output.write(
                    "#!/bin/sh -e\n"
                    "exec %s" % (
                        " ".join([quote(arg) for arg in argv])
                        )
                    )

                if stdin is not None:
                    output.write(
                        " <<'EOF'\n"
                        "%s%s"
                        "EOF\n" % (
                            stdin,
                            "" if stdin[-1] == "\n" else "\n"
                        )
                    )
                else:
                    # PORT: This is Unix-specific.
                    output.write(" < /dev/null\n")


        except Exception as ex:

            for remove in self.stages:
                try:
                    os.unlink(remove)
                except IOError:
                    pass  # This is best effort only.

            raise ex


    def run(self,
            # These are lifted straight from run_program.
            line_call=None,    # Lambda to call when a line arrives
            timeout=None,      # Seconds
            timeout_ok=False,  # Treat timeouts as not being an error
            fail_message=None, # Exit with this failure message
            env=None,          # Environment for new process, None=existing
            env_add=None,      # Add hash to existing environment
            attempts=10):      # Max attempts to start the process
        """
        Run the chain.  Return semantics are the same as for
        run_program(): a tuple of status, stdout, stderr.
        """

        # TODO: Is there a more-pythonic way to do this than pasting
        # in all of the args?
        result = run_program([self.stages[0]],
                             line_call=line_call,
                             timeout=timeout,
                             timeout_ok=timeout_ok,
                             fail_message=fail_message,
                             env=env,
                             env_add=env_add,
                             attempts=attempts
        )

        for remove in self.stages:
            try:
                pass # os.unlink(remove)
            except IOError:
                pass  # This is best effort only.

        return result





if __name__ == "__main__":

    def dump_result(title, tup):
        """Spit out a run result"""
        print()
        print("#\n# %s\n#" % (title))
        (status, stdout, stderr) = tup
        print("Exited", status)
        print("Stdout", stdout)
        print("Stderr", stderr)

    do_all = True

    if do_all or False:
        dump_result(
            "Plain run",
            run_program(
                ['id']
            ))

    if do_all or False:
        dump_result(
            "Failure with stderr",
            run_program(
                ['ls', '/bad/path']
            ))

    if do_all or False:
        dump_result(
            "Timeout",
            run_program(
                ['sleep', '2'],
                timeout=1
            ))

    if do_all or False:
        lines = []

        def line_writer(add_line):
            """Add a line to the list of those received."""
            lines.append(add_line)

        dump_result(
            "Line-at-a-time",
            run_program(
                ['ls', '/'],
                line_call=line_writer
            ))

        print("Lines:")
        print("\n".join(["  %s" % (line) for line in lines]))

    if do_all or False:
        inp = "\n".join([str(number) for number in range(1, 1000000)])
        dump_result(
            "Induced pipe error (Should show no errors)",
            run_program(
                ['head', '-10'],
                stdin=inp
            ))





class ExternalProgram(object):
    """Long-running external program."""

    def __init__(self, args):
        self.args = args
        self.process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        self.err = None

    def stdin(self):
        return self.process.stdin

    def stdout(self):
        return self.process.stdout

    def stderr(self):
        return self.process.stderr

    def returncode(self):
        self.process.poll()
        return self.process.returncode

    def running(self):
        self.process.poll()
        return self.process.returncode is None

    def done(self):
        self.process.stdin.close()
        _end_process(self.process)

    def kill(self):
        self.done()
        self.process.kill()



class StreamingJSONProgramFailure(Exception):
    pass


class StreamingJSONProgram(object):

    """Interface to a program that repeatedly takes a single blob of
    delimited JSON and returns the same.  Should the program fail, a
    StreamingJSONProgramFailure exception (with explanation) will be
    thrown and an attempt to re-establish it will be made during the
    next call.

    This class is fully thread-safe.
    """

    def __init__(self, args, retries=3, timeout=None):
        """Construct an instance.

        Arguments:

        args - Array of program arguments
        retries - Number of times to try restarting the program before
            giving up.
        """

        self.args = args
        self.retries = retries
        self.timeout = timeout

        self.lock = threading.Lock()
        self.program = None
        self.emitter = None
        self.parser = None

        self.__establish()


    def __establish(self):
        """Start the program"""

        if self.program is not None:
            return

        self.program = ExternalProgram(self.args)
        self.emitter = RFC7464Emitter(self.program.stdin(),
                                      timeout=self.timeout)
        self.parser = RFC7464Parser(self.program.stdout(),
                                    timeout=self.timeout)


    def __call__(self, json):
        """Send the program a blob of JSON and get one back.
        Throws StopIteration if the program exits with EOF.
        """

        tries = self.retries

        with self.lock:

            while tries:

                tries -= 1

                self.__establish()

                try:
                    # These will throw an I/O error if they times out.
                    self.emitter(json)
                    return self.parser()
                except IOError as ex:
                    self.program.kill()
                    self.program = None
                    raise StreamingJSONProgramFailure(ex)
                except StopIteration:
                    rc = self.program.returncode()
                    # TODO: We seem to hit this a lot.
                    if rc is None:
                        rc = 1
                    err = self.program.stderr().read().strip()
                    self.done()
                    if tries > 0:
                        continue
                    raise StreamingJSONProgramFailure(
                        "Program exited %d: %s" % (rc, err))

                assert False, "Should not be reached."


    def done(self):
        if self.program is not None:
            self.program.done()
            self.program = None
