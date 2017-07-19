"""
tests for the data-is-valid command
"""

import pscheduler
import unittest

class DataIsValidTest(pscheduler.ArchiverDataIsValidUnitTest):
    name = 'syslog'

    """
    Data validation tests.
    """


    def test_schema(self):
        self.assert_cmd('{}')
        self.assert_cmd('{"schema": 1}')
        self.assert_cmd('{"schema": 2}', expected_valid=False)


    def test_ident(self):
        self.assert_cmd('{"ident": "ident"}')


    def test_facility(self):
        for facility in \
            ["kern", "user", "mail", "daemon", "auth", "lpr", "news",
             "uucp", "cron", "syslog", "local0", "local1", "local2",
             "local3", "local4", "local5", "local6", "local7"]:
            self.assert_cmd('{"facility": "%s"}' % (facility))

        self.assert_cmd('{"facility": "invalid"}', expected_valid=False)


    def test_priority(self):
        for priority in \
            ["emerg", "alert", "crit", "err", "warning", "notice",
             "info", "debug"]:
            self.assert_cmd('{"priority": "%s"}' % (priority))

        self.assert_cmd('{"priority": "invalid"}', expected_valid=False)


    def test_additional(self):
        self.assert_cmd('{"invalid-property": 123}', expected_valid=False)



if __name__ == '__main__':
    unittest.main()
