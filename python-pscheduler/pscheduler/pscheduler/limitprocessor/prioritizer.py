"""
Processor for Task Task Prioritization
"""

import copy
import re
import pyjq

from ..jqfilter import *

class Prioritizer(object):

    """
    Class that handles determining priority
    """

    PRIVATE_KEY = "__PRIORITIZER_PRIVATE__"

    DEFAULT_PRIORITY = 0

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

            "def default: %d;" % (self.DEFAULT_PRIORITY),

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
            "  | note(\"\\($message)  (\\(if $value > 0 then \"+\" else \"-\" end)\\($value | length))\")",
            ";",

            script
            ]

        transform["script"] = script_lines

        self.transform = JQFilter(
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
            "priority": self.DEFAULT_PRIORITY,
            "diags": []
        }


        result = self.transform(task_in)[0]

        try:
            priority = result[self.PRIVATE_KEY]["priority"]
            diags = result[self.PRIVATE_KEY]["diags"]
        except KeyError:
            raise ValueError("Prioritizer destroyed private data")

        return priority, diags
