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

def _is_link_local(ip):
    """
    Determine if an address (possibly with a %scope suffix) is link-local
    """
    try:
        return netaddr.IPAddress(ip.split('%')[0]).is_link_local()
    except (netaddr.AddrFormatError, ValueError):
        return False


def _get_ip_v4v6(addr):
    """
    Return the first IPv4 and the first IPv6 address that getaddrinfo()
    gives for addr, regardless of addr being a hostname or an IP.

    getaddrinfo() returns addresses in order of preference (RFC 6724),
    so the first address of each family is the one a client would use.
    When a name resolves to several addresses of the same family, for
    example a host's own name answered by systemd-resolved with every
    local address including a Docker bridge, the last one is not
    meaningful and may not be reachable from the other end.

    This is the same choice dns_resolve() makes, which takes the first
    result.

    When addr is a name, link-local addresses are handled as follows:

    - IPv4 link-local (169.254/16) is used only if the name has no
      other IPv4 address.  It works without a scope, e.g. for hosts
      cabled back to back.

    - IPv6 link-local (fe80::/10) is not used.  getaddrinfo() does not
      include the scope in the address string, so such an address
      cannot be used as a source, bind or destination address, and
      choosing it would also make IPv6 preferred over a usable IPv4
      address.

    A literal address is returned as given.
    """
    ip_v4 = None
    ip_v6 = None
    ll_v4 = None
    is_name = not is_ip(addr.split('%')[0])
    try:
        addrinfo = socket.getaddrinfo(addr, None)
        for ai in addrinfo:
            ip = ai[4][0]
            link_local = is_name and _is_link_local(ip)
            if ai[0] == socket.AF_INET:
                if link_local:
                    ll_v4 = ll_v4 or ip
                elif ip_v4 is None:
                    ip_v4 = ip
            elif ai[0] == socket.AF_INET6:
                if not link_local and ip_v6 is None:
                    ip_v6 = ip
    except:
        pass
    return ip_v4 or ll_v4, ip_v6


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
