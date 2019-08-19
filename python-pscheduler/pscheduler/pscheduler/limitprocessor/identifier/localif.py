"""
Identifier Class for localif
"""

import ipaddress
import netifaces

def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """

    if type(data) == dict and len(data) == 0:
        return True, None

    return False, "Data is not an object or not empty."


class IdentifierLocalIF():


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
            if netifaces.AF_INET in ifaddrs:
                for ifaddr in ifaddrs[netifaces.AF_INET]:
                    if 'addr' in ifaddr:
                        self.cidrs.append(ipaddress.ip_network(str(ifaddr['addr'])))
            if netifaces.AF_INET6 in ifaddrs:
                for ifaddr in ifaddrs[netifaces.AF_INET6]:
                    if 'addr' in ifaddr:
                        #add v6 but remove stuff like %eth0 that gets thrown on end of some addrs
                        self.cidrs.append(ipaddress.ip_network(str(ifaddr['addr'].split('%')[0])))



    def evaluate(self,
                 hints  # Information used for doing identification
                 ):

        """Given a set of hints, evaluate this identifier and return True if
        an identification is made.

        """

        try:
            ip = ipaddress.ip_network(str(hints['requester']))
        except KeyError:
            return False

        # TODO: Find out of there's a more hash-like way to do this
        # instead of a linear search.  This would be great if it
        # weren't GPL: https://pypi.python.org/pypi/pytricia

        for cidr in self.cidrs:
            if cidr.overlaps(ip):
                return True

        return False

# A short test program

if __name__ == "__main__":

    ident = IdentifierLocalIF({})

    for ip in [ "127.0.0.1", "::1", "10.1.1.1", "198.129.254.30", "10.0.0.7" ]:
        print(ip, ident.evaluate({ "requester": ip }))
