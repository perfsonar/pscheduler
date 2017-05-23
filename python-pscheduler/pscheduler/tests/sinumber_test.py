"""
test for the Sinumber module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.sinumber import number_as_si, si_as_number, si_range


class TestSinumber(PschedTestBase):
    """
    Sinumber tests.
    """

    def test_si_as_number(self):
        """SI as number test"""
        conversion_map = {
            '1234': 1234,
            '1234K': 1234000,
            '-1234ki': -1263616,
            '5g': 5000000000,
            '5G': 5000000000,
            '-5Gi': -5368709120,
            '2y': 2000000000000000000000000,
            '12.34': 12.34,
            '123.4K': 123400.0,
            '106.9m': 106900000.0,
            '3.1415P': 3.1415e+15,
        }

        for i in conversion_map.keys():
            self.assertEqual(conversion_map.get(i), si_as_number(i))

        for i in ["ki", "Steak", "123e1", 3.1415]:
            with self.assertRaises(ValueError):
                si_as_number(i)

    def test_number_to_si(self):
        """Number to SI test"""
        conversion_map = {
            1000: ('1000.00', '1000.00', '1000.000'),
            1000000000: ('1000.00M', '953.67Mi', '1000.000M'),
            1234567890: ('1.23G', '1.15Gi', '1.235G'),
            '9.8': ('9.80', '9.80', '9.800'),
            0: ('0.00', '0.00', '0.000'),
        }

        for k, v in conversion_map.items():
            self.assertEqual(number_as_si(k), v[0])
            self.assertEqual(number_as_si(k, base=2), v[1])
            self.assertEqual(number_as_si(k, places=3), v[2])

    def test_si_range(self):
        """SI range test"""
        self.assertEqual(
            si_range(15, default_lower=0),
            {'upper': 15, 'lower': 15})
        self.assertEqual(
            si_range('16ki', default_lower=0),
            {'upper': 16384, 'lower': 16384})
        self.assertEqual(
            si_range({'upper': 1000}, default_lower=0),
            {'upper': 1000, 'lower': 0})
        self.assertEqual(
            si_range({'upper': 2000, 'lower': 1000}, default_lower=0),
            {'upper': 2000, 'lower': 1000})
        self.assertEqual(
            si_range({'upper': '2k', 'lower': 1000}, default_lower=0),
            {'upper': 2000, 'lower': 1000})
        self.assertEqual(
            si_range({'upper': 2000, 'lower': '1k'}, default_lower=0),
            {'upper': 2000, 'lower': 1000})
        self.assertEqual(
            si_range({'upper': '2k', 'lower': '1k'}, default_lower=0),
            {'upper': 2000, 'lower': 1000})

        with self.assertRaises(ValueError):
            si_range({"lower": "2k", "upper": "1k"}, default_lower=0)


if __name__ == '__main__':
    unittest.main()
