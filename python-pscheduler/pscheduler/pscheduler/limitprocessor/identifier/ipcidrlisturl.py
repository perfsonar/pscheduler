"""
Identifier Class for ip-cidr-list-url
"""

import datetime
import radix
import time
import threading

from ...iso8601 import *
from ...jqfilter import *
from ...jsonval import *
from ...psjson import *
from ...psurl import *


data_validator = {
    "type": "object",
    "properties": {
        "source": { "$ref": "#/pScheduler/URL" },
        "transform": { "$ref": "#/pScheduler/JQTransformSpecification" },
        "bind": { "$ref": "#/pScheduler/Host" },
        "transform": { "$ref": "#/pScheduler/JQTransformSpecification" },
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
    valid, error = json_validate(data, data_validator)
    if not valid:
        return valid, error
    return valid, error



class IdentifierIPCIDRListURL(object):

    """Class that holds and processes identifiers as lists of CIDRs
    fetched from a URL.
    """

    def __len__(self):
        with self.data_lock:
            return self.length



    def __populate_cidrs_update__(self):

        """
        Update the CIDR list.  It is assumed that the caller will have
        protected against calling two of these at once.
        """

        status, text = url_get(self.source, bind=self.bind,
                               json=False, throw=False)

        possible_next_attempt = datetime.datetime.now() + self.retry

        if status != 200:
            # TODO: Would be nice if we could log the failure
            with self.data_lock:
                self.next_attempt = possible_next_attempt
            return

        # If there's a transform, apply it.
        if self.transform is not None:
            try:
                json = json_load(text)
                text = self.transform(json)
            except (ValueError,
                    JQRuntimeError):
                # TODO: Would be nice if we could log the failure
                with self.data_lock:
                    self.next_attempt = possible_next_attempt
                return


        # TODO: Consider caching this on disk someplace so that it can
        # be retrieved if we fail to fetch at startup.

        # TODO: When threaded, hold this separately and swap old list
        new_cidrs = radix.Radix()
        new_length = 0

        for cidr in text.split('\n'):

            # Remove comments and ditch excess whitespace
            cidr = cidr.split('#', 1)[0].strip()
            if len(cidr) == 0:
                continue
            try:
                new_cidrs.add(cidr)
                new_length += 1
            except ValueError:
                # Just ignore anything that looks fishy.
                # TODO: Log it?
                pass

        with self.data_lock:
            self.cidrs = new_cidrs
            self.length = new_length
            self.next_attempt = datetime.datetime.now() + self.update



    def __populate_cidrs__(self):

        with self.data_lock:
            if self.updating or self.next_attempt > datetime.datetime.now():
                # Not time yet or an update is already underway.
                return
            self.updating = True

        try:
            self.__populate_cidrs_update__()
        finally:
            with self.data_lock:
                self.updating = False




    def __init__(self,
                 data   # Data suitable for this class
                 ):

        valid, message = data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.source = data['source']
        self.bind = data.get('bind', None)
        self.update = iso8601_as_timedelta(data['update'])
        self.retry = iso8601_as_timedelta(data['retry'])
        self.fail_state = data.get('fail-state', False)
        try:
            # This will raise a ValueError if it's wrong.
            transform = data["transform"]
            self.transform = JQFilter(transform["script"],
                                      transform.get("args", {} ),
                                                 output_raw=True)
        except KeyError:
            self.transform = None


        self.exclusions = radix.Radix()
        if 'exclude' in data:
            try:
                for excl in data['exclude']:
                    self.exclusions.add(excl)
            except ValueError:
                raise ValueError("Invalid IP or CIDR '%s'" % excl)


        self.data_lock = threading.Lock()
        self.updating = False

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
