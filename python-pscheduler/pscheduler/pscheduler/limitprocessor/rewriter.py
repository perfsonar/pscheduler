"""
Processor for Task Rewriting
"""

import copy
import re
import pyjq

from ..jqfilter import *
from ..psjson import *

class Rewriter(object):

    """
    Class that handles rewriting tasks
    """

    PRIVATE_KEY = "__REWRITER_PRIVATE__"

    def __init__(self,
                 transform  # JSON JQTransformSpecification, assumed validated
                 ):

        # We modify this.
        transform = copy.deepcopy(transform)

        if isinstance(transform["script"], list):
            script = "\n".join(transform["script"])
        else:
            script = transform["script"]

        SCRIPT_HEADER = [

            "def classifiers:",
            "  ." + self.PRIVATE_KEY + ".classifiers",
            ";",

            "def classifiers_has($value):",
            "  ." + self.PRIVATE_KEY + ".classifiers",
            "  | contains([$value])",
            ";",

            "def change($message):",
            "  ." + self.PRIVATE_KEY + ".changed = true",
            "  | if $message != null",
            "    then",
            "      ." + self.PRIVATE_KEY + ".diags += [ $message | tostring ]",
           "    else",
            "      .",
            "    end",
            ";",

            "def hint($name):",
            "  ." + self.PRIVATE_KEY + ".hints[$name]",
            ";",

            "def reject($message):",
            "  error(\"Task rejected: \" + ($message | tostring))",
            ";",

            "def __END_HEADER__:",
            "  .",
            ";",
            "__END_HEADER__ | "
        ]

        # Stuff the entire header onto the first line so errors
        # reflect the line numbers of what the user provided.
        
        transform["script"] = ' '.join(SCRIPT_HEADER) + script

        self.transform = JQFilter(
            filter_spec=transform,
            args=transform.get("args", {}),
            groom=True,
            strip_errors_to='__END_HEADER__ | '
        )


    def __call__(self, proposal, classifiers):
        """
        Rewrite the task given the classifiers.  Returns a tuple
        containing the rewritten task and an array of diagnostic
        messages.

        Returns a tuple containing a boolean indicating whether or not
        the task was changed, the revised task and an array of strings
        containing diagnostic information.

        The caller is expected to catch and deal with any
        JQRuntimeError that is thrown.
        """

        task_in = copy.deepcopy(proposal["task"])

        # Rewriter-private data
        task_in[self.PRIVATE_KEY] = {
            "classifiers": classifiers,
            "changed": False,
            "diags": [],
            "hints": proposal["hints"]
        }


        result = self.transform(task_in)[0]

        if ("test" not in result) \
           or ("type" not in result["test"]) \
           or (not isinstance(result["test"]["type"], str)) \
           or ("spec" not in result["test"]) \
           or (result["test"]["type"] != proposal["task"]["test"]["type"]):
            raise ValueError("Invalid rewriter result:\n%s" \
                             % json_dump(result))

        changed = result[self.PRIVATE_KEY]["changed"]
        diags = result[self.PRIVATE_KEY]["diags"]
        del result[self.PRIVATE_KEY]

        return changed, result, diags
