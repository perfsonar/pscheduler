"""
Functions for diagnosing path MTU
Fix https://github.com/perfsonar/pscheduler/issues/1588
"""

import netaddr
import re
import socket

from .ipaddr import ip_addr_version
from .program import run_program

def find_last_hop(hops):
    null_hop_pattern = r'^\s?\d+\s+\*'
    for hop in reversed(hops):
        match = re.search(null_hop_pattern, hop)

        if match:
            continue
        else:
            return hop



def extract_ip(input_string):
    """
    Extracts the first string surrounded by parentheses in the input string: the ip in the first line of traceroute output.
    """
    pattern = r'\((.*?)\)'

    match = re.search(pattern, input_string)

    if match:
        # Group 1 (match.group(1)) contains the content captured inside the inner parentheses
        return match.group(1)
    else:
        return None

def check_host_in_hop(input_string, host):
    """
    Checks if the input_string starts with:
    space + [one or more digits] + [one or more spaces] + [host string] + [one or more spaces]
    
    Args:
        input_string (str): The string to search within.
        host (str): The specific string content to match (e.g., an IP or domain).
        
    Returns:
        bool: True if the pattern is found at the beginning, False otherwise.
    """
    escaped_host = re.escape(host)
    pattern = rf'^\s?\d+\s+{escaped_host}\s+'
    

    if re.search(pattern, input_string):
        return True
    else:
        return False


def mtu_traceroute(host,
                   ip_version=None,
                   bind=None,
                   max_hops=30,
                   hop_time=2
                   ):
    '''
    Determine MTU using traceroute

    Returns a tuple of (MTU, All-MTUs, NumHops, Message).  MTU will be
    None if none was determined.  All-MTUs is a list of MTUs in the
    order encountered.

    '''

    assert isinstance(host, str), "host must be a string"
    assert ip_version in [ None, 4, 6 ], "ip_version must be None, 4 or 6"
    assert bind is None or isinstance(bind, str), "bind must be a string"
    assert isinstance(max_hops, int), "max_hops must be an integer"
    assert isinstance(hop_time, int), "hop_timemust be an integer"

    args = [
        'traceroute',
        '-n',
        '-q', '1',
        '-m', max_hops,
        '-w', hop_time,
        '--mtu',
    ]

    if bind is not None:
        args += ['-s', bind]

    if ip_version is not None:
        args.append(f'-{ip_version}')

    args.append(host)

    status, stdout, stderr = run_program(
        [ str(arg) for arg in args ],
        timeout=(max_hops * hop_time)+5
    )

    if status != 0:
        return (None, None, None, f'Failed to measure MTU: {stderr}')

    size_matcher = re.compile(r'traceroute to\s.*\s([0-9]+)\s+byte packets')
    hop_matcher = re.compile(r'^\s+[0-9]+\s')
    mtu_matcher = re.compile(r'(?<=F=)[0-9]+')
    
    packet_size = None
    all_mtus = []
    min_mtu = None
    hops = 0
    lines =  stdout.split('\n')

    last_hop = ""

    for line in lines:

        size_match = size_matcher.search(line)
        if size_match:
            packet_size = int(size_match.group(1))
            continue

        hop_match = hop_matcher.search(line)
        if hop_match:
            hops += 1

        match = mtu_matcher.search(line)
        if match is None:
            continue

        hop_mtu = int(match.group(0))
        all_mtus.append(hop_mtu)

        try:
            min_mtu = min(min_mtu, hop_mtu)
        except TypeError:
            # Tried to comare with None, so this is the first.
            min_mtu = hop_mtu

    # If no MTUs were reported, do a best guess

    dest_ip = extract_ip(lines[0])

    if  hops > 0:
        #last_hop = lines[-2]
        last_hop = find_last_hop(lines[0:-1])
        if check_host_in_hop(last_hop, dest_ip) is True:
            return (min_mtu, all_mtus, hops, 'OK')
        else:
            return(None, None, hops, f"Destination |{dest_ip}| must be the last hop --- Possible PMTUD failure in |{last_hop}|")

    if min_mtu is None:
        if packet_size is not None and hops == 1:
            # One hop, likely local
            return (packet_size, [packet_size], hops, 'Path looks local.')
        else:
            # No clue at all about MTU.  Punt
            return (None, None, hops, 'Found no MTU for path.')

    return (min_mtu, all_mtus, hops, 'OK')


def mtu_path_is_safe(host, ipversion=None):
    """
    Using tracepath, check to see if the MTU along the path to 'host'
    gets any narrower than what it is locally.

    Set 'ipversion' to 4 or 6 to force a particular IP version.  If
    not provided, the function will try to figure it out using the
    resolver.

    Returns a tuple of (boolean, status message).
    """

    (mtu, mtus, num_hops, message) = mtu_traceroute(host, ip_version=ipversion)

    if num_hops is not None and num_hops == 1:
        return(True, 'N/A (Local)')

    if mtu is None:
        return (False, message)

    initial_mtu = mtus[0]

    if len(mtus) == 1:
        return (True, str(initial_mtu))

    last_low_mtu = initial_mtu
    drops = []

    for mtu in mtus[1:]:
        if mtu < last_low_mtu:
            drops.append(str(mtu))
            last_low_mtu = mtu

    if drops:
        return (False, "MTU along path drops from %d to %s" % (
            initial_mtu, " to ".join(drops)))

    return (True, f'{initial_mtu}+')




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
