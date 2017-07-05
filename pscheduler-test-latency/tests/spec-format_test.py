"""
tests for the spec-format command
"""

import pscheduler

class SpecFormatTest(pscheduler.TestSpecFormatUnitTest):
    name = 'latency'
    
    def test_format(self):
        #test invalid format
        self.assert_formatted_output("text/html", "{}", expected_status=1, 
            expected_stderr="Unsupported format 'text/html'\n"
        )
        #test a valid result
        input = '{"source": "antg-staging.es.net", "dest": "lbl-owamp-v6.es.net", "flip": true, "ip-version": 6, "packet-interval": 0.001, "packet-count": 600, "schema": 1}'
        expected_stdout = """
Source   ............ antg-staging.es.net
Destination ......... lbl-owamp-v6.es.net
Packet Count ........ 600
Packet Interval ..... 0.001
Packet Timeout. ..... Not Specified
Packet Padding. ..... Not Specified
Data Ports .......... Not Specified
IP TOS .............. Not Specified
IP Version .......... IPv6
Bucket Width ........ Not Specified
Output Raw Packets .. Not Specified
Flip Mode ........... True
        """
        self.assert_formatted_output("text/plain", input, expected_stdout=expected_stdout)
        
if __name__ == '__main__':
    unittest.main()
