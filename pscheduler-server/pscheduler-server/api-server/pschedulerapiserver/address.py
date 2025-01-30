#
# Address Functions
#

from flask import request


def _clean_address(address):
    """
    Remove scope (e.g., '1234::5%eth0') from an IP address.  Does not
    apply to IPv4s but is safe to apply.
    """
    return address.split(sep='%', maxsplit=1)[0]


def remote_address():
    """Return a cleaned version of the remote address"""
    return _clean_address(request.remote_addr)
