"""
tests for the merged-results command
"""

import pscheduler

class MergedResultsTest(pscheduler.ToolMergedResultsUnitTest):
    name = 'powstream'

    def test_merged_results(self):
        #only to check here is that we get back the one item we put in
        #NOTE: There is code for two results but it is not used
        
        #don't really care about the format since code doesn't check it, just care that
        # program runs and we get out what we put in
        results = [{"succeeded": True, "param": 1}]
        self.assert_result_at_index(results, 0)
      
if __name__ == '__main__':
    unittest.main()


