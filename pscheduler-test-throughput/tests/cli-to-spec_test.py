import pscheduler

class CliToSpecTest(pscheduler.TestCliToSpecUnitTest):
    name = 'throughput'

    def test_all_options(self):

        # every option supported
        self.assert_arg_map({
            "source": {"val": "10.0.0.1" },
            "source-node": {"val": "10.0.0.1" },
            "dest": {"val": "10.0.0.2" },
            "dest-node": {"val": "10.0.0.2" },
            "duration": {"val": "10", "json_val": "PT10S" },
            "interval": {"val": "1", "short": "i", "json_val": "PT1S" },
            "udp": { "short": "u" },
            "bandwidth": {"val": "100000000", "short": "b" },
            "window-size": {"val": "64k", "json_val": "64000" },
            "mss": {"val": "9000" },
            "buffer-length": {"val": "1600" },
            "ip-tos": {"val": "10" },
            "ip-version": { "val": 4 },
            "local-address": {"val": "10.0.0.1" },
            "omit": {"val": "5", "json_val": "PT5S" },
            "no-delay": {},
            "congestion": {"val": "reno" },
            "client-cpu-affinity": {"val": "1" },
            "server-cpu-affinity": {"val": "0" },
            "reverse": {}
        })
    
    def test_flow_label(self):
        # test separate since it overrides ip-version
        self.assert_arg_map({
            "source": {"val": "10.0.0.1" },
            "dest": {"val": "10.0.0.2" },
            "flow-label": {"val": "10" },
        })
            

    def test_bandwidth_types(self):
        self.assert_arg_map({
            "bandwidth": {"val": "100M", "json_val": 100 * 10**6 },
        })
        
        self.assert_arg_map({
            "bandwidth": {"val": "10G", "json_val": 10 * 10**9 },
        })
        
        self.assert_arg_map({
            "bandwidth": {"val": "1000K", "json_val": 1000 * 10**3 },
        })
            
    def test_time(self):
    
        self.assert_arg_map({
            "duration": {"val": "10", "json_val": "PT10S" },
        })
        
        self.assert_arg_map({
            "duration": {"val": "PT05M" },
        })


    def test_omit(self):
        
        self.assert_arg_map({
            "omit": {"val": "10", "json_val": "PT10S" },
        })
        
        self.assert_arg_map({
            "omit": {"val": "PT05M" },
        })
        

    def test_bad_input(self):
        self.run_cmd("", args=["--nope", "5"], expected_status=1, 
            json_out=False, expected_stderr= "no such option: --nope\n")

        self.run_cmd("", 
            args=["--bandwidth", "butterfly"], 
            expected_status=1, 
            json_out=False, 
            expected_stderr="Invalid value \"butterfly\" for bandwidth: Invalid SI value 'butterfly'\n")


if __name__ == "__main__":
    unittest.main()
