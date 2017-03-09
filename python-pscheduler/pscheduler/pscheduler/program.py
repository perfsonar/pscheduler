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

this = sys.modules[__name__]
this.running = None

def __terminate_running():
    """Internal use:  Terminate a running process."""
    __init_running()
    for process in this.running:
        try:
            process.terminate()
        except Exception:
            pass  # This is a best-effort effort.
    # Sometimes this gets called twice, so clean the list.
    this.running.clear()


def __init_running():
    """Internal use:  Initialize the running hash if it isn't."""
    if this.running is None:
        this.running = {}
        atexit.register(__terminate_running)

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





# Only used in _Popen
import errno
import os

class _Popen(subprocess32.Popen):
    """
    Improved version of subprocess32's Popen that handles SIGPIPE
    without throwing an exception.
    """

    def _communicate_with_poll(self, input, endtime, orig_timeout):

        # This is just to maintain the indentation of the original.
        if True:

            stdout = None # Return
            stderr = None # Return

            if not self._communication_started:
                self._fd2file = {}

            poller = select.poll()
            def register_and_append(file_obj, eventmask):
                poller.register(file_obj.fileno(), eventmask)
                self._fd2file[file_obj.fileno()] = file_obj

            def close_unregister_and_remove(fd):
                poller.unregister(fd)
                self._fd2file[fd].close()
                self._fd2file.pop(fd)

            if self.stdin and input:
                register_and_append(self.stdin, select.POLLOUT)

            # Only create this mapping if we haven't already.
            if not self._communication_started:
                self._fd2output = {}
                if self.stdout:
                    self._fd2output[self.stdout.fileno()] = []
                if self.stderr:
                    self._fd2output[self.stderr.fileno()] = []

            select_POLLIN_POLLPRI = select.POLLIN | select.POLLPRI
            if self.stdout:
                register_and_append(self.stdout, select_POLLIN_POLLPRI)
                stdout = self._fd2output[self.stdout.fileno()]
            if self.stderr:
                register_and_append(self.stderr, select_POLLIN_POLLPRI)
                stderr = self._fd2output[self.stderr.fileno()]

            # Save the input here so that if we time out while communicating,
            # we can continue sending input if we retry.
            if self.stdin and self._input is None:
                self._input_offset = 0
                self._input = input
                if self.universal_newlines and isinstance(self._input, unicode):
                    self._input = self._input.encode(
                            self.stdin.encoding or sys.getdefaultencoding())

            while self._fd2file:
                try:
                    ready = poller.poll(self._remaining_time(endtime))
                except select.error, e:
                    if e.args[0] == errno.EINTR:
                        continue
                    raise
                self._check_timeout(endtime, orig_timeout)

                for fd, mode in ready:
                    if mode & select.POLLOUT:
                        chunk = self._input[self._input_offset :
                                            self._input_offset
                                            + subprocess32._PIPE_BUF]

                        # Handle EPIPE, because having this module
                        # restore the signals doesn't seem to work.

                        try:
                            self._input_offset += os.write(fd, chunk)
                            if self._input_offset >= len(self._input):
                                close_unregister_and_remove(fd)
                        except OSError as ex:
                            if ex.errno != errno.EPIPE:
                                raise ex
                            close_unregister_and_remove(fd)

                    elif mode & select_POLLIN_POLLPRI:
                        data = os.read(fd, 4096)
                        if not data:
                            close_unregister_and_remove(fd)
                        self._fd2output[fd].append(data)
                    else:
                        # Ignore hang up or errors.
                        close_unregister_and_remove(fd)

            return (stdout, stderr)




def run_program(argv,              # Program name and args
                stdin=None,        # What to send to stdin
                line_call=None,    # Lambda to call when a line arrives
                timeout=None,      # Seconds
                short=False,       # Force timeout to two seconds
                timeout_ok=False,  # Treat timeouts as not being an error
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

    if short:
        timeout = 2

    process = None

    if [arg for arg in argv if arg is None]:
        raise Exception("Can't run with null arguments.")

    try:
        process = _Popen(argv,
                         stdin=subprocess32.PIPE,
                         stdout=subprocess32.PIPE,
                         stderr=subprocess32.PIPE)


        __running_add(process)

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
                end_time = pscheduler.time_now() \
                           + pscheduler.seconds_as_timedelta(timeout)
            else:
                time_left = None

            while True:

                if timeout is not None:
                    time_left = pscheduler.timedelta_as_seconds(
                        end_time - pscheduler.time_now())

                reads, _, _ = select.select(fds, [], [], time_left)

                if len(reads) == 0:
                    __running_drop(process)
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

    if fail_message is not None and status != 0:
        pscheduler.fail("%s: %s" % (fail_message, stderr))

    return status, stdout, stderr



if __name__ == "__main__":

    def dump_result(title, tup):
        """Spit out a run result"""
        print
        print "#\n# %s\n#" % (title)
        (status, stdout, stderr) = tup
        print "Exited", status
        print "Stdout", stdout
        print "Stderr", stderr

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

        print "Lines:"
        print "\n".join(["  %s" % (line) for line in lines])


    if do_all or False:
        inp = "\n".join([str(number) for number in range(1, 1000000)])
        dump_result(
            "Induced pipe error (Should show no errors)",
            run_program(
                ['head', '-10'],
                stdin=inp
            ))
