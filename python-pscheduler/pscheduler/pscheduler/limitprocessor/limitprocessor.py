"""
pScheduler Limit Processor
"""

import io
import os

from ..exception import *
from ..jsonval import *
from ..psjson import *
from ..text import *

from .identifierset  import IdentifierSet
from .classifierset  import ClassifierSet
from .rewriter       import Rewriter
from .limitset       import LimitSet
from .applicationset import ApplicationSet
from .prioritizer    import Prioritizer

class LimitProcessor(object):

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
            validation = json_load(validation_file)
        except Exception as ex:
            raise ValueError("Invalid validation file: %s" % (str(ex)))
        finally:
            validation_file.close()

        #
        # Inhale the source and validate it
        #

        if isinstance(source, str):
            source = open(source, 'r')
        elif isinstance(source, io.IOBase):
            pass  # We're good with this.
        else:
            raise ValueError("Source must be a file or path")

        # At this point, source is a file.

        assert isinstance(source, io.IOBase)
        limit_config = json_load(source)

        if not isinstance(limit_config, dict):
            raise ValueError("Limit configuration must be an object.")

        schema = limit_config.get("schema", 1)
        temp_schema = {
            "local": validation["local"],
            "$ref":"#/local/LimitConfiguration_V%d" % schema
        }

        valid, message = json_validate(limit_config, temp_schema)

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


    def _process(self, task, hints, rewrite=True, prioritize=False):
        """Wrapped function; see process()."""

        if self.inert:
            return True, [], "No limits were applied", None, None

        # TODO: Should this be JSON, or is text sufficient?
        diags = []

        if hints is not None and len(hints) > 0:
            diags.append("Hints:")
            diags.extend([
                indent("%s: %s" % (item, str(hints[item])))
                for item in sorted(hints)
            ])

        # Everything we know about what's being proposed
        proposal = {
            "hints": hints,
            "task": task,
        }

        #
        # Identification
        #

        identifications = self.identifiers.identities(hints)
        if not identifications:
            diags.append("Made no identifications.")
            return False, [], '\n'.join(diags), None, None
        diags.append("Identified as %s" % (', '.join(identifications)))

        #
        # Classification
        #

        classifications = self.classifiers.classifications(identifications)
        if not classifications:
            diags.append("Made no classifications.")
            return False, [], '\n'.join(diags), None, None
        diags.append("Classified as %s" % (', '.join(classifications)))

        check_schedule='run_schedule' in task

        re_new_task = None

        #
        # Rewriting
        #

        if self.rewriter is not None and rewrite:

            try:
                re_changed, re_new_task, re_diags \
                    = self.rewriter(proposal, classifications)
            except Exception as ex:
                return False, [], "Error while rewriting: %s" % (str(ex)), None, None

            if re_changed:
                diags.append("Rewriter made changes:")
                if len(re_diags):
                    diags += ["  " + s for s in re_diags]
                else:
                    diags.append("  (Not enumerated)")
                task = re_new_task


        #
        # Applications
        #

        passed, app_limits_passed, app_diags \
            = self.applications.check(proposal, classifications, check_schedule)

        diags.append(app_diags)
        diags.append("Proposal %s limits" % ("meets" if passed else "does not meet"))

        # If any of the passed applications had no task limits, there
        # should be no limits placed on the run.

        unlimited = len(app_limits_passed) == 0 \
                    or min([ len(item) for item in app_limits_passed ]) == 0


        #
        # Priorities
        #

        if prioritize and passed and self.prioritizer is not None:
            try:
                priority, pri_diags = self.prioritizer(task, classifications)
            except Exception as ex:
                return False, [], "Error determining priority: %s" % (str(ex)), None, None

            if priority is None:
                return False, [], "Prioritizer produced no result", None, None

            requested_priority = task.get("priority", None)
            if requested_priority is not None:
                requested_message = " %d requested," % (requested_priority)
            else:
                requested_message =""

            diags.append("Priority%s set at %d%s" % (
                requested_message, priority, ":" if len(pri_diags) else "."))
            if len(pri_diags):
                diags += ["  " + s for s in pri_diags]
        else:
            priority = 0
            diags.append("Priority set to default of %d" % (priority))



        return passed, \
            [] if (unlimited or not passed) else app_limits_passed, \
            '\n'.join(diags), \
            re_new_task, \
            priority



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

        This is an exception-safe wrapper around _process().
        """

        try:
            return self._process(task, hints, rewrite, prioritize)
        except Exception as ex:
            diags = 'Failed to process limits: processor threw an exception.\n\n' \
                    f'{formatted_exception(ex)}\n\n' \
                    'Please report this as a bug.'
            return (False, [], diags, task, None)



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

    print(passed)
    print(limits_passed)
    print(diags)

