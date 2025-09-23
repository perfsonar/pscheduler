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
from .identifier import ipcymruasn
from .identifier import ipcymrubogon
from .identifier import ipreversedns
from .identifier import localif
from .identifier import localsubnet

identifier_creator = {
    'always':           lambda data: always.IdentifierAlways(data),
    'hint':             lambda data: hint.IdentifierHint(data),
    'jq':               lambda data: jq.IdentifierJQ(data),
    'ip-cidr-list':     lambda data: ipcidrlist.IdentifierIPCIDRList(data),
    'ip-cidr-list-url': lambda data: ipcidrlisturl.IdentifierIPCIDRListURL(data),
    'ip-cymru-asn':     lambda data: ipcymruasn.IdentifierIPCymruASN(data),
    'ip-cymru-bogon':   lambda data: ipcymrubogon.IdentifierIPCymruBogon(data),
    'ip-reverse-dns':   lambda data: ipreversedns.IdentifierIPReverseDNS(data),
    'localif':          lambda data: localif.IdentifierLocalIF(data),
    'local-subnet':     lambda data: localsubnet.IdentifierLocalSubnet(data)
    }


class IdentifierSet(object):

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
            except KeyError:
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
        diags = []

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
            assert isinstance(invert, bool)

            try:
                identified = evaluator.evaluate(hints)
            except Exception as ex:
                diags.append("Identifier %s threw an exception:\n%s\nPlease report this as a bug."
                             % (identifier['name'], str(ex)))
                identified = False

            if identified and not invert:
                result.append(identifier['name'])

        return result, diags
