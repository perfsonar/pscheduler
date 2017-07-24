"""
tests for the spec-to-cli command
"""

import pscheduler
import unittest

class CliToSpecTest(pscheduler.TestSpecToCliUnitTest):
    name = 'latency'
    
    def test_srcdst_opts(self):
        #dest-only
        expected_args = {
            '--dest': '10.0.0.1'
        }
        self.assert_spec_to_cli('{"dest": "10.0.0.1"}', expected_args)
        
        #source and dest
        expected_args = {
            '--source': '10.0.0.1',
            '--dest': '10.0.0.2'
        }
        self.assert_spec_to_cli('{"source": "10.0.0.1", "dest": "10.0.0.2"}', expected_args)
        
        #source-node and dest-node
        expected_args = {
            '--source': '10.0.0.1',
            '--dest': '10.0.0.2',
            '--source-node': '10.1.1.1',
            '--dest-node': '10.1.1.2'
        }
        self.assert_spec_to_cli("""
            { "source": "10.0.0.1", 
              "dest": "10.0.0.2", 
              "source-node": "10.1.1.1", 
              "dest-node": "10.1.1.2"}""", expected_args)

    def test_packet_opts(self):
        #packet-options
        expected_args = {
            '--source': '10.0.0.1',
            '--dest': '10.0.0.2',
            '--packet-count': 600,
            '--packet-interval': '0.001',
            '--packet-timeout': '1',
            '--packet-padding': '1000',
            '--bucket-width': '0.001'
        }
        self.assert_spec_to_cli("""
            { "source": "10.0.0.1", 
              "dest": "10.0.0.2", 
              "packet-count": 600, 
              "packet-interval": 0.001,
              "packet-timeout": 1, 
              "packet-padding": 1000,
              "bucket-width": 0.001}""", expected_args)
    
    def test_ctrlport_opts(self):   
        #control ports
        expected_args = {
            '--source': '10.0.0.1',
            '--dest': '10.0.0.2',
            '--ctrl-port': 861,
        }
        self.assert_spec_to_cli("""
            { "source": "10.0.0.1", 
              "dest": "10.0.0.2", 
              "ctrl-port": 861}""", expected_args)
    
    def test_dataports_opts(self):  
        #data ports
        expected_args = {
            '--source': '10.0.0.1',
            '--dest': '10.0.0.2',
            '--data-ports': '1000-2000',
        }
        self.assert_spec_to_cli("""
            { "source": "10.0.0.1", 
              "dest": "10.0.0.2", 
              "data-ports": {"lower": 1000, "upper": 2000}}""", expected_args)

    def test_ip_opts(self):  
        #ip opts
        expected_args = {
            '--source': '10.0.0.1',
            '--dest': '10.0.0.2',
            '--ip-version': 4,
            '--ip-tos': 128,
        }
        self.assert_spec_to_cli("""
            { "source": "10.0.0.1", 
              "dest": "10.0.0.2", 
              "ip-version": 4,
              "ip-tos": 128}""", expected_args)
    
    def test_boolean_opts(self):  
        #boolean opts
        expected_args = {
            '--source': '10.0.0.1',
            '--dest': '10.0.0.2',
            '--flip': None,
            '--output-raw': None,
        }
        self.assert_spec_to_cli("""
            { "source": "10.0.0.1", 
              "dest": "10.0.0.2", 
              "flip": true,
              "output-raw": true}""", expected_args)

    def test_failure(self):
        #dest-only
        self.run_cmd('{"garbage": "10.0.0.1"}', expected_status=1, json_out=False)
        
if __name__ == '__main__':
    unittest.main()
