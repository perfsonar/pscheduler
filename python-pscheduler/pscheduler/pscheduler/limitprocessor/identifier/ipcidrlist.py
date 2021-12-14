"""
Identifier Class for ip-cidr-list
"""

import ipaddress

from ...jsonval import *

data_validator = {
    "type": "object",
    "properties": {
        "cidrs": {
            "type": "array",
            "items": { 
                "anyOf": [
                    { "$ref": "#/pScheduler/IPCIDR" },
                    { "$ref": "#/pScheduler/IPAddress" }
                ]
            }
        }
    },
    "required": [ "cidrs" ]
}

def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return json_validate(data, data_validator)



class IdentifierIPCIDRList(object):


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
            self.cidrs.append(ipaddress.ip_network(str(cidr)))



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

    ident = IdentifierIPCIDRList({
        "cidrs": [ "10.0.0.0/8",
                   "172.16.0.0/12",
                   "192.168.0.0/16",
                   "fd00::/8"
               ]
    })

    for ip in [ "10.9.8.6", "198.6.1.1", "fd00:dead:beef::1" ]:
        print(ip, ident.evaluate({ "requester": ip }))
