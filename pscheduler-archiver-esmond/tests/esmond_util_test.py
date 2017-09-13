"""
tests for the esmond_util module.
"""

import unittest
import json
from esmond import esmond_util

class EsmondUtilTest(unittest.TestCase):
    """
    Esmond Util tests.
    """
    
    def test_handle_storage_error(self):
        msg = "Test message"
        attempts=0
        expected_error = "Archiver permanently abandoned registering test after {0} attempt(s): {1}"
        policy = [{"attempts": 2, "wait":"PT30S"}, {"attempts": 3, "wait":"PT60S"}]
        
        #No policy, first attempt
        result = esmond_util._handle_storage_error(msg, attempts=attempts, policy=[])
        assert('succeeded' in result)
        assert('error' in result)
        assert('retry' not in result)
        self.assertEqual(result['succeeded'], False)
        self.assertEqual(result['error'], expected_error.format(attempts+1, msg))
        
        #policy, first attempt
        result = esmond_util._handle_storage_error(msg, attempts=attempts, policy=policy)
        assert('succeeded' in result)
        assert('error' in result)
        assert('retry' in result)
        self.assertEqual(result['succeeded'], False)
        self.assertEqual(result['error'], msg)
        self.assertEqual(result['retry'], "PT30S")
        
        #policy, middle attempt
        attempts = 2
        result = esmond_util._handle_storage_error(msg, attempts=attempts, policy=policy)
        assert('succeeded' in result)
        assert('error' in result)
        assert('retry' in result)
        self.assertEqual(result['succeeded'], False)
        self.assertEqual(result['error'], msg)
        self.assertEqual(result['retry'], "PT60S")
        
        #policy, last attempt
        attempts = 5
        result = esmond_util._handle_storage_error(msg, attempts=attempts, policy=policy)
        assert('succeeded' in result)
        assert('error' in result)
        assert('retry' not in result)
        self.assertEqual(result['succeeded'], False)
        self.assertEqual(result['error'], expected_error.format(attempts+1, msg))
    
    def test_esmond_latency_record(self):
        EXPECTED_METADATA = {'time-duration': 60, 'pscheduler-test-type': 'latency', 'source': '10.0.0.1', 'measurement-agent': '10.0.0.1', 'input-destination': '10.0.0.2', 'destination': '10.0.0.2', 'event-types': [{'event-type': 'failures'}, {'summaries': [{'summary-type': 'aggregation', 'summary-window': 300, 'event-type': 'packet-count-sent'}, {'summary-type': 'aggregation', 'summary-window': 3600, 'event-type': 'packet-count-sent'}, {'summary-type': 'aggregation', 'summary-window': 86400, 'event-type': 'packet-count-sent'}], 'event-type': 'packet-count-sent'}, {'summaries': [{'summary-type': 'aggregation', 'summary-window': 300, 'event-type': 'histogram-owdelay'}, {'summary-type': 'statistics', 'summary-window': 300, 'event-type': 'histogram-owdelay'}, {'summary-type': 'aggregation', 'summary-window': 3600, 'event-type': 'histogram-owdelay'}, {'summary-type': 'statistics', 'summary-window': 0, 'event-type': 'histogram-owdelay'}, {'summary-type': 'statistics', 'summary-window': 3600, 'event-type': 'histogram-owdelay'}, {'summary-type': 'aggregation', 'summary-window': 86400, 'event-type': 'histogram-owdelay'}, {'summary-type': 'statistics', 'summary-window': 86400, 'event-type': 'histogram-owdelay'}], 'event-type': 'histogram-owdelay'}, {'event-type': 'histogram-ttl'}, {'event-type': 'packet-duplicates'}, {'summaries': [{'summary-type': 'aggregation', 'summary-window': 300, 'event-type': 'packet-loss-rate'}, {'summary-type': 'aggregation', 'summary-window': 3600, 'event-type': 'packet-loss-rate'}, {'summary-type': 'aggregation', 'summary-window': 86400, 'event-type': 'packet-loss-rate'}], 'event-type': 'packet-loss-rate'}, {'summaries': [{'summary-type': 'aggregation', 'summary-window': 300, 'event-type': 'packet-count-lost'}, {'summary-type': 'aggregation', 'summary-window': 3600, 'event-type': 'packet-count-lost'}, {'summary-type': 'aggregation', 'summary-window': 86400, 'event-type': 'packet-count-lost'}], 'event-type': 'packet-count-lost'}, {'event-type': 'packet-reorders'}, {'event-type': 'time-error-estimates'}], 'subject-type': 'point-to-point', 'input-source': '10.0.0.1', 'tool-name': 'powstream', 'time-probe-interval': 0.001}
        EXPECTED_DATA = [{'ts': 1497971206, 'val': [{'val': 0, 'event-type': 'time-error-estimates'}, {'val': 0, 'event-type': 'packet-duplicates'}, {'val': {'39.40': 11, '39.53': 77, '39.49': 32, '39.48': 51, '39.47': 40, '39.51': 40, '39.45': 12, '39.44': 9, '39.43': 9, '39.55': 2, '39.41': 10, '39.57': 1, '39.50': 39, '39.42': 12, '39.54': 34, '39.56': 1, '39.39': 3, '39.46': 30, '39.52': 187}, 'event-type': 'histogram-owdelay'}, {'val': {'247': 600}, 'event-type': 'histogram-ttl'}, {'val': 600, 'event-type': 'packet-count-sent'}, {'val': 0, 'event-type': 'packet-reorders'}, {'val': 0, 'event-type': 'packet-count-lost'}, {'val': {'denominator': 600, 'numerator': 0}, 'event-type': 'packet-loss-rate'}]}]
        test_spec = {
            "source": "10.0.0.1",
            "dest": "10.0.0.2",
            "packet-interval": .001,
        }
        lead_participant = "10.0.0.1"
        measurement_agent = "10.0.0.1"
        tool_name = "powstream"
        summary_map = None
        duration = 60
        fast_mode = False
        test_start_time = 1497971206
        test_result = {
            "schema": 1,
            "succeeded": True,
            "packets-sent": 600,
            "packets-received": 600,
            "packets-lost": 0,
            "packets-duplicated": 0,
            "packets-reordered": 0,
            "max-clock-error": 0,
            "histogram-latency": {
                "39.57": 1, 
                "39.44": 9, 
                "39.39": 3, 
                "39.49": 32, 
                "39.48": 51, 
                "39.47": 40, 
                "39.51": 40, 
                "39.45": 12, 
                "39.53": 77, 
                "39.43": 9, 
                "39.55": 2, 
                "39.41": 10, 
                "39.42": 12, 
                "39.50": 39, 
                "39.54": 34, 
                "39.56": 1, 
                "39.46": 30, 
                "39.40": 11, 
                "39.52": 187},
            "histogram-ttl": {"247": 600}
        }
        
        #test latency record
        record = esmond_util.EsmondLatencyRecord(
            test_spec=test_spec,
            lead_participant=lead_participant,
            measurement_agent=measurement_agent,
            tool_name=tool_name,
            summaries=summary_map,
            duration=duration,
            ts=test_start_time, 
            test_result=test_result,
            fast_mode=fast_mode
        )
        self.assertEqual(record.test_type, "latency")
        self.assertEqual(json.dumps(record.metadata, sort_keys=True), json.dumps(EXPECTED_METADATA, sort_keys=True))
        self.assertEqual(json.dumps(record.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))
    
        #test latency bg
        recordbg = esmond_util.EsmondLatencyBGRecord(
            test_spec=test_spec,
            lead_participant=lead_participant,
            measurement_agent=measurement_agent,
            tool_name=tool_name,
            summaries=summary_map,
            duration=duration,
            ts=test_start_time, 
            test_result=test_result,
            fast_mode=fast_mode
        )
        EXPECTED_METADATA['pscheduler-test-type'] = "latencybg"
        self.assertEqual(recordbg.test_type, "latencybg")
        self.assertEqual(record.test_type, "latency") # make sure the class variable works as expected
        self.assertEqual(json.dumps(recordbg.metadata, sort_keys=True), json.dumps(EXPECTED_METADATA, sort_keys=True))
        self.assertEqual(json.dumps(recordbg.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))
        
        
    
    def test_esmond_throughput_record(self):
        EXPECTED_METADATA = {'time-duration': 30, 'pscheduler-test-type': 'throughput', 'source': '10.0.0.1', 'measurement-agent': '10.0.0.1', 'input-destination': '10.0.0.2', 'destination': '10.0.0.2', 'event-types': [{'event-type': 'failures'}, {'summaries': [{'summary-type': 'average', 'summary-window': 86400, 'event-type': 'throughput'}], 'event-type': 'throughput'}, {'event-type': 'throughput-subintervals'}, {'event-type': 'packet-retransmits'}, {'event-type': 'packet-retransmits-subintervals'}], 'subject-type': 'point-to-point', 'ip-transport-protocol': 'tcp', 'input-source': '10.0.0.1', 'tool-name': 'iperf3'}
        EXPECTED_DATA = [{"ts": 1497971206, "val": [{"event-type": "throughput", "val": 4438908000.0}, {"event-type": "packet-retransmits", "val": 0}, {"event-type": "throughput-subintervals", "val": [{"duration": 1.000059, "start": 0, "val": 891236903.11585104}, {"duration": 1.0000009999999999, "start": 1.000059, "val": 524287500.00047702}, {"duration": 1.0000019999999998, "start": 2.0000599999999999, "val": 83885920.000304997}, {"duration": 1.0000200000000001, "start": 3.0000619999999998, "val": 524277500.21028101}, {"duration": 0.99997899999999973, "start": 4.0000819999999999, "val": 692074680.30464804}, {"duration": 1.0000169999999999, "start": 1.8e-05, "val": 775905172.17367601}, {"duration": 1.0, "start": 1.000035, "val": 891289600}, {"duration": 1.0000049999999998, "start": 2.000035, "val": 1205856000.0}, {"duration": 1.0000010000000006, "start": 3.0000399999999998, "val": 1562377000.0}, {"duration": 0.99999599999999944, "start": 4.0000410000000004, "val": 2034245000.0}, {"duration": 1.000006, "start": 5.0000369999999998, "val": 2474625000.0}, {"duration": 0.99999800000000061, "start": 6.0000429999999998, "val": 3303021000.0}, {"duration": 0.99999299999999902, "start": 7.0000410000000004, "val": 4099961000.0}, {"duration": 1.0000020000000003, "start": 8.0000339999999994, "val": 4781497000.0}, {"duration": 0.99999799999999972, "start": 9.0000359999999997, "val": 5714750000.0}, {"duration": 0.99996100000000077, "start": 10.000033999999999, "val": 6480452000.0}, {"duration": 1.0000389999999992, "start": 10.999995, "val": 7559939000.0}, {"duration": 1.000019, "start": 12.000033999999999, "val": 8210193000.0}, {"duration": 0.99998200000000104, "start": 13.000052999999999, "val": 8944515000.0}, {"duration": 1.0001800000000003, "start": 14.000035, "val": 8544356000.0}]}, {"event-type": "streams-throughput-subintervals", "val": []}, {"event-type": "packet-retransmits-subintervals", "val": [{"duration": 1.000059, "start": 0, "val": 0}, {"duration": 1.0000009999999999, "start": 1.000059, "val": 1}, {"duration": 1.0000019999999998, "start": 2.0000599999999999, "val": 1}, {"duration": 1.0000200000000001, "start": 3.0000619999999998, "val": 0}, {"duration": 0.99997899999999973, "start": 4.0000819999999999, "val": 0}, {"duration": 1.0000169999999999, "start": 1.8e-05, "val": 0}, {"duration": 1.0, "start": 1.000035, "val": 0}, {"duration": 1.0000049999999998, "start": 2.000035, "val": 0}, {"duration": 1.0000010000000006, "start": 3.0000399999999998, "val": 0}, {"duration": 0.99999599999999944, "start": 4.0000410000000004, "val": 0}, {"duration": 1.000006, "start": 5.0000369999999998, "val": 0}, {"duration": 0.99999800000000061, "start": 6.0000429999999998, "val": 0}, {"duration": 0.99999299999999902, "start": 7.0000410000000004, "val": 0}, {"duration": 1.0000020000000003, "start": 8.0000339999999994, "val": 0}, {"duration": 0.99999799999999972, "start": 9.0000359999999997, "val": 0}, {"duration": 0.99996100000000077, "start": 10.000033999999999, "val": 0}, {"duration": 1.0000389999999992, "start": 10.999995, "val": 0}, {"duration": 1.000019, "start": 12.000033999999999, "val": 0}, {"duration": 0.99998200000000104, "start": 13.000052999999999, "val": 0}, {"duration": 1.0001800000000003, "start": 14.000035, "val": 0}]}, {"event-type": "streams-packet-retransmits-subintervals", "val": []}, {"event-type": "streams-packet-rtt-subintervals", "val": []}, {"event-type": "streams-tcp-windowsize-subintervals", "val": []}]}]
        test_spec = {
            "source": "10.0.0.1",
            "dest": "10.0.0.2",
            "duration": "PT30S",
        }
        lead_participant = "10.0.0.1"
        measurement_agent = "10.0.0.1"
        tool_name = "iperf3"
        summary_map = None
        duration = 30
        fast_mode = False
        test_start_time = 1497971206
        test_result = {  
           "diags":"YAY RESULTS\n-------------STUFF HERE",
           "intervals":[  
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":5574604,
                       "end":1.000059,
                       "stream-id":4,
                       "omitted":True,
                       "rtt":63000,
                       "throughput-bits":891236903.11585104,
                       "retransmits":0,
                       "throughput-bytes":111411200,
                       "start":0
                    }
                 ],
                 "summary":{  
                    "end":1.000059,
                    "omitted":True,
                    "start":0,
                    "throughput-bits":891236903.11585104,
                    "retransmits":0,
                    "throughput-bytes":111411200
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":10317044,
                       "end":2.0000599999999999,
                       "stream-id":4,
                       "omitted":True,
                       "rtt":62875,
                       "throughput-bits":524287500.00047702,
                       "retransmits":1,
                       "throughput-bytes":65536000,
                       "start":1.000059
                    }
                 ],
                 "summary":{  
                    "end":2.0000599999999999,
                    "omitted":True,
                    "start":1.000059,
                    "throughput-bits":524287500.00047702,
                    "retransmits":1,
                    "throughput-bytes":65536000
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":1539056,
                       "end":3.0000619999999998,
                       "stream-id":4,
                       "omitted":True,
                       "rtt":1467375,
                       "throughput-bits":83885920.000304997,
                       "retransmits":1,
                       "throughput-bytes":10485760,
                       "start":2.0000599999999999
                    }
                 ],
                 "summary":{  
                    "end":3.0000619999999998,
                    "omitted":True,
                    "start":2.0000599999999999,
                    "throughput-bits":83885920.000304997,
                    "retransmits":1,
                    "throughput-bytes":10485760
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":5243528,
                       "end":4.0000819999999999,
                       "stream-id":4,
                       "omitted":True,
                       "rtt":63000,
                       "throughput-bits":524277500.21028101,
                       "retransmits":0,
                       "throughput-bytes":65536000,
                       "start":3.0000619999999998
                    }
                 ],
                 "summary":{  
                    "end":4.0000819999999999,
                    "omitted":True,
                    "start":3.0000619999999998,
                    "throughput-bits":524277500.21028101,
                    "retransmits":0,
                    "throughput-bytes":65536000
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":5628292,
                       "end":5.0000609999999996,
                       "stream-id":4,
                       "omitted":True,
                       "rtt":63000,
                       "throughput-bits":692074680.30464804,
                       "retransmits":0,
                       "throughput-bytes":86507520,
                       "start":4.0000819999999999
                    }
                 ],
                 "summary":{  
                    "end":5.0000609999999996,
                    "omitted":True,
                    "start":4.0000819999999999,
                    "throughput-bits":692074680.30464804,
                    "retransmits":0,
                    "throughput-bytes":86507520
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":6827324,
                       "end":1.000035,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":62875,
                       "throughput-bits":775905172.17367601,
                       "retransmits":0,
                       "throughput-bytes":96993280,
                       "start":1.8e-05
                    }
                 ],
                 "summary":{  
                    "end":1.000035,
                    "omitted":False,
                    "start":1.8e-05,
                    "throughput-bits":775905172.17367601,
                    "retransmits":0,
                    "throughput-bytes":96993280
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":8259004,
                       "end":2.000035,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":62875,
                       "throughput-bits":891289600,
                       "retransmits":0,
                       "throughput-bytes":111411200,
                       "start":1.000035
                    }
                 ],
                 "summary":{  
                    "end":2.000035,
                    "omitted":False,
                    "start":1.000035,
                    "throughput-bits":891289600,
                    "retransmits":0,
                    "throughput-bytes":111411200
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":10728652,
                       "end":3.0000399999999998,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":63000,
                       "throughput-bits":1205856000.0,
                       "retransmits":0,
                       "throughput-bytes":150732800,
                       "start":2.000035
                    }
                 ],
                 "summary":{  
                    "end":3.0000399999999998,
                    "omitted":False,
                    "start":2.000035,
                    "throughput-bits":1205856000.0,
                    "retransmits":0,
                    "throughput-bytes":150732800
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":14084152,
                       "end":4.0000410000000004,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":63250,
                       "throughput-bits":1562377000.0,
                       "retransmits":0,
                       "throughput-bytes":195297280,
                       "start":3.0000399999999998
                    }
                 ],
                 "summary":{  
                    "end":4.0000410000000004,
                    "omitted":False,
                    "start":3.0000399999999998,
                    "throughput-bits":1562377000.0,
                    "retransmits":0,
                    "throughput-bytes":195297280
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":18191284,
                       "end":5.0000369999999998,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":63000,
                       "throughput-bits":2034245000.0,
                       "retransmits":0,
                       "throughput-bytes":254279680,
                       "start":4.0000410000000004
                    }
                 ],
                 "summary":{  
                    "end":5.0000369999999998,
                    "omitted":False,
                    "start":4.0000410000000004,
                    "throughput-bits":2034245000.0,
                    "retransmits":0,
                    "throughput-bytes":254279680
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":22880036,
                       "end":6.0000429999999998,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":62875,
                       "throughput-bits":2474625000.0,
                       "retransmits":0,
                       "throughput-bytes":309329920,
                       "start":5.0000369999999998
                    }
                 ],
                 "summary":{  
                    "end":6.0000429999999998,
                    "omitted":False,
                    "start":5.0000369999999998,
                    "throughput-bits":2474625000.0,
                    "retransmits":0,
                    "throughput-bytes":309329920
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":28973624,
                       "end":7.0000410000000004,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":63000,
                       "throughput-bits":3303021000.0,
                       "retransmits":0,
                       "throughput-bytes":412876800,
                       "start":6.0000429999999998
                    }
                 ],
                 "summary":{  
                    "end":7.0000410000000004,
                    "omitted":False,
                    "start":6.0000429999999998,
                    "throughput-bits":3303021000.0,
                    "retransmits":0,
                    "throughput-bytes":412876800
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":35210380,
                       "end":8.0000339999999994,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":63875,
                       "throughput-bits":4099961000.0,
                       "retransmits":0,
                       "throughput-bytes":512491520,
                       "start":7.0000410000000004
                    }
                 ],
                 "summary":{  
                    "end":8.0000339999999994,
                    "omitted":False,
                    "start":7.0000410000000004,
                    "throughput-bits":4099961000.0,
                    "retransmits":0,
                    "throughput-bytes":512491520
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":41769264,
                       "end":9.0000359999999997,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":63500,
                       "throughput-bits":4781497000.0,
                       "retransmits":0,
                       "throughput-bytes":597688320,
                       "start":8.0000339999999994
                    }
                 ],
                 "summary":{  
                    "end":9.0000359999999997,
                    "omitted":False,
                    "start":8.0000339999999994,
                    "throughput-bits":4781497000.0,
                    "retransmits":0,
                    "throughput-bytes":597688320
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":48963456,
                       "end":10.000033999999999,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":63125,
                       "throughput-bits":5714750000.0,
                       "retransmits":0,
                       "throughput-bytes":714342400,
                       "start":9.0000359999999997
                    }
                 ],
                 "summary":{  
                    "end":10.000033999999999,
                    "omitted":False,
                    "start":9.0000359999999997,
                    "throughput-bits":5714750000.0,
                    "retransmits":0,
                    "throughput-bytes":714342400
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":56363452,
                       "end":10.999995,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":63000,
                       "throughput-bits":6480452000.0,
                       "retransmits":0,
                       "throughput-bytes":810024960,
                       "start":10.000033999999999
                    }
                 ],
                 "summary":{  
                    "end":10.999995,
                    "omitted":False,
                    "start":10.000033999999999,
                    "throughput-bits":6480452000.0,
                    "retransmits":0,
                    "throughput-bytes":810024960
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":64926688,
                       "end":12.000033999999999,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":63000,
                       "throughput-bits":7559939000.0,
                       "retransmits":0,
                       "throughput-bytes":945029120,
                       "start":10.999995
                    }
                 ],
                 "summary":{  
                    "end":12.000033999999999,
                    "omitted":False,
                    "start":10.999995,
                    "throughput-bits":7559939000.0,
                    "retransmits":0,
                    "throughput-bytes":945029120
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":70080736,
                       "end":13.000052999999999,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":64875,
                       "throughput-bits":8210193000.0,
                       "retransmits":0,
                       "throughput-bytes":1026293760,
                       "start":12.000033999999999
                    }
                 ],
                 "summary":{  
                    "end":13.000052999999999,
                    "omitted":False,
                    "start":12.000033999999999,
                    "throughput-bits":8210193000.0,
                    "retransmits":0,
                    "throughput-bytes":1026293760
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":75583756,
                       "end":14.000035,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":65000,
                       "throughput-bits":8944515000.0,
                       "retransmits":0,
                       "throughput-bytes":1118044160,
                       "start":13.000052999999999
                    }
                 ],
                 "summary":{  
                    "end":14.000035,
                    "omitted":False,
                    "start":13.000052999999999,
                    "throughput-bits":8944515000.0,
                    "retransmits":0,
                    "throughput-bytes":1118044160
                 }
              },
              {  
                 "streams":[  
                    {  
                       "tcp-window-size":77543368,
                       "end":15.000215000000001,
                       "stream-id":4,
                       "omitted":False,
                       "rtt":65875,
                       "throughput-bits":8544356000.0,
                       "retransmits":0,
                       "throughput-bytes":1068236800,
                       "start":14.000035
                    }
                 ],
                 "summary":{  
                    "end":15.000215000000001,
                    "omitted":False,
                    "start":14.000035,
                    "throughput-bits":8544356000.0,
                    "retransmits":0,
                    "throughput-bytes":1068236800
                 }
              }
           ],
           "succeeded":True,
           "summary":{  
              "streams":[  
                 {  
                    "end":15.000215000000001,
                    "stream-id":4,
                    "throughput-bytes":8323072000,
                    "rtt":133618,
                    "retransmits":0,
                    "throughput-bits":4438908000.0,
                    "start":0
                 }
              ],
              "summary":{  
                 "throughput-bytes":8323072000,
                 "start":0,
                 "end":15.000215000000001,
                 "throughput-bits":4438908000.0,
                 "retransmits":0
              }
           }
        }
        
        #test throughput record
        record = esmond_util.EsmondThroughputRecord(
            test_spec=test_spec,
            lead_participant=lead_participant,
            measurement_agent=measurement_agent,
            tool_name=tool_name,
            summaries=summary_map,
            duration=duration,
            ts=test_start_time, 
            test_result=test_result,
            fast_mode=fast_mode
        )
        self.assertEqual(record.test_type, "throughput")
        self.assertEqual(json.dumps(record.metadata, sort_keys=True), json.dumps(EXPECTED_METADATA, sort_keys=True))
        self.assertEqual(json.dumps(record.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))
        
        #test udp
        EXPECTED_METADATA = {'time-duration': 30, 'pscheduler-test-type': 'throughput', 'source': '10.0.0.1', 'measurement-agent': '10.0.0.1', 'input-destination': '10.0.0.2', 'destination': '10.0.0.2', 'event-types': [{'event-type': 'failures'}, {'summaries': [{'summary-type': 'average', 'summary-window': 86400, 'event-type': 'throughput'}], 'event-type': 'throughput'}, {'event-type': 'throughput-subintervals'}, {'summaries': [{'summary-type': 'aggregation', 'summary-window': 300, 'event-type': 'packet-loss-rate'}, {'summary-type': 'aggregation', 'summary-window': 3600, 'event-type': 'packet-loss-rate'}, {'summary-type': 'aggregation', 'summary-window': 86400, 'event-type': 'packet-loss-rate'}], 'event-type': 'packet-loss-rate'}, {'summaries': [{'summary-type': 'aggregation', 'summary-window': 300, 'event-type': 'packet-count-lost'}, {'summary-type': 'aggregation', 'summary-window': 3600, 'event-type': 'packet-count-lost'}, {'summary-type': 'aggregation', 'summary-window': 86400, 'event-type': 'packet-count-lost'}], 'event-type': 'packet-count-lost'}, {'summaries': [{'summary-type': 'aggregation', 'summary-window': 300, 'event-type': 'packet-count-sent'}, {'summary-type': 'aggregation', 'summary-window': 3600, 'event-type': 'packet-count-sent'}, {'summary-type': 'aggregation', 'summary-window': 86400, 'event-type': 'packet-count-sent'}], 'event-type': 'packet-count-sent'}], 'subject-type': 'point-to-point', 'ip-transport-protocol': 'udp', 'input-source': '10.0.0.1', 'tool-name': 'iperf3'}
        EXPECTED_DATA = [{'ts': 1497971206, 'val': [{'val': 49554301.592703998, 'event-type': 'throughput'}, {'val': 42779, 'event-type': 'packet-count-sent'}, {'val': 0, 'event-type': 'packet-count-lost'}, {'val': {'denominator': 42779, 'numerator': 0}, 'event-type': 'packet-loss-rate'}, {'val': [{'duration': 1.000149, 'start': 0, 'val': 45553084.061515003}, {'duration': 0.99999700000000002, 'start': 1.000149, 'val': 49996687.041669004}, {'duration': 1.000067, 'start': 2.000146, 'val': 49738363.747446999}, {'duration': 0.99993799999999977, 'start': 3.000213, 'val': 50266091.936255999}, {'duration': 1.000019, 'start': 4.0001509999999998, 'val': 50076688.802174002}, {'duration': 1.0001280000000001, 'start': 5.0001699999999998, 'val': 49909066.103488997}, {'duration': 0.99985400000000002, 'start': 6.0002979999999999, 'val': 49725783.597010002}, {'duration': 1.0000149999999994, 'start': 7.0001519999999999, 'val': 50030544.522685997}, {'duration': 0.99999500000000019, 'start': 8.0001669999999994, 'val': 50332732.005427003}, {'duration': 1.0000180000000007, 'start': 9.0001619999999996, 'val': 49914563.458053}], 'event-type': 'throughput-subintervals'}, {'val': [], 'event-type': 'streams-throughput-subintervals'}]}]
        test_spec = {
            "source": "10.0.0.1",
            "dest": "10.0.0.2",
            "duration": "PT30S",
            "udp": True,
            
        }
        test_result = {"diags": "YAY RESULTS\n----", "intervals": [{"streams": [{"throughput-bytes": 5694984, "end": 1.000149, "stream-id": 4, "omitted": False, "start": 0, "throughput-bits": 45553084.061515003, "sent": 3933}], "summary": {"end": 1.000149, "omitted": False, "start": 0, "throughput-bits": 45553084.061515003, "throughput-bytes": 5694984, "sent": 3933}}, {"streams": [{"throughput-bytes": 6249568, "end": 2.000146, "stream-id": 4, "omitted": False, "start": 1.000149, "throughput-bits": 49996687.041669004, "sent": 4316}], "summary": {"end": 2.000146, "omitted": False, "start": 1.000149, "throughput-bits": 49996687.041669004, "throughput-bytes": 6249568, "sent": 4316}}, {"streams": [{"throughput-bytes": 6217712, "end": 3.000213, "stream-id": 4, "omitted": False, "start": 2.000146, "throughput-bits": 49738363.747446999, "sent": 4294}], "summary": {"end": 3.000213, "omitted": False, "start": 2.000146, "throughput-bits": 49738363.747446999, "throughput-bytes": 6217712, "sent": 4294}}, {"streams": [{"throughput-bytes": 6282872, "end": 4.0001509999999998, "stream-id": 4, "omitted": False, "start": 3.000213, "throughput-bits": 50266091.936255999, "sent": 4339}], "summary": {"end": 4.0001509999999998, "omitted": False, "start": 3.000213, "throughput-bits": 50266091.936255999, "throughput-bytes": 6282872, "sent": 4339}}, {"streams": [{"throughput-bytes": 6259704, "end": 5.0001699999999998, "stream-id": 4, "omitted": False, "start": 4.0001509999999998, "throughput-bits": 50076688.802174002, "sent": 4323}], "summary": {"end": 5.0001699999999998, "omitted": False, "start": 4.0001509999999998, "throughput-bits": 50076688.802174002, "throughput-bytes": 6259704, "sent": 4323}}, {"streams": [{"throughput-bytes": 6239432, "end": 6.0002979999999999, "stream-id": 4, "omitted": False, "start": 5.0001699999999998, "throughput-bits": 49909066.103488997, "sent": 4309}], "summary": {"end": 6.0002979999999999, "omitted": False, "start": 5.0001699999999998, "throughput-bits": 49909066.103488997, "throughput-bytes": 6239432, "sent": 4309}}, {"streams": [{"throughput-bytes": 6214816, "end": 7.0001519999999999, "stream-id": 4, "omitted": False, "start": 6.0002979999999999, "throughput-bits": 49725783.597010002, "sent": 4292}], "summary": {"end": 7.0001519999999999, "omitted": False, "start": 6.0002979999999999, "throughput-bits": 49725783.597010002, "throughput-bytes": 6214816, "sent": 4292}}, {"streams": [{"throughput-bytes": 6253912, "end": 8.0001669999999994, "stream-id": 4, "omitted": False, "start": 7.0001519999999999, "throughput-bits": 50030544.522685997, "sent": 4319}], "summary": {"end": 8.0001669999999994, "omitted": False, "start": 7.0001519999999999, "throughput-bits": 50030544.522685997, "throughput-bytes": 6253912, "sent": 4319}}, {"streams": [{"throughput-bytes": 6291560, "end": 9.0001619999999996, "stream-id": 4, "omitted": False, "start": 8.0001669999999994, "throughput-bits": 50332732.005427003, "sent": 4345}], "summary": {"end": 9.0001619999999996, "omitted": False, "start": 8.0001669999999994, "throughput-bits": 50332732.005427003, "throughput-bytes": 6291560, "sent": 4345}}, {"streams": [{"throughput-bytes": 6239432, "end": 10.00018, "stream-id": 4, "omitted": False, "start": 9.0001619999999996, "throughput-bits": 49914563.458053, "sent": 4309}], "summary": {"end": 10.00018, "omitted": False, "start": 9.0001619999999996, "throughput-bits": 49914563.458053, "throughput-bytes": 6239432, "sent": 4309}}], "succeeded": True, "summary": {"streams": [{"end": 10.00018, "lost": 0, "stream-id": 4, "throughput-bits": 49554301.592703998, "start": 0, "jitter": 0.017999999999999999, "throughput-bytes": 61943992, "sent": 42779}], "summary": {"end": 10.00018, "lost": 0, "throughput-bytes": 61943992, "start": 0, "jitter": 0.017999999999999999, "throughput-bits": 49554301.592703998, "sent": 42779}}}
        record = esmond_util.EsmondThroughputRecord(
            test_spec=test_spec,
            lead_participant=lead_participant,
            measurement_agent=measurement_agent,
            tool_name=tool_name,
            summaries=summary_map,
            duration=duration,
            ts=test_start_time, 
            test_result=test_result,
            fast_mode=fast_mode
        )
        
        self.assertEqual(record.test_type, "throughput")
        self.assertEqual(json.dumps(record.metadata, sort_keys=True), json.dumps(EXPECTED_METADATA, sort_keys=True))
        self.assertEqual(json.dumps(record.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))
     
        #test parallel
        EXPECTED_METADATA = {'time-duration': 30, 'pscheduler-test-type': 'throughput', 'source': '10.0.0.1', 'measurement-agent': '10.0.0.1', 'input-destination': '10.0.0.2', 'destination': '10.0.0.2', 'event-types': [{'event-type': 'failures'}, {'summaries': [{'summary-type': 'average', 'summary-window': 86400, 'event-type': 'throughput'}], 'event-type': 'throughput'}, {'event-type': 'throughput-subintervals'}, {'event-type': 'streams-throughput'}, {'event-type': 'streams-throughput-subintervals'}, {'event-type': 'packet-retransmits'}, {'event-type': 'packet-retransmits-subintervals'}, {'event-type': 'streams-packet-retransmits'}, {'event-type': 'streams-packet-retransmits-subintervals'}], 'subject-type': 'point-to-point', 'ip-transport-protocol': 'tcp', 'input-source': '10.0.0.1', 'bw-parallel-streams': 2, 'tool-name': 'iperf3'}
        EXPECTED_DATA = [{"ts": 1497971206, "val": [{"event-type": "throughput", "val": 7309196000.0}, {"event-type": "packet-retransmits", "val": 33}, {"event-type": "streams-throughput", "val": [3687368000.0, 3621827000.0]}, {"event-type": "streams-packet-retransmits", "val": [15, 18]}, {"event-type": "streams-packet-rtt", "val": [78525, 78412]}, {"event-type": "throughput-subintervals", "val": [{"duration": 1.0000979999999999, "start": 0, "val": 69071791.652649}, {"duration": 0.99998200000000015, "start": 1.0000979999999999, "val": 803814565.324489}, {"duration": 1.0000239999999998, "start": 2.0000800000000001, "val": 2600406000.0}, {"duration": 0.99995500000000037, "start": 3.0001039999999999, "val": 6920913000.0}, {"duration": 0.99999899999999986, "start": 4.0000590000000003, "val": 9961482000.0}, {"duration": 1.000006, "start": 5.0000580000000001, "val": 9888013000.0}, {"duration": 1.0000119999999999, "start": 6.0000640000000001, "val": 9898437000.0}, {"duration": 0.99998199999999926, "start": 7.000076, "val": 9877765000.0}, {"duration": 1.0000020000000003, "start": 8.0000579999999992, "val": 9929993000.0}, {"duration": 0.99999799999999972, "start": 9.0000599999999995, "val": 9919550000.0}, {"duration": 1.0, "start": 10.000057999999999, "val": 9898557440}, {"duration": 1.0, "start": 11.000057999999999, "val": 9888071680}, {"duration": 1.0000550000000015, "start": 12.000057999999999, "val": 9887527000.0}, {"duration": 0.99994499999999853, "start": 13.000113000000001, "val": 9878130000.0}, {"duration": 1.0000020000000003, "start": 14.000057999999999, "val": 9856593000.0}, {"duration": 0.99999200000000066, "start": 15.00006, "val": 9919609000.0}, {"duration": 1.0001080000000009, "start": 16.000052, "val": 5997207000.0}, {"duration": 0.99989899999999921, "start": 17.000160000000001, "val": 3429190000.0}, {"duration": 1.000004999999998, "start": 18.000059, "val": 3638541000.0}, {"duration": 1.0000220000000013, "start": 19.000063999999998, "val": 3921587000.0}]}, {"event-type": "streams-throughput-subintervals", "val": [[{"duration": 1.0000979999999999, "start": 0, "val": 41800959.922431998}, {"duration": 0.99998200000000015, "start": 1.0000979999999999, "val": 441881181.45125598}, {"duration": 1.0000239999999998, "start": 2.0000800000000001, "val": 1415544000.0}, {"duration": 0.99995500000000037, "start": 3.0001039999999999, "val": 3974282000.0}, {"duration": 0.99999899999999986, "start": 4.0000590000000003, "val": 5033170000.0}, {"duration": 1.000006, "start": 5.0000580000000001, "val": 4938764000.0}, {"duration": 1.0000119999999999, "start": 6.0000640000000001, "val": 4949219000.0}, {"duration": 0.99998199999999926, "start": 7.000076, "val": 4917911000.0}, {"duration": 1.0000020000000003, "start": 8.0000579999999992, "val": 4959754000.0}, {"duration": 0.99999799999999972, "start": 9.0000599999999995, "val": 4959775000.0}, {"duration": 1.0, "start": 10.000057999999999, "val": 4949278720}, {"duration": 1.0, "start": 11.000057999999999, "val": 4938792960}, {"duration": 1.0000550000000015, "start": 12.000057999999999, "val": 4949006000.0}, {"duration": 0.99994499999999853, "start": 13.000113000000001, "val": 4939065000.0}, {"duration": 1.0000020000000003, "start": 14.000057999999999, "val": 4928297000.0}, {"duration": 0.99999200000000066, "start": 15.00006, "val": 4938833000.0}, {"duration": 1.0001080000000009, "start": 16.000052, "val": 2988119000.0}, {"duration": 0.99989899999999921, "start": 17.000160000000001, "val": 1709352000.0}, {"duration": 1.000004999999998, "start": 18.000059, "val": 1824513000.0}, {"duration": 1.0000220000000013, "start": 19.000063999999998, "val": 1950308000.0}], [{"duration": 1.0001070000000001, "start": 0, "val": 27270584.685490999}, {"duration": 0.99997700000000012, "start": 1.0001070000000001, "val": 361935282.333287}, {"duration": 1.0000239999999998, "start": 2.0000840000000002, "val": 1184862000.0}, {"duration": 0.99995499999999993, "start": 3.000108, "val": 2946631000.0}, {"duration": 0.99999899999999986, "start": 4.0000629999999999, "val": 4928312000.0}, {"duration": 1.000006, "start": 5.0000619999999998, "val": 4949249000.0}, {"duration": 1.0000119999999999, "start": 6.0000679999999997, "val": 4949219000.0}, {"duration": 0.99998499999999968, "start": 7.0000799999999996, "val": 4959839000.0}, {"duration": 1.000001000000001, "start": 8.0000649999999993, "val": 4970246000.0}, {"duration": 0.99999599999999944, "start": 9.0000660000000003, "val": 4959785000.0}, {"duration": 1.0, "start": 10.000062, "val": 4949278720}, {"duration": 0.99999900000000075, "start": 11.000062, "val": 4949283000.0}, {"duration": 1.0000549999999997, "start": 12.000061000000001, "val": 4938521000.0}, {"duration": 0.99994599999999956, "start": 13.000116, "val": 4939060000.0}, {"duration": 1.0000029999999995, "start": 14.000062, "val": 4928292000.0}, {"duration": 0.99999100000000141, "start": 15.000064999999999, "val": 4980781000.0}, {"duration": 1.0001069999999999, "start": 16.000056000000001, "val": 3009091000.0}, {"duration": 0.99989899999999921, "start": 17.000163000000001, "val": 1719838000.0}, {"duration": 1.0000059999999991, "start": 18.000062, "val": 1814026000.0}, {"duration": 1.0000220000000013, "start": 19.000067999999999, "val": 1971280000.0}]]}, {"event-type": "packet-retransmits-subintervals", "val": [{"duration": 1.0000979999999999, "start": 0, "val": 0}, {"duration": 0.99998200000000015, "start": 1.0000979999999999, "val": 0}, {"duration": 1.0000239999999998, "start": 2.0000800000000001, "val": 0}, {"duration": 0.99995500000000037, "start": 3.0001039999999999, "val": 0}, {"duration": 0.99999899999999986, "start": 4.0000590000000003, "val": 0}, {"duration": 1.000006, "start": 5.0000580000000001, "val": 0}, {"duration": 1.0000119999999999, "start": 6.0000640000000001, "val": 0}, {"duration": 0.99998199999999926, "start": 7.000076, "val": 0}, {"duration": 1.0000020000000003, "start": 8.0000579999999992, "val": 0}, {"duration": 0.99999799999999972, "start": 9.0000599999999995, "val": 0}, {"duration": 1.0, "start": 10.000057999999999, "val": 0}, {"duration": 1.0, "start": 11.000057999999999, "val": 0}, {"duration": 1.0000550000000015, "start": 12.000057999999999, "val": 0}, {"duration": 0.99994499999999853, "start": 13.000113000000001, "val": 0}, {"duration": 1.0000020000000003, "start": 14.000057999999999, "val": 0}, {"duration": 0.99999200000000066, "start": 15.00006, "val": 0}, {"duration": 1.0001080000000009, "start": 16.000052, "val": 33}, {"duration": 0.99989899999999921, "start": 17.000160000000001, "val": 0}, {"duration": 1.000004999999998, "start": 18.000059, "val": 0}, {"duration": 1.0000220000000013, "start": 19.000063999999998, "val": 0}]}, {"event-type": "streams-packet-retransmits-subintervals", "val": [[{"duration": 1.0000979999999999, "start": 0, "val": 0}, {"duration": 0.99998200000000015, "start": 1.0000979999999999, "val": 0}, {"duration": 1.0000239999999998, "start": 2.0000800000000001, "val": 0}, {"duration": 0.99995500000000037, "start": 3.0001039999999999, "val": 0}, {"duration": 0.99999899999999986, "start": 4.0000590000000003, "val": 0}, {"duration": 1.000006, "start": 5.0000580000000001, "val": 0}, {"duration": 1.0000119999999999, "start": 6.0000640000000001, "val": 0}, {"duration": 0.99998199999999926, "start": 7.000076, "val": 0}, {"duration": 1.0000020000000003, "start": 8.0000579999999992, "val": 0}, {"duration": 0.99999799999999972, "start": 9.0000599999999995, "val": 0}, {"duration": 1.0, "start": 10.000057999999999, "val": 0}, {"duration": 1.0, "start": 11.000057999999999, "val": 0}, {"duration": 1.0000550000000015, "start": 12.000057999999999, "val": 0}, {"duration": 0.99994499999999853, "start": 13.000113000000001, "val": 0}, {"duration": 1.0000020000000003, "start": 14.000057999999999, "val": 0}, {"duration": 0.99999200000000066, "start": 15.00006, "val": 0}, {"duration": 1.0001080000000009, "start": 16.000052, "val": 15}, {"duration": 0.99989899999999921, "start": 17.000160000000001, "val": 0}, {"duration": 1.000004999999998, "start": 18.000059, "val": 0}, {"duration": 1.0000220000000013, "start": 19.000063999999998, "val": 0}], [{"duration": 1.0001070000000001, "start": 0, "val": 0}, {"duration": 0.99997700000000012, "start": 1.0001070000000001, "val": 0}, {"duration": 1.0000239999999998, "start": 2.0000840000000002, "val": 0}, {"duration": 0.99995499999999993, "start": 3.000108, "val": 0}, {"duration": 0.99999899999999986, "start": 4.0000629999999999, "val": 0}, {"duration": 1.000006, "start": 5.0000619999999998, "val": 0}, {"duration": 1.0000119999999999, "start": 6.0000679999999997, "val": 0}, {"duration": 0.99998499999999968, "start": 7.0000799999999996, "val": 0}, {"duration": 1.000001000000001, "start": 8.0000649999999993, "val": 0}, {"duration": 0.99999599999999944, "start": 9.0000660000000003, "val": 0}, {"duration": 1.0, "start": 10.000062, "val": 0}, {"duration": 0.99999900000000075, "start": 11.000062, "val": 0}, {"duration": 1.0000549999999997, "start": 12.000061000000001, "val": 0}, {"duration": 0.99994599999999956, "start": 13.000116, "val": 0}, {"duration": 1.0000029999999995, "start": 14.000062, "val": 0}, {"duration": 0.99999100000000141, "start": 15.000064999999999, "val": 0}, {"duration": 1.0001069999999999, "start": 16.000056000000001, "val": 18}, {"duration": 0.99989899999999921, "start": 17.000163000000001, "val": 0}, {"duration": 1.0000059999999991, "start": 18.000062, "val": 0}, {"duration": 1.0000220000000013, "start": 19.000067999999999, "val": 0}]]}, {"event-type": "streams-packet-rtt-subintervals", "val": [[{"duration": 1.0000979999999999, "start": 0, "val": 68000}, {"duration": 0.99998200000000015, "start": 1.0000979999999999, "val": 70250}, {"duration": 1.0000239999999998, "start": 2.0000800000000001, "val": 68750}, {"duration": 0.99995500000000037, "start": 3.0001039999999999, "val": 70000}, {"duration": 0.99999899999999986, "start": 4.0000590000000003, "val": 70875}, {"duration": 1.000006, "start": 5.0000580000000001, "val": 71000}, {"duration": 1.0000119999999999, "start": 6.0000640000000001, "val": 71000}, {"duration": 0.99998199999999926, "start": 7.000076, "val": 76875}, {"duration": 1.0000020000000003, "start": 8.0000579999999992, "val": 86875}, {"duration": 0.99999799999999972, "start": 9.0000599999999995, "val": 93000}, {"duration": 1.0, "start": 10.000057999999999, "val": 86000}, {"duration": 1.0, "start": 11.000057999999999, "val": 86875}, {"duration": 1.0000550000000015, "start": 12.000057999999999, "val": 87625}, {"duration": 0.99994499999999853, "start": 13.000113000000001, "val": 89750}, {"duration": 1.0000020000000003, "start": 14.000057999999999, "val": 94000}, {"duration": 0.99999200000000066, "start": 15.00006, "val": 97000}, {"duration": 1.0001080000000009, "start": 16.000052, "val": 70875}, {"duration": 0.99989899999999921, "start": 17.000160000000001, "val": 70875}, {"duration": 1.000004999999998, "start": 18.000059, "val": 70000}, {"duration": 1.0000220000000013, "start": 19.000063999999998, "val": 70875}], [{"duration": 1.0001070000000001, "start": 0, "val": 68000}, {"duration": 0.99997700000000012, "start": 1.0001070000000001, "val": 68375}, {"duration": 1.0000239999999998, "start": 2.0000840000000002, "val": 69000}, {"duration": 0.99995499999999993, "start": 3.000108, "val": 69875}, {"duration": 0.99999899999999986, "start": 4.0000629999999999, "val": 70000}, {"duration": 1.000006, "start": 5.0000619999999998, "val": 70875}, {"duration": 1.0000119999999999, "start": 6.0000679999999997, "val": 71000}, {"duration": 0.99998499999999968, "start": 7.0000799999999996, "val": 76875}, {"duration": 1.000001000000001, "start": 8.0000649999999993, "val": 86875}, {"duration": 0.99999599999999944, "start": 9.0000660000000003, "val": 93000}, {"duration": 1.0, "start": 10.000062, "val": 86000}, {"duration": 0.99999900000000075, "start": 11.000062, "val": 86875}, {"duration": 1.0000549999999997, "start": 12.000061000000001, "val": 87750}, {"duration": 0.99994599999999956, "start": 13.000116, "val": 89625}, {"duration": 1.0000029999999995, "start": 14.000062, "val": 94500}, {"duration": 0.99999100000000141, "start": 15.000064999999999, "val": 97000}, {"duration": 1.0001069999999999, "start": 16.000056000000001, "val": 70875}, {"duration": 0.99989899999999921, "start": 17.000163000000001, "val": 70875}, {"duration": 1.0000059999999991, "start": 18.000062, "val": 70000}, {"duration": 1.0000220000000013, "start": 19.000067999999999, "val": 70875}]]}, {"event-type": "streams-tcp-windowsize-subintervals", "val": [[{"duration": 1.0000979999999999, "start": 0, "val": 885852}, {"duration": 0.99998200000000015, "start": 1.0000979999999999, "val": 6415716}, {"duration": 1.0000239999999998, "start": 2.0000800000000001, "val": 18388140}, {"duration": 0.99995500000000037, "start": 3.0001039999999999, "val": 48542900}, {"duration": 0.99999899999999986, "start": 4.0000590000000003, "val": 48542900}, {"duration": 1.000006, "start": 5.0000580000000001, "val": 48542900}, {"duration": 1.0000119999999999, "start": 6.0000640000000001, "val": 48542900}, {"duration": 0.99998199999999926, "start": 7.000076, "val": 48542900}, {"duration": 1.0000020000000003, "start": 8.0000579999999992, "val": 53482196}, {"duration": 0.99999799999999972, "start": 9.0000599999999995, "val": 57446160}, {"duration": 1.0, "start": 10.000057999999999, "val": 57571432}, {"duration": 1.0, "start": 11.000057999999999, "val": 57571432}, {"duration": 1.0000550000000015, "start": 12.000057999999999, "val": 57571432}, {"duration": 0.99994499999999853, "start": 13.000113000000001, "val": 57571432}, {"duration": 1.0000020000000003, "start": 14.000057999999999, "val": 58385700}, {"duration": 0.99999200000000066, "start": 15.00006, "val": 60085820}, {"duration": 1.0001080000000009, "start": 16.000052, "val": 15220548}, {"duration": 0.99989899999999921, "start": 17.000160000000001, "val": 15417404}, {"duration": 1.000004999999998, "start": 18.000059, "val": 16374840}, {"duration": 1.0000220000000013, "start": 19.000063999999998, "val": 18236024}], [{"duration": 1.0001070000000001, "start": 0, "val": 608464}, {"duration": 0.99997700000000012, "start": 1.0001070000000001, "val": 5592500}, {"duration": 1.0000239999999998, "start": 2.0000840000000002, "val": 13833608}, {"duration": 0.99995499999999993, "start": 3.000108, "val": 37778456}, {"duration": 0.99999899999999986, "start": 4.0000629999999999, "val": 43379904}, {"duration": 1.000006, "start": 5.0000619999999998, "val": 43532020}, {"duration": 1.0000119999999999, "start": 6.0000679999999997, "val": 43898888}, {"duration": 0.99998499999999968, "start": 7.0000799999999996, "val": 47164908}, {"duration": 1.000001000000001, "start": 8.0000649999999993, "val": 53473248}, {"duration": 0.99999599999999944, "start": 9.0000660000000003, "val": 57410368}, {"duration": 1.0, "start": 10.000062, "val": 57553536}, {"duration": 0.99999900000000075, "start": 11.000062, "val": 57553536}, {"duration": 1.0000549999999997, "start": 12.000061000000001, "val": 57553536}, {"duration": 0.99994599999999956, "start": 13.000116, "val": 57553536}, {"duration": 1.0000029999999995, "start": 14.000062, "val": 58376752}, {"duration": 0.99999100000000141, "start": 15.000064999999999, "val": 60542168}, {"duration": 1.0001069999999999, "start": 16.000056000000001, "val": 15283184}, {"duration": 0.99989899999999921, "start": 17.000163000000001, "val": 15462144}, {"duration": 1.0000059999999991, "start": 18.000062, "val": 16401684}, {"duration": 1.0000220000000013, "start": 19.000067999999999, "val": 18271816}]]}]}]
        test_spec = {
            "source": "10.0.0.1",
            "dest": "10.0.0.2",
            "duration": "PT30S",
            "parallel": 2,
        }
        test_result = {"diags": "YAY RESULTS\n----", "intervals": [{"streams": [{"tcp-window-size": 885852, "end": 1.0000979999999999, "stream-id": 4, "omitted": False, "rtt": 68000, "throughput-bits": 41800959.922431998, "retransmits": 0, "throughput-bytes": 5225632, "start": 0}, {"tcp-window-size": 608464, "end": 1.0001070000000001, "stream-id": 6, "omitted": False, "rtt": 68000, "throughput-bits": 27270584.685490999, "retransmits": 0, "throughput-bytes": 3409188, "start": 0}], "summary": {"end": 1.0000979999999999, "omitted": False, "start": 0, "throughput-bits": 69071791.652649, "retransmits": 0, "throughput-bytes": 8634820}}, {"streams": [{"tcp-window-size": 6415716, "end": 2.0000800000000001, "stream-id": 4, "omitted": False, "rtt": 70250, "throughput-bits": 441881181.45125598, "retransmits": 0, "throughput-bytes": 55234160, "start": 1.0000979999999999}, {"tcp-window-size": 5592500, "end": 2.0000840000000002, "stream-id": 6, "omitted": False, "rtt": 68375, "throughput-bits": 361935282.333287, "retransmits": 0, "throughput-bytes": 45240864, "start": 1.0001070000000001}], "summary": {"end": 2.0000800000000001, "omitted": False, "start": 1.0000979999999999, "throughput-bits": 803814565.324489, "retransmits": 0, "throughput-bytes": 100475024}}, {"streams": [{"tcp-window-size": 18388140, "end": 3.0001039999999999, "stream-id": 4, "omitted": False, "rtt": 68750, "throughput-bits": 1415544000.0, "retransmits": 0, "throughput-bytes": 176947200, "start": 2.0000800000000001}, {"tcp-window-size": 13833608, "end": 3.000108, "stream-id": 6, "omitted": False, "rtt": 69000, "throughput-bits": 1184862000.0, "retransmits": 0, "throughput-bytes": 148111360, "start": 2.0000840000000002}], "summary": {"end": 3.0001039999999999, "omitted": False, "start": 2.0000800000000001, "throughput-bits": 2600406000.0, "retransmits": 0, "throughput-bytes": 325058560}}, {"streams": [{"tcp-window-size": 48542900, "end": 4.0000590000000003, "stream-id": 4, "omitted": False, "rtt": 70000, "throughput-bits": 3974282000.0, "retransmits": 0, "throughput-bytes": 496762880, "start": 3.0001039999999999}, {"tcp-window-size": 37778456, "end": 4.0000629999999999, "stream-id": 6, "omitted": False, "rtt": 69875, "throughput-bits": 2946631000.0, "retransmits": 0, "throughput-bytes": 368312320, "start": 3.000108}], "summary": {"end": 4.0000590000000003, "omitted": False, "start": 3.0001039999999999, "throughput-bits": 6920913000.0, "retransmits": 0, "throughput-bytes": 865075200}}, {"streams": [{"tcp-window-size": 48542900, "end": 5.0000580000000001, "stream-id": 4, "omitted": False, "rtt": 70875, "throughput-bits": 5033170000.0, "retransmits": 0, "throughput-bytes": 629145600, "start": 4.0000590000000003}, {"tcp-window-size": 43379904, "end": 5.0000619999999998, "stream-id": 6, "omitted": False, "rtt": 70000, "throughput-bits": 4928312000.0, "retransmits": 0, "throughput-bytes": 616038400, "start": 4.0000629999999999}], "summary": {"end": 5.0000580000000001, "omitted": False, "start": 4.0000590000000003, "throughput-bits": 9961482000.0, "retransmits": 0, "throughput-bytes": 1245184000}}, {"streams": [{"tcp-window-size": 48542900, "end": 6.0000640000000001, "stream-id": 4, "omitted": False, "rtt": 71000, "throughput-bits": 4938764000.0, "retransmits": 0, "throughput-bytes": 617349120, "start": 5.0000580000000001}, {"tcp-window-size": 43532020, "end": 6.0000679999999997, "stream-id": 6, "omitted": False, "rtt": 70875, "throughput-bits": 4949249000.0, "retransmits": 0, "throughput-bytes": 618659840, "start": 5.0000619999999998}], "summary": {"end": 6.0000640000000001, "omitted": False, "start": 5.0000580000000001, "throughput-bits": 9888013000.0, "retransmits": 0, "throughput-bytes": 1236008960}}, {"streams": [{"tcp-window-size": 48542900, "end": 7.000076, "stream-id": 4, "omitted": False, "rtt": 71000, "throughput-bits": 4949219000.0, "retransmits": 0, "throughput-bytes": 618659840, "start": 6.0000640000000001}, {"tcp-window-size": 43898888, "end": 7.0000799999999996, "stream-id": 6, "omitted": False, "rtt": 71000, "throughput-bits": 4949219000.0, "retransmits": 0, "throughput-bytes": 618659840, "start": 6.0000679999999997}], "summary": {"end": 7.000076, "omitted": False, "start": 6.0000640000000001, "throughput-bits": 9898437000.0, "retransmits": 0, "throughput-bytes": 1237319680}}, {"streams": [{"tcp-window-size": 48542900, "end": 8.0000579999999992, "stream-id": 4, "omitted": False, "rtt": 76875, "throughput-bits": 4917911000.0, "retransmits": 0, "throughput-bytes": 614727680, "start": 7.000076}, {"tcp-window-size": 47164908, "end": 8.0000649999999993, "stream-id": 6, "omitted": False, "rtt": 76875, "throughput-bits": 4959839000.0, "retransmits": 0, "throughput-bytes": 619970560, "start": 7.0000799999999996}], "summary": {"end": 8.0000579999999992, "omitted": False, "start": 7.000076, "throughput-bits": 9877765000.0, "retransmits": 0, "throughput-bytes": 1234698240}}, {"streams": [{"tcp-window-size": 53482196, "end": 9.0000599999999995, "stream-id": 4, "omitted": False, "rtt": 86875, "throughput-bits": 4959754000.0, "retransmits": 0, "throughput-bytes": 619970560, "start": 8.0000579999999992}, {"tcp-window-size": 53473248, "end": 9.0000660000000003, "stream-id": 6, "omitted": False, "rtt": 86875, "throughput-bits": 4970246000.0, "retransmits": 0, "throughput-bytes": 621281280, "start": 8.0000649999999993}], "summary": {"end": 9.0000599999999995, "omitted": False, "start": 8.0000579999999992, "throughput-bits": 9929993000.0, "retransmits": 0, "throughput-bytes": 1241251840}}, {"streams": [{"tcp-window-size": 57446160, "end": 10.000057999999999, "stream-id": 4, "omitted": False, "rtt": 93000, "throughput-bits": 4959775000.0, "retransmits": 0, "throughput-bytes": 619970560, "start": 9.0000599999999995}, {"tcp-window-size": 57410368, "end": 10.000062, "stream-id": 6, "omitted": False, "rtt": 93000, "throughput-bits": 4959785000.0, "retransmits": 0, "throughput-bytes": 619970560, "start": 9.0000660000000003}], "summary": {"end": 10.000057999999999, "omitted": False, "start": 9.0000599999999995, "throughput-bits": 9919550000.0, "retransmits": 0, "throughput-bytes": 1239941120}}, {"streams": [{"tcp-window-size": 57571432, "end": 11.000057999999999, "stream-id": 4, "omitted": False, "rtt": 86000, "throughput-bits": 4949278720, "retransmits": 0, "throughput-bytes": 618659840, "start": 10.000057999999999}, {"tcp-window-size": 57553536, "end": 11.000062, "stream-id": 6, "omitted": False, "rtt": 86000, "throughput-bits": 4949278720, "retransmits": 0, "throughput-bytes": 618659840, "start": 10.000062}], "summary": {"end": 11.000057999999999, "omitted": False, "start": 10.000057999999999, "throughput-bits": 9898557440, "retransmits": 0, "throughput-bytes": 1237319680}}, {"streams": [{"tcp-window-size": 57571432, "end": 12.000057999999999, "stream-id": 4, "omitted": False, "rtt": 86875, "throughput-bits": 4938792960, "retransmits": 0, "throughput-bytes": 617349120, "start": 11.000057999999999}, {"tcp-window-size": 57553536, "end": 12.000061000000001, "stream-id": 6, "omitted": False, "rtt": 86875, "throughput-bits": 4949283000.0, "retransmits": 0, "throughput-bytes": 618659840, "start": 11.000062}], "summary": {"end": 12.000057999999999, "omitted": False, "start": 11.000057999999999, "throughput-bits": 9888071680, "retransmits": 0, "throughput-bytes": 1236008960}}, {"streams": [{"tcp-window-size": 57571432, "end": 13.000113000000001, "stream-id": 4, "omitted": False, "rtt": 87625, "throughput-bits": 4949006000.0, "retransmits": 0, "throughput-bytes": 618659840, "start": 12.000057999999999}, {"tcp-window-size": 57553536, "end": 13.000116, "stream-id": 6, "omitted": False, "rtt": 87750, "throughput-bits": 4938521000.0, "retransmits": 0, "throughput-bytes": 617349120, "start": 12.000061000000001}], "summary": {"end": 13.000113000000001, "omitted": False, "start": 12.000057999999999, "throughput-bits": 9887527000.0, "retransmits": 0, "throughput-bytes": 1236008960}}, {"streams": [{"tcp-window-size": 57571432, "end": 14.000057999999999, "stream-id": 4, "omitted": False, "rtt": 89750, "throughput-bits": 4939065000.0, "retransmits": 0, "throughput-bytes": 617349120, "start": 13.000113000000001}, {"tcp-window-size": 57553536, "end": 14.000062, "stream-id": 6, "omitted": False, "rtt": 89625, "throughput-bits": 4939060000.0, "retransmits": 0, "throughput-bytes": 617349120, "start": 13.000116}], "summary": {"end": 14.000057999999999, "omitted": False, "start": 13.000113000000001, "throughput-bits": 9878130000.0, "retransmits": 0, "throughput-bytes": 1234698240}}, {"streams": [{"tcp-window-size": 58385700, "end": 15.00006, "stream-id": 4, "omitted": False, "rtt": 94000, "throughput-bits": 4928297000.0, "retransmits": 0, "throughput-bytes": 616038400, "start": 14.000057999999999}, {"tcp-window-size": 58376752, "end": 15.000064999999999, "stream-id": 6, "omitted": False, "rtt": 94500, "throughput-bits": 4928292000.0, "retransmits": 0, "throughput-bytes": 616038400, "start": 14.000062}], "summary": {"end": 15.00006, "omitted": False, "start": 14.000057999999999, "throughput-bits": 9856593000.0, "retransmits": 0, "throughput-bytes": 1232076800}}, {"streams": [{"tcp-window-size": 60085820, "end": 16.000052, "stream-id": 4, "omitted": False, "rtt": 97000, "throughput-bits": 4938833000.0, "retransmits": 0, "throughput-bytes": 617349120, "start": 15.00006}, {"tcp-window-size": 60542168, "end": 16.000056000000001, "stream-id": 6, "omitted": False, "rtt": 97000, "throughput-bits": 4980781000.0, "retransmits": 0, "throughput-bytes": 622592000, "start": 15.000064999999999}], "summary": {"end": 16.000052, "omitted": False, "start": 15.00006, "throughput-bits": 9919609000.0, "retransmits": 0, "throughput-bytes": 1239941120}}, {"streams": [{"tcp-window-size": 15220548, "end": 17.000160000000001, "stream-id": 4, "omitted": False, "rtt": 70875, "throughput-bits": 2988119000.0, "retransmits": 15, "throughput-bytes": 373555200, "start": 16.000052}, {"tcp-window-size": 15283184, "end": 17.000163000000001, "stream-id": 6, "omitted": False, "rtt": 70875, "throughput-bits": 3009091000.0, "retransmits": 18, "throughput-bytes": 376176640, "start": 16.000056000000001}], "summary": {"end": 17.000160000000001, "omitted": False, "start": 16.000052, "throughput-bits": 5997207000.0, "retransmits": 33, "throughput-bytes": 749731840}}, {"streams": [{"tcp-window-size": 15417404, "end": 18.000059, "stream-id": 4, "omitted": False, "rtt": 70875, "throughput-bits": 1709352000.0, "retransmits": 0, "throughput-bytes": 213647360, "start": 17.000160000000001}, {"tcp-window-size": 15462144, "end": 18.000062, "stream-id": 6, "omitted": False, "rtt": 70875, "throughput-bits": 1719838000.0, "retransmits": 0, "throughput-bytes": 214958080, "start": 17.000163000000001}], "summary": {"end": 18.000059, "omitted": False, "start": 17.000160000000001, "throughput-bits": 3429190000.0, "retransmits": 0, "throughput-bytes": 428605440}}, {"streams": [{"tcp-window-size": 16374840, "end": 19.000063999999998, "stream-id": 4, "omitted": False, "rtt": 70000, "throughput-bits": 1824513000.0, "retransmits": 0, "throughput-bytes": 228065280, "start": 18.000059}, {"tcp-window-size": 16401684, "end": 19.000067999999999, "stream-id": 6, "omitted": False, "rtt": 70000, "throughput-bits": 1814026000.0, "retransmits": 0, "throughput-bytes": 226754560, "start": 18.000062}], "summary": {"end": 19.000063999999998, "omitted": False, "start": 18.000059, "throughput-bits": 3638541000.0, "retransmits": 0, "throughput-bytes": 454819840}}, {"streams": [{"tcp-window-size": 18236024, "end": 20.000086, "stream-id": 4, "omitted": False, "rtt": 70875, "throughput-bits": 1950308000.0, "retransmits": 0, "throughput-bytes": 243793920, "start": 19.000063999999998}, {"tcp-window-size": 18271816, "end": 20.00009, "stream-id": 6, "omitted": False, "rtt": 70875, "throughput-bits": 1971280000.0, "retransmits": 0, "throughput-bytes": 246415360, "start": 19.000067999999999}], "summary": {"end": 20.000086, "omitted": False, "start": 19.000063999999998, "throughput-bits": 3921587000.0, "retransmits": 0, "throughput-bytes": 490209280}}], "succeeded": True, "summary": {"streams": [{"end": 20.000086, "stream-id": 4, "throughput-bytes": 9218460432, "rtt": 78525, "retransmits": 15, "throughput-bits": 3687368000.0, "start": 0}, {"end": 20.000086, "stream-id": 6, "throughput-bytes": 9054607172, "rtt": 78412, "retransmits": 18, "throughput-bits": 3621827000.0, "start": 0}], "summary": {"throughput-bytes": 18273067604, "start": 0, "end": 20.000086, "throughput-bits": 7309196000.0, "retransmits": 33}}}
        record = esmond_util.EsmondThroughputRecord(
            test_spec=test_spec,
            lead_participant=lead_participant,
            measurement_agent=measurement_agent,
            tool_name=tool_name,
            summaries=summary_map,
            duration=duration,
            ts=test_start_time, 
            test_result=test_result,
            fast_mode=fast_mode
        )
        self.assertEqual(record.test_type, "throughput")
        self.assertEqual(json.dumps(record.metadata, sort_keys=True), json.dumps(EXPECTED_METADATA, sort_keys=True))
        self.assertEqual(json.dumps(record.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))
        
        
    def test_esmond_trace_record(self):
        EXPECTED_METADATA = {'time-probe-interval': 1.0, 'time-test-timeout': 60.0, 'time-duration': 30, 'pscheduler-test-type': 'trace', 'source': '10.0.0.1', 'measurement-agent': '10.0.0.1', 'input-destination': '10.0.0.2', 'destination': '10.0.0.2', 'event-types': [{'event-type': 'failures'}, {'event-type': 'packet-trace'}, {'event-type': 'path-mtu'}], 'subject-type': 'point-to-point', 'input-source': '10.0.0.1', 'tool-name': 'traceroute', 'trace-first-ttl': 2}
        EXPECTED_DATA = [{'ts': 1497971206, 'val': [{'val': [{'success': 1, 'ip': '198.129.252.141', 'hostname': 'lblmr2-lblowamp.es.net', 'rtt': 0.10000000000000001, 'as': {'owner': 'ESNET-WEST - ESnet, US', 'number': 292}, 'ttl': 1, 'query': 1}, {'success': 1, 'ip': '134.55.37.49', 'hostname': 'sacrcr5-ip-a-lblmr2.es.net', 'rtt': 3.2000000000000002, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 2, 'query': 1}, {'success': 1, 'ip': '134.55.50.202', 'hostname': 'denvcr5-ip-a-sacrcr5.es.net', 'rtt': 23.599999999999998, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 3, 'query': 1}, {'success': 1, 'ip': '134.55.49.58', 'hostname': 'kanscr5-ip-a-denvcr5.es.net', 'rtt': 34.200000000000003, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 4, 'query': 1}, {'success': 1, 'ip': '134.55.43.81', 'hostname': 'chiccr5-ip-a-kanscr5.es.net', 'rtt': 45.299999999999997, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 5, 'query': 1}, {'success': 1, 'ip': '134.55.36.46', 'hostname': 'washcr5-ip-a-chiccr5.es.net', 'rtt': 62.399999999999999, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 6, 'query': 1}, {'success': 1, 'ip': '134.55.219.2', 'hostname': 'eqxashcr5-ip-c-washcr5.es.net', 'rtt': 62.899999999999999, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 7, 'query': 1}, {'success': 1, 'ip': '198.124.238.78', 'hostname': 'eqx-ash-owamp.es.net', 'rtt': 62.700000000000003, 'as': {'owner': 'ESNET-EAST - ESnet, US', 'number': 291}, 'ttl': 8, 'query': 1}], 'event-type': 'packet-trace'}]}]
        test_spec = {
            "source": "10.0.0.1",
            "dest": "10.0.0.2",
            "first-ttl": 2,
            "sendwait": "PT1S",
            "wait": "PT60S"
        }
        lead_participant = "10.0.0.1"
        measurement_agent = "10.0.0.1"
        tool_name = "traceroute"
        summary_map = None
        duration = 30
        fast_mode = False
        test_start_time = 1497971206
        test_result = {  
          "paths":[  
             [  
                {  
                   "ip":"198.129.252.141",
                   "as":{  
                      "owner":"ESNET-WEST - ESnet, US",
                      "number":292
                   },
                   "hostname":"lblmr2-lblowamp.es.net",
                   "rtt":"PT0.0001S"
                },
                {  
                   "ip":"134.55.37.49",
                   "as":{  
                      "owner":"ESNET - ESnet, US",
                      "number":293
                   },
                   "hostname":"sacrcr5-ip-a-lblmr2.es.net",
                   "rtt":"PT0.0032S"
                },
                {  
                   "ip":"134.55.50.202",
                   "as":{  
                      "owner":"ESNET - ESnet, US",
                      "number":293
                   },
                   "hostname":"denvcr5-ip-a-sacrcr5.es.net",
                   "rtt":"PT0.0236S"
                },
                {  
                   "ip":"134.55.49.58",
                   "as":{  
                      "owner":"ESNET - ESnet, US",
                      "number":293
                   },
                   "hostname":"kanscr5-ip-a-denvcr5.es.net",
                   "rtt":"PT0.0342S"
                },
                {  
                   "ip":"134.55.43.81",
                   "as":{  
                      "owner":"ESNET - ESnet, US",
                      "number":293
                   },
                   "hostname":"chiccr5-ip-a-kanscr5.es.net",
                   "rtt":"PT0.0453S"
                },
                {  
                   "ip":"134.55.36.46",
                   "as":{  
                      "owner":"ESNET - ESnet, US",
                      "number":293
                   },
                   "hostname":"washcr5-ip-a-chiccr5.es.net",
                   "rtt":"PT0.0624S"
                },
                {  
                   "ip":"134.55.219.2",
                   "as":{  
                      "owner":"ESNET - ESnet, US",
                      "number":293
                   },
                   "hostname":"eqxashcr5-ip-c-washcr5.es.net",
                   "rtt":"PT0.0629S"
                },
                {  
                   "ip":"198.124.238.78",
                   "as":{  
                      "owner":"ESNET-EAST - ESnet, US",
                      "number":291
                   },
                   "hostname":"eqx-ash-owamp.es.net",
                   "rtt":"PT0.0627S"
                }
             ]
          ],
          "succeeded":True,
          "schema":1
       }
        
        #test trace record
        record = esmond_util.EsmondTraceRecord(
            test_spec=test_spec,
            lead_participant=lead_participant,
            measurement_agent=measurement_agent,
            tool_name=tool_name,
            summaries=summary_map,
            duration=duration,
            ts=test_start_time, 
            test_result=test_result,
            fast_mode=fast_mode
        )
        self.assertEqual(record.test_type, "trace")
        self.assertEqual(json.dumps(record.metadata, sort_keys=True), json.dumps(EXPECTED_METADATA, sort_keys=True))
        self.assertEqual(json.dumps(record.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))
        #test enabling raw data
        record.enable_data_raw(test_result=test_result)
        EXPECTED_DATA = [{'ts': 1497971206, 'val': [{'val': [{'success': 1, 'ip': '198.129.252.141', 'hostname': 'lblmr2-lblowamp.es.net', 'rtt': 0.10000000000000001, 'as': {'owner': 'ESNET-WEST - ESnet, US', 'number': 292}, 'ttl': 1, 'query': 1}, {'success': 1, 'ip': '134.55.37.49', 'hostname': 'sacrcr5-ip-a-lblmr2.es.net', 'rtt': 3.2000000000000002, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 2, 'query': 1}, {'success': 1, 'ip': '134.55.50.202', 'hostname': 'denvcr5-ip-a-sacrcr5.es.net', 'rtt': 23.599999999999998, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 3, 'query': 1}, {'success': 1, 'ip': '134.55.49.58', 'hostname': 'kanscr5-ip-a-denvcr5.es.net', 'rtt': 34.200000000000003, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 4, 'query': 1}, {'success': 1, 'ip': '134.55.43.81', 'hostname': 'chiccr5-ip-a-kanscr5.es.net', 'rtt': 45.299999999999997, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 5, 'query': 1}, {'success': 1, 'ip': '134.55.36.46', 'hostname': 'washcr5-ip-a-chiccr5.es.net', 'rtt': 62.399999999999999, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 6, 'query': 1}, {'success': 1, 'ip': '134.55.219.2', 'hostname': 'eqxashcr5-ip-c-washcr5.es.net', 'rtt': 62.899999999999999, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 7, 'query': 1}, {'success': 1, 'ip': '198.124.238.78', 'hostname': 'eqx-ash-owamp.es.net', 'rtt': 62.700000000000003, 'as': {'owner': 'ESNET-EAST - ESnet, US', 'number': 291}, 'ttl': 8, 'query': 1}], 'event-type': 'packet-trace'}, {'val': {'paths': [[{'ip': '198.129.252.141', 'as': {'owner': 'ESNET-WEST - ESnet, US', 'number': 292}, 'hostname': 'lblmr2-lblowamp.es.net', 'rtt': 'PT0.0001S'}, {'ip': '134.55.37.49', 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'hostname': 'sacrcr5-ip-a-lblmr2.es.net', 'rtt': 'PT0.0032S'}, {'ip': '134.55.50.202', 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'hostname': 'denvcr5-ip-a-sacrcr5.es.net', 'rtt': 'PT0.0236S'}, {'ip': '134.55.49.58', 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'hostname': 'kanscr5-ip-a-denvcr5.es.net', 'rtt': 'PT0.0342S'}, {'ip': '134.55.43.81', 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'hostname': 'chiccr5-ip-a-kanscr5.es.net', 'rtt': 'PT0.0453S'}, {'ip': '134.55.36.46', 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'hostname': 'washcr5-ip-a-chiccr5.es.net', 'rtt': 'PT0.0624S'}, {'ip': '134.55.219.2', 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'hostname': 'eqxashcr5-ip-c-washcr5.es.net', 'rtt': 'PT0.0629S'}, {'ip': '198.124.238.78', 'as': {'owner': 'ESNET-EAST - ESnet, US', 'number': 291}, 'hostname': 'eqx-ash-owamp.es.net', 'rtt': 'PT0.0627S'}]], 'succeeded': True, 'schema': 1}, 'event-type': 'pscheduler-raw'}]}]
        self.assertEqual(json.dumps(record.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))
        
        #test MTU
        EXPECTED_METADATA = {'time-duration': 30, 'pscheduler-test-type': 'trace', 'source': '10.0.0.1', 'measurement-agent': '10.0.0.1', 'input-destination': '10.0.0.2', 'destination': '10.0.0.2', 'event-types': [{'event-type': 'failures'}, {'event-type': 'packet-trace'}, {'event-type': 'path-mtu'}], 'subject-type': 'point-to-point', 'input-source': '10.0.0.1', 'time-test-timeout': 60.0, 'tool-name': 'tracepath', 'trace-first-ttl': 2, 'time-probe-interval': 1.0}
        EXPECTED_DATA = [{'ts': 1497971206, 'val': [{'val': [{'success': 1, 'ip': '198.129.254.29', 'hostname': 'lblmr2-lblpt1.es.net', 'mtu': 9000, 'rtt': 7.7270000000000003, 'as': {'owner': 'ESNET-WEST - ESnet, US', 'number': 292}, 'ttl': 1, 'query': 1}, {'success': 1, 'ip': '134.55.37.49', 'hostname': 'sacrcr5-ip-a-lblmr2.es.net', 'mtu': 9000, 'rtt': 2.8029999999999999, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 2, 'query': 1}, {'success': 1, 'ip': '134.55.50.202', 'hostname': 'denvcr5-ip-a-sacrcr5.es.net', 'mtu': 9000, 'rtt': 23.716000000000001, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 3, 'query': 1}, {'success': 1, 'ip': '134.55.49.58', 'hostname': 'kanscr5-ip-a-denvcr5.es.net', 'mtu': 9000, 'rtt': 34.311, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 4, 'query': 1}, {'success': 1, 'ip': '134.55.43.81', 'hostname': 'chiccr5-ip-a-kanscr5.es.net', 'mtu': 9000, 'rtt': 45.302, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 5, 'query': 1}, {'success': 1, 'ip': '134.55.36.46', 'hostname': 'washcr5-ip-a-chiccr5.es.net', 'mtu': 9000, 'rtt': 62.466000000000001, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 6, 'query': 1}, {'query': 1, 'mtu': 9000, 'success': 1, 'ttl': 7}, {'success': 1, 'ip': '134.55.37.78', 'hostname': 'newycr5-ip-a-aofacr5.es.net', 'mtu': 9000, 'rtt': 67.718000000000004, 'as': {'owner': 'ESNET - ESnet, US', 'number': 293}, 'ttl': 8, 'query': 1}, {'success': 1, 'ip': '198.124.238.54', 'hostname': 'newy-pt1.es.net', 'mtu': 9000, 'rtt': 67.436999999999998, 'as': {'owner': 'ESNET-EAST - ESnet, US', 'number': 291}, 'ttl': 9, 'query': 1}], 'event-type': 'packet-trace'}, {'val': 9000, 'event-type': 'path-mtu'}]}]
        tool_name = "tracepath"
        test_result = {"paths": [[{"ip": "198.129.254.29", "as": {"owner": "ESNET-WEST - ESnet, US", "number": 292}, "hostname": "lblmr2-lblpt1.es.net", "mtu": 9000, "rtt": "PT0.007727S"}, {"ip": "134.55.37.49", "as": {"owner": "ESNET - ESnet, US", "number": 293}, "hostname": "sacrcr5-ip-a-lblmr2.es.net", "mtu": 9000, "rtt": "PT0.002803S"}, {"ip": "134.55.50.202", "as": {"owner": "ESNET - ESnet, US", "number": 293}, "hostname": "denvcr5-ip-a-sacrcr5.es.net", "mtu": 9000, "rtt": "PT0.023716S"}, {"ip": "134.55.49.58", "as": {"owner": "ESNET - ESnet, US", "number": 293}, "hostname": "kanscr5-ip-a-denvcr5.es.net", "mtu": 9000, "rtt": "PT0.034311S"}, {"ip": "134.55.43.81", "as": {"owner": "ESNET - ESnet, US", "number": 293}, "hostname": "chiccr5-ip-a-kanscr5.es.net", "mtu": 9000, "rtt": "PT0.045302S"}, {"ip": "134.55.36.46", "as": {"owner": "ESNET - ESnet, US", "number": 293}, "hostname": "washcr5-ip-a-chiccr5.es.net", "mtu": 9000, "rtt": "PT0.062466S"}, {}, {"ip": "134.55.37.78", "as": {"owner": "ESNET - ESnet, US", "number": 293}, "hostname": "newycr5-ip-a-aofacr5.es.net", "mtu": 9000, "rtt": "PT0.067718S"}, {"ip": "198.124.238.54", "as": {"owner": "ESNET-EAST - ESnet, US", "number": 291}, "hostname": "newy-pt1.es.net", "mtu": 9000, "rtt": "PT0.067437S"}]], "succeeded": True, "schema": 1}
        record = esmond_util.EsmondTraceRecord(
            test_spec=test_spec,
            lead_participant=lead_participant,
            measurement_agent=measurement_agent,
            tool_name=tool_name,
            summaries=summary_map,
            duration=duration,
            ts=test_start_time, 
            test_result=test_result,
            fast_mode=fast_mode
        )
        self.assertEqual(record.test_type, "trace")
        self.assertEqual(json.dumps(record.metadata, sort_keys=True), json.dumps(EXPECTED_METADATA, sort_keys=True))
        self.assertEqual(json.dumps(record.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))

        
    def test_esmond_rtt_record(self):
        EXPECTED_METADATA = {"destination": "10.0.0.2", "event-types": [{"event-type": "failures"}, {"event-type": "packet-count-sent", "summaries": [{"event-type": "packet-count-sent", "summary-type": "aggregation", "summary-window": 300}, {"event-type": "packet-count-sent", "summary-type": "aggregation", "summary-window": 3600}, {"event-type": "packet-count-sent", "summary-type": "aggregation", "summary-window": 86400}]}, {"event-type": "histogram-rtt", "summaries": [{"event-type": "histogram-rtt", "summary-type": "statistics", "summary-window": 0}, {"event-type": "histogram-rtt", "summary-type": "aggregation", "summary-window": 3600}, {"event-type": "histogram-rtt", "summary-type": "statistics", "summary-window": 3600}, {"event-type": "histogram-rtt", "summary-type": "aggregation", "summary-window": 86400}, {"event-type": "histogram-rtt", "summary-type": "statistics", "summary-window": 86400}]}, {"event-type": "histogram-ttl-reverse"}, {"event-type": "packet-duplicates-bidir"}, {"event-type": "packet-loss-rate-bidir", "summaries": [{"event-type": "packet-loss-rate-bidir", "summary-type": "aggregation", "summary-window": 3600}, {"event-type": "packet-loss-rate-bidir", "summary-type": "aggregation", "summary-window": 86400}]}, {"event-type": "packet-count-lost-bidir", "summaries": [{"event-type": "packet-count-lost-bidir", "summary-type": "aggregation", "summary-window": 300}, {"event-type": "packet-count-lost-bidir", "summary-type": "aggregation", "summary-window": 3600}, {"event-type": "packet-count-lost-bidir", "summary-type": "aggregation", "summary-window": 86400}]}, {"event-type": "packet-reorders-bidir"}], "input-destination": "10.0.0.2", "input-source": "10.0.0.1", "measurement-agent": "10.0.0.1", "pscheduler-test-type": "rtt", "sample-size": 60, "source": "10.0.0.1", "subject-type": "point-to-point", "time-duration": 30, "tool-name": "ping"}
        EXPECTED_DATA = [{'ts': 1497971206, 'val': [{'val': 0, 'event-type': 'packet-duplicates-bidir'}, {'val': 0, 'event-type': 'packet-reorders-bidir'}, {'val': 0, 'event-type': 'packet-count-lost-bidir'}, {'val': 5, 'event-type': 'packet-count-sent'}, {'val': {'53.90': 2, '53.80': 3}, 'event-type': 'histogram-rtt'}, {'val': {54: 5}, 'event-type': 'histogram-ttl-reverse'}, {'val': {'denominator': 5, 'numerator': 0}, 'event-type': 'packet-loss-rate-bidir'}]}]
        test_spec = {
            "source": "10.0.0.1",
            "dest": "10.0.0.2",
            "count": 60,
        }
        lead_participant = "10.0.0.1"
        measurement_agent = "10.0.0.1"
        tool_name = "ping"
        summary_map = None
        duration = 30
        fast_mode = False
        test_start_time = 1497971206
        test_result = {  
          "loss":0.0,
          "succeeded":True,
          "lost":0,
          "min":"PT0.053848S",
          "duplicates":0,
          "max":"PT0.053934S",
          "received":5,
          "reorders":0,
          "stddev":"PT0.000256S",
          "roundtrips":[  
             {  
                "seq":1,
                "ip":"207.75.164.248",
                "hostname":"internet2.edu",
                "rtt":"PT0.0538S",
                "length":64,
                "ttl":54
             },
             {  
                "seq":2,
                "ip":"207.75.164.248",
                "hostname":"internet2.edu",
                "rtt":"PT0.0538S",
                "length":64,
                "ttl":54
             },
             {  
                "seq":3,
                "ip":"207.75.164.248",
                "hostname":"internet2.edu",
                "rtt":"PT0.0539S",
                "length":64,
                "ttl":54
             },
             {  
                "seq":4,
                "ip":"207.75.164.248",
                "hostname":"internet2.edu",
                "rtt":"PT0.0539S",
                "length":64,
                "ttl":54
             },
             {  
                "seq":5,
                "ip":"207.75.164.248",
                "hostname":"internet2.edu",
                "rtt":"PT0.0538S",
                "length":64,
                "ttl":54
             }
          ],
          "mean":"PT0.053889S",
          "sent":5,
          "schema":1
        }
        
        #test rtt record
        record = esmond_util.EsmondRTTRecord(
            test_spec=test_spec,
            lead_participant=lead_participant,
            measurement_agent=measurement_agent,
            tool_name=tool_name,
            summaries=summary_map,
            duration=duration,
            ts=test_start_time, 
            test_result=test_result,
            fast_mode=fast_mode
        )
        
        self.assertEqual(record.test_type, "rtt")
        self.assertEqual(json.dumps(record.metadata, sort_keys=True), json.dumps(EXPECTED_METADATA, sort_keys=True))
        self.assertEqual(json.dumps(record.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))

    def test_esmond_raw_record(self):
        EXPECTED_METADATA = {'time-duration': 30, 'pscheduler-bar-example-key': 99, 'event-types': [{'event-type': 'pscheduler-raw'}], 'pscheduler-bar-dict-key-key1': 'val1', 'pscheduler-bar-dict-key-key2': 'val2', 'pscheduler-bar-dest': '10.0.0.2', 'subject-type': 'point-to-point', 'measurement-agent': '10.0.0.1', 'destination': '10.0.0.2', 'source': '10.0.0.1', 'pscheduler-bar-dict-key-key4-key4_1': 'val4_1', 'pscheduler-bar-list-key-0': 0, 'pscheduler-bar-list-key-1': 1, 'pscheduler-bar-list-key-2': 'blue', 'pscheduler-bar-list-key-3': True, 'pscheduler-bar-list-key-4': {'key1': 'val1'}, 'pscheduler-test-type': 'bar', 'pscheduler-bar-dict-key-key3-2': 'c', 'pscheduler-bar-dict-key-key3-0': 'a', 'pscheduler-bar-dict-key-key3-1': 'b', 'input-source': '10.0.0.1', 'input-destination': '10.0.0.2', 'pscheduler-bar-another-key': 'example', 'tool-name': 'foo', 'pscheduler-bar-source': '10.0.0.1'}
        EXPECTED_DATA = [{'ts': 1497971206, 'val': [{'val': {'string': 'yay', 'succeeded': True, 'int': 12345, 'object': {'two': 2, 'one': 1}, 'num': 123.45, 'array': ['one', 'two']}, 'event-type': 'pscheduler-raw'}]}]
        test_spec = {
            "source": "10.0.0.1",
            "dest": "10.0.0.2",
            "example-key": 99,
            "another-key": "example",
            "list-key" : [0, 1, "blue", True, {"key1": "val1"}],
            "dict-key": {
                "key1": "val1",
                "key2": "val2",
                "key3": ['a', 'b', 'c'],
                "key4": {"key4_1": "val4_1"}
            }
        }
        lead_participant = "10.0.0.1"
        measurement_agent = "10.0.0.1"
        tool_name = "foo"
        test_type="bar"
        summary_map = None
        duration = 30
        fast_mode = False
        test_start_time = 1497971206
        test_result = {  
          "succeeded": True,
          "string" : "yay",
          "int": 12345,
          "num": 123.45,
          "array": [ "one", "two" ],
          "object": {
            "one": 1,
            "two": 2,
          }
        }
        
        #test raw record
        record = esmond_util.EsmondRawRecord(
            test_type=test_type,
            test_spec=test_spec,
            lead_participant=lead_participant,
            measurement_agent=measurement_agent,
            tool_name=tool_name,
            summaries=summary_map,
            duration=duration,
            ts=test_start_time, 
            test_result=test_result,
            fast_mode=fast_mode
        )
        self.assertEqual(record.test_type, test_type)
        self.assertEqual(json.dumps(record.metadata, sort_keys=True), json.dumps(EXPECTED_METADATA, sort_keys=True))
        self.assertEqual(json.dumps(record.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))

    def test_failure(self):
        test_spec = {
            "source": "10.0.0.1",
            "dest": "10.0.0.2",
            "example-key": 99,
            "another-key": "example"
        }
        lead_participant = "10.0.0.1"
        measurement_agent = "10.0.0.1"
        tool_name = "foo"
        test_type="bar"
        summary_map = None
        duration = 30
        fast_mode = False
        test_start_time = 1497971206
        test_result = {  
          "succeeded": False,
          "error" : "Error provided by test"
        }
        
        #test given failure record
        EXPECTED_DATA = [{'ts': 1497971206, 'val': [{'val': {'error': 'Error provided by test'}, 'event-type': 'failures'}]}]
        record = esmond_util.EsmondRawRecord(
            test_type=test_type,
            test_spec=test_spec,
            lead_participant=lead_participant,
            measurement_agent=measurement_agent,
            tool_name=tool_name,
            summaries=summary_map,
            duration=duration,
            ts=test_start_time, 
            test_result=test_result,
            fast_mode=fast_mode
        )
        self.assertEqual(json.dumps(record.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))
        
        #test when no success field or error
        EXPECTED_DATA = [{'ts': 1497971206, 'val': [{'val': {'error': 'The test failed for an unspecified reason. See the server logs of the testing host(s).'}, 'event-type': 'failures'}]}]
        record = esmond_util.EsmondRawRecord(
            test_type=test_type,
            test_spec=test_spec,
            lead_participant=lead_participant,
            measurement_agent=measurement_agent,
            tool_name=tool_name,
            summaries=summary_map,
            duration=duration,
            ts=test_start_time, 
            test_result={},
            fast_mode=fast_mode
        )
        
        self.assertEqual(json.dumps(record.data, sort_keys=True), json.dumps(EXPECTED_DATA, sort_keys=True))

        
if __name__ == '__main__':
    unittest.main()


