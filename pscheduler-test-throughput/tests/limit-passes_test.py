import pscheduler

import os
from json import dumps

class TestLimitPasses(pscheduler.TestLimitPassesUnitTest):
    name = 'throughput'

    path = os.path.dirname(os.path.realpath(__file__))
    (local_addr, local_intf) = pscheduler.source_interface("www.perfsonar.net")

    # TODO: change this to unittest.skip once EL6 has gone away
    if not local_addr:
        print "Unable to find routable address to reach www.perfsonar.net, skipping test"
        sys.exit(1)

    def test_limit_duration(self):

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
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))
        
        spec["duration"] = "PT05M"
        self.assert_cmd(dumps({"limit": limit, "spec": spec}), expected_valid=False)

    def test_limit_source(self):

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
        self.assert_cmd(
            dumps({"limit": limit, "spec": spec}), 
            expected_valid=False, 
            expected_errors=["address 192.168.1.23 not allowed in source limit"]
        )


        # manually set source, should work now
        spec['source'] = "192.168.254.10"
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))


    def test_limit_dest(self):

        limit = {
            "dest": {
                "cidr": ["{0}/32".format(self.local_addr)]
            }
        }

        spec = {
            "dest": self.local_addr,
            "schema": 1
        }
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))


        # pretend this is another interface on the computer
        # and we're trying to limit throughput to only that
        limit['dest']['cidr'][0] = "1.2.3.4/32"

        self.assert_cmd(dumps({"limit": limit, "spec": spec}), expected_valid=False)


        # modify the spec so that we're no longer the dest, shouldn't care anymore
        # since it should assume we are now the source since 1.2.3.4 isn't
        # in any interfaces
        spec = {
            "dest": "1.2.3.4"
        }
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))

    def test_limit_dest_hostname(self):

        limit = {
            "source": {
                "cidr": ["{0}/32".format(self.local_addr)]
            }
        }

        spec = {
            "dest": "www.perfsonar.net",
            "schema": 1
        }


        self.assert_cmd(dumps({"limit": limit, "spec": spec}))

        spec['source'] = self.local_addr
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))

        # pretend other interface on the same host
        spec['source'] = "1.2.3.4"
        self.assert_cmd(dumps({"limit": limit, "spec": spec}), expected_valid=False)

    def test_limit_ip_version_source(self):

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


        self.assert_cmd(dumps({"limit": limit, "spec": spec}))

        spec['ip-version'] = 6
        self.run_cmd(dumps({"limit": limit, "spec": spec}), expected_status=1, json_out=False)

        spec['ip-version'] = 4
        spec['source'] = self.local_addr
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))


    def test_limit_ip_version_dest(self):

        limit = {
            "dest": {
                # TODO - this is the ipv4 address of www.perfsonar.net
                # a better system might be to look this up dynamically
                "cidr": ["{0}/32".format(self.local_addr)]
            }
        }

        spec = {
            "dest": self.local_addr,            
            "ip-version": 6,
            "schema": 1
        }
        
        self.run_cmd(dumps({"limit": limit, "spec": spec}), expected_status=1, json_out=False)

        spec['ip-version'] = 4
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))

        spec['source'] = "www.perfsonar.net"
        del spec['ip-version']
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))

    def test_limit_endpoint(self):

        limit = {
            "endpoint": {
                "cidr": ["1.2.3.4/32"]
            }
        }

        spec = {
            "dest": self.local_addr,            
            "schema": 1
        }


        self.assert_cmd(dumps({"limit": limit, "spec": spec}), expected_valid=False)

        # add allowed address as source
        spec['source'] = "1.2.3.4"
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))


        # do the same but with dest
        spec = {"dest": "1.2.3.4",
                "source": self.local_addr}
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))


        # do the check with hostname
        limit = {
            "endpoint": {
                "cidr": ["207.75.164.248/32"]
                }
            }
        spec = {"dest": "www.perfsonar.net",
                "source": self.local_addr}
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))

        # should fail if we force v6 since only the v4 is in the endpoint list
        spec['ip-version'] = 6
        self.assert_cmd(dumps({"limit": limit, "spec": spec}), expected_valid=False)

        # check when only endpoint is local addr that a test going out still works
        limit = {
            "endpoint": {
                "cidr": ["{0}/32".format(self.local_addr)]
                }
            }
        spec = {"dest": "www.perfsonar.net"}
        self.assert_cmd(dumps({"limit": limit, "spec": spec}))
        
        
if __name__ == "__main__":
    unittest.main()
