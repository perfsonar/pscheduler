"""
Set of Limits
"""

from __future__ import absolute_import

import copy

# TODO: It would be nice if we could paw through the directory, import
# all of the modules and set this up automagically.

from .limit import passfail
from .limit import rundaterange
from .limit import runschedule
from .limit import test
from .limit import testtype

limit_creator = {
    'pass-fail':     lambda data: passfail.LimitPassFail(data),
    'run-daterange': lambda data: rundaterange.LimitRunDateRange(data),
    'run-schedule':  lambda data: runschedule.LimitRunSchedule(data),
    'test':          lambda data: test.LimitTest(data),
    'test-type':     lambda data: testtype.LimitTestType(data)
    }


class LimitSet():

    """
    Class that holds and processes limits
    """

    def __init__(self,
                 fodder,      # Set of limits as read from a limit file
                 ):

        self.limits = {}

        for limit in fodder:

            name = limit['name']

            # Weed out dupes
            if name in self.limits:
                raise ValueError("Duplicate limit '%s'" % name)

            # If this is a cloned limit, find and duplicate the old one.

            if 'clone' in limit:

                try:
                    source_limit = self.limits[limit['clone']]
                except KeyError:
                    raise ValueError("Limit '%s': "
                                     "Unable to clone undefined limit '%s'"
                                     % (clone_name, clone_source))

                new_limit = {
                    "name": name,
                    "description": limit['description'],
                    "type": source_limit['type'],
                    "data": copy.deepcopy(source_limit['data'])
                }                   

                # Overlay any data provided by the new limit.  No need
                # to deep copy this since it isn't going to change.

                for overlay in limit['data']:
                    new_limit['data'][overlay] = limit['data'][overlay]

                limit = new_limit

            # Process the limit, cloned or not, as normal.

            limit_type = limit['type']
            data = limit['data']

            try:
                evaluator = limit_creator[limit_type]
            except KeyError as ex:
                raise ValueError("Limit '%s' has unsupported type '%s'" \
                                 % (limit['name'], limit_type))

            # This will chuck whatever exceptions the evaluator does
            limit['evaluator'] = evaluator(data)

            self.limits[name] = limit


    def __contains__(self, name):
        return name in self.limits


    def check(self,
              task,           # Task to use as limit fodder
              limit,          # The limit to check against
              check_schedule  # Keep/disregard time-related limits

              ):
        """Evaluate a single limit and return a hash:
        {
          "passed": <Boolean>       # True if passed
          "reasons": [ <String> ]   # Optional array of failure reasons
        }
        """

        try:
            evaluator = self.limits[limit]['evaluator']
        except KeyError:
            raise ValueError("Undefined limit '%s'" % limit)
        assert evaluator is not None
        evaluated = evaluator.evaluate(task, check_schedule)

        return evaluated



# A small test program

if __name__ == "__main__":

    thelimits = [
	{
	    "name": "always",
	    "description": "Always passes",
	    "type": "pass-fail",
	    "data": {
		"pass": True
	    }
	},
	{
	    "name": "never",
	    "description": "Always fails",
	    "clone": "always",
	    "data": {
		"pass": False
	    }
	},
        {
            "name": "lunchtime",
	    "description": "Never at noon",
	    "type": "run-schedule",
	    "data": {
                "hour": [ 12 ],
                "overlap": True
            }
	},
        {
            "name": "century20",
	    "description": "The 20th century",
	    "type": "run-daterange",
	    "data": {
                "start": "1901-01-01T00:00:00",
                "end": "2001-01-01T00:00:00"
            }
	},
        {
            "name": "century21",
	    "description": "The 21st century",
	    "type": "run-daterange",
	    "data": {
                "start": "2001-01-01T00:00:00",
                "end": "2101-01-01T00:00:00"
            }
	},
        {
            "name": "innocuous-tests",
	    "description": "Tests that are harmless",
	    "type": "test-type",
	    "data": {
		"types": [ "rtt", "latency", "trace" ]
            }
	}
    ]


    theset = LimitSet(thelimits)

    task = {
        "type": "bogus",
        "test": { },
        "schedule": {
            "start": "2016-01-01T11:50:00",
            "duration": "PT1H"
        },
        "invert": True
        }

    for limit in thelimits:
        print limit['name'], theset.check(task, limit['name'])
