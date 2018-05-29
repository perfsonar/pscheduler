"""
Functions for diagnosing path MTU
"""

import re
from program import run_program

def mtu_path_is_safe(host):

    """
    Using tracepath, check to see if the MTU along the path to 'host'
    gets any narrower than what it is locally.

    Returns a tuple of (boolean, status message).
    """

    status, stdout, stderr = run_program(["tracepath", host], timeout=30)

    if status != 0:
        return(False, "Error: %s" % (stderr.strip()))

    mtu_match = re.compile("^.*pmtu ([0-9]+)")


    mtus = []
    for line in stdout.split("\n"):
        matches = mtu_match.match(line)
        if matches is not None:
            mtu = int(matches.groups()[0])
            mtus.append(mtu)

    if not mtus:
        return (False, "Found no MTU information in trace to %s" % (host))

    if len(mtus) == 1:
        return (False, "Found only one MTU in trace to %s" % (host))

    initial_mtu = mtus[0]
    last_low_mtu = initial_mtu
    drops = []

    for mtu in mtus[1:]:
        if mtu < last_low_mtu:
            drops.append(str(mtu))
            last_low_mtu = mtu

    if drops:
        return "MTU along path drops from %d to %s" % (
            initial_mtu, " to ".join(drops) )


    return (True, "%d+" % (initial_mtu))




if __name__ == "__main__":

    for host in [ "localhost", "www.perfsonar.net" ]:
        print host, mtu_path_is_safe(host)

