"""
Set of Limits
"""



import copy

# TODO: It would be nice if we could paw through the directory, import
# all of the modules and set this up automagically.

if __name__ == "__main__":
    from limit import jq
    from limit import passfail
    from limit import rundaterange
    from limit import runschedule
    # TODO: #824: Remove this in 5.1
    from limit import test
    from limit import testtype
    from limit import urlfetch
else:
    from .limit import jq
    from .limit import passfail
    from .limit import rundaterange
    from .limit import runschedule
    # TODO: #824: Remove this in 5.1
    from .limit import test
    from .limit import testtype
    from .limit import urlfetch


limit_creator = {
    'jq':            lambda data: jq.LimitJQ(data),
    'pass-fail':     lambda data: passfail.LimitPassFail(data),
    'run-daterange': lambda data: rundaterange.LimitRunDateRange(data),
    'run-schedule':  lambda data: runschedule.LimitRunSchedule(data),
    'test-type':     lambda data: testtype.LimitTestType(data),
    'url-fetch':     lambda data: urlfetch.LimitURLFetch(data)
    }



def merge_dicts(a, b, path=None):
    """
    Merge two dictionaries.
    Source: http://stackoverflow.com/a/7205107/180674
    """
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                a[key] = b[key]  # Overlay conflicting values
                # raise ValueError('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a



class LimitSet(object):

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
                                     % (limit['name'], limit['clone']))

                new_limit = {
                    "name": limit['name'],
                    "description": limit['description'],
                    "type": source_limit['type'],
                    "data": merge_dicts(
                        copy.deepcopy(source_limit['data']),
                        copy.deepcopy(limit['data']))
                }

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
              proposal,       # Task and hints
              limit,          # The limit to check against
              check_schedule  # Keep/disregard time-related limits
              ):
        """Evaluate a single limit and return a hash:
        {
          "passed": <Boolean>,       # True if passed
          "reasons": [ <String> ],   # Optional array of failure reasons
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
        assert isinstance(invert, bool)

        # Bypass limits that check the schedule if we've been asked to
        # do that.
        if not check_schedule and evaluator.checks_schedule():
            return { "passed": True }

        evaluated = evaluator.evaluate(proposal)

        passed = evaluated["passed"]
        result = {
            "passed": passed,
            "reasons": evaluated.get("reasons", [])
        }

        result["inverted"] = invert
        if invert:
            passed = not passed
            result["passed"] = passed
            if not passed:
                result["reasons"] = ["Passed but inverted"]

        return result
