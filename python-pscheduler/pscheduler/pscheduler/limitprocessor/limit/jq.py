"""
Limit Class for jq
"""

import pscheduler


# Note that this is done with a string because we don't support args
# or raw output here.
JQ_DATA_VALIDATOR = {
    "$ref": "#/pScheduler/JQTransformSpecification"
}


def jq_data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return pscheduler.json_validate(data, JQ_DATA_VALIDATOR)



class LimitJQ():

    """
    Use JQ to return a true/false for pass/fail
    """

    def __init__(self,
                 data   # Data suitable for this class
    ):

        valid, message = jq_data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.jqfilter = pscheduler.JQFilter(
            data["script"],
            args=data.get("args", {})
            # Don't bother with raw output.  We don't care.
        )


    def checks_schedule(self):
        return False


    def evaluate(self,
                 proposal  # Task and hints
                ):

        """Run the filter against the script.  Expect back one of:

        true/false (Boolean) - Limit passed or failed

        "reason" (String) - Limit failed, string is reason
        """

        try:
            returned = self.jqfilter(proposal["task"])[0]
        except Exception as ex:
            return {
                "passed": False,
                "reasons": [ "Failed to process task: %s" % (str(ex)) ]
                }

        result = {}

        if type(returned) == bool:
            passed = returned
            reason = None if passed else "Unspecified reason"
        elif isinstance(returned, basestring):
            passed = False
            reason = returned
        else:
            passed = False
            reason = "Script returned unusable data"

        result = {"passed": passed}
        if reason is not None:
            result["reasons"] = [reason]

        return result



# A short test program

if __name__ == "__main__":

    test = {
        "type": "trace",
        "spec": {
            "dest": "foo.bar.org",
            "hops": 2
        }
    }

    for script in [
            "\"Script-provided failure reason\"",
            "if .type == \"foo\" then true else \"Wrong test type\" end",
            "if .type == \"trace\" and .spec.hops > 20 then \"Too many hops\" else true end"
    ]:

        data = {
            "script": script,
            "args": {}
        }

        print jq_data_is_valid(data)

        limit = LimitJQ(data)

        print test
        print limit.evaluate(test)
        print
