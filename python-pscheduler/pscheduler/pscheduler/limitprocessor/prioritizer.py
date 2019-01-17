"""
Processor for Task Task Prioritization
"""

import copy
import re
import pscheduler
import pyjq

class Prioritizer():

    """
    Class that handles determining priority
    """

    PRIVATE_KEY = "__PRIORITIZER_PRIVATE__"

    def __init__(self,
                 transform  # JSON JQTransformSpecification, assumed validated
                 ):

        # We modify this.
        transform = copy.deepcopy(transform)

        if isinstance(transform["script"], list):
            script = "\n".join(transform["script"])
        else:
            script = transform["script"]


        # Insert our function definition(s)
        script_lines = [

            "def classifiers:",
            "  ." + self.PRIVATE_KEY + ".classifiers",
            ";",

            "def classifiers_has($value):",
            "  ." + self.PRIVATE_KEY + ".classifiers",
            "  | contains([$value])",
            ";",

            "def default:",
            "  0"
            ";",

            # This will be embedded in the task.
            "def requested:",
            "  .priority",
            ";",

            "def note($message):",
            "  if $message != null",
            "  then",
            "    ." + self.PRIVATE_KEY + ".diags += "
            "       [ \"\\($message | tostring)\" ]"
            "  else",
            "    .",
            "  end",
            ";",

            "def priority:",
            "  ." + self.PRIVATE_KEY + ".priority",
            ";",

            "def set($value; $message):",
            "  # TODO: Must be an integer",
            "  ." + self.PRIVATE_KEY + ".priority = $value",
            "  | note(\"\\($message)  (Set to \\($value))\")",
            ";",

            "def adjust($value; $message):",
            "  # TODO: Must be an integer",
            "  ." + self.PRIVATE_KEY + ".priority += $value",
            "  | note(\"\\($message)  (\\(if $value > 0 then \"Added\" else \"Subtracted\" end) \\($value | length) to \\(."
            + self.PRIVATE_KEY + ".priority))\")",
            ";",

            script
            ]

        transform["script"] = script_lines

        self.transform = pscheduler.JQFilter(
            filter_spec=transform,
            args=transform.get("args", {}),
            groom=True
        )


    def __call__(self, task, classifiers):
        """
        Determine what the priority will be.

        Returns an integer.

        The caller is expected to catch and deal with any
        JQRuntimeError that is thrown.
        """

        task_in = copy.deepcopy(task)

        # Rewriter-private data
        task_in[self.PRIVATE_KEY] = {
            "classifiers": classifiers,
            "priority": 0,
            "diags": []
        }


        result = self.transform(task_in)[0]

        try:
            priority = result[self.PRIVATE_KEY]["priority"]
            diags = result[self.PRIVATE_KEY]["diags"]
        except KeyError:
            raise ValueError("Prioritizer destroyed private data")

        return priority, diags



# A small test program
if __name__ == "__main__":

    prioritizer = Prioritizer({
        "script": [

            ".",

            "# Start with the lower of the requested and default priorities",
            "| set([default, requested] | min; \"Initial priority\")",

	    "# Friendly requesters get a small bump in priority.",
	    "| if classifiers_has(\"friendlies\")",
            "  then adjust(5; \"Friendly requester\") else . end",

	    "# Knock everyone off their high horses just because.",
	    "| adjust(-1; \"We don't like you.\")",

	    "# Allow at least the requested priority for those who are",
	    "# allowed to do so.  Do this last in case things done",
	    "# above push the priority higher than was requested",
	    "| if classifiers_has(\"priority-positive\")",
	    "  and requested and requested > priority"
	    "  then set(requested; \"High requested priority\")",
            "  else . end",

	    "# The end.  (This takes care of the no-comma-at-end problem)"

            ]
    })


    task = {
        "schema": 3,

        "lead-bind": "127.0.0.1",
        "schedule": {
            "max-runs": 3,
            "repeat": "PT10S",
            "slip": "PT5M"
        },
        "test": {
            "spec": {
                "dest": "www.perfsonar.net",
                "schema": 1
            },
            "type": "trace"
        },
        "tools": [ "traceroute", "paris-traceroute" ],
        "priority": -86
    }


    try:
        print "Priority", prioritizer(task, ["friendlies", "priority-positive"])
    except Exception as ex:
        print "Failed:", ex
