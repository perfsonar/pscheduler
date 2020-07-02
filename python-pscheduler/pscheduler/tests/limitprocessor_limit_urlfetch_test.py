#!/usr/bin/env python3
"""
Test for urlfetch limit
"""

import tempfile
import unittest

from base_test import PschedTestBase

from pscheduler.limitprocessor.limit.urlfetch import *


LIMIT = {
    "url": "filled-in-later",
    "timeout": "PT3S",
    "params": { "foo": 123, "bar": 456 },
    "params-transform": {
        "script": ".params.baz = 789 | .params.test = 9999 | .params.hinted = hint(\"requester\")"
    },
    "headers": { "Content-Type": "application/json" },
    "headers-transform": {
        "script": [
            "  .headers.\"X-Argument\" = $foobar",
            "| .headers.\"X-Hinted\" = hint(\"requester\")"
        ],
        "args": {
            "foobar": "Arg-U-Ment"
        }
    }
}


URL_RETURN = """
{
  "passed": true,
  "message": "We approve."
}
"""


class TestLimitprocessorLimitURLFetch(PschedTestBase):
    """
    Test the Limit
    """

    def test_data_is_valid(self):
        """Limit Processor / Limit URLFetch / Data Validation"""

        self.assertEqual(urlfetch_data_is_valid(LIMIT), (True, "OK"))
        self.assertEqual(urlfetch_data_is_valid({}), (False, "At /: 'url' is a required property"))



    def test_limit(self):
        """Limit Processor / Limit URLFetch / Limit"""


        # TODO: The code below causes Python 3 to crash.

        return

        with tempfile.NamedTemporaryFile() as urlfile:
            urlfile.write(bytes(URL_RETURN, "ascii"))
            urlfile.flush()

            LIMIT["url"] = "file://" + urlfile.name

            print(LIMIT)
            limit = LimitURLFetch(LIMIT)

            # TODO: Finish this.
            self.AssertEqual(1,2)







if __name__ == '__main__':
    unittest.main()
