"""
tests for the cli-to-spec command
"""

import pscheduler

class CliToSpecTest(pscheduler.TestCliToSpecUnitTest):
    name = 'latency'
    
    def test_opts(self):
        #dest-only
        self.assert_arg_map({
            "dest": {
                "val": "10.0.0.2"
            },
        })
        
        #source and dest
        self.assert_arg_map({
            "source": {
                "val": "10.0.0.1"
            },
            "dest": {
                "val": "10.0.0.2"
            },
        })
        
        #add source-node and dest-node
        self.assert_arg_map({
            "source": {
                "val": "10.0.0.1"
            },
            "dest": {
                "val": "10.0.0.2"
            },
             "source-node": {
                "val": "10.1.1.1"
            },
            "dest-node": {
                "val": "10.1.1.2"
            },
        })
        
        #add packet options
        self.assert_arg_map({
            "source": {
                "val": "10.0.0.1"
            },
            "dest": {
                "val": "10.0.0.2"
            },
            "packet-count": {
                "val": "60000"
            },
            "packet-interval": {
                "val": "0.001"
            },
            "packet-timeout": {
                "val": "1.0"
            },
            "packet-padding": {
                "val": "1000"
            },
            "bucket-width": {
                "val": "0.001"
            },
        })
        
        #control port
        self.assert_arg_map({
            "source": {
                "val": "10.0.0.1"
            },
            "dest": {
                "val": "10.0.0.2"
            },
            "ctrl-port": {
                "val": "861"
            }
        })
        
        #ip-tos and ip-version
        self.assert_arg_map({
            "source": {
                "val": "10.0.0.1"
            },
            "dest": {
                "val": "10.0.0.2"
            },
            "ip-tos": {
                "val": "128"
            },
            "ip-version": {
                "val": "6"
            }
        })
        
        #boolean options
        self.assert_arg_map({
            "source": {
                "val": "10.0.0.1"
            },
            "dest": {
                "val": "10.0.0.2"
            },
            "flip": {},
            "output-raw": {}
        })
        
        #short options
        self.assert_arg_map({
            "source": {
                "val": "10.0.0.1",
                "short": "s"
            },
            "dest": {
                "val": "10.0.0.2",
                "short": "d"
            },
            "packet-count": {
                "val": "60000",
                "short": "c"
            },
            "packet-interval": {
                "val": "0.001",
                "short": "i"
            },
            "packet-timeout": {
                "val": "1.0",
                "short": "L"
            },
            "packet-padding": {
                "val": "1000",
                "short": "p"
            },
            "ctrl-port": {
                "val": "861",
                "short": "C"
            },
            "ip-tos": {
                "val": "128",
                "short": "T"
            },
            "bucket-width": {
                "val": "0.001",
                "short": "b"
            },
            "flip": {"short": "f"},
            "output-raw": {"short": "R"}
        })

    def test_data_ports(self):
        #test data_ports
        args = [
            "--source", "10.0.0.1",
            "--dest", "10.0.0.2",
            "--data-ports", "2000-3000"
        ]
        result_json=self.run_cmd("", args=args)
        assert('data-ports' in result_json)
        assert('upper' in result_json['data-ports'])
        assert('lower' in result_json['data-ports'])
        self.assertEquals(result_json['data-ports']['lower'], 2000)
        self.assertEquals(result_json['data-ports']['upper'], 3000)
    
    def test_failure(self):
        self.run_cmd("", args=["--garbage"], expected_status=1, json_out=False)

        
if __name__ == '__main__':
    unittest.main()
