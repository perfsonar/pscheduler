"""
Functions for bulk-resolving AS numbers from IPs
"""

import multiprocessing
import multiprocessing.pool
import netaddr

from psdns import dns_resolve


def __asresolve__(arg):
    """
    Query Cymru for AS information, ignoring non-unicast and private
    IPs.
    """

    # Fish out the ASN

    try:
        ip = netaddr.IPAddress(arg)
    except netaddr.core.AddrFormatError:
        return (arg, None)

    # Don't try for things that are unroutable
    if not ip.is_unicast() or ip.is_private():
        return (arg, None)

    revoctets =  ip.reverse_dns.split('.')
    reverse_type = revoctets[-3]
    revoctets = revoctets[:-3]

    if reverse_type == 'in-addr':
        suffix = '.origin.asn.cymru.com.'
    elif reverse_type == 'ip6':
        suffix = '.origin6.asn.cymru.com.'
    else:
        raise Exception("Unsupported IP format")

    ip_returned = dns_resolve('.'.join(revoctets) + suffix, query='TXT')
    if ip_returned is None:
        return (arg, None)

    asn = ip_returned[1:].split(' | ')[0]

    # Determine the owner

    owner_returned = dns_resolve('AS' + asn + '.asn.cymru.com', query='TXT')
    if owner_returned is not None:
        owner = owner_returned.split(' | ')[-1][:-1]
    else:
        owner = None

    return (arg, (int(asn), owner))



def as_bulk_resolve(candidates, threads=50):
    """
    Resolve a list of IPs to AS information.

    Returns a map of each result as a tuple of (ASN, owner) keyed to
    its candidate.  Returns None if no ASN could be found or (ASN,
    None) if an ASN was found but no owner is available.

    WARNING: This function will create a pool of up to 'threads'
    threads.
    """

    result = {}

    pool = multiprocessing.pool.ThreadPool(
        processes=min(len(candidates), threads) )

    for ip, as_ in pool.imap(
        __asresolve__,
        candidates,
        chunksize=1):
        result[ip] = as_
    pool.close()
    return result



if __name__ == "__main__":

    print as_bulk_resolve([
        '8.8.8.8',
        '198.6.1.1',
        '8.8.8.0',
        '2607:f8b0:4002:c06::67',
        'this-is-not-valid',
        '192.168.1.1',
    ])
