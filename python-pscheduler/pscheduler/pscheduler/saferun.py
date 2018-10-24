#
# Safe Lambda Runner
#

import os
import pickle
import pscheduler
import resource
import sys
import time

# Environment variable used to convey state between runs
STATE_VARIABLE = "PSCHEDULER_SAFERUN_STATE"

def safe_run(function,
             name=None,
             backoff=0.25,     # Backoff time increment
             backoff_max=60.0, # Longest allowable backoff
             restart=True      # Call again if the function returns
             ):
    """
    Safely call a long-running lambda (usually a main program),
    catching and logging exceptions.  If an exception is thrown, the
    calling program will be re-exec'd using the same arguments
    immediately if it simply returns or after a linearly-increasing
    backoff if it raises an exception.  The backoff always applies if
    the function has not yet run successfully and time will reset once
    the lambda runs any longer than the last backoff delay.
    """

    if not isinstance(function, type(lambda: 0)):
        raise ValueError("Function provided is not a lambda.")

    log = pscheduler.Log(name=name,
                         prefix='safe_run',
                         signals=False,
                         quiet=True
                         )

    # Inherit state from the environment

    if STATE_VARIABLE in os.environ:

        try:
            depickled = pickle.loads(os.environ[STATE_VARIABLE])

            initial_backoff = depickled['initial_backoff']
            assert type(initial_backoff) in [int, float]

            current_backoff = depickled['current_backoff']
            assert type(current_backoff) in [int, float]

            runs = depickled['runs']
            assert type(runs) == int

        except Exception as ex:
            log.error("Failed to decode %s '%s': %s"
                           % (STATE_VARIABLE, os.environ[STATE_VARIABLE], ex))
            exit(1)
    else:

        initial_backoff = backoff
        current_backoff = backoff
        runs = 0


    # Run the function

    do_restart = False

    try:
        started = pscheduler.time_now()
        function()
        runs += 1
        do_restart = restart

    except KeyboardInterrupt:
        pass

    except Exception as ex:
        ran = pscheduler.time_now() - started
        ran_seconds = pscheduler.timedelta_as_seconds(ran)

        log.error("Program threw an exception after %s", ran)
        log.exception()

        # Running longer than the backoff is a good excuse to try
        # starting over.
        if ran_seconds > current_backoff and runs != 0:
            currrent_backoff = initial_backoff
        else:
            log.error("Waiting %s seconds before restarting",
                      current_backoff)
            time.sleep(current_backoff)
            if current_backoff < backoff_max:
                current_backoff += initial_backoff

        do_restart = True

    if not do_restart:
        log.error("Exiting")
        exit(0)

    log.error("Restarting: %s", sys.argv)

    #
    # Pickle the current state to pass along
    #

    to_pickle = {
        'initial_backoff': initial_backoff,
        'current_backoff': current_backoff,
        'runs': runs
    }
    os.environ[STATE_VARIABLE] = pickle.dumps(to_pickle)

    # Close all open FDs other than stdin/stdout/stderr so they don't
    # get inherited by the exec'd process.
    # PORT: Make sure this is portable to OS X and elsewhere
    (file_max_soft, file_max_hard) = resource.getrlimit(resource.RLIMIT_NOFILE)
    os.closerange(sys.stderr.fileno() + 1, file_max_soft)

    os.execvp(sys.argv[0], sys.argv)



# Test program

if __name__ == "__main__":

    def foo():
        print "FOO"
        time.sleep(2)
        raise Exception("Yuck!")

    safe_run(foo, restart=False)
