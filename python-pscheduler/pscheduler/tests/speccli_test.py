"""
test for the Speccli module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.speccli import speccli_build_args


class TestSpeccli(PschedTestBase):
    """
    Speccli tests.
    """

    def test_speccli(self):
        """Speccli test"""
        args = dict(foo='bar', baz=False)

        ret = speccli_build_args(args, strings=[('foo', 'foo')], bools=[('baz', 'baz')])
        self.assertEqual(ret, ['--foo', 'bar', '--no-baz'])


if __name__ == '__main__':
    unittest.main()
