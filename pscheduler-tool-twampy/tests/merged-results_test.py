"""
tests for the merged-results command
"""

import pscheduler
import unittest

class MergedResultsTest(pscheduler.ToolMergedResultsUnitTest):
    name = 'twampy'

    def test_merged_results(self):
        # single result passthrough
        results = [{"succeeded": True, "param": 1}]
        self.assert_result_at_index(results, 0)

    def test_merged_results_two(self):
        # two results, no flip - returns first
        results = [
            {"succeeded": True, "param": 1},
            {"succeeded": True, "param": 2}
        ]
        self.assert_result_at_index(results, 0)

    def test_merged_results_flip(self):
        # two results with flip - returns second
        results = [
            {"succeeded": True, "param": 1},
            {"succeeded": True, "param": 2}
        ]
        self.assert_result_at_index(results, 1, test_spec={"flip": True})

if __name__ == '__main__':
    unittest.main()
