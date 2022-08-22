#!/usr/bin/env python3
"""
Tests for the ping module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.ping import parse_ping

class TestPing(PschedTestBase):
    """
    Parse ping tests.
    """

    def test_basic(self):
        """Basic ping output parse test:
        ping -c 5 www.umich.edu"""

        output = """PING 141.211.243.251 (141.211.243.251) 56(84) bytes of data.
64 bytes from 141.211.243.251: icmp_seq=1 ttl=63 time=0.704 ms
64 bytes from 141.211.243.251: icmp_seq=2 ttl=63 time=1.37 ms
64 bytes from 141.211.243.251: icmp_seq=3 ttl=63 time=1.26 ms
64 bytes from 141.211.243.251: icmp_seq=4 ttl=63 time=1.10 ms
64 bytes from 141.211.243.251: icmp_seq=5 ttl=63 time=1.16 ms

--- 141.211.243.251 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4005ms
rtt min/avg/max/mdev = 0.704/1.122/1.372/0.231 ms"""

        parsed_results = parse_ping(output, 5)
        expected_result = {'roundtrips':
                              [{'seq': 1, 'length': 64, 'ip': '141.211.243.251', 'ttl': 63, 'rtt': 'PT0.000704S'},
                               {'seq': 2, 'length': 64, 'ip': '141.211.243.251', 'ttl': 63, 'rtt': 'PT0.00137S'},
                               {'seq': 3, 'length': 64, 'ip': '141.211.243.251', 'ttl': 63, 'rtt': 'PT0.00126S'},
                               {'seq': 4, 'length': 64, 'ip': '141.211.243.251', 'ttl': 63, 'rtt': 'PT0.0011S'},
                               {'seq': 5, 'length': 64, 'ip': '141.211.243.251', 'ttl': 63, 'rtt': 'PT0.00116S'}],
                           'ips': ['141.211.243.251', '141.211.243.251', '141.211.243.251', '141.211.243.251', '141.211.243.251'],
                           'min': 'PT0.000704S',
                           'max': 'PT0.001372S',
                           'mean': 'PT0.001122S',
                           'stddev': 'PT0.000231S'
                          }

        self.assertEqual(parsed_results, expected_result)

    def test_more_options(self):
        """Ping output parse test with more options:
        ping -n -c 3 -i 0.5 -W 0:00:02 -s 100 www.umich.edu"""

        output = """PING 141.211.243.251 (141.211.243.251) 100(128) bytes of data.
108 bytes from 141.211.243.251: icmp_seq=1 ttl=63 time=0.872 ms
108 bytes from 141.211.243.251: icmp_seq=2 ttl=63 time=1.25 ms
108 bytes from 141.211.243.251: icmp_seq=3 ttl=63 time=1.08 ms

--- 141.211.243.251 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 1014ms
rtt min/avg/max/mdev = 0.872/1.072/1.255/0.156 ms"""

        parsed_results = parse_ping(output, 3)
        expected_result = {'roundtrips':
                              [{'seq': 1, 'length': 108, 'ip': '141.211.243.251', 'ttl': 63, 'rtt': 'PT0.000872S'},
                               {'seq': 2, 'length': 108, 'ip': '141.211.243.251', 'ttl': 63, 'rtt': 'PT0.00125S'},
                               {'seq': 3, 'length': 108, 'ip': '141.211.243.251', 'ttl': 63, 'rtt': 'PT0.00108S'}],
                           'ips': ['141.211.243.251', '141.211.243.251', '141.211.243.251'],
                           'min': 'PT0.000872S',
                           'max': 'PT0.001255S',
                           'mean': 'PT0.001072S',
                           'stddev': 'PT0.000156S'}

        self.assertEqual(parsed_results, expected_result)


if __name__ == '__main__':
    unittest.main()
