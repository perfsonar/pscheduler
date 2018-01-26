"""
Limit Class for rundaterange
"""

import pscheduler


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
    return pscheduler.json_validate(data, rundaterange_data_validator)



class LimitRunDateRange():

    """
    Limit according to rundaterange criteria
    """

    def __init__(self,
                 data   # Data suitable for this class
                 ):

        
        valid, message = rundaterange_data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.start = pscheduler.iso8601_as_datetime(data['start'])
        self.end = pscheduler.iso8601_as_datetime(data['end'])

        if self.end < self.start:
            raise ValueError("End must be after start.")

        self.overlap = data['overlap'] if 'overlap' in data else False


    def checks_schedule(self):
        return True


    def evaluate(self,
                 run             # The proposed run
                 ):

        """Check that the proposed times don't overlap with this limit"""

        start = pscheduler.iso8601_as_datetime(run['run_schedule']['start'])
        duration = pscheduler.iso8601_as_timedelta(run['run_schedule']['duration'])
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

    ev = limit.evaluate(test)
    print test, ev
