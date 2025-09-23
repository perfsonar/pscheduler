"""
Class for doing enumerated matches
"""

from .jsonval import json_validate
import netaddr

class IPCIDRMatcher(object):

    "Class that matches an IP Cidr list."

    def __init__(self, match):
        """Construct a matcher.  The 'cidr' argument is a dict that conforms to
        an IPCIDRList as described in the pScheduler JSON Style Guide
        and Type Dictionary.
        """
        valid, message = json_validate(match,
                                       {
                                           "type": "object",
                                           "properties": {
                                               "cidr": { "$ref": "#/pScheduler/IPCIDRList" },
                                               "invert": { "$ref": "#/pScheduler/Boolean" },
                                           },
                                           "additionalProperties": False,
                                           "required": [ "cidr" ]
                                       })

        if not valid:
            raise ValueError("Invalid match: " + message)

        try:
            self.invert = match["invert"]
        except KeyError:
            self.invert = False

        self.cidr = match["cidr"]


    def contains(self, ip_address):
        "Try to match a candidate ip_address and see whether it was in the list of allowed cidrs"

        ip_address = netaddr.IPNetwork(ip_address)

        result = False
        for cidr in self.cidr:
            net = netaddr.IPNetwork(cidr)

            if ip_address in net:
                result = True
                break

        if self.invert:
            return not result
        return result
