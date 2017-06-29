#!/usr/bin/python

import unittest
import pscheduler
import json
import os
import sys


class TestLimitPasses(unittest.TestCase):

    path = os.path.dirname(os.path.realpath(__file__))
    (local_addr, local_intf) = pscheduler.source_interface("www.perfsonar.net")

    # TODO: change this to unittest.skip once EL6 has gone away
    if not local_addr:
        print "Unable to find routable address to reach www.perfsonar.net, skipping test"
        sys.exit(1)

    
    def get_output(self, limit, spec, check_success=True):

        args = {"limit": limit, "spec": spec}

        print json.dumps(args)
        
        # actually run cli-to-spec with the input
        code, stdout, stderr = pscheduler.run_program("%s/../limit-passes" % self.path,
                                                      stdin = json.dumps(args))

        print stdout
        print stderr
        
        if check_success:
            # make sure it succeeded
            self.assertEqual(code, 0)

        # get json out
        if code != 0:
            return stderr
        return json.loads(stdout)
        

    def test_limit_duration(self):
        return
        # unknown field
        limit = {
            'duration': {
                'range': {
                'upper': 'PT60S', 'lower': 'PT10S'
                }
            }
        }
            
        spec = {
            "dest": "10.0.2.4",
            "schema": 1,
            "duration": "PT20S"
        }
        
        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], True, "passed")

        # bad duration
        spec["duration"] = "PT5M"
        args = ["--bandwidth", "butterfly"]
        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], False, "failed")
        self.assertEqual(len(data["errors"]), 1, "got 1 error back")


    def test_limit_source(self):
        return
        # test auto source discovery
        # TODO: it's possible this will work on a machine
        # where its address is in the subnet below
        limit = {
            "source": {
                "cidr": ["192.168.254.0/24"]
                }
            }

        spec = {
            "dest": "10.0.0.1",
            "schema": 1
            }

                
        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], False, "failed, not allowed source")


        # manually set source, should work now
        spec['source'] = "192.168.254.10"
        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], True, "allowed source")


    def test_limit_dest(self):
        return
        limit = {
            "dest": {
                "cidr": ["%s/32" % self.local_addr]
            }
        }

        spec = {
            "dest": self.local_addr,
            "schema": 1
        }


        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], True, "allowed dest")


        # pretend this is another interface on the computer
        # and we're trying to limit throughput to only that
        limit['dest']['cidr'][0] = "1.2.3.4/32"

        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], False, "not allowed dest")


        # modify the spec so that we're no longer the dest, shouldn't care anymore
        # since it should assume we are now the source since 1.2.3.4 isn't
        # in any interfaces
        spec = {
            "dest": "1.2.3.4"
        }

        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], True, "not allowed dest")

        
    def test_limit_dest_hostname(self):
        return
        limit = {
            "source": {
                "cidr": ["%s/32" % self.local_addr]
            }
        }

        spec = {
            "dest": "www.perfsonar.net",
            "schema": 1
        }


        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], True, "succeeds because only source is limited")

        spec['source'] = self.local_addr
        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], True, "succeeds because is source in the limit")


        # pretend other interface on the same host
        spec['source'] = "1.2.3.4"
        data = self.get_output(limit, spec, check_success=False)
        self.assertEqual(data["passes"], False, "fails because source is limited and wrong")
        self.assertEqual(len(data["errors"]), 1, "got 1 error")


    def test_limit_ip_version_source(self):
        return
        limit = {
            "source": {
                "cidr": ["%s/32" % self.local_addr]
            }
        }

        spec = {
            "dest": "192.168.254.254",
            "ip-version": 4,
            "schema": 1
        }


        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], True, "succeeds because ip-version is manually set")

        spec['ip-version'] = 6
        data = self.get_output(limit, spec, check_success=False)
        self.assertEqual("Unable to determine source interface to get to 192.168.254.254" in data,
                         True,
                         "fails forced ip-version is incompatible when trying to find source address")

        spec['ip-version'] = 4
        spec['source'] = self.local_addr
        data = self.get_output(limit, spec, check_success=False)
        self.assertEqual(data["passes"], True, "passes source and ip-version spec")


    def test_limit_ip_version_dest(self):

        limit = {
            "dest": {
                # TODO - this is the ipv4 address of www.perfsonar.net
                # a better system might be to look this up dynamically
                "cidr": ["%s/32" % self.local_addr]
            }
        }

        spec = {
            "dest": self.local_addr,            
            "ip-version": 6,
            "schema": 1
        }


        data = self.get_output(limit, spec, check_success=False)
        self.assertEqual("Unable to resolve" in data, True, "fails because unable to resolve IP address")

        spec['ip-version'] = 4
        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], True, "succeeds because dest is v4")

        spec['source'] = "www.perfsonar.net"
        del spec['ip-version']
        data = self.get_output(limit, spec)
        self.assertEqual(data["passes"], True, "succeeds because dest is v4")

        
if __name__ == "__main__":
    unittest.main()
