"""
Functions for handling IP addresses
"""

import netaddr
import socket

from .psdns import *


def is_ip(addr):
    """
    Determine if an address looks like IPv4 or IPv6
    """
    for family in [socket.AF_INET, socket.AF_INET6]:
        try:
            socket.inet_pton(family, addr)
            return True
        except socket.error:
            pass

    return False




# Map of IP versions to socket address families
__ip_families = {
    4: socket.AF_INET,
    6: socket.AF_INET6
}

# Map of socket address families to IP versions
__ip_versions = {
    socket.AF_INET: 4,
    socket.AF_INET6: 6
}


def ip_addr_version(addr,
                    resolve=True,
                    ip_version=None,
                    family=False,
                    timeout=dns_default_timeout()):
    """Determine what IP version an address, CIDR block or hostname
    represents.  When resolving hostnames to an IP, the system search
    order will be A followed.

    The returned tuple is (version, ip), where version is 4, 6 or None
    of nothing can be determined and ip is the ip address supplied or
    resolved.

    If 'ip_version' is 4 or 6, only that version will be used attempting
    to do resolutions.

    If 'family' is True, the returned version will be the address
    family as defined by the socket module.

    """

    assert addr is not None
    assert isinstance(addr, str)
    assert ip_version in [None, 4, 6]


    # Chop out any CIDR suffix.

    slash_index = addr.find('/')
    if slash_index > 0:
        try:
            int(addr[slash_index + 1:])
            addr = addr[:slash_index]
        except ValueError:
            # DNS resolution will torpedo this.
            pass

    # If it looks like an IP address, act on it, but only if it's the
    # version requested.

    try:
        addr_version = netaddr.IPAddress(addr).version

        # Version mismatches are bad.
        if ip_version is not None and addr_version != ip_version:
            return (None, None)

        if family:
            addr_version = __ip_families[addr_version]

        return (addr_version, addr)

    except (netaddr.core.AddrFormatError, ValueError):
        # Don't care, will resolve.
        pass

    if not resolve:
        return (None, None)

    # Try to figure it out by resolution.

    ipversion = None

    try:

        # This will return the preferred address family first.
        # Use that.
        addrinfo = socket.getaddrinfo(addr, None)
        for info in addrinfo:
            try:
                ipversion = info[0]
                break
            except KeyError:
                continue

    except socket.gaierror as ex:
        (err, string) = ex.args
        return (None, string)

    if ipversion is None:
        return (None, "Unable to resolve '%s' or find a supported IP version" % (host))

    version_list = [4, 6] if ip_version is None else [ip_version]

    for ip_version in version_list:
        resolved = dns_resolve(addr, ip_version=ip_version, timeout=timeout)
        if resolved is not None:
            return (ip_addr_version(resolved, resolve=False,
                                    family=family)[0], resolved)

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
    if ip_version == 6:
        src_ip = src_ip_v6
        dest_ip = dest_ip_v6
    elif ip_version == 4:
        src_ip = src_ip_v4
        dest_ip = dest_ip_v4
    elif src_ip_v6 and dest_ip_v6:
        src_ip = src_ip_v6
        dest_ip = dest_ip_v6
    elif src_ip_v4 and dest_ip_v4:
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
        print(addr, "->", ip_addr_version(addr))
        print(addr, "->", ip_addr_version(addr, resolve=False))
        print()
