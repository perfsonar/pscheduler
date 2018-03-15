#
# Validator for "throughput" Test
#

from pscheduler import json_validate
import json

SPEC_SCHEMA = {        
    "title": "pScheduler Throughput Specification Schema",
    "type": "object",
    "additionalProperties": False,
    "local": {
        },
    "required": ["dest"],
    "properties": {           
        "schema":      { "$ref": "#/pScheduler/Cardinal" },
        "source":      { "$ref": "#/pScheduler/Host" },
        "source-node": { "$ref": "#/pScheduler/URLHostPort" },
        "dest":        { "$ref": "#/pScheduler/Host" },
        "dest-node":   { "$ref": "#/pScheduler/URLHostPort" },
        "duration":    { "$ref": "#/pScheduler/Duration" },
        "interval":    { "$ref": "#/pScheduler/Duration" },
        "parallel":    { "$ref": "#/pScheduler/Cardinal" },
        "udp":         { "$ref": "#/pScheduler/Boolean" },
        "bandwidth":   { "$ref": "#/pScheduler/Cardinal" },           
        "window-size": { "$ref": "#/pScheduler/Cardinal" },
        "mss":         { "$ref": "#/pScheduler/Cardinal" },
        "buffer-length": { "$ref": "#/pScheduler/Cardinal" },
        "ip-tos":        { "$ref": "#/pScheduler/IPTOS" },
        "ip-version":    { "$ref": "#/pScheduler/ip-version" },
        "local-address": { "$ref": "#/pScheduler/Host" },
        "omit":          { "$ref": "#/pScheduler/Duration" },
        "no-delay":    { "$ref": "#/pScheduler/Boolean" },
        "congestion":    { "enum": ["reno", "cubic", "bic", "htcp", "vegas",
                                    "westwood", "yeah", "bbr"]
                           },
        "zero-copy":    { "$ref": "#/pScheduler/Boolean" },
        "flow-label":    { "$ref": "#/pScheduler/Cardinal" },
        "client-cpu-affinity":    { "$ref": "#/pScheduler/Integer" },
        "server-cpu-affinity":    { "$ref": "#/pScheduler/Integer" },
        "single-ended": { "$ref": "#/pScheduler/Boolean" },
        "reverse": { "$ref": "#/pScheduler/Boolean" }
        }
    }

RESULT_SCHEMA = {        
    "title": "pScheduler Throughput Response Schema",
    "type": "object",
    "additionalProperties": False,
    "local": {
        "throughput-data": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "throughput-bits": {
                    "description": "Summarized view of the overall sender throughput rate in bits/second",
                    "type": "number"
                    },
                "throughput-bytes": {
                    "description": "Summarized view of the overall sender throughput rate in bytes/second",
                    "type": "number"
                    },
                "receiver-throughput-bits": {
                    "description": "Summarized view of the overall receiver throughput rate in bits/second",
                    "type": "number"
                    },
                "sent": {
                    "description": "Number of packets sent",
                    "type": ["integer", "null"]
                    },
                "lost": {
                    "description": "Summarized view of the overall lost packets",
                    "type": ["integer", "null"]
                    },
                "jitter": {
                    "description": "Jitter reported",
                    "type": ["number", "null"]
                    },
                "stream-id": {
                    "description": "The ID of the stream, most relevant when running parallel streams",
                    "type": ["string", "integer"]
                    },
                "start": {
                    "description": "The relative start time of this reporting interval, relative to the start of the test",
                    "type": "number"
                    },
                "end": {
                    "description": "The relative end time of this reporting interval, relative to the start of the test",
                    "type": "number"
                    },
                "rtt": {
                    "description": "The RTT of the request",
                    "type": ["number", "null"]
                    },
                "tcp-window-size": {
                    "description": "The TCP window size at this point in time",
                    "type": ["integer", "null"]
                    },
                "retransmits": {
                    "description": "The number of retransmitted packets during this window",
                    "type": ["integer", "null"]
                    },
                "omitted": {
                    "description": "Whether this interval was omitted for the summary",
                    "$ref": "#/pScheduler/Boolean"
                    }
                }
            }
        },
    "required": ["succeeded", "diags", "intervals", "summary"],
    "properties": {           
        "schema": { "$ref": "#/pScheduler/Cardinal" },
        "succeeded": {
            "description": "Indicates if the test ran successfully",
            "type": "boolean"
            },
        "diags": {
            "description": "Raw output from the underlying tool",
            "type": "string"
            },
        "mss": {
            "description": "The max segment size reported by the tool",
            "type": "integer"
            },
        "mtu": {
            "description": "The MTU reported by the tool",
            "type": "integer"
            },
        "tcp-window-size": {
            "description": "The tcp window size used by the tool",
            "type": "integer"
            },
        "requested-tcp-window-size": {
            "description": "The tcp window size used by the tool",
            "type": "integer"
            },
        "intervals": {
            "description": "The breakdown of intervals of the test",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "streams": {
                        "description": "An array of information about each of the streams during this interval",
                        "type": "array",
                        "items": { "$ref": "#/local/throughput-data" }
                        },
                    "summary": { "$ref": "#/local/throughput-data" }                        
                    }
                }
            },
        "summary": {
            "description": "An object containing summaries of each stream and the test as a whole",
            "type": "object",
            "properties": {
                "streams": {
                    "description": "An array of objects containing summarized information for all streams for a given start/end period",
                    "type": "array",
                    "items": { "$ref": "#/local/throughput-data" }
                    },
                "summary": {"$ref": "#/local/throughput-data"}
                }
            }
        }
    }

LIMIT_SCHEMA = {
    "type": "object",
    "properties": {
        "schema":     { "$ref": "#/pScheduler/Cardinal" },
        "bandwidth":  { "$ref": "#/pScheduler/Limit/SINumber" },
        "duration":   { "$ref": "#/pScheduler/Limit/Duration" },
        "udp":        { "$ref": "#/pScheduler/Limit/Boolean" },
        "ip-version": { "$ref": "#/pScheduler/Limit/IPVersionList" },
        "parallel":   { "$ref": "#/pScheduler/Limit/Cardinal"},
        "source":     { "$ref": "#/pScheduler/Limit/IPCIDRList"},
        "dest":       { "$ref": "#/pScheduler/Limit/IPCIDRList"},
        "endpoint":   { "$ref": "#/pScheduler/Limit/IPCIDRList"}
        },
    "additionalProperties": False
    }


def spec_is_valid(input_json):
    return json_validate(input_json, SPEC_SCHEMA)


def result_is_valid(input_json):
    return json_validate(input_json, RESULT_SCHEMA)


def limit_is_valid(input_json):
    return json_validate(input_json, LIMIT_SCHEMA)


if __name__ == "__main__":
    print result_is_valid({"diags": "------------------------------------------------------------\nClient connecting to 10.0.2.4, TCP port 5001\nTCP window size: 19.3 KByte (default)\n------------------------------------------------------------\n[  3] local 10.0.2.15 port 35914 connected with 10.0.2.4 port 5001\n[ ID] Interval       Transfer     Bandwidth\n[  3]  0.0- 1.0 sec   165 MBytes  1.39 Gbits/sec\n[  3]  1.0- 2.0 sec   207 MBytes  1.73 Gbits/sec\n[  3]  2.0- 3.0 sec   188 MBytes  1.58 Gbits/sec\n[  3]  3.0- 4.0 sec   213 MBytes  1.78 Gbits/sec\n[  3]  4.0- 5.0 sec   210 MBytes  1.76 Gbits/sec\n[  3]  5.0- 6.0 sec   224 MBytes  1.88 Gbits/sec\n[  3]  6.0- 7.0 sec   221 MBytes  1.85 Gbits/sec\n[  3]  7.0- 8.0 sec   221 MBytes  1.85 Gbits/sec\n[  3]  8.0- 9.0 sec   227 MBytes  1.90 Gbits/sec\n[  3]  9.0-10.0 sec   223 MBytes  1.87 Gbits/sec\n[  3]  0.0-10.0 sec  2.05 GBytes  1.76 Gbits/sec\n", "intervals": [{"streams": [{"jitter": None, "throughput-bits": 1390000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 120000000, "start": 0.0, "end": 1.0, "sent": None}], "summary": {"jitter": None, "throughput-bits": 1390000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 165000000.0, "start": 0.0, "end": 1.0, "sent": None}}, {"streams": [{"jitter": None, "throughput-bits": 1730000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 207000000.0, "start": 1.0, "end": 2.0, "sent": None}], "summary": {"jitter": None, "throughput-bits": 1730000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 207000000.0, "start": 1.0, "end": 2.0, "sent": None}}, {"streams": [{"jitter": None, "throughput-bits": 1580000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 188000000.0, "start": 2.0, "end": 3.0, "sent": None}], "summary": {"jitter": None, "throughput-bits": 1580000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 188000000.0, "start": 2.0, "end": 3.0, "sent": None}}, {"streams": [{"jitter": None, "throughput-bits": 1780000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 213000000.0, "start": 3.0, "end": 4.0, "sent": None}], "summary": {"jitter": None, "throughput-bits": 1780000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 213000000.0, "start": 3.0, "end": 4.0, "sent": None}}, {"streams": [{"jitter": None, "throughput-bits": 1760000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 210000000.0, "start": 4.0, "end": 5.0, "sent": None}], "summary": {"jitter": None, "throughput-bits": 1760000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 210000000.0, "start": 4.0, "end": 5.0, "sent": None}}, {"streams": [{"jitter": None, "throughput-bits": 1880000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 224000000.0, "start": 5.0, "end": 6.0, "sent": None}], "summary": {"jitter": None, "throughput-bits": 1880000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 224000000.0, "start": 5.0, "end": 6.0, "sent": None}}, {"streams": [{"jitter": None, "throughput-bits": 1850000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 221000000.0, "start": 6.0, "end": 7.0, "sent": None}], "summary": {"jitter": None, "throughput-bits": 1850000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 221000000.0, "start": 6.0, "end": 7.0, "sent": None}}, {"streams": [{"jitter": None, "throughput-bits": 1850000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 221000000.0, "start": 7.0, "end": 8.0, "sent": None}], "summary": {"jitter": None, "throughput-bits": 1850000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 221000000.0, "start": 7.0, "end": 8.0, "sent": None}}, {"streams": [{"jitter": None, "throughput-bits": 1900000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 227000000.0, "start": 8.0, "end": 9.0, "sent": None}], "summary": {"jitter": None, "throughput-bits": 1900000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 227000000.0, "start": 8.0, "end": 9.0, "sent": None}}, {"streams": [{"jitter": None, "throughput-bits": 1870000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 223000000.0, "start": 9.0, "end": 10.0, "sent": None}], "summary": {"jitter": None, "throughput-bits": 1870000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 223000000.0, "start": 9.0, "end": 10.0, "sent": None}}], "succeeded": True, "summary": {"streams": [{"jitter": None, "throughput-bits": 1760000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 2049999999.9999998, "start": 0.0, "end": 10.0, "sent": None}], "summary": {"jitter": None, "throughput-bits": 1760000000.0, "lost": None, "stream-id": 3, "throughput-bytes": 2049999999.9999998, "start": 0.0, "end": 10.0, "sent": None}}})

