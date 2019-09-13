"""
Limit Class for rundaterange
"""

from ...iso8601 import *
from ...jsonval import *


rundaterange_data_validator = {

    "type": "object",
    "properties": {
        "start": {"$ref": "#/pScheduler/Timestamp" },
        "end": {"$ref": "#/pScheduler/Timestamp" },
        "overlap": {"$ref": "#/pScheduler/Boolean" }
    },
    "additionalProperties": False
    # Nothing is required.
}



def rundaterange_data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return json_validate(data, rundaterange_data_validator)



class LimitRunDateRange(object):

    """
    Limit according to rundaterange criteria
    """

    def __init__(self,
                 data   # Data suitable for this class
                 ):

        
        valid, message = rundaterange_data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.start = iso8601_as_datetime(data['start'])
        self.end = iso8601_as_datetime(data['end'])

        if self.end < self.start:
            raise ValueError("End must be after start.")

        self.overlap = data['overlap'] if 'overlap' in data else False


    def checks_schedule(self):
        return True


    def evaluate(self,
                 proposal  # Task and hints
                 ):

        """Check that the proposed times don't overlap with this limit"""

        start = iso8601_as_datetime(proposal['task']['run_schedule']['start'])
        duration = iso8601_as_timedelta(proposal['task']['run_schedule']['duration'])
        end = start + duration

        subset = start >= self.start and end < self.end

        if self.overlap:
            passed = ( (start <= self.start < end)
                       or (start <= self.end < end)
                       or subset
                   )
        else:
            passed = subset

        result = { "passed": passed }
        if not passed:
            result['reasons'] = [ "Ranges do not match" ]

        return result



# A short test program

if __name__ == "__main__":

    test = {
        "run_schedule": {
            "start": "2015-12-31T23:59:50-04",
            "duration": "PT20S"
            }
        }

    limit = LimitRunDateRange({
        "start": "2015-01-01T00:00:00-04",
        "end":   "2015-12-31T23:59:59-04",
        "overlap": True
    })

    ev = limit.evaluate({ "task": test })
    print(test, ev)
