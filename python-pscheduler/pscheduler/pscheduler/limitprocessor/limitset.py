"""
Set of Limits
"""

from __future__ import absolute_import

import copy

# TODO: It would be nice if we could paw through the directory, import
# all of the modules and set this up automagically.

if __name__ == "__main__":
    from limit import passfail
    from limit import rundaterange
    from limit import runschedule
    from limit import test
    from limit import testtype
else:
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
          "passed": <Boolean>,       # True if passed
          "reasons": [ <String> ],   # Optional array of failure reasons
          "keep": {                  # Limit info to be passed along to run
              "limit": <AnyJSON>,    # Limit evaluated and passed
              "inverted": <Boolean>  # True if passed because of inversion
          }
        }
        """

        try:
            evaluator = self.limits[limit]['evaluator']
        except KeyError:
            raise ValueError("Undefined limit '%s'" % limit)
        assert evaluator is not None

        try:
            invert = self.limits[limit]["invert"]
        except KeyError:
            invert = False
        assert type(invert) == bool

        # Bypass limits that check the schedule if we've been asked to
        # do that.
        if not check_schedule and evaluator.checks_schedule():
            return { "passed": True }

        evaluated = evaluator.evaluate(task)

        result = {}

        for key in [ "passed", "limit", "reasons" ]:
            try:
                result[key] = evaluated[key]
            except KeyError:
                pass

        result["inverted"] = invert
        if invert:
            result["passed"] = not result["passed"]
            if result["passed"]:
                result["reasons"] = ["Passed but inverted"]

        return result



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
	},
        {
            "name": "innocuous-tests-inv",
	    "description": "Tests that are harmful",
	    "type": "test-type",
	    "data": {
		"types": [ "rtt", "latency", "trace" ]
            },
            "invert": True
	},
        ]


    # This only works on a fully-installed system with
    # pscheduler-test-idle installed.

    if False:
        thelimits.append({
            "name": "idle-default",
            "description": "Idle for most visitors",
            "type": "test",
            "data": {
                "test": "idle",
                "limit": {
                    "duration": {
                        "range": {
                            "lower": "PT2S",
                            "upper": "PT10S"
                        }
                    },
                    "starting-comment" : {
                        "description": "Starting comment can't contain the word 'platypus'.",
                        "match": {
                            "style": "regex",
                            "match": "platypus",
                            "invert": True
                        }
                    },
                    "parting-comment" : {
                        "description": "Parting comment must contain a vowel if not empty", 
                        "match": {
                            "style": "regex",
                            "match": "(^$|[aeiou])"
                        }
                    }
                }
            }
        })


    theset = LimitSet(thelimits)

    task = {
        "type": "idle",
        "spec": {
            "schema": 1,
            "duration": "PT10S"
        },
        "schedule": {
            "start": "2016-01-01T11:50:00",
            "duration": "PT10S"
        }
    }

    for limit in thelimits:
        print limit['name'], theset.check(task, limit['name'], True)
