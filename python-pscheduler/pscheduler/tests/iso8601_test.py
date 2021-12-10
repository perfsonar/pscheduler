#!/usr/bin/env python3
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
    timedelta_as_iso8601,
    iso8601_absrel
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
        self.assertRaises(ValueError, iso8601_as_datetime, iso)

    def test_delta(self):
        """iso delta conversion"""

        tdelt = datetime.timedelta(hours=1)

        isod = timedelta_as_iso8601(tdelt)
        delt = iso8601_as_timedelta(isod)

        self.assertEqual(tdelt, delt)


    def test_absrel(self):
        """Absolute/Relative Conversion"""

        # Bogus input
        self.assertRaises(ValueError, iso8601_absrel, "X")  # Too short
        self.assertRaises(ValueError, iso8601_absrel, "BadAbsolute")
        self.assertRaises(ValueError, iso8601_absrel, "-BadNegative")
        self.assertRaises(ValueError, iso8601_absrel, "+BadPositive")
        self.assertRaises(ValueError, iso8601_absrel, 1234)  # Wrong 'when' type
        self.assertRaises(ValueError, iso8601_absrel, "-PT1M", now="WrongNowType")

        # Fake now, so we know what the outcome will be.
        now = iso8601_as_datetime("2020-09-01T12:00:00-00:00")

        # Absolute
        self.assertEqual(iso8601_absrel("2020-09-01T12:00:00-00:00"),
                         iso8601_as_datetime("2020-09-01T12:00:00-00:00"))

        # Relative negative
        self.assertEqual(iso8601_absrel("-PT1M", now=now),
                         iso8601_as_datetime("2020-09-01T11:59:00-00:00"))

        # Relative positive
        self.assertEqual(iso8601_absrel("+PT1M", now=now),
                         iso8601_as_datetime("2020-09-01T12:01:00-00:00"))



if __name__ == '__main__':
    unittest.main()
