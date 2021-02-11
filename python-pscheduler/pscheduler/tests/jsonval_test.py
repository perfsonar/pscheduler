#!/usr/bin/env python3
"""
test for the Jsonval module.
"""

import unittest
import sys

from base_test import PschedTestBase

from pscheduler.jsonval import json_validate


class TestJsonval(PschedTestBase):
    """
    Jsonval tests.
    """

    def test_jsonval(self):
        """Test jsonval"""
        sample = {
            "schema": 10,
            "when": "2015-06-12T13:48:19.234",
            "howlong": "PT10M",
            "sendto": "bob@example.com",
            "x-factor": 3.14,
            "protocol": "udp",
            "ipv": 6,
            "ip": "fc80:dead:beef::",
            "archspec": { "data": { "bar": "baz" } },
        }

        schema = {
            "local": {
                "protocol": {
                    "type": "string",
                    "enum": ['icmp', 'udp', 'tcp']
                }
            },
            "type": "object",
            "properties": {
                "schema": {"$ref": "#/pScheduler/Cardinal"},
                "when": {"$ref": "#/pScheduler/Timestamp"},
                "howlong": {"$ref": "#/pScheduler/Duration"},
                "sendto": {"$ref": "#/pScheduler/Email"},
                "ipv": {"$ref": "#/pScheduler/ip-version"},
                "ip": {"$ref": "#/pScheduler/IPAddress"},
                "protocol": {"$ref": "#/local/protocol"},
                "x-factor": {"type": "number"},
                "archspec": {"$ref": "#/pScheduler/ArchiveSpecification"},

            },
            "required": ["sendto", "x-factor"]
        }

        # missing an attr
        valid, message = json_validate(sample, schema)

        self.assertFalse(valid)

        self.assertEqual(message, "At /archspec: 'archiver' is a required property")

        # add it in now
        sample['archspec']['archiver'] = 'tar'

        valid, message = json_validate(sample, schema)

        self.assertEqual((valid, message), (True, 'OK'))


        # Bad schemas

        valid, message = json_validate(sample, schema, max_schema=5)
        self.assertEqual((valid, message), (False, "Schema version 10 is not supported (highest is 5)."))

        sample['schema'] = "This is bad."
        valid, message = json_validate(sample, schema, max_schema=5)
        self.assertEqual((valid, message), (False, "Schema value must be an integer."))


if __name__ == '__main__':
    unittest.main()
