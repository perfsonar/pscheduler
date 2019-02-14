"""
Processor for Task Rewriting
"""

import copy
import re
import pscheduler
import pyjq

class Rewriter():

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


        script_lines = [

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

            script
            ]

        transform["script"] = script_lines

        self.transform = pscheduler.JQFilter(
            filter_spec=transform,
            args=transform.get("args", {}),
            groom=True
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
           or (not isinstance(result["test"]["type"], basestring)) \
           or ("spec" not in result["test"]) \
           or (result["test"]["type"] != task["test"]["type"]):
            raise ValueError("Invalid rewriter result:\n%s" \
                             % pscheduler.json_dump(result))

        changed = result[self.PRIVATE_KEY]["changed"]
        diags = result[self.PRIVATE_KEY]["diags"]
        del result[self.PRIVATE_KEY]

        return changed, result, diags



# A small test program
if __name__ == "__main__":

    rewriter = Rewriter({
        "script": [

            "import \"pscheduler/iso8601\" as iso;",

            ".",

            "# Exercise the hint function",
            "| change(\"Hello there \\(hint(\"requester\"))\")",

            "| if .test.spec.bandwidth > 99999",
            "  then",
            "    .test.spec.bandwidth = 99999",
            "    | change(\"Throttled bandwidth to 99999\")",
            "  else",
            "    .",
            "  end",

            "| if .schedule.repeat != null"
            "    and iso::duration_as_seconds(.schedule.repeat) < 60",
            "  then",
            "    .schedule.repeat = \"PT1M\"",
            "    | change(\"Bumped repeat to one-minute minimum\")",
            "  else",
            "    .",
            "  end",

            "| if classifiers | contains([\"c2\"])",
            "  then",
            "    change(\"Found a c2 in the classifiers (No real change)\")",
            "  else",
            "    .",
            "  end",

            "| if .test.type == \"trace\"",
            "    and .tools != null",
            "    and (.tools | [ .[] | select(startswith(\"trace\") | not) ] | length) > 0",
            "  then"
            "    .tools = [ .tools[] | select(startswith(\"trace\")) ]",
            "    | change(\"Removed tool selections that don't begin with 'trace'\")",
            "  else"
            "    ."
            "  end"

            # Invalid modifications
            "# | .test.type = \"bogus\"",
            "# | .test.type = 8686",

            # Other oddities
            "# | reject(classifiers)",
            "# | reject(\"Yuck.\")",
            "# | change(null)",
            "# | change(\"This task is brought to you by perfSONAR\")",
            "#END"
            ]
    })

    hints = {
        "requester": "127.0.0.1",
        "server": "127.0.0.1",
        "protocol": "https"
    }

    task = {
        "schema": 1,

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
        "tools": [ "traceroute", "paris-traceroute" ]
    }


    try:
        (changed, new_task, diags)  = rewriter(
            { "task": task, "hints": hints }, ["c1", "c2", "c3"])

        if changed:
            if len(diags):
                print "Diagnostics:"
                print "\n".join(map(lambda s: " - " + s,diags))
            else:
                print "No diagnostics."
            print
            print pscheduler.json_dump(new_task, pretty=True)
        else:
            print "No changes."
    except Exception as ex:
        print "Failed:", ex
