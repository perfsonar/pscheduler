"""
Set of Identifiers
"""

# TODO: It would be nice if we could paw through the directory, import
# all of the modules and set this up automagically.

from .identifier import always
from .identifier import hint
from .identifier import jq
from .identifier import ipcidrlist
from .identifier import ipcidrlisturl
from .identifier import ipcymrubogon
from .identifier import ipreversedns
from .identifier import localif

identifier_creator = {
    'always':           lambda data: always.IdentifierAlways(data),
    'hint':             lambda data: hint.IdentifierHint(data),
    'jq':               lambda data: jq.IdentifierJQ(data),
    'ip-cidr-list':     lambda data: ipcidrlist.IdentifierIPCIDRList(data),
    'ip-cidr-list-url': lambda data: ipcidrlisturl.IdentifierIPCIDRListURL(data),
    'ip-cymru-bogon':   lambda data: ipcymrubogon.IdentifierIPCymruBogon(data),
    'ip-reverse-dns':   lambda data: ipreversedns.IdentifierIPReverseDNS(data),
    'localif':          lambda data: localif.IdentifierLocalIF(data)
    }


class IdentifierSet():

    """
    Class that holds and processes identifiers
    """

    def __init__(self,
                 fodder   # Set of identifiers as read from a limit file
                 ):

        self.identifiers = []
        self.seen = {}

        for identifier in fodder:

            name = identifier['name']

            # Weed out dupes
            if name in self.seen:
                raise ValueError("Duplicate identifier '%s'" % name)
            self.seen[name] = 1


            id_type = identifier['type']
            data = identifier['data']
            try:
                creator = identifier_creator[id_type]
            except KeyError as ex:
                raise ValueError("Identifier '%s' has unsupported type '%s'" \
                                 % (identifier['name'], id_type))
            id_object = creator(data)
            identifier['evaluator'] = id_object
            self.identifiers.append(identifier)


    def __contains__(self, name):
        return name in self.seen


    def identities(self,
                 hints  # Information used for doing identification
                 ):
        """Given a set of hints, return a list of all of the identifier names
        that match."""

        result = []

        # TODO: Thread this so things like DNS lookups run in
        # pseudo-parallel.

        for identifier in self.identifiers:

            try:
                evaluator = identifier['evaluator']
            except KeyError:
                continue
            assert evaluator is not None

            try:
                invert = identifier['invert']
            except KeyError:
                invert = False
            assert type(invert) == bool

            if evaluator.evaluate(hints) and not invert:
                result.append(identifier['name'])

        return result


# A small test program

if __name__ == "__main__":

    hints = {
        "requester": "10.0.0.7",
        "server": "10.0.0.7",
        "protocol": "https"
    }

    iset = IdentifierSet([
        {
	    "name": "everybody",
	    "description": "An identifier that always identifies",
	    "type": "always",
	    "data": { }
	},
        {
	    "name": "nobody",
	    "description": "An identifier that never identifies",
	    "type": "always",
	    "data": { },
            "invert": True
	},
        {
	    "name": "local-interface",
	    "description": "Requests from local interfaces",
	    "type": "localif",
	    "data": { }
	},
	{
	    "name": "private-ip",
	    "description": "Private IP Blocks per RFCs 1918 and 4193",
	    "type": "ip-cidr-list",
	    "data": {
		"cidrs": [
                    "10.0.0.0/8",
                    "172.16.0.0/12",
                    "192.168.0.0/16",
                    "fd00::/8"
		]
	    }
	},
        {
            "name": "secure-user",
            "description": "Request arrived using a secure protocol",
            "type": "hint",
            "data": {
                "hint": "protocol",
                "match": {
                    "style": "exact",
                    "match": "https"
                }
            }
        }
        ])

    print iset.identities(hints)
