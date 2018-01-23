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


        # One quirk of jq is that imports have to be at the top of the
        # file.  Pull any in the script out and move them to the top
        # before we define our function or any user code.

        import_include = r"((import|include) [^;]+;)"


        # Put imports and includes at the top
        lines = map(
            lambda x: x[0],
            re.findall(import_include, script)
        )

        # Insert our function definition(s)
        lines.extend([

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

            "def reject($message):",
            "  error(\"Task rejected: \" + ($message | tostring))",
            ";",

            ])

        # Add the rest of the script without the imports and includes
        lines.append(re.sub(import_include, "", script))

        transform["script"] = lines

        self.transform = pscheduler.JQFilter(
            filter_spec=transform,
            args=transform.get("args", {}),
        )


    def __call__(self, task, classifiers, validate_callback=None):
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

        task_in = copy.deepcopy(task)

        # Rewriter-private data
        task_in[self.PRIVATE_KEY] = {
            "classifiers": classifiers,
            "changed": False,
            "diags": []
        }


        result = self.transform(task_in)[0]

#        print "RES", pscheduler.json_dump(result, pretty=True)

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
                "dest": "www.notonthe.net",
                "schema": 1
            },
            "type": "trace"
        },
        "tools": [ "traceroute", "paris-traceroute" ]
    }


    try:
        (changed, new_task, diags)  = rewriter(
            task, ["c1", "c2", "c3"])

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
