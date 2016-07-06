"""
Identifier Class for ip-reverse-dns
"""

import dns
import ipaddr
import pscheduler
import re
import sre_constants

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
    return pscheduler.json_validate(data, data_validator)



class IdentifierIPReverseDNS():


    """
    Class that does reverse DNS identification
    """


    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.matcher = pscheduler.StringMatcher(data['match'])

        timeout = pscheduler.timedelta_as_seconds(
            pscheduler.iso8601_as_timedelta(data['timeout']))

        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout




    def evaluate(self,
                 hints  # Information used for doing identification
                 ):

        """Given a set of hints, evaluate this identifier and return True if
        an identification is made.

        """

        ip = hints['ip']
        addr = ipaddr.IPAddress(ip)

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



# A short test program

if __name__ == "__main__":

    ips = [
        "207.75.164.248",      # webprod2.internet2.edu (RRs to internet2.edu)
        "192.52.179.242",      # ntp.internet2.edu
        "2001:48a8:68fe::248", # webprod2.internet2.edu
        "198.124.252.90",      # {chronos,saturn}.es.net
        "198.6.1.1"            # cache00.ns.uu.net
    ]

    print "First:"

    ident = IdentifierIPReverseDNS({
        "match": {
            "style": "regex",
            "match": "^(ntp\\.internet2\\.edu|chronos\\.es\\.net|saturn\\.es\\.net)$"
        },
        "timeout": "PT2S"
    })

    for ip in ips:
        result = ident.evaluate({ "ip": ip })
        print ip, result

    print "\nSecond:"

    ident = IdentifierIPReverseDNS({
        "match": {
            "style": "regex",
            "match": "^(|.*\\.)(internet2.edu|es.net)"
        },
        "timeout": "PT2S"
    })

    for ip in ips:
        result = ident.evaluate({ "ip": ip })
        print ip, result
