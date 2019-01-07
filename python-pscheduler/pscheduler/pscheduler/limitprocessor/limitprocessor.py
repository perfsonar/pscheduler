"""
pScheduler Limit Processor
"""

import os
import pscheduler

from identifierset  import IdentifierSet
from classifierset  import ClassifierSet
from rewriter       import Rewriter
from limitset       import LimitSet
from applicationset import ApplicationSet
from prioritizer    import Prioritizer

class LimitProcessor():

    """
    pScheduler limit processing class
    """


    def __init__(self,
                 source=None  # Open file or path to file with limit set
    ):
        """Construct a limit processor.

        The 'source' argument can be one of three types:

        string - Path to a file to open and read.

        file - Open file handle to read.

        None - The limit processor becomes inert and passes all limits
        unconditionally.
        """

        # If we were given no source, put the processor into an inert
        # mode where everything passes.
        self.inert = source is None
        if self.inert:
            return


        #
        # Load the validation data
        #

        validation_path = os.path.join(os.path.dirname(__file__),
                                       'pscheduler-limits-validate.json')
        # TODO: Throw something nicer than IOError if this fails.
        validation_file = open(validation_path, 'r')
        # NOTE: Don't max_schema this.  The limit validation file is
        # tied to this module.
        try:
            validation = pscheduler.json_load(validation_file)
        except Exception as ex:
            raise ValueError("Invalid validation file: %s" % (str(ex)))
        finally:
            validation_file.close()

        #
        # Inhale the source and validate it
        #

        if type(source) is str or type(source) is unicode:
            source = open(source, 'r')
        elif type(source) is file:
            pass  # We're good with this.
        else:
            raise ValueError("Source must be a file or path")

        # At this point, source is a file.

        assert type(source) is file
        limit_config = pscheduler.json_load(source)

        valid, message = pscheduler.json_validate(limit_config, validation)

        if not valid:
            raise ValueError("Invalid limit file: %s" % message)

        #
        # Set up all of the stages
        #

        self.identifiers  = IdentifierSet(limit_config['identifiers'])
        self.classifiers  = ClassifierSet(limit_config['classifiers'],
                                          self.identifiers)
        self.rewriter     = Rewriter(limit_config['rewrite']) \
                            if 'rewrite' in limit_config else None
        self.limits       = LimitSet(limit_config['limits'])
        self.applications = ApplicationSet(limit_config['applications'],
                                           self.classifiers, self.limits)

        try:
            self.prioritizer = Prioritizer(limit_config["priority"])
        except KeyError:
            self.prioritizer = None


    def process(self, task, hints, rewrite=True, prioritize=False):
        """Evaluate a proposed task against the full limit set.

        If the task has no 'run_schedule' section it will be assumed that
        is being evaluated on all other parameters except when it
        runs.  (This will be used for restricting submission of new
        tasks.)

        Arguments:
            task - The proposed task, with run_schedule if there's a run time
            hints - A hash of the hints to be used in identification
            rewrite - True if the rewriter should be applied
            prioritize - True to prioritize the task

        Returns a tuple containing:
            passed - True if the proposed task passed the limits applied
            limits - A list of the limits that passed
            diags - A textual summary of how the conclusion was reached
            task - The task, after rewriting or None if unchanged
            priority - Integer priority or None of not calculated
        """

        if self.inert:
            return True, [], "No limits were applied", None, None

        # TODO: Should this be JSON, or is text sufficient?
        diags = []

        if hints is not None and len(hints) > 0:
            diags.append("Hints:")
            diags.extend([
                pscheduler.indent("%s: %s" % (item, str(hints[item])))
                for item in sorted(hints)
            ])

        identifications = self.identifiers.identities(hints)
        if not identifications:
            diags.append("Made no identifications.")
            return False, [], '\n'.join(diags), None, None
        diags.append("Identified as %s" % (', '.join(identifications)))

        classifications = self.classifiers.classifications(identifications)
        if not classifications:
            diags.append("Made no classifications.")
            return False, [], '\n'.join(diags), None, None
        diags.append("Classified as %s" % (', '.join(classifications)))

        check_schedule='run_schedule' in task

        re_new_task = None

        if self.rewriter is not None and rewrite:

            try:
                re_changed, re_new_task, re_diags \
                    = self.rewriter(task, classifications)
            except Exception as ex:
                return False, [], "Error while rewriting: %s" % (str(ex)), None, None

            if re_changed:
                diags.append("Rewriter made changes:")
                if len(re_diags):
                    diags += map(lambda s: "  " + s, re_diags)
                else:
                    diags.append("  (Not enumerated)")
                task = re_new_task


        passed, app_limits_passed, app_diags \
            = self.applications.check(task, classifications, check_schedule)

        diags.append(app_diags)
        diags.append("Proposal %s limits" % ("meets" if passed else "does not meet"))

        # If any of the passed applications had no task limits, there
        # should be no limits placed on the run.

        unlimited = len(app_limits_passed) == 0 \
                    or min([ len(item) for item in app_limits_passed ]) == 0


        # Run the prioritizer if there's a need to

        if prioritize and passed and self.prioritizer is not None:
            try:
                priority, pri_diags = self.prioritizer(task, classifications)
            except Exception as ex:
                return False, [], "Error determining priority: %s" % (str(ex)), None, None

            diags.append("Prioritized at priority %d%s" % (
                priority, ":" if len(pri_diags) else "."))
            if len(pri_diags):
                diags += map(lambda s: "  " + s, pri_diags)
        else:
            priority = None



        return passed, \
            [] if (unlimited or not passed) else app_limits_passed, \
            '\n'.join(diags), \
            re_new_task, \
            priority





# Test program

if __name__ == "__main__":

    # TODO: This should refer to a sample file in the distribution
    processor = LimitProcessor('/home/mfeit/tmp/limits-pri')

    passed, limits_passed, diags, rewritten, priority = processor.process(
        {
            "type": "rtt",
            "spec": {
                "schema": 1,
                "count": 50,
                "dest": "www.perfsonar.edu"
            },
            "run_schedule": {
                "start": "2016-06-15T14:33:38-04",
                "duration": "PT20S"
            }
        },
        {
            "#requester": "10.0.0.7",        "#": "Dev VM",
            "#requester": "128.82.4.1",      "#": "Nobody in particular",
            "#requester": "198.51.100.3",    "#": "Hacker",
            "#requester": "62.40.106.13",    "#": "GEANT",
            "#requester": "140.182.44.164",  "#": "IU",
            "requester": "192.52.179.242",   "#": "Internet2",
        })

    print passed
    print limits_passed
    print diags

