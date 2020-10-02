"""
Functions for diagnosing path MTU
"""

import netaddr
import re
import socket

from .ipaddr import ip_addr_version
from .program import run_program

mtu_match = re.compile("^.*pmtu ([0-9]+)")
hop_match = re.compile("^\s*[0-9]+\??:")


def mtu_path_is_safe(host, ipversion=None):

    """
    Using tracepath, check to see if the MTU along the path to 'host'
    gets any narrower than what it is locally.

    Set 'ipversion' to 4 or 6 to force a particular IP version.  If
    not provided, the function will try to figure it out using the
    resolver.

    Returns a tuple of (boolean, status message).
    """

    assert ipversion in [ 4, 6, None ], "Invalid IP version"

    if ipversion is None:
        (ipversion, message) = ip_addr_version(host)
        if ipversion is None:
            return (False, message)

    assert ipversion is not None, "No ip version; cannot proceed."

    if ipversion == 6:
        tracepath = "tracepath6"
    else:
        tracepath = "tracepath"

    status, stdout, stderr = run_program([tracepath, host], timeout=30)

    if status != 0:
        return(False, "Error: %s" % (stderr.strip()))

    mtus = []
    hops = 0

    for line in stdout.split("\n"):
        matches = mtu_match.match(line)
        if matches is not None:
            mtu = int(matches.groups()[0])
            mtus.append(mtu)

        matches = hop_match.match(line)
        if matches is not None:
            hops += 1

    if not mtus:
        return (False, "Found no MTU information in trace to %s" % (host))

    if hops == 1:
        return (True, "%d (Local)" % (mtus[0]))

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
        return (False, "MTU along path drops from %d to %s" % (
            initial_mtu, " to ".join(drops)))


    return (True, "%d+" % (initial_mtu))




if __name__ == "__main__":

    for pair in [
            ("localhost", None),
            ("dev6", 6),
            ("dev6v6", 6),
            ("www.perfsonar.net", None),
            ("badhost.perfsonar.net", None)
    ]:
        host, version = pair
        print(host, version, mtu_path_is_safe(host, ipversion=version))
