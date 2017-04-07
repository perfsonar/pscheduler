"""
Identifier Class for ip-cidr-list-url
"""

import datetime
import radix
import pscheduler


data_validator = {
    "type": "object",
    "properties": {
        "source": { "$ref": "#/pScheduler/URL" },
        "transform": { "$ref": "#/pScheduler/JQTransformSpecification" },
        "bind": { "$ref": "#/pScheduler/Host" },
        "exclude": {
            "type": "array",
            "items": { 
                "anyOf": [
                    { "$ref": "#/pScheduler/IPCIDR" },
                    { "$ref": "#/pScheduler/IPAddress" }
                ]
            }
        },
        "update": { "$ref": "#/pScheduler/Duration" },
        "retry": { "$ref": "#/pScheduler/Duration" },
        "fail-state": { "$ref": "#/pScheduler/Boolean" }
    },
    "additionalProperties": False,
    "required": [ "source", "update", "retry" ]
}

def data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    valid, error = pscheduler.json_validate(data, data_validator)
    if not valid:
        return valid, error
    if "transform" in data:
        return False, "Transforms are not yet supported."
    return valid, error



class IdentifierIPCIDRListURL():

    """Class that holds and processes identifiers as lists of CIDRs
    fetched from a URL.
    """

    def __len__(self):
        return self.length


    def __populate_cidrs__(self):

        # TODO: Turn this into a thread so checks aren't delayed.

        if self.next_attempt > datetime.datetime.now():
            # Not time yet.
            return

        status, text = pscheduler.url_get(self.source, bind=self.bind,
                                          json=False, throw=False)

        if status != 200:
            # TODO: Would be nice if we could log the failure
            self.next_attempt = datetime.datetime.now() + self.retry
            return

        # TODO: Consider caching this on disk someplace so that it can
        # be retrieved if we fail to fetch at startup.

        # TODO: When threaded, hold this separately and swap old list
        self.cidrs = radix.Radix()
        self.length = 0

        for cidr in text.split('\n'):

            # Remove comments and ditch excess whitespace
            cidr = cidr.split('#', 1)[0].strip()
            if len(cidr) == 0:
                continue
            try:
                self.cidrs.add(cidr)
                self.length += 1
            except ValueError:
                # Just ignore anything that looks fishy.
                # TODO: Log it?
                pass

        self.next_attempt = datetime.datetime.now() + self.update



    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.source = data['source']
        self.bind = data.get('bind', None)
        self.update = pscheduler.iso8601_as_timedelta(data['update'])
        self.retry = pscheduler.iso8601_as_timedelta(data['retry'])
        self.fail_state = data.get('fail-state', False)

        self.exclusions = radix.Radix()
        if 'exclude' in data:
            try:
                for excl in data['exclude']:
                    self.exclusions.add(excl)
            except ValueError:
                raise ValueError("Invalid IP or CIDR '%s'" % excl)

        # TODO: Would be nice to support a timeout so the system
        # doesn't sit for too long.

        self.cidrs = radix.Radix()
        self.length = 0

        # Prime the timer with the epoch and do a first load of the list
        self.next_attempt = datetime.datetime.utcfromtimestamp(0)
        self.__populate_cidrs__()




    def evaluate(self,
                 hints  # Information used for doing identification
                 ):

        """Given a set of hints, evaluate this identifier and return True if
        an identification is made.

        """

        self.__populate_cidrs__()
        if self.length == 0:
            return self.fail_state

        try:
            ip = hints['requester']
        except KeyError:
            return False

        try:
            prefix = self.cidrs.search_best(ip)
        except ValueError:
            raise ValueError("Invalid IP '%s'" % ip)

        if prefix is None:
            return False

        return self.exclusions.search_best(ip) is None




# A short test program

if __name__ == "__main__":

    data = {
        "source": "http://software.internet2.edu/data/pscheduler/limit-cidrs/ren",
#        "transform": { "script": "foo" },
        "exclude": [
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16"
        ],
        "update": "P1D",
        "retry": "PT1H",
        "fail-state": True
    }

    print data_is_valid(data)

    ident = IdentifierIPCIDRListURL(data)

    print "LEN", len(ident)

    for ip in [ 
            # Trues
            "35.132.6.7",
            "128.82.4.1",
            "64.185.56.0",
            # Falses
            "10.9.8.6",
            "198.6.1.1",
            "192.168.4.3",
    ]:
        print ip, ident.evaluate({ "requester": ip })
