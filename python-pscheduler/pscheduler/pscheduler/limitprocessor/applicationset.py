"""
Set of Limit Applications
"""

from classifierset import ClassifierSet
from limitset import LimitSet


# These functions and table are used in __check_group() to evaluate
# whether or not the group of limits tested results in a pass or fail
# overall.  The argument is a single tuple of (passes, fails) and the
# return value is a boolean.

def __test_none(data):    # Nothing passes
    passes, fails = data
    return passes == 0

def __test_one(data):     # Only one passes
    passes, fails = data
    return passes == 1

def __test_any(data):     # One or more passes
    passes, fails = data
    return passes > 0

def __test_all(data):     # All passed (nothing failed)
    passes, fails = data
    return fails == 0


group_conditions = {
    "none": { "stop-on": True,  "check": lambda data: __test_none(data) },
    "one":  { "stop-on": None,  "check": lambda data: __test_one(data)  },
    "any":  { "stop-on": True,  "check": lambda data: __test_any(data)  },
    "all":  { "stop-on": False, "check": lambda data: __test_all(data)  }
}





class ApplicationSet():

    """
    Class that holds and processes limit applications
    """


    def __init__(self,
                 fodder,      # Set of applications as read from a limit file
                 classifiers, # Classifer set
                 limits,      # Limit set
                 ):

        assert isinstance(classifiers, ClassifierSet)
        assert isinstance(limits, LimitSet)

        unknown_classifiers = {}
        unknown_limits = {}

        for application in fodder:

            try:
                classifier = application['classifier']
                if classifier not in classifiers:
                    unknown_classifiers[classifier] = 1
            except KeyError:
                pass  # No classifier is okay

            # Dodges a reserved word
            for apply_ in application['apply']:
                for limit in apply_['limits']:
                    if limit not in limits:
                        unknown_limits[limit] = 1

        errors = []
        if len(unknown_classifiers) > 0:
            errors.append("Unknown classifiers: %s" \
                          % (', '.join(unknown_classifiers)))
        if len(unknown_limits) > 0:
            errors.append("Unknown limits: %s" % (', '.join(unknown_limits)))

        if errors:
            raise ValueError('.  '.join(errors))


        self.applications = fodder
        self.limits = limits


    def __check_group(self, task, group, check_schedule):
        """
        Check a group of limits and return pass/fail and an array of diags
        """

        diags = []

        requirement = group['require']
 
        conditions = group_conditions[requirement]
        total = len(group['limits'])

        stop_on = conditions['stop-on']

        # These will come up False if stop_on is None
        stop_on_fail = stop_on == False
        stop_on_pass = stop_on == True

        fails = 0
        passes = 0
        stopped = False

        for limit in group['limits']:

            # TODO: Consider finding a way to cache these results so
            # that if the same limit is applied in multiple places, it
            # doesn't have to be processed again.  Might not actually
            # be an issue.

            evaluated = self.limits.check(task, limit, check_schedule)
            limit_passed = evaluated['passed']

            if limit_passed:
                passes += 1
                diags.append("Limit '%s' passed" % limit)
                if stop_on_pass:
                    stopped = True
                    diags.append("Stopped on pass")
                    break
            else:
                fails += 1
                diags.append("Limit '%s' failed: %s" % (
                    limit,
                    '; '.join(evaluated['reasons'])))
                if stop_on_fail:
                    stopped = True
                    diags.append("Stopped on fail")
                    break

        passed = conditions['check']((passes, fails))

        diags.append("Want %s, %d/%d passed, %d/%d failed: %s" %
                     ( requirement,
                       passes, total,
                       fails, total,
                       "PASS" if passed else "FAIL" ))

        return passed, diags


    def __check_application(self, application, task, classifiers, check_schedule):

        """Evaluate the groups of limits in an application, stopping when one fails."""

        diags = []

        group_no = 0
        groups_failed = len(application['apply'])

        for group in application['apply']:
            group_no += 1
            group_passed, group_diags = self.__check_group(task, group, check_schedule)
            diags.extend([ "Group %d: %s" % (group_no, diag) for diag in group_diags ])
            if group_passed:
                groups_failed -= 1
            else:
                diags.append("Group %d: Failed; stopping here." % group_no)
                break

        try:
            stop_on_failure = application['stop-on-failure']
        except KeyError:
            stop_on_failure = False

        pass_ = groups_failed == 0
        invert = application['invert'] if 'invert' in application else False
        if invert:
            pass_ = not pass_

        diags.append("Application %s%s" %
                     ( "PASSES" if pass_ else "FAILS",
                       " (Inverted)" if invert else "" ))

        return pass_, stop_on_failure, diags



    def check(self,
              task,                # Task to check
              classifiers,         # List of the classifiers
              check_schedule=True  # Keep/disregard time-related limits
              ):

        """Determine if a task can be run, return true/false and a string of
        diagnostics"""

        diags = []

        # Run through each application, stopping when one passes or a
        # failed one has stop-on-failure

        for application in self.applications:

            # See if the classifier applies

            try:
                classifier = application['classifier']
                if classifier not in classifiers:
                    continue
            except KeyError:
                # No classifier always applies
                pass

            # Description

            try:
                diags.append("Application: " + application['description'])
            except KeyError:
                diags.append("Application: (No description)")


            passed, forced_stop, app_diags \
                = self.__check_application(application, task, classifiers,
                                           check_schedule)

            diags.extend(["    " + diag for diag in app_diags])
            if passed or forced_stop:
                if not passed and forced_stop:
                    diags.append("    Failed - Stop Forced")
                return passed, '\n'.join(diags)

        # If we got here, nothing passed.
        return False, '\n'.join(diags)
