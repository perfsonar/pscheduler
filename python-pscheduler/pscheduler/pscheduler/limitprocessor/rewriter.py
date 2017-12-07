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
            "def change($message):",
            "  .[\"_changed\"] = true",
            "  | if $message != null",
            "    then",
            "      .[\"_diags\"] += [ $message | tostring ]",
            "    else",
            "      .",
            "    end",
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

        result = self.transform({
            "task": task,
            "classifiers": classifiers,
            "_changed": False,
            "_diags": []
        })[0]

        if ("task" not in result) \
           or ("type" not in result["task"]) \
           or (not isinstance(result["task"]["type"], basestring)) \
           or ("spec" not in result["task"]) \
           or (result["task"]["type"] != task["type"]):
            raise ValueError("Rewriter made an invalid modification.")

        return result["_changed"], result["task"], result["_diags"]



# A small test program
if __name__ == "__main__":

    rewriter = Rewriter({
        "script": [

            "import \"pscheduler/si\" as si;",

            ".",

            "| if .task.spec.bandwidth > 99999",
            "  then",
            "    .task.spec.bandwidth = 99999",
            "    | change(\"Throttled bandwidth to 99999\")",
            "  else",
            "    .",
            "  end",

            # Invalid modifications
            "# | .task.type = \"bogus\"",
            "# | .task.type = 8686",

            # Other oddities
            "| error(\"Yuck.\")",
            "# | change(null)",
            "# | change(\"This task is brought to you by perfSONAR\")",
            "#END"
            ]
    })

    task = {
        "type": "throughput",
        "spec": {
            "dest": "somehost",
            "bandwidth": 100000
        }
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
        print "Failed: ", str(ex)
