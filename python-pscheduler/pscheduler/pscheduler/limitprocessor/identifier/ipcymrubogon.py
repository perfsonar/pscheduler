"""
Identifier Class for ip-cymru-bogon
"""

import dns
import ipaddr
import pscheduler

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
    return pscheduler.json_validate(data, data_validator)



class IdentifierIPCymruBogon():

    """
    Identifier for finding bogons/martians via DNS
    """

    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.exclude = [ ipaddr.IPNetwork(addr)
                         for addr in data['exclude'] ]

        try:
            timeout = pscheduler.iso8601_as_timedelta(data['timeout'])
            self.timeout = pscheduler.timedelta_as_seconds(timeout)
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

        octets = dns.reversename.from_address(ip)[0:-3]
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
                dns.resolver.NoNameservers):
            return self.fail_result

        # The query will return 127.0.0.2 if it's in the bogon list.
        # See http://www.team-cymru.org/bogon-reference-dns.html.

        if str(resolved) != '127.0.0.2':
            return False

        # At this point, we have a bogon.  Filter out exclusions.

        net_ip = ipaddr.IPAddress(ip)
        for exclude in self.exclude:
            if net_ip in exclude:
                return False

        # Not excluded; must be a legit bogon.

        return True


# A short test program

if __name__ == "__main__":

    ident = IdentifierIPCymruBogon({
        "exclude": [
            "10.0.0.0/8"
            ],
        "timeout": "PT2S",
        "fail-result": False
    })

    for ip in [
            # Trues
            "192.168.1.1",
            "240.0.0.1",
            "1000:dead:beef::1",
            # Falses
            "10.9.8.6",
            "198.6.1.1",
            "128.82.4.1",
            "2001:48a8:68fe::248"  # www.perfsonar.net
    ]:
        result = ident.evaluate({ "requester": ip })
        print ip, result
