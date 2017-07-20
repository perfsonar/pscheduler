"""
tests for the result-format command
"""

import pscheduler
import unittest

class ResultFormatTest(pscheduler.TestResultFormatUnitTest):
    name = 'latencybg'
    
    def test_format(self):
        #test invalid format
        self.assert_formatted_output("text/html", "{}", expected_status=1, 
            expected_stderr="Unsupported format 'text/html'\n"
        )
        #test bad json
        self.assert_formatted_output("text/plain", "{}", expected_status=1, 
            expected_stderr="Missing 'result' key in input passed to result-format\n"
        )
        #test a valid result
        input = '{"result": {"max-clock-error": 0.27000000000000002, "packets-duplicated": 0, "succeeded": true, "histogram-latency": {"2.72": 4, "2.80": 2, "2.81": 1, "88.21": 1, "2.74": 3, "2.77": 7, "2.53": 11, "2.52": 3, "2.51": 4, "2.57": 54, "2.56": 30, "2.55": 30, "2.54": 25, "2.71": 12, "2.70": 8, "2.59": 43, "2.58": 52, "2.75": 9, "32.87": 1, "27.91": 1, "2.76": 10, "2.79": 4, "2.78": 2, "51.17": 1, "2.68": 6, "2.69": 9, "2.66": 18, "2.67": 17, "2.64": 36, "2.65": 27, "2.62": 37, "2.63": 39, "2.60": 50, "2.61": 38, "2.73": 5}, "histogram-ttl": {"252": 600}, "packets-sent": 600, "packets-reordered": 0, "packets-lost": 0, "packets-received": 600, "schema": 1}}'
        expected_stdout = """
Packet Statistics
-----------------
Packets Sent ......... 600 packets
Packets Received ..... 600 packets
Packets Lost ......... 0 packets
Packets Duplicated ... 0 packets
Packets Reordered .... 0 packets

One-way Latency Statistics
--------------------------
Delay Median ......... 2.60 ms
Delay Minimum ........ 2.51 ms
Delay Maximum ........ 88.21 ms
Delay Mean ........... 2.93 ms
Delay Mode ........... 2.57 ms 
Delay 25th Percentile ... 2.57 ms
Delay 75th Percentile ... 2.64 ms
Delay 95th Percentile ... 2.76 ms
Max Clock Error ...... 0.27 ms
Common Jitter Measurements:
    P95 - P50 ........ 0.16 ms
    P75 - P25 ........ 0.07 ms
    Variance ......... 18.64 ms
    Std Deviation .... 4.32 ms
Histogram:
    2.51 ms: 4 packets
    2.52 ms: 3 packets
    2.53 ms: 11 packets
    2.54 ms: 25 packets
    2.55 ms: 30 packets
    2.56 ms: 30 packets
    2.57 ms: 54 packets
    2.58 ms: 52 packets
    2.59 ms: 43 packets
    2.60 ms: 50 packets
    2.61 ms: 38 packets
    2.62 ms: 37 packets
    2.63 ms: 39 packets
    2.64 ms: 36 packets
    2.65 ms: 27 packets
    2.66 ms: 18 packets
    2.67 ms: 17 packets
    2.68 ms: 6 packets
    2.69 ms: 9 packets
    2.70 ms: 8 packets
    2.71 ms: 12 packets
    2.72 ms: 4 packets
    2.73 ms: 5 packets
    2.74 ms: 3 packets
    2.75 ms: 9 packets
    2.76 ms: 10 packets
    2.77 ms: 7 packets
    2.78 ms: 2 packets
    2.79 ms: 4 packets
    2.80 ms: 2 packets
    2.81 ms: 1 packets
    27.91 ms: 1 packets
    32.87 ms: 1 packets
    51.17 ms: 1 packets
    88.21 ms: 1 packets

TTL Statistics
--------------
TTL Median ........... 252.00 
TTL Minimum .......... 252.00 
TTL Maximum .......... 252.00 
TTL Mean ............. 252.00 
TTL Mode ............. 252.00 
TTL 25th Percentile ... 252.00 
TTL 75th Percentile ... 252.00 
TTL 95th Percentile ... 252.00 
Histogram:
    252: 600 packets
        """
        self.assert_formatted_output("text/plain", input, expected_stdout=expected_stdout)
        
if __name__ == '__main__':
    unittest.main()
