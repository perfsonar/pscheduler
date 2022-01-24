"""
Set of Limit Applications
"""

from .classifierset import ClassifierSet
from .limitset import LimitSet

from pscheduler import indent


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


group_condition_tests = {
    "none": lambda data: __test_none(data),
    "one":  lambda data: __test_one(data),
    "any":  lambda data: __test_any(data),
    "all":  lambda data: __test_all(data)
}





class ApplicationSet(object):

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


    def __check_group(self, proposal, group, check_schedule):
        """
        Check a group of limits and return a tuple:
            pass - True if the group passed
            diags - Array of diagnostic messages
        """

        diags = []

        requirement = group['require']
 
        total = len(group['limits'])

        fails = 0
        passes = 0


        for limit in group['limits']:

            # TODO: Consider finding a way to cache these results so
            # that if the same limit is applied in multiple places, it
            # doesn't have to be processed again.  Might not actually
            # be an issue.

            try:
                evaluated = self.limits.check(proposal, limit, check_schedule)
            except Exception as ex:
                evaluated = {
                    "passed": False,
                    "reasons": [ "Limit %s threw an exception:\n%s" % (limit, str(ex)) ]
                }

            limit_passed = evaluated['passed']

            if limit_passed:
                diags.append("Limit '%s' passed" % limit)
                passes += 1
            else:
                fails += 1
                diags.append("Limit '%s' failed: %s" % (
                    limit,
                    '; '.join(evaluated['reasons'])))

        passed = group_condition_tests[requirement]((passes, fails))

        diags.append("Want %s, %d/%d passed, %d/%d failed: %s" %
                     ( requirement,
                       passes, total,
                       fails, total,
                       "PASS" if passed else "FAIL" ))

        return passed, diags


    def __check_application(self, application, proposal, classifiers, check_schedule):

        """Evaluate the groups of limits in an application, stopping when one
        fails.
        """

        diags = []

        group_no = 0
        groups_failed = len(application['apply'])

        for group in application['apply']:
            group_no += 1
            group_passed, group_diags \
                = self.__check_group(proposal, group, check_schedule)
            diags.extend([ "Group %d: %s" % (group_no, diag) for diag in group_diags ])
            if group_passed:
                groups_failed -= 1
            else:
                break

        stop_on_failure = application.get('stop-on-failure', False)

        pass_ = groups_failed == 0
        invert = application['invert'] if 'invert' in application else False
        if invert:
            pass_ = not pass_

        diags.append("Application %s%s" %
                     ( "PASSES" if pass_ else "FAILS",
                       " (Inverted)" if invert else "" ))

        return pass_, stop_on_failure, diags



    def check(self,
              proposal,            # Task and hints
              classifiers,         # List of the classifiers
              check_schedule=True  # Keep/disregard time-related limits
              ):

        """Determine if a task can be run, return true/false, a list of lists
        (see below) and a string of diagnostics.

        The list of lists contains one list per application passed,
        with that list containing descriptions of the limits passed
        for that application.  (See the code in the top-level limit
        processor to see how this is used.)
        """

        diags = []
        passed_enough = False

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
            diags.append("Application: %s" % 
                         application.get('description', "(No description)"))

            passed, forced_stop, app_diags \
                = self.__check_application(application, proposal, classifiers,
                                           check_schedule)
           
            diags.extend([ indent(diag) for diag in app_diags])

            # A pass short-circuits the win
            if passed:
                diags.append("Passed one application.  Stopping.")
                passed_enough = True
                break

            # Forced stop ends it all
            if forced_stop:
                diags.append("Failed; stop forced")
                break


        return passed_enough, '\n'.join(diags)
