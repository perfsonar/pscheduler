#!/usr/bin/env python3
"""
Test for IdentifierSet
"""

import unittest

from test_base import PschedTestBase
from pscheduler.limitprocessor.identifierset import *

class TestIdentifierSet(PschedTestBase):
    """
    Test for IdentifierSet
    """
    def test_IdentifierSet(self):
        
        hints = {
            "requester": "10.0.0.7",
            "server": "10.0.0.7",
            "protocol": "https"
        }

        iset = IdentifierSet([
            {
                "name": "everybody",
                "description": "An identifier that always identifies",
                "type": "always",
                "data": { }
            },
            {
                "name": "nobody",
                "description": "An identifier that never identifies",
                "type": "always",
                "data": { },
                "invert": True
            },
            {
                "name": "local-interface",
                "description": "Requests from local interfaces",
                "type": "localif",
                "data": { }
            },
            {
                "name": "private-ip",
                "description": "Private IP Blocks per RFCs 1918 and 4193",
                "type": "ip-cidr-list",
                "data": {
                    "cidrs": [
                        "10.0.0.0/8",
                        "172.16.0.0/12",
                        "192.168.0.0/16",
                        "fd00::/8"
                    ]
                }
            },
            {
                "name": "secure-user",
                "description": "Request arrived using a secure protocol",
                "type": "hint",
                "data": {
                    "hint": "protocol",
                    "match": {
                        "style": "exact",
                        "match": "https"
                    }
                }
            }
        ])

        self.assertEqual(iset.identities(hints)[0], ['everybody', 'private-ip', 'secure-user'])

if __name__ == '__main__':
    unittest.main()

