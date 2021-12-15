#!/usr/bin/env python3
"""
test for the process module.
"""

import os
import psutil

from base_test import PschedTestBase

from pscheduler.process import (
    process_exists
)


class TestProcess(PschedTestBase):
    """
    Process Tests
    """

    def test_process_exists(self):

        # Our own process should always exist.
        self.assertEqual(process_exists(os.getpid()), True)

        # Find the first empty slot in the table and make sure it doesn't exist.
        for pid in range(1,999999):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                self.assertEqual(process_exists(pid), False)
                break
            except PermissionError:
                pass            # Exists but not ours



    def test_kill_processes(self):
        # TODO: Need to instantiate some processes for this to operate
        # against.
        pass


if __name__ == '__main__':
    unittest.main()
