import re
import pscheduler
import pprint
import json

logger = pscheduler.Log()

# A whole bunch of pattern matching against the output of the "iperf3" tool
# client output. Builds up an object of interesting bits from it.
def parse_output(lines):
    results = {}
    results['succeeded'] = True

    try:
        content = json.loads("".join(lines))
    except Exception as e:
        results['succeeded'] = False
        results['error'] = "Unable to parse iperf3 output as JSON: %s" % e  
        return results

    intervals = content['intervals']

    final_streams = []

    # Go through the JSON and convert to what we're expecting in throughput tests
    # This is mostly a renaming since it's so similar
    for interval in intervals:
        streams = interval['streams']
        summary = interval['sum']        

        renamed_streams = []

        for stream in streams:
            new_stream = rename_json(stream)
            renamed_streams.append(new_stream)

        renamed_summary = rename_json(summary)

        final_streams.append({
                "streams": renamed_streams,
                "summary": renamed_summary
                })


    sum_end = content['end']

    # the "summary" keys are different for UDP/TCP here
    if sum_end.has_key("sum_sent"):
        summary = sum_end["sum_sent"]
    else:
        summary = sum_end['sum']

    final_summary = rename_json(summary)

    results["intervals"] = final_streams
    results["summary"]   = final_summary

    return results


def rename_json(obj):
    new_obj = {}

    lookup = {
        "socket": "stream-id",
        "start": "start",
        "end": "end",
        "bytes": "throughput-bytes",
        "bits_per_second": "throughput-bits",
        "ommitted": "omitted",

        # only for UDP
        "packets": "sent",
        "lost_packets": "lost",

        # only for TCP
        "retransmits": "retransmits",
        "snd_cwnd": "window",
        "rtt": "rtt"
        }

    for k,v in obj.iteritems():
        if lookup.has_key(k):
            new_obj[lookup[k]] = v


    # alright this is a hack. the "lost_packets" key won't be
    # present if it's == 0, but "packets" will be. To make things
    # easier later, add the missing field if needed
    if new_obj.has_key("sent") and not new_obj.has_key("lost"):
        new_obj["lost"] = 0

    return new_obj

 
if __name__ == "__main__":

    # Test "regular" output
    test_output = """
{
    "start": {
        "connected": [{
            "socket": 4,
            "local_host": "10.0.2.15",
            "local_port": 33600,
            "remote_host": "10.0.2.4",
            "remote_port": 5201
        }],
        "version": "iperf 3.1.3",
        "system_info": "Linux ps-test1 2.6.32-642.3.1.el6.x86_64 #1 SMP Tue Jul 12 18:30:56 UTC 2016 x86_64",
        "timestamp": {
            "time": "Tue, 16 Aug 2016 03:39:47 GMT",
            "timesecs": 1471318787
        },
        "connecting_to": {
            "host": "10.0.2.4",
            "port": 5201
        },
        "cookie": "ps-test1.1471318787.639126.54345cb13",
        "tcp_mss_default": 1448,
        "test_start": {
            "protocol": "TCP",
            "num_streams": 1,
            "blksize": 131072,
            "omit": 0,
            "duration": 10,
            "bytes": 0,
            "blocks": 0,
            "reverse": 0
        }
    },
    "intervals": [{
        "streams": [{
            "socket": 4,
            "start": 0,
            "end": 1.000375,
            "seconds": 1.000375,
            "bytes": 1982312,
            "bits_per_second": 15852550.779440,
            "retransmits": 4,
            "snd_cwnd": 53576,
            "rtt": 7375,
            "omitted": false
        }],
        "sum": {
            "start": 0,
            "end": 1.000375,
            "seconds": 1.000375,
            "bytes": 1982312,
            "bits_per_second": 15852550.779440,
            "retransmits": 4,
            "omitted": false
        }
    }, {
        "streams": [{
            "socket": 4,
            "start": 1.000375,
            "end": 2.004007,
            "seconds": 1.003632,
            "bytes": 301184,
            "bits_per_second": 2400752.302863,
            "retransmits": 2,
            "snd_cwnd": 53576,
            "rtt": 67000,
            "omitted": false
        }],
        "sum": {
            "start": 1.000375,
            "end": 2.004007,
            "seconds": 1.003632,
            "bytes": 301184,
            "bits_per_second": 2400752.302863,
            "retransmits": 2,
            "omitted": false
        }
    }, {
        "streams": [{
            "socket": 4,
            "start": 2.004007,
            "end": 3.002219,
            "seconds": 0.998212,
            "bytes": 860864,
            "bits_per_second": 6899248.818251,
            "retransmits": 1,
            "snd_cwnd": 72400,
            "rtt": 3375,
            "omitted": false
        }],
        "sum": {
            "start": 2.004007,
            "end": 3.002219,
            "seconds": 0.998212,
            "bytes": 860864,
            "bits_per_second": 6899248.818251,
            "retransmits": 1,
            "omitted": false
        }
    }, {
        "streams": [{
            "socket": 4,
            "start": 3.002219,
            "end": 4.003231,
            "seconds": 1.001012,
            "bytes": 2033744,
            "bits_per_second": 16253502.044018,
            "retransmits": 3,
            "snd_cwnd": 99912,
            "rtt": 10500,
            "omitted": false
        }],
        "sum": {
            "start": 3.002219,
            "end": 4.003231,
            "seconds": 1.001012,
            "bytes": 2033744,
            "bits_per_second": 16253502.044018,
            "retransmits": 3,
            "omitted": false
        }
    }, {
        "streams": [{
            "socket": 4,
            "start": 4.003231,
            "end": 5.000839,
            "seconds": 0.997608,
            "bytes": 2805528,
            "bits_per_second": 22498040.518909,
            "retransmits": 3,
            "snd_cwnd": 136112,
            "rtt": 3750,
            "omitted": false
        }],
        "sum": {
            "start": 4.003231,
            "end": 5.000839,
            "seconds": 0.997608,
            "bytes": 2805528,
            "bits_per_second": 22498040.518909,
            "retransmits": 3,
            "omitted": false
        }
    }, {
        "streams": [{
            "socket": 4,
            "start": 5.000839,
            "end": 6.002020,
            "seconds": 1.001181,
            "bytes": 23605296,
            "bits_per_second": 188619584.572292,
            "retransmits": 48,
            "snd_cwnd": 36200,
            "rtt": 1875,
            "omitted": false
        }],
        "sum": {
            "start": 5.000839,
            "end": 6.002020,
            "seconds": 1.001181,
            "bytes": 23605296,
            "bits_per_second": 188619584.572292,
            "retransmits": 48,
            "omitted": false
        }
    }, {
        "streams": [{
            "socket": 4,
            "start": 6.002020,
            "end": 7.000188,
            "seconds": 0.998168,
            "bytes": 52243840,
            "bits_per_second": 418717814.537474,
            "retransmits": 48,
            "snd_cwnd": 194032,
            "rtt": 1875,
            "omitted": false
        }],
        "sum": {
            "start": 6.002020,
            "end": 7.000188,
            "seconds": 0.998168,
            "bytes": 52243840,
            "bits_per_second": 418717814.537474,
            "retransmits": 48,
            "omitted": false
        }
    }, {
        "streams": [{
            "socket": 4,
            "start": 7.000188,
            "end": 8.000270,
            "seconds": 1.000082,
            "bytes": 179971920,
            "bits_per_second": 1.439657e+09,
            "retransmits": 1,
            "snd_cwnd": 231680,
            "rtt": 1875,
            "omitted": false
        }],
        "sum": {
            "start": 7.000188,
            "end": 8.000270,
            "seconds": 1.000082,
            "bytes": 179971920,
            "bits_per_second": 1.439657e+09,
            "retransmits": 1,
            "omitted": false
        }
    }, {
        "streams": [{
            "socket": 4,
            "start": 8.000270,
            "end": 9.000164,
            "seconds": 0.999894,
            "bytes": 213855120,
            "bits_per_second": 1.711022e+09,
            "retransmits": 45,
            "snd_cwnd": 204168,
            "rtt": 1875,
            "omitted": false
        }],
        "sum": {
            "start": 8.000270,
            "end": 9.000164,
            "seconds": 0.999894,
            "bytes": 213855120,
            "bits_per_second": 1.711022e+09,
            "retransmits": 45,
            "omitted": false
        }
    }, {
        "streams": [{
            "socket": 4,
            "start": 9.000164,
            "end": 10.001024,
            "seconds": 1.000860,
            "bytes": 8983392,
            "bits_per_second": 71805385.105436,
            "retransmits": 4,
            "snd_cwnd": 60816,
            "rtt": 2250,
            "omitted": false
        }],
        "sum": {
            "start": 9.000164,
            "end": 10.001024,
            "seconds": 1.000860,
            "bytes": 8983392,
            "bits_per_second": 71805385.105436,
            "retransmits": 4,
            "omitted": false
        }
    }],
    "end": {
        "streams": [{
            "sender": {
                "socket": 4,
                "start": 0,
                "end": 10.001024,
                "seconds": 10.001024,
                "bytes": 486643200,
                "bits_per_second": 389274697.967401,
                "retransmits": 159,
                "max_snd_cwnd": 231680,
                "max_rtt": 67000,
                "min_rtt": 1875,
                "mean_rtt": 10175
            },
            "receiver": {
                "socket": 4,
                "start": 0,
                "end": 10.001024,
                "seconds": 10.001024,
                "bytes": 485969880,
                "bits_per_second": 388736097.120548
            }
        }],
        "sum_sent": {
            "start": 0,
            "end": 10.001024,
            "seconds": 10.001024,
            "bytes": 486643200,
            "bits_per_second": 389274697.967401,
            "retransmits": 159
        },
        "sum_received": {
            "start": 0,
            "end": 10.001024,
            "seconds": 10.001024,
            "bytes": 485969880,
            "bits_per_second": 388736097.120548
        },
        "cpu_utilization_percent": {
            "host_total": 2.181510,
            "host_user": 0.148710,
            "host_system": 2.101865,
            "remote_total": 4.763802,
            "remote_user": 0.015363,
            "remote_system": 4.763079
        }
    }
}
"""


    result = parse_output(test_output.split("\n"))
    pprint.PrettyPrinter(indent=4).pprint(result)


    test_output = """
{
       "start":       {
       "connected":   [{
                       "socket":          4,
                       "local_host":      "10.0.2.15",
                       "local_port":      49036,
                       "remote_host":     "10.0.2.4",
                       "remote_port":     5201
                   }],
               "version":         "iperf 3.1.3",
               "system_info":     "Linux ps-test1 2.6.32-642.3.1.el6.x86_64 #1 SMP Tue Jul 12 18:30:56 UTC 2016 x86_64",
               "timestamp":       {
                   "time":    "Tue, 16 Aug 2016 04:48:35 GMT",
                   "timesecs":        1471322915
               },
               "connecting_to":           {
                   "host":    "10.0.2.4",
                   "port":    5201
               },
               "cookie":          "ps-test1.1471322915.508871.24c661250",
               "test_start":      {
                   "protocol":        "UDP",
                   "num_streams":     1,
                   "blksize":         8192,
                   "omit":    0,
                   "duration":        10,
                   "bytes":           0,
                   "blocks":          0,
                   "reverse":         0
               }
           },
           "intervals":       [{
                   "streams":         [{
                           "socket":          4,
                           "start":           0,
                           "end":     1.001342,
                           "seconds":         1.001342,
                           "bytes":           131072,
                           "bits_per_second":         1047170.885411,
                           "packets":         16,
                           "omitted":         false
                       }],
                   "sum":     {
                       "start":           0,
                       "end":     1.001342,
                       "seconds":         1.001342,
                       "bytes":           131072,
                       "bits_per_second":         1047170.885411,
                       "packets":         16,
                       "omitted":         false
                   }
               }, {
                   "streams":         [{
                           "socket":          4,
                           "start":           1.001342,
                           "end":     2.001610,
                           "seconds":         1.000268,
                           "bytes":           131072,
                           "bits_per_second":         1048295.075283,
                           "packets":         16,
                           "omitted":         false
                       }],
                   "sum":     {
                       "start":           1.001342,
                       "end":     2.001610,
                       "seconds":         1.000268,
                       "bytes":           131072,
                       "bits_per_second":         1048295.075283,
                       "packets":         16,
                       "omitted":         false
                   }
               }, {
                   "streams":         [{
                           "socket":          4,
                           "start":           2.001610,
                           "end":     3.001298,
                           "seconds":         0.999688,
                           "bytes":           131072,
                           "bits_per_second":         1048903.102007,
                           "packets":         16,
                           "omitted":         false
                       }],
                   "sum":     {
                       "start":           2.001610,
                       "end":     3.001298,
                       "seconds":         0.999688,
                       "bytes":           131072,
                       "bits_per_second":         1048903.102007,
                       "packets":         16,
                       "omitted":         false
                   }
               }, {
                   "streams":         [{
                           "socket":          4,
                           "start":           3.001298,
                           "end":     4.001750,
                           "seconds":         1.000452,
                           "bytes":           131072,
                           "bits_per_second":         1048102.214171,
                           "packets":         16,
                           "omitted":         false
                       }],
                   "sum":     {
                       "start":           3.001298,
                       "end":     4.001750,
                       "seconds":         1.000452,
                       "bytes":           131072,
                       "bits_per_second":         1048102.214171,
                       "packets":         16,
                       "omitted":         false
                   }
               }, {
                   "streams":         [{
                           "socket":          4,
                           "start":           4.001750,
                           "end":     5.001297,
                           "seconds":         0.999547,
                           "bytes":           131072,
                           "bits_per_second":         1049051.215270,
                           "packets":         16,
                           "omitted":         false
                       }],
                   "sum":     {
                       "start":           4.001750,
                       "end":     5.001297,
                       "seconds":         0.999547,
                       "bytes":           131072,
                       "bits_per_second":         1049051.215270,
                       "packets":         16,
                       "omitted":         false
                   }
               }, {
                   "streams":         [{
                           "socket":          4,
                           "start":           5.001297,
                           "end":     6.000906,
                           "seconds":         0.999609,
                           "bytes":           131072,
                           "bits_per_second":         1048986.160375,
                           "packets":         16,
                           "omitted":         false
                       }],
                   "sum":     {
                       "start":           5.001297,
                       "end":     6.000906,
                       "seconds":         0.999609,
                       "bytes":           131072,
                       "bits_per_second":         1048986.160375,
                       "packets":         16,
                       "omitted":         false
                   }
               }, {
                   "streams":         [{
                           "socket":          4,
                           "start":           6.000906,
                           "end":     7.001737,
                           "seconds":         1.000831,
                           "bytes":           131072,
                           "bits_per_second":         1047705.473311,
                           "packets":         16,
                           "omitted":         false
                       }],
                   "sum":     {
                       "start":           6.000906,
                       "end":     7.001737,
                       "seconds":         1.000831,
                       "bytes":           131072,
                       "bits_per_second":         1047705.473311,
                       "packets":         16,
                       "omitted":         false
                   }
               }, {
                   "streams":         [{
                           "socket":          4,
                           "start":           7.001737,
                           "end":     8.001043,
                           "seconds":         0.999306,
                           "bytes":           131072,
                           "bits_per_second":         1049304.255436,
                           "packets":         16,
                           "omitted":         false
                       }],
                   "sum":     {
                       "start":           7.001737,
                       "end":     8.001043,
                       "seconds":         0.999306,
                       "bytes":           131072,
                       "bits_per_second":         1049304.255436,
                       "packets":         16,
                       "omitted":         false
                   }
               }, {
                   "streams":         [{
                           "socket":          4,
                           "start":           8.001043,
                           "end":     9.001251,
                           "seconds":         1.000208,
                           "bytes":           131072,
                           "bits_per_second":         1048357.795417,
                           "packets":         16,
                           "omitted":         false
                       }],
                   "sum":     {
                       "start":           8.001043,
                       "end":     9.001251,
                       "seconds":         1.000208,
                       "bytes":           131072,
                       "bits_per_second":         1048357.795417,
                       "packets":         16,
                       "omitted":         false
                   }
               }, {
                   "streams":         [{
                           "socket":          4,
                           "start":           9.001251,
                           "end":     10.000900,
                           "seconds":         0.999649,
                           "bytes":           131072,
                           "bits_per_second":         1048944.129196,
                           "packets":         16,
                           "omitted":         false
                       }],
                   "sum":     {
                       "start":           9.001251,
                       "end":     10.000900,
                       "seconds":         0.999649,
                       "bytes":           131072,
                       "bits_per_second":         1048944.129196,
                       "packets":         16,
                       "omitted":         false
                   }
               }],
           "end":     {
               "streams":         [{
                       "udp":     {
                           "socket":          4,
                           "start":           0,
                           "end":     10.000900,
                           "seconds":         10.000900,
                           "bytes":           1310720,
                           "bits_per_second":         1048481.633493,
                           "jitter_ms":       2735.461000,
                           "lost_packets":    0,
                           "packets":         159,
                           "lost_percent":    0,
                           "out_of_order":    0
                       }
                   }],
               "sum":     {
                   "start":           0,
                   "end":     10.000900,
                   "seconds":         10.000900,
                   "bytes":           1310720,
                   "bits_per_second":         1048481.633493,
                   "jitter_ms":       2735.461000,
                   "lost_packets":    0,
                   "packets":         159,
                   "lost_percent":    0
               },
               "cpu_utilization_percent":         {
                   "host_total":      0.892589,
                   "host_user":       0.019825,
                   "host_system":     0.971782,
                   "remote_total":    0.135247,
                   "remote_user":     0,
                   "remote_system":           0.135226
               }
           }
}
"""

    result = parse_output(test_output.split("\n"))
    pprint.PrettyPrinter(indent=4).pprint(result)

