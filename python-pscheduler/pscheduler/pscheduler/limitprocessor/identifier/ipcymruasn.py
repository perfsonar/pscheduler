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
        host += '.origin.asn.cymru.com' if len(octets) == 4 \
                else '.origin6.asn.cymru.com'

        try:
            resolved = self.resolver.query(host, 'TXT')[0]
        except dns.resolver.NXDOMAIN:
            return False
        except (dns.exception.Timeout,
                dns.resolver.NoAnswer,
                dns.resolver.NoNameservers):
            return self.fail_result

        # The query will return this in a string:
        #   "ASN | CIDR | Country | Registrar | Date"
        #
        # For example:
        #   "23028 | 216.90.108.0/24 | US | arin | 1998-09-25"
        #
        # See https://team-cymru.com/community-services/ip-asn-mapping for more.

        try:
            asn = int(str(resolved)[1:].split(" ")[0])
        except ValueError:
            # Doesn't look like an integer.
            return False

        # If it's in the list, it's a match.
        return asn in self.asns
