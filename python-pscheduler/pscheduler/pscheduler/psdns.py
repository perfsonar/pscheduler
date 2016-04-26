"""
Functions for resolving hostnames and IPs
"""

import dns.reversename
import dns.resolver 
import multiprocessing
import multiprocessing.pool


__TIMEOUT__ = 2


def __forwarder__(arg):
    """
    Query DNS for (name) and return (name, ip))
    """
    name = arg
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = __TIMEOUT__
        resolver.lifetime = __TIMEOUT__
        answers = resolver.query(name, 'A')
        return (name, str(answers[0]))
    except dns.resolver.NXDOMAIN:
        return (name, None)


def __reverser__(arg):
    """
    Query reverse DNS for (ip) and return (ip, hostname)
    """
    ip = arg
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = __TIMEOUT__
        resolver.lifetime = __TIMEOUT__
        revname = dns.reversename.from_address(ip)
        answers = resolver.query(revname, 'PTR')
        return (ip, str(answers[0]))
    except dns.resolver.NXDOMAIN:
        return (ip, None)


def dns_bulk_resolve(candidates, reverse=False, threads=50):
    """
    Resolve a list of host names to IPs or, if reverse is true, IPs to
    host names.  Return a map of each result keyed to its candidate.

    WARNING: This function will create a pool of up to 'threads'
    threads.
    """

    result = {}

    pool = multiprocessing.pool.ThreadPool(
        processes=min(len(candidates), threads) )

    for ip, name in pool.imap(
        __reverser__ if reverse else __forwarder__,
        candidates,
        chunksize=1):
        result[ip] = name
    pool.close()
    return result



if __name__ == "__main__":
    print dns_bulk_resolve([
            'www.perfsonar.net',
            'www.es.net',
            'www.geant.org',
            'www.iu.edu',
            'www.internet2.edu'
            ])

    print dns_bulk_resolve([
            '8.8.8.8',
            '198.6.1.1',
            '8.8.8.0'
            ], reverse=True)
