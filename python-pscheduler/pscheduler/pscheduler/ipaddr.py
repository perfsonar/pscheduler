"""
Functions for handling IP addresses
"""

import netaddr

from psdns import *


def ip_addr_version(addr, resolve=True, timeout=dns_default_timeout()):
    """Determine what IP version an address, CIDR block or hostname
    represents.  When resolving hostnames to an IP, the search order
    will be A followed by AAAA.

    The returned tuple is (version, ip), where version is 4, 6 or None
    of nothing can be determined and ip is the ip address supplied or
    resolved.
    """

    # Chop out any CIDR suffix.

    slash_index = addr.rfind('/')
    if slash_index > 0:
        try:
            int(addr[slash_index + 1:])
            addr = addr[:slash_index]
        except ValueError:
            # Do nothing; will try to resolve if doing that.
            pass

    try:
        return (netaddr.IPAddress(addr).version, addr)
    except (netaddr.core.AddrFormatError, ValueError):
        # Don't care, will resolve.
        pass

    if not resolve:
        return (None, None)

    for ip_version in [4, 6]:
        resolved = dns_resolve(addr, ip_version=ip_version, timeout=timeout)
        if resolved is not None:
            return (ip_addr_version(resolved, resolve=False)[0], resolved)

    return (None, None)


#
# Find common IP version between two addresses

def _get_ip_v4v6(addr):
    # get ip addresses regardless of addr being hostname of ip
    ip_v4 = None
    ip_v6 = None
    try:
        addrinfo = socket.getaddrinfo(addr, None)
        for ai in addrinfo:
            if ai[0] == socket.AF_INET:
                ip_v4 = ai[4][0]
            elif ai[0] == socket.AF_INET6:
                ip_v6 = ai[4][0]
    except:
        pass
    return ip_v4, ip_v6


def ip_normalize_version(src, dest, ip_version=None):
    src_ip = None
    dest_ip = None
    src_ip_v4, src_ip_v6 = _get_ip_v4v6(src)
    dest_ip_v4, dest_ip_v6 = _get_ip_v4v6(dest)
    # prefer v6 if not specified
    if not ip_version or ip_version == 6:
        if src_ip_v6 and dest_ip_v6:
            src_ip = src_ip_v6
            dest_ip = dest_ip_v6
    if not src_ip or not dest_ip or ip_version == 4:
        if src_ip_v4 and dest_ip_v4:
            src_ip = src_ip_v4
            dest_ip = dest_ip_v4

    return src_ip, dest_ip


if __name__ == "__main__":

    for addr in [
            "127.0.0.1",
            "127.0.0.1/32",
            "127.0.0.1/quack",
            "::1",
            "::1/32",
            "::1/quack",
            "www.perfsonar.net",
            "ipv4.test-ipv6.com",
            "ipv6.test-ipv6.com"
    ]:
        print addr, "->", ip_addr_version(addr)
        print addr, "->", ip_addr_version(addr, resolve=False)
        print
