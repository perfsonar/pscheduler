"""
Identifier Class for ip-cymru-asn
"""

import dns
import ipaddress

from ...iso8601 import *
from ...jsonval import *
from ...pstime import *


data_validator = {
    "type": "object",
    "properties": {
        "asns": {
            "type": "array",
            "items": { "$ref": "#/pScheduler/Cardinal" }
        },
        "peers": { "$ref": "#/pScheduler/Boolean" },
        "timeout": { "$ref": "#/pScheduler/Duration" },
        "fail-result": { "$ref": "#/pScheduler/Boolean" }
    },
    "required": [ "fail-result" ]
}


def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return json_validate(data, data_validator)



class IdentifierIPCymruASN(object):

    """
    Identifier for matching requester IP ASNs
    """

    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.asns = dict((asn, True) for asn in data['asns'])
        self.peers = data.get('peers', False)

        try:
            timeout = iso8601_as_timedelta(data['timeout'])
            self.timeout = timedelta_as_seconds(timeout)
        except KeyError:
            self.timeout = 2

        try:
            self.fail_result = data['fail-result']
        except KeyError:
            self.fail_result = False

        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = self.timeout
        self.resolver.lifetime = self.timeout



    def evaluate(self,
                 hints  # Information used for doing identification
                 ):

        """Given a set of hints, evaluate this identifier and return True if
        an identification is made.

        """

        try:
            ip = hints['requester']
        except KeyError:
            return False

        octets = [ octet.decode("ascii")
                   for octet in dns.reversename.from_address(ip)[0:-3] ]
        host = '.'.join(octets)
        if self.peers:
            host += '.peer'
        else:
            host += '.origin' if len(octets) == 4 else '.origin6'
        host += ".asn.cymru.com"

        try:
            resolved = self.resolver.query(host, 'TXT')[0]
        except dns.resolver.NXDOMAIN:
            return False
        except (dns.exception.Timeout,
                dns.resolver.NoAnswer,
                dns.resolver.NoNameservers):
            return self.fail_result


        # The query will return one or more newline-separated strings
        # in this format:
        #   "ASN | CIDR | Country | Registrar | Date"
        #
        # For example:
        #   "23028 | 216.90.108.0/24 | US | arin | 1998-09-25"
        #
        # When querying peers, there will be multiple ASNs (e.g.,
        # 12345 6789 | ...).
        #
        # See https://team-cymru.com/community-services/ip-asn-mapping for more.

        # Split lines and strip quotes
        results = [ result[1:-1] for result in str(resolved).split("\n") ]

        # Split first section of each into ASNs
        result_asns = [ result.split(" | ")[0].split() for result in results ]

        # Flatten the list
        asns = [item for sublist in result_asns for item in sublist]

        for candidate_asn in asns:

            try:
                asn = int(candidate_asn)
            except ValueError:
                # Doesn't look like an integer.
                continue

            if asn in self.asns:
                return True

        # Nothing matched.
        return False
