"""
tests for the spec-format command
"""

import pscheduler
import unittest

class SpecFormatTest(pscheduler.TestSpecFormatUnitTest):
    name = 'latency'
    
    def test_format(self):

        #test invalid format
        self.assert_formatted_output("text/unsupported-format", "{}", expected_status=1, 
            expected_stderr="Unsupported format 'text/unsupported-format'\n"
        )

        #test a valid result
        input = '{"source": "antg-staging.es.net", "dest": "lbl-owamp-v6.es.net", "flip": true, "ip-version": 6, "packet-interval": 0.001, "packet-count": 600, "data-ports": { "lower": 1234, "upper": 5678 }, "schema": 1}'
        expected_stdout = """
Source   ............ antg-staging.es.net
Destination ......... lbl-owamp-v6.es.net
Packet Count ........ 600
Packet Interval ..... 0.001
Packet Timeout. ..... Not Specified
Packet Padding. ..... Not Specified
Data Ports .......... 1234 - 5678
IP TOS .............. Not Specified
IP Version .......... 6
Bucket Width ........ Not Specified
Output Raw Packets .. Not Specified
Flip Mode ........... True
Reverse Mode ........ Not Specified
        """
        self.assert_formatted_output("text/plain", input, expected_stdout=expected_stdout)


        #test a valid result
        input = '{"source": "antg-staging.es.net", "dest": "lbl-owamp-v6.es.net", "flip": true, "ip-version": 6, "packet-interval": 0.001, "packet-count": 600, "data-ports": { "lower": 1234, "upper": 5678 }, "schema": 1}'
        expected_stdout = """
<table>
<tr><td>Source</td><td>antg-staging.es.net</td></tr>
<tr><td>Destination</td><td>lbl-owamp-v6.es.net</td></tr>
<tr><td>Packet Count</td><td>600</td></tr>
<tr><td>Packet Interval</td><td>0.001</td></tr>
<tr><td>Packet Timeout</td><td>Not Specified</td></tr>
<tr><td>Packet Padding</td><td>Not Specified</td></tr>
<tr><td>Data Ports</td><td>1234 - 5678</td></tr>
<tr><td>IP TOS</td><td>Not Specified</td></tr>
<tr><td>IP Version</td><td>6</td></tr>
<tr><td>Bucket Width</td><td>Not Specified</td></tr>
<tr><td>Output Raw Packets</td><td>Not Specified</td></tr>
<tr><td>Flip Mode</td><td>True</td></tr>
<tr><td>Reverse Mode</td><td>Not Specified</td></tr>
</table>
        """
        self.assert_formatted_output("text/html", input, expected_stdout=expected_stdout)
        
if __name__ == '__main__':
    unittest.main()
