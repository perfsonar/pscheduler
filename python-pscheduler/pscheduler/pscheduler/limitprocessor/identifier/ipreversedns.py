"""
Identifier Class for ip-reverse-dns
"""

import dns
import ipaddress
import re
import sre_constants

from ...iso8601 import *
from ...psjson import *
from ...pstime import *
from ...stringmatcher import *


data_validator = {
    "type": "object",
    "properties": {
        "match": { "$ref": "#/pScheduler/StringMatch" },
        "timeout": { "$ref": "#/pScheduler/Duration" }
    },
    "additionalProperties": False,
    "required": [ "match", "timeout" ]
}

def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return json_validate(data, data_validator)



class IdentifierIPReverseDNS(object):


    """
    Class that does reverse DNS identification
    """


    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.matcher = StringMatcher(data['match'])

        timeout = timedelta_as_seconds(
            iso8601_as_timedelta(data['timeout']))

        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout




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

        addr = ipaddress.ip_address(str(ip))

        ip_reverse = dns.reversename.from_address(ip)

        # Resolve to a FQDN

        try:
            reverse = str(self.resolver.query(ip_reverse, 'PTR')[0])
        except (dns.resolver.NXDOMAIN,
                dns.exception.Timeout,
                dns.resolver.NoAnswer,
                dns.resolver.NoNameservers):
            return False

        # Resolve the FQDN back to an IP and see if they match.  This
        # prevents someone in control over their reverse resolution
        # from claiming they're someone they're not.

        # TODO: Check against _all_ returned IPs

        record = 'A' if addr.version == 4 else 'AAAA'
        try:
            forwards = self.resolver.query(reverse, record)
        except (dns.resolver.NXDOMAIN,
                dns.exception.Timeout,
                dns.resolver.NoAnswer,
                dns.resolver.NoNameservers):
            return False

        if ip not in [ str(f) for f in forwards ]:
            return False

        # Try to match with and without the dot at the end.

        for reverse_candidate in [ reverse, reverse.rstrip('.') ]:
            if self.matcher.matches(reverse_candidate):
                return True


        # No match, no dice.
        return False
