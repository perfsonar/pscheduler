#!/usr/bin/env python3
"""
Functions for running external programs neatly
"""

import atexit
import copy
import errno
import os
import psutil
import select
import stat
import subprocess
import sys
import tempfile
import threading
import traceback
import os

from shlex import quote

from .debuggable import *
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
    except SystemExit:
        pass
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
                    return (0 if timeout_ok else 2), None, "Process took too long to run."

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

            # Siphon off anything left on stdout and stderr

            while True:
                got_line = process.stdout.readline()
                if got_line == '':
                    break
                line_call(got_line[:-1])

            stderr += process.stderr.read()

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


class Program:
    
    def __init__(self, argv,              # Program name and args
                    stdin="",          # What to send to stdin
                    line_call=None,    # Lambda to call when a line arrives
                    timeout=None,      # Seconds
                    timeout_ok=False,  # Treat timeouts as not being an error
                    fail_message=None, # Exit with this failure message
                    env=None,          # Environment for new process, None=existing
                    env_add=None,      # Add hash to existing environment
                    attempts=10):      # Max attempts to start the process
        self._argv = argv
        self._stdin = stdin
        self._line_call = line_call
        self._timeout = timeout
        self._timeout_ok = timeout_ok
        self._fail_message = fail_message
        self._env = env
        self._env_add = env_add
        self._attempts = attempts
        self._module = sys.modules[__name__]
        self._lock = threading.Lock()
        self._terminating = False
        self._running = None
        self._process = None
        self._worker = None
        
        if [arg for arg in self._argv if arg is None]:
            raise Exception("Can't run with null arguments.")
        
        self._start_process()
        
    
    def terminate_early(self):
        if self._running is not None:
            self._terminate_running()
        else:
            print("No process to terminate")
            
    
    def _init_running(self):
        """Internal use:  Initialize the running hash if it isn't."""
        with self._lock:
            if self._running is None:
                self._running = {}
                on_graceful_exit(self._terminate_running)
    
    
    def _running_add(self, process):
        """Internal use:  Add a running process."""
        self._init_running()
        self._running[process] = 1

    
    def _terminate_running(self):
        """Internal use:  Terminate a running process."""
        self._init_running()
        while len(self._running) > 0:
            with self._lock:
                process = list(self._running.keys())[0]
            try:
                process.terminate()
                process.wait()
            except Exception:
                pass  # This is a best-effort effort.
            with self._lock:
                try:
                    del self._running[process]
                except KeyError:
                    pass  # Best effort.
    
        # Sometimes this gets called twice, so clean the list.
        self._running.clear()
    
    
    def _running_drop(self, process):
        """Internal use:  Drop a running process."""
        self._init_running()
        try:
            del self._running[process]
        except KeyError:
            pass
    
    
    def _line_worker(self):
        
        if not isinstance(self._line_call, type(lambda: 0)):
            raise ValueError("Function provided is not a lambda.")
        
        if self.stdin is not None:
            self._process.stdin.write(self._stdin)
        self._process.stdin.close()
        
        stderr = ''
        
        stdout_fileno = self._process.stdout.fileno()
        stderr_fileno = self._process.stderr.fileno()
        
        fds = [stdout_fileno, stderr_fileno]
        
        if self._timeout is not None:
            end_time = time_now() \
                + seconds_as_timedelta(self._timeout)
        else:
            time_left = None
        
        while True: 
            if self._timeout is not None:
                time_left = timedelta_as_seconds(
                    end_time - time_now())
            
            reads, _, _ = polled_select(fds, [], [], time_left)
            
            if len(reads) == 0:
                self._running_drop(self._process)
                _end_process(self._process)
                return (0 if self._timeout_ok else 2), None, "Process took too long to run."
            
            for readfd in reads:
                if readfd == stdout_fileno:
                    got_line = process.stdout.readline()
                    if got_line != '':
                        line_call(got_line[:-1])
                elif readfd == stderr_fileno:
                    got_line = self._process.stderr.readline()
                    if got_line != '':
                        stderr += got_line
            
            if self._process.poll() != None:
                break
    
    
    def _start_process(self):
        # Build up a new, incorruptable copy of the environment for the
        # child process to use.
        
        if self._env_add is None:
            env_add = {}
        
        if self._env is None and len(env_add) == 0:
            new_env = None
        else:
            new_env = (os.environ if self._env is None else self._env).copy()
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
            self._process = __get_process(self._argv, new_env, self._attempts)
            self._running_add(process)
            
        except Exception as ex:
            extype, _, trace = sys.exc_info()
            status = 2
            stdout = ''
            stderr = ''.join(traceback.format_exception_only(extype, ex)) \
                + ''.join(traceback.format_exception(extype, ex, trace)).strip()
        
        if self._line_call is not None:
            # i think this will have to be factored out and moved beneath line call worker *function*
            self._worker = threading.Thread(target=self._line_worker)
            
            
    def join(self):
        try:
            if self._line_call is None:
            
                # Single-shot I/O with optional timeout
            
                try:
                    stdout, stderr = self._process.communicate(self._stdin, timeout=self._timeout)
                    status = self._process.returncode
            
                except subprocess.TimeoutExpired:
                    _end_process(self._process)
                    status = 0 if self._timeout_ok else 2
                    stdout = ''
                    stderr = "Process took too long to run."
            else:
                self._worker.join()
            
                while True:
                    got_line = self._process.stdout.readline()
                    if got_line == '':
                        break
                    line_call(got_line[:-1])
            
                stderr += self._process.stderr.read()
            
                self._process.wait()
            
                status = self._process.returncode
                stdout = None
        
        except Exception as ex:
            extype, _, trace = sys.exc_info()
            status = 2
            stdout = ''
            stderr = ''.join(traceback.format_exception_only(extype, ex)) \
                + ''.join(traceback.format_exception(extype, ex, trace)).strip()
        
        if process is not None:
            self._running_drop(process)
            _end_process(process)
        
        if self._fail_message is not None and status != 0:
            fail("%s: %s" % (self._fail_message, stderr))
       
        return status, stdout, stderr
        
        
    def kill(self, timeout):
        try:
            self._process.terminate()
            self._process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()

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
                os.unlink(remove)
            except IOError:
                pass  # This is best effort only.

        return result




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
        self.pid = self.process.pid
        self.returned_code = None
        self.err = None

    def stdin(self):
        return self.process.stdin

    def stdout(self):
        return self.process.stdout

    def stderr(self):
        return self.process.stderr

    def returncode(self):
        if self.returned_code is None:
            self.process.poll()
            self.returned_code = self.process.returncode
        return self.returned_code

    def running(self):
        try:
            process = psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            return False

        if process.status() == psutil.STATUS_ZOMBIE:
            _unused = self.returncode()
            return False

        if process.status() == psutil.STATUS_DEAD:
            return False

        return self.returned_code is None

    def done(self):
        self.process.poll()
        try:
            _end_process(self.process)
        except AttributeError:
            pass   # Not there?  Don't care.


    def __del__(self):
        self.done()






class StreamingJSONProgramFailure(Exception):
    pass


class StreamingJSONProgram(Debuggable):

    """
    Interface to a program that repeatedly takes a single blob of RFC
    7464-delimited JSON and returns the same.  Should the program fail
    more than the specified number of times, a StreamingJSONProgramFailure
    exception (with explanation) will be thrown.

    This class is fully thread-safe.
    """

    def __init__(self, args, retries=3, timeout=None, debug=lambda s: None, label=None):
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

        super().__init__(debug, label=label if label else args[0])

        self.__establish()

    def __establish(self):
        """Start the program"""

        if self.program is not None:
            if self.program.running():
                return
            else:
                del self.program
                # TODO: Not strictly necessary.
                self.program = None

        # At this point, there is no program.

        self.debug("Starting program %s", self.args)
        self.program = ExternalProgram(self.args)
        self.emitter = RFC7464Emitter(self.program.stdin(), timeout=self.timeout)
        self.parser = RFC7464Parser(self.program.stdout(), timeout=self.timeout)
        self.debug("Program is running")


    def __roundtrip(self, json):
        """
        Do a full round trip to the program and return the result.  If the
        program died in the middle, throw an exception.
        """

        self.__establish()

        result = None

        try:
            self.emitter(json)
            result = next(self.parser)

            if (result is None) and (not self.program.running()):
                raise IOError("Program exited unexpectedly.")

        except IOError as ex:
            self.debug("Exception: %s", ex)
            self.done()
            raise ex

        except StopIteration:
            rc = self.program.returncode()
            # TODO: We seem to hit this a lot.
            if rc is None:
                rc = 1
            err = self.program.stderr().read().strip()
            self.debug("Exited with %s.  Stderr = %s", rc, err)
            self.done()
            raise IOError("Program exited %d: %s" % (rc, err))

        except Exception as ex:
            # Anything else is just bad.
            self.done()
            raise StreamingJSONProgramFailure(str(ex))

        return result
        

    def __call__(self, json):

        """Send the program a blob of JSON and get one back.
        Throws StopIteration if the program exits with EOF.
        """

        tries = self.retries
        exception = None

        with self.lock:
            while tries:

                tries -= 1

                try:
                    return self.__roundtrip(json)
                except IOError as ex:
                    if tries:
                        self.debug("I/O error.  Trying again.")
                        continue
                    else:
                        self.debug("Giving up")
                        exception = ex

            # If we fell out of the loop, we ran out of tries and
            # should have an exception to report.  Don't do this
            # inside the catch above because it makes the error
            # messages confusing.

            assert not tries, "Should have no tries left."
            assert exception is not None, "Should have an exception"

            raise StreamingJSONProgramFailure(
                "Program failed to start after %d tries: %s"
                % (self.retries, exception))


    def running(self):
        return self.program.running()


    def done(self):
        if self.program is not None:
            self.program.done()
            del self.program
            self.program = None
