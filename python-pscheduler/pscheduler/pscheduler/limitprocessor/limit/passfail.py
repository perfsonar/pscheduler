"""
Limit Class for pass-fail
"""

import pscheduler


passfail_data_validator = {
    "type": "object",
    "properties": {
        "pass": { "$ref": "#/pScheduler/Boolean" },
    },
    "additionalProperties": False,
    "required": [ "pass" ]
}

def passfail_data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return pscheduler.json_validate(data, passfail_data_validator)




class LimitPassFail():

    """
    Limit that passes or fails according to a hard-wired value.
    """

    def __init__(self,
                 data   # Data suitable for this class
                 ):

        
        valid, message = passfail_data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        # Dodges a reserved word
        self.pass_ = data['pass']


    def checks_schedule(self):
        return False


    def evaluate(self,
                 proposal  # Task and hints (ignored here)
                 ):

        """Always return the set value"""

        if self.pass_:
            return { "passed": True }

        return { "passed": False, "reasons": [ "Forced failure" ] }



# A short test program

if __name__ == "__main__":

    passer = LimitPassFail({ "pass": True })
    failer = LimitPassFail({ "pass": False })

    for ip in [ "10.9.8.6", "198.6.1.1", "fd00:dead:beef::1" ]:
        for limit in [ passer, failer ]:
            print(ip, limit.evaluate({}))

