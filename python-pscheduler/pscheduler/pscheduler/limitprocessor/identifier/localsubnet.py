"""
Identifier Class for localsubnet
"""

import ipaddress
import netifaces
import re

def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """

    if type(data) == dict and len(data) == 0:
        return True, None

    return False, "Data is not an object or not empty."



# These are for ue by ipv6_netmask_size()

ipv6_netmask_re = re.compile("^([f]*)([ec80]?)0*$")

ipv6_digit_bits = {
    "e": 3,
    "c": 2,
    "8": 1,
    "0": 0,
    "": 0
}

def ipv6_netmask_size(mask_in):
    """
    Convert an IPv6 netmask (e.g., ffff:ffff::) to a prefix size
    (32).
    """

    mask = mask_in.lower()

    # Lead-pad any parts with less than four digits
    parts = [ '0' * (4-len(part)) + part for part in mask.split(":") ]
    mask = "".join(parts)
    matches = ipv6_netmask_re.search(mask)
    if matches is None:
        raise ValueError("Invalid IPv6 netmask '%s'" % (mask_in))

    bits = len(matches.group(1)) * 4

    last = matches.group(2)
    if last is not None:
        bits += ipv6_digit_bits[last]

    return bits



class IdentifierLocalSubnet():


    """
    Class that holds and processes identifiers
    """


    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.cidrs = []

        for iface in netifaces.interfaces():

            ifaddrs = netifaces.ifaddresses(iface)

            pairs = []

            for ifaddr in ifaddrs[netifaces.AF_INET] \
                if netifaces.AF_INET in ifaddrs else []:
                self.cidrs.append(ipaddress.IPv4Network(
                    unicode("%s/%s" % (ifaddr["addr"], ifaddr["netmask"])),
                    strict=False  # Don't complain about host bits being set.
                ))

            for ifaddr in ifaddrs[netifaces.AF_INET6] \
                if netifaces.AF_INET6 in ifaddrs else []:
                self.cidrs.append(ipaddress.IPv6Network(
                    unicode("%s/%s" % (
                        ifaddr["addr"].split("%")[0],
                        ipv6_netmask_size(ifaddr["netmask"]))),
                    strict=False  # Don't complain about host bits being set.
                ))



    def evaluate(self,
                 hints  # Information used for doing identification
                 ):

        """Given a set of hints, evaluate this identifier and return True if
        an identification is made.

        """


        try:
            ip = ipaddress.ip_network(unicode(hints["requester"]))
        except KeyError:
            return False

        for cidr in self.cidrs:
            if cidr.overlaps(ip):
                return True

        return False



# A short test program

if __name__ == "__main__":

    ident = IdentifierLocalSubnet({})

    for ip in [
            "127.0.0.1",
            "::1", "10.1.1.1",
            "198.129.254.30",
            "dead:beef::1",
            "10.0.2.12"
    ]:
        print ip, ident.evaluate({ "requester": ip })
