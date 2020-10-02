"""
Class for interpreting retry policies
"""

import copy

from .iso8601 import *
from .jsonval import *


class RetryPolicy(object):

    """
    Class that implements retry policies as an array of ("n1 attempts
    at intervals of t1", "n2 attempts at intervals of t2", etc.).
    Takes a dictionary of RetryPolicyEntries as defined in the JSON
    dictionary.  If iso8601 is True on initialization, returned values
    are in that format (wihout conversion); otherwise they are
    datetime.timedeltas.
    """

    def __init__(self, policy, iso8601=False):

        valid, message = json_validate({"policy": policy}, {
            "type": "object",
            "properties": {
                "policy": {
                    "type": "array",
                    "items": {"$ref": "#/pScheduler/RetryPolicyEntry"}
                }
            }
        })

        if not valid:
            raise ValueError(message)

        self.iso8601 = iso8601

        if iso8601:
            self.policy = copy.deepcopy(policy)
        else:
            self.policy = []
            for item in policy:
                self.policy.append({
                    "attempts": item["attempts"],
                    "wait": iso8601_as_timedelta(item["wait"])
                })

    def retry(self, attempts):
        """
        Calculate a retry interval based on a number of attempts,
        returning an interval or None of no attempt at retrying should
        be made.
        """

        for segment in self.policy:
            attempts -= segment["attempts"]
            if attempts < 0:
                return segment["wait"]

        # TODO
        return None


# Test program

if __name__ == "__main__":

    policy = RetryPolicy([
        {"attempts": 1, "wait": "PT10S"},
        {"attempts": 4, "wait": "PT1M"},
        {"attempts": 5, "wait": "PT1H"}
    ])

    for attempt in range(0, 12):
        print(attempt, policy.retry(attempt))
