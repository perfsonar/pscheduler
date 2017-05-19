#
# Safe Lambda Runner
#

import pscheduler
import time


def safe_run(function,
             name=None,
             backoff=0.25,     # Backoff time increment
             backoff_max=60,   # Longest allowable backoff
             restart=True      # Call again if the function returns
             ):
    """
    Safely call a long-running lambda (usually a main program),
    catching and logging exceptions.  The lambda will be re-called
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

    initial_backoff = backoff
    current_backoff = backoff
    runs = 0

    while True:

        try:
            started = pscheduler.time_now()
            function()
            runs += 1
            if not restart:
                break

        except KeyboardInterrupt:
            break

        except Exception as ex:
            ran = pscheduler.time_now() - started
            ran_seconds = pscheduler.timedelta_as_seconds(ran)

            log.error("Program threw an exception after %s", ran)
            log.exception()

            # Running longer than the backoff is a good excuse to try
            # starting over.
            if ran_seconds > current_backoff and runs != 0:
                currrent_backoff = initial_backoff
                log.error("Restarting immediately.")
            else:
                log.error("Waiting %s seconds before restarting",
                          current_backoff)
                time.sleep(current_backoff)
                if current_backoff < backoff_max:
                    current_backoff += initial_backoff
                log.error("Restarting")


# Test program

if __name__ == "__main__":

    def foo():
        print "FOO"
        time.sleep(3)
        raise Exception("Yuck!")

    safe_run(lambda: foo(), restart=False)
