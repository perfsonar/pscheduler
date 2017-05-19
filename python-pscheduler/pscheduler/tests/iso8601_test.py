"""
test for the Iso8601 module.
"""

import datetime
import unittest

from base_test import PschedTestBase

from pscheduler.iso8601 import (
    datetime_as_iso8601,
    iso8601_as_datetime,
    iso8601_as_timedelta,
    timedelta_as_iso8601
)


class TestIso8601(PschedTestBase):
    """
    Iso8601 tests. Verify round trip.
    """

    def test_iso(self):
        """iso dt conversion"""
        now = datetime.datetime.utcnow()

        # TODO: The conversion in the library uses another library
        # that chops out the fractional seconds.  If that's ever
        # fixed, adjust the tests accordingly.
        now = now.replace(microsecond=0)

        # round trip - microsecond accuracy is lost
        iso = datetime_as_iso8601(now)
        isodt = iso8601_as_datetime(iso)

        self.assertEqual(now, isodt)

        iso = 'bogusness'
        with self.assertRaises(ValueError):
            iso8601_as_datetime(iso)

    def test_delta(self):
        """iso delta conversion"""

        tdelt = datetime.timedelta(hours=1)

        isod = timedelta_as_iso8601(tdelt)
        delt = iso8601_as_timedelta(isod)

        self.assertEqual(tdelt, delt)


if __name__ == '__main__':
    unittest.main()
