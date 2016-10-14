"""
Identifier Class for ip-cidr-list
"""

import ipaddr
import pscheduler
import netifaces

data_validator = {
    "type": "object",
    "properties": {
        "cidrs": {
            "type": "array",
            "items": { 
                "anyOf": [ 
                    {"$ref": "#/pScheduler/IPCIDR"}, 
                    {"type": "string", "enum": ["local"]}
                ] 
            }
        },
    },
    "required": [ "cidrs" ]
}

def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return pscheduler.json_validate(data, data_validator)



class IdentifierIPCIDRList():


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
        for cidr in data['cidrs']:
            if cidr == 'local':
                for iface in netifaces.interfaces():
                    ifaddrs = netifaces.ifaddresses(iface)
                    if netifaces.AF_INET in ifaddrs:
                        for ifaddr in ifaddrs[netifaces.AF_INET]:
                            if 'addr' in ifaddr:
                                self.cidrs.append(ipaddr.IPNetwork(ifaddr['addr']))
                    if netifaces.AF_INET6 in ifaddrs:
                        for ifaddr in ifaddrs[netifaces.AF_INET6]:
                            if 'addr' in ifaddr:
                                #add v6 but remove stuff like %eth0 that gets thrown on end of some addrs
                                self.cidrs.append(ipaddr.IPNetwork(ifaddr['addr'].split('%')[0]))
            else:
                self.cidrs.append(ipaddr.IPNetwork(cidr))



    def evaluate(self,
                 hints  # Information used for doing identification
                 ):

        """Given a set of hints, evaluate this identifier and return True if
        an identification is made.

        """

        try:
            ip = ipaddr.IPNetwork(hints['ip'])
        except KeyError:
            return False

        # TODO: Find out of there's a more hash-like way to do this
        # instead of a linear search.  This would be great if it
        # weren't GPL: https://pypi.python.org/pypi/pytricia

        for cidr in self.cidrs:
            if ip in cidr:
                return True

        return False


# A short test program

if __name__ == "__main__":

    ident = IdentifierIPCIDRList({
        "cidrs": [ "10.0.0.0/8",
                   "172.16.0.0/12",
                   "192.168.0.0/16",
                   "fd00::/8"
               ]
    })

    for ip in [ "10.9.8.6", "198.6.1.1", "fd00:dead:beef::1" ]:
        print ip, ident.evaluate({ "ip": ip })
