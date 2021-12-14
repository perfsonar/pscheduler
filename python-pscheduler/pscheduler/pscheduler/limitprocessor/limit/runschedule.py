"""
Limit Class for runschedule
"""

from ...iso8601 import *
from ...jsonval import *


def wrappable_range_overlaps(start, end, test,
                             wrap_after=59, wrap_to=0,
                             overlap=False
                             ):

    """Figure out whether a range of numbers (specified by 'start' and
    'end') has any overlap with the set of numbers in the set 'test'.
    The numbers in the range may wrap (e.g., the 60th minute wraps to
    the 0th or the 12th month wraps to the 1st); where the wrap occurs
    is governed by 'wrap_after' (default 59) and where it wraps is
    governed by 'wrap_to' (default 0).  If 'overlap' is true, the
    start and end must simply overlap with the test set, otherwise it
    must be completely contained within it.
    """

    if not isinstance(test, set):
        raise ValueError("Type of 'test' must be 'set'")

    if wrap_to >= wrap_after:
        raise ValueError("Unusuable wrap values.")

    if not ( (wrap_to <= start <= wrap_after)
             and (wrap_to <= end <= wrap_after) ):
        raise ValueError("Start and end must be in [%d..%d]" \
                         % (wrap_to, wrap_after))

    ranges = []
    if end >= start:
        ranges.extend(list(range(start, end+1)))
    else:
        ranges.extend(list(range(start, wrap_after+1)))
        ranges.extend(list(range(0, wrap_to+1)))
    ranges = set(ranges)

    return bool(test.intersection(ranges)) if overlap \
        else ranges.issubset(test)




runschedule_data_validator = {

    "local": {

        "Year": {
            "type": "integer",
            "minimum": 1,
            "maximum": 294276
        },
        "YearRange": {
            "type": "object",
            "properties": {
                "lower": { "$ref": "#/local/Year" },
                "upper": { "$ref": "#/local/Year" }
            },
            "additionalProperties": False,
            "required": [ "lower", "upper" ]
        },
        "YearSingleOrRange": {
            "oneOf": [
                { "$ref": "#/local/Year" },
                { "$ref": "#/local/YearRange" },
                ]
        },

        "Month": {
            "type": "integer",
            "minimum": 1,
            "maximum": 12
        },
        "MonthRange": {
            "type": "object",
            "properties": {
                "lower": { "$ref": "#/local/Month" },
                "upper": { "$ref": "#/local/Month" }
            },
            "additionalProperties": False,
            "required": [ "lower", "upper" ]
        },
        "MonthSingleOrRange": {
            "oneOf": [
                { "$ref": "#/local/Month" },
                { "$ref": "#/local/MonthRange" },
                ]
        },

        "Week": {
            "type": "integer",
            "minimum": 1,
            "maximum": 53
        },
        "WeekRange": {
            "type": "object",
            "properties": {
                "lower": { "$ref": "#/local/Week" },
                "upper": { "$ref": "#/local/Week" }
            },
            "additionalProperties": False,
            "required": [ "lower", "upper" ]
        },
        "WeekSingleOrRange": {
            "oneOf": [
                { "$ref": "#/local/Week" },
                { "$ref": "#/local/WeekRange" },
                ]
        },

        "Day": {
            "type": "integer",
            "minimum": 1,
            "maximum": 31
        },
        "DayRange": {
            "type": "object",
            "properties": {
                "lower": { "$ref": "#/local/Day" },
                "upper": { "$ref": "#/local/Day" }
            },
            "additionalProperties": False,
            "required": [ "lower", "upper" ]
        },
        "DaySingleOrRange": {
            "oneOf": [
                { "$ref": "#/local/Day" },
                { "$ref": "#/local/DayRange" },
                ]
        },

        "Weekday": {
            "type": "integer",
            "minimum": 0,
            "maximum": 7
        },
        "WeekdayRange": {
            "type": "object",
            "properties": {
                "lower": { "$ref": "#/local/Weekday" },
                "upper": { "$ref": "#/local/Weekday" }
            },
            "additionalProperties": False,
            "required": [ "lower", "upper" ]
        },
        "WeekdaySingleOrRange": {
            "oneOf": [
                { "$ref": "#/local/Weekday" },
                { "$ref": "#/local/WeekdayRange" },
                ]
        },

        "Hour": {
            "type": "integer",
            "minimum": 0,
            "maximum": 23
        },
        "HourRange": {
            "type": "object",
            "properties": {
                "lower": { "$ref": "#/local/Hour" },
                "upper": { "$ref": "#/local/Hour" }
            },
            "additionalProperties": False,
            "required": [ "lower", "upper" ]
        },
        "HourSingleOrRange": {
            "oneOf": [
                { "$ref": "#/local/Hour" },
                { "$ref": "#/local/HourRange" },
                ]
        },

        "MinuteSecond": {
            "type": "integer",
            "minimum": 0,
            "maximum": 59
        },
        "MinuteSecondRange": {
            "type": "object",
            "properties": {
                "lower": { "$ref": "#/local/MinuteSecond" },
                "upper": { "$ref": "#/local/MinuteSecond" }
            },
            "additionalProperties": False,
            "required": [ "lower", "upper" ]
        },
        "MinuteSecondSingleOrRange": {
            "oneOf": [
                { "$ref": "#/local/MinuteSecond" },
                { "$ref": "#/local/MinuteSecondRange" },
                ]
        },

    },

    "type": "object",
    "properties": {
        "year": {
            "type": "array",
            "items": { "$ref": "#/local/YearSingleOrRange" }
        },
        "month": {
            "type": "array",
            "items": { "$ref": "#/local/MonthSingleOrRange" }
        },
        "week": {
            "type": "array",
            "items": { "$ref": "#/local/weekSingleOrRange" }
        },
        "day": {
            "type": "array",
            "items": { "$ref": "#/local/DaySingleOrRange" }
        },
        "weekday": {
            "type": "array",
            "items": { "$ref": "#/local/WeekdaySingleOrRange" }
        },
        "hour": {
            "type": "array",
            "items": { "$ref": "#/local/HourSingleOrRange" }
        },
        "minute": {
            "type": "array",
            "items": { "$ref": "#/local/MinuteSecondSingleOrRange" }
        },
        "second": {
            "type": "array",
            "items": { "$ref": "#/local/MinuteSecondSingleOrRange" }
        },
        "overlap": { "$ref": "#/pScheduler/Boolean" }
    },
    "additionalProperties": False
}



def runschedule_data_is_valid(data):
    """Check to see if data is valid for this class.  Returns a tuple of
    (bool, string) indicating valididty and any error message.
    """
    return json_validate(data, runschedule_data_validator)



class LimitRunSchedule(object):

    """
    Limit according to runschedule criteria
    """

    def __init__(self,
                 data   # Data suitable for this class
                 ):

        
        valid, message = runschedule_data_is_valid(data)
        if not valid:
            raise ValueError("Invalid data: %s" % message)

        self.overlap = data['overlap'] if 'overlap' in data else False

        # Turn numbers and ranges into one flat set

        self.matches = {}

        for flatten in [ "year", "month", "week", "weekday",
                         "day", "hour", "minute", "second" ]:
            if flatten not in data:
                continue
            value_list = []
            for item in data[flatten]:
                if isinstance(item, dict):
                    value_list.extend(list(range(item['lower'], item['upper']+1)))
                else:
                    value_list.append(item)

            self.matches[flatten] = set(value_list)



    def checks_schedule(self):
        return True


    def evaluate(self,
                 proposal  # Task and hints
                 ):

        """Check that the proposed times don't overlap with this limit"""

        start = iso8601_as_datetime(proposal['task']['run_schedule']['start'])
        duration = iso8601_as_timedelta(proposal['task']['run_schedule']['duration'])
        end = start + duration

        # Python's datetime doesn't have methods to get this.  Bravo.
        start_week = start.isocalendar()[1]
        end_week = end.isocalendar()[1]

        match_failures = []

        for name, lower, upper, wrap_after, wrap_to in [
                # Feel free to resurrect me if this ever wraps.  :-)
                ('year', start.year, end.year, 294276, 1),
                ('month', start.month, end.month, 12, 1),
                ('week', start_week, end_week, 53, 1),
                ('weekday', start.isoweekday(), end.isoweekday(), 7, 1),
                ('day', start.day, end.day, 31, 1),
                ('hour', start.hour, end.hour, 23, 0),
                ('minute', start.minute, end.minute, 59, 0),
                ('second', start.second, end.second, 59, 0)
                ]:

            # Don't bother matching things that weren't specified
            if name not in self.matches:
                continue

            print("CHECK", name, lower, upper, wrap_after, wrap_to)

            if not wrappable_range_overlaps(lower, upper, self.matches[name],
                                            wrap_after=wrap_after,
                                            wrap_to=wrap_to,
                                            overlap=self.overlap):
                match_failures.append(name)

        result = { "passed": not match_failures }
        if match_failures:
            result['reasons'] = [ "Mismatch on " + mis
                                  for mis in match_failures ]

        return result



# A short test program

if __name__ == "__main__":

    test = {
        "run_schedule": {
            "start": "2015-12-31T23:59:50-04",
            "duration": "PT20S"
            }
        }

    limit = LimitRunSchedule({
#        "year": [ 2015, 2016, 2017, 2018 ],
#        "month": [ { "lower": 1, "upper": 6 } ],
#        "week": [],
#        "day": [],
#        "weekday": [ { "lower": 3, "upper": 6 } ],
#        "hour": [3, 4, { "lower": 7, "upper": 11 } ],
        "minute": [ 12,34 ],
#        "second": [],
#        "overlap": False
    })


    ev = limit.evaluate({ "task": test })
    print(test, ev)
