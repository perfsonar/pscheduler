"""
Function to parse output of a ping command.
Takes the output of the command, which will probably come from
stdout when using pscheduler.run_program.
"""
from .iso8601 import *
import re

def parse_ping(output, count):
    """
    Parse the results of a ping based on the output of a ping
    and the count of how many pings were sent.
    Returns a dictionary:
        "roundtrips": a list of roundtrip times and stats for each ping
        "ips": a list of ips
        "min", "max", "mean", "stddev": stats for all pings
    """

    #
    # Matchers for output lines we care about
    #

    PACKET_RETURNED = re.compile("^([0-9]+) bytes"
    "\s+from (.*):"
    "\s+icmp_[rs]eq=([0-9]+)"
    "\s+ttl=([0-9]+)"
    "\s+time=([0-9.]+) ms"
    "$")

    # Error:   From 5.6.7.8 icmp_seq=7 Destination Net Unreachable

    ERROR_RETURNED = re.compile("^From"
    "\s+([^\s]+)"
    "\s+icmp_seq=([0-9]+)"
    "\s+(.*)"
    "$")

    # Error messages known to be output by ping
    ERROR_STRINGS = {
        "Destination Net Unreachable": 'net-unreachable',
        "Destination Host Unreachable": 'host-unreachable',
        "Destination Protocol Unreachable": 'protocol-unreachable',
        "Destination Port Unreachable": 'port-unreachable',
        "Source Route Failed": 'source-route-failed',
        "Packet filtered": 'communication-administratively-prohibited',
        }

    # Same, but require regexps to match
    ERROR_MATCHES = [
        ( re.compile("^Frag needed and DF set"), 'fragmentation-needed-and-df-set' )
        ]

    # Times:   rtt min/avg/max/mdev = 19.631/24.191/29.874/4.262 ms
    TIMES_RETURNED = re.compile("^rtt min/avg/max/mdev\s*=\s*"
    "([0-9.]+)"
    "/([0-9.]+)"
    "/([0-9.]+)"
    "/([0-9.]+)"
    "\s+ms$")

    roundtrips = []
    ips = []

    rtt_min = None
    rtt_mean = None
    rtt_max = None
    rtt_stddev = None

    for line in output.split('\n'):
        line = line.strip()

        # Returned Packet

        matches = PACKET_RETURNED.match(line)
        if matches is not None:
            length, ip, seq, ttl, rtt = matches.groups()
            length = int(length)
            seq = int(seq)
            ttl = int(ttl)
            rtt = float(rtt)
            if seq > count:
                continue

            # Under some conditions, ping6 returns the interface with the
            # IP.  Remove that.
            ip = ip.split("%")[0]

            #append as we may get multiple of same seq (duplicates) or seq out of order (reorders)
            roundtrips.append({
                'seq': seq,
                'length': length,
                'ip': ip,
                'ttl': ttl,
                'rtt': timedelta_as_iso8601(
                    datetime.timedelta(seconds=rtt/1000.0) )
                })
            ips.append(ip)
            continue

        # Error

        matches = ERROR_RETURNED.match(line)
        if matches is not None:
            ip, seq, error = matches.groups()
            seq = int(seq)
            if seq > count:
                continue

            if error in ERROR_STRINGS:
                error = ERROR_STRINGS[error]
            else:
                error_str = error
                error = None
                for regex, string in ERROR_MATCHES:
                    if regex.match(error_str):
                        error = string
                        break

            roundtrips.append({
                'seq': seq,
                'ip': ip,
                'error': error
                })
            ips.append(ip)
            continue

        # Error

        matches = ERROR_RETURNED.match(line)
        if matches is not None:
            ip, seq, error = matches.groups()
            seq = int(seq)
            if seq > count:
                continue

            if error in ERROR_STRINGS:
                error = ERROR_STRINGS[error]
            else:
                error_str = error
                error = None
                for regex, string in ERROR_MATCHES:
                    if regex.match(error_str):
                        error = string
                        break

            roundtrips.append({
                'seq': seq,
                'ip': ip,
                'error': error
                })
            ips.append(ip)
            continue

        # Final times
        matches = TIMES_RETURNED.match(line)
        if matches is not None:
            rtt_min, rtt_mean, rtt_max, rtt_stddev = matches.groups()
            # This is the last line we care about.
            break

        # Anything else we just ignore.

    summary_results = {
        'roundtrips': roundtrips,
        'ips': ips
    }

    if rtt_min is not None:
        summary_results['min'] = timedelta_as_iso8601(
            datetime.timedelta(seconds=float(rtt_min)/1000.0))

    if rtt_max is not None:
        summary_results['max'] = timedelta_as_iso8601(
            datetime.timedelta(seconds=float(rtt_max)/1000.0))

    if rtt_mean is not None:
        summary_results['mean'] = timedelta_as_iso8601(
            datetime.timedelta(seconds=float(rtt_mean)/1000.0))

    if rtt_stddev is not None:
        summary_results['stddev'] = timedelta_as_iso8601(
            datetime.timedelta(seconds=float(rtt_stddev)/1000.0))

    return summary_results
