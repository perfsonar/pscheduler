"""
Functions for resolving hostnames and IPs
"""

import dns.reversename
import dns.resolver 
import multiprocessing
import multiprocessing.pool


__TIMEOUT__ = 2


def __check_ip_version__(ip_version):
    if not ip_version in [4, 6]:
        raise ValueError("Invalid IP version; must be 4 or 6")


#
# Single Resolution
#

def dns_resolve(host, ip_version=4):
    """
    Resolve a hostname to its A record, returning None if not found
    """
    __check_ip_version__(ip_version)
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = __TIMEOUT__
        resolver.lifetime = __TIMEOUT__
        answers = resolver.query(host, 'A' if ip_version == 4 else 'AAAA')
        return str(answers[0])
    except dns.resolver.NXDOMAIN:
        return None


def dns_resolve_reverse(ip):
    """
    Resolve an IP (v4 or v6) to its hostname, returning None if not found.
    """
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = __TIMEOUT__
        resolver.lifetime = __TIMEOUT__
        revname = dns.reversename.from_address(ip)
        answers = resolver.query(revname, 'PTR')
        return str(answers[0])
    except dns.resolver.NXDOMAIN:
        return None
    except dns.exception.SyntaxError:
        return None



#
# Bulk Resolution
#


def __forwarder__(arg):
    """
    Query DNS for (name) and return (name, ip))
    """
    host, ip_version = arg
    return (host, dns_resolve(host, ip_version=ip_version))


def __reverser__(arg):
    """
    Query reverse DNS for (ip) and return (ip, hostname)
    """
    host, ip_version = arg
    return (host, dns_resolve_reverse(host))


def dns_bulk_resolve(candidates, reverse=False, ip_version=None, threads=50):
    """
    Resolve a list of host names to IPs or, if reverse is true, IPs to
    host names.  Return a map of each result keyed to its candidate.

    WARNING: This function will create a pool of up to 'threads'
    threads.
    """

    # This is based loosely on http://stackoverflow.com/a/34377198

    if reverse and ip_version is not None:
        raise ValueError("Unable to force IP version when reverse-resolving")

    if ip_version is None:
        ip_version = 4
    __check_ip_version__(ip_version)

    result = {}

    pool = multiprocessing.pool.ThreadPool(
        processes=min(len(candidates), threads) )

    candidate_args = [ (candidate, ip_version) for candidate in candidates ]

    for ip, name in pool.imap(
        __reverser__ if reverse else __forwarder__,
        candidate_args,
        chunksize=1):
        result[ip] = name
    pool.close()
    return result



if __name__ == "__main__":
    print dns_resolve('www.perfsonar.net', ip_version=4)
    print dns_bulk_resolve([
        'www.perfsonar.net',
        'www.es.net',
        'www.geant.org',
        'www.iu.edu',
        'www.internet2.edu',
        'does-not-exist.internet2.edu',
    ], ip_version=4)

    print dns_resolve('www.perfsonar.net', ip_version=6)
    print dns_bulk_resolve([
        'www.perfsonar.net',
    ], ip_version=6)


    print dns_bulk_resolve([
        '8.8.8.8',
        '198.6.1.1',
        '8.8.8.0',
        '2607:f8b0:4002:c06::67',
        'this-is-not-valid'
    ], reverse=True)
