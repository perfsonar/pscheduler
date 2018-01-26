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
            "  .priority // default",
            ";",

            # This will be embedded in the task.
            "def priority:",
            "  ." + self.PRIVATE_KEY + ".priority",
            ";",

            "def set($value):",
            "  # TODO: Must be an integer",
            "  ." + self.PRIVATE_KEY + ".priority = $value",
            ";",

            "def adjust($value):",
            "  # TODO: Must be an integer",
            "  ." + self.PRIVATE_KEY + ".priority += $value",
            ";",

            "def change($message):",
            "  if $message != null",
            "  then",
            "    ." + self.PRIVATE_KEY + ".diags += "
            "       [ \"\\($message | tostring) (\\(."
                    + self.PRIVATE_KEY + ".priority))\" ]"
            "  else",
            "    .",
            "  end",
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
            "| set([default, requested] | min)",
            "| change(\"Initial priority\")",

	    "# Friendly requesters get a small bump in priority.",
	    "| if classifiers_has(\"friendlies\")",
            "  then adjust(5) | change(\"Friendly requester\") else . end",

	    "# Allow at least the requested priority for those who are",
	    "# allowed to do so.  Do this last in case things done",
	    "# above push the priority higher than was requested",
	    "| if classifiers_has(\"priority-positive\")",
	    "  and requested > priority"
	    "  then set(requested) | change(\"High requested priority\")",
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
