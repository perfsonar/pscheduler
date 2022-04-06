#!/usr/bin/env python3
"""
test for the Threadsafe module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.threadsafe import ThreadSafeSet
from pscheduler.threadsafe import ThreadWithReturnValue

class TestThreadsafe(PschedTestBase):
    """
    Threadsafe tests.
    """

    def test_safe_set(self):
        """Thread safe set test"""
        tss = ThreadSafeSet()

        num = 10
        half = int(num / 2)

        self.assertEqual(len(tss),0)

        for item in range(0,num):
            tss.add(item)
            self.assertTrue(item in tss)
        self.assertEqual(len(tss), num)

        for item in range(0,half):
            tss.remove(item)
            self.assertTrue(item not in tss)
        self.assertEqual(len(tss),num - half)

        self.assertEqual(tss.items(),list(range(half, num)))


    def test_thread_with_return_value(self):
        """Test ThreadWithReturnValue"""

        def func():
            return "returned-value"

        thread = ThreadWithReturnValue(target=func)
        thread.start()
        self.assertEqual(thread.join(), "returned-value")



if __name__ == '__main__':
    unittest.main()
