"""
test for the Interface module.
"""

import unittest

from base_test import PschedTestBase

from pscheduler.interface import interface_affinity, source_interface, LocalIPList


class TestInterface(PschedTestBase):
    """
    Interface tests.
    """

    # TODO: - need to get clarity on how we can standardize this
    # because it looks like these things will vary depending on the network
    # configuration of the machine run the test on.

    # These are wrappers around another library, so a lot of testing
    # is probably not necessary.

    def test_source_interface(self):
        """Interface test"""
        for dest in ["198.6.1.1", "127.0.0.1"]:
            (addr, intf) = source_interface(dest)
            # print "For dest %s, addr = %s, intf = %s" % (dest, addr, intf)

    def test_source_affinity(self):
        """Affinity test"""
        for interface in ["eth0", "eth1", "lo", "eth1.412", "eth0.120"]:
            affinity = interface_affinity(interface)
            # print "interface affinity = %s for %s" % (affinity, interface)

    def test_local_ip(self):
        """Local ip test"""
        localips = LocalIPList(refresh=5)

        self.assertTrue('127.0.0.1' in localips)

        # for addr in ["1.2.3.4", "5.6.7.8", "10.0.0.1", "127.0.0.1"]:
        #     print addr, addr in localips
        #     pass


if __name__ == '__main__':
    unittest.main()
