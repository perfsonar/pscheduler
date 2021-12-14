"""
Identifier Class for ip-cymru-bogon
"""

import dns
import ipaddress

from ...iso8601 import *
from ...jsonval import *
from ...pstime import *


data_validator = {
    "type": "object",
    "properties": {
        "exclude": {
            "type": "array",
            "items": { "$ref": "#/pScheduler/IPCIDR" }
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



class IdentifierIPCymruBogon(object):

    """
    Identifier for finding bogons/martians via DNS
    """

    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.exclude = [ ipaddress.ip_network(str(addr))
                         for addr in data['exclude'] ]

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
        host += '.v4.fullbogons.cymru.com' if len(octets) == 4 \
                else '.v6.fullbogons.cymru.com'

        # The query for this is always for an 'A' record, even for
        # IPv6 hosts.

        try:
            resolved = self.resolver.query(host, 'A')[0]
        except dns.resolver.NXDOMAIN:
            return False
        except (dns.exception.Timeout,
                dns.resolver.NoAnswer,
                dns.resolver.NoNameservers,
                # This happens if there's something wrong with the reply.
                dns.exception.SyntaxError
        ):
            return self.fail_result

        # The query will return 127.0.0.2 if it's in the bogon list.
        # See http://www.team-cymru.org/bogon-reference-dns.html.

        if str(resolved) != '127.0.0.2':
            return False

        # At this point, we have a bogon.  Filter out exclusions.

        net_ip = ipaddress.ip_network(str(ip))
        for exclude in self.exclude:
            if exclude.overlaps(net_ip):
                return False

        # Not excluded; must be a legit bogon.

        return True
