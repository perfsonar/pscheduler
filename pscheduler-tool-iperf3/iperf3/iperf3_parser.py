import re
import pscheduler
import pprint
import json

logger = pscheduler.Log(quiet=True)
        

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
    
    intervals = []
    if 'intervals' in content:
        intervals = content['intervals']
    else:
        results['succeeded'] = False
        results['error'] = "iperf3 output is missing required field 'intervals'" 
        return results
    
    final_streams = []

    # Go through the JSON and convert to what we're expecting in throughput tests
    # This is mostly a renaming since it's so similar
    for interval in intervals:
        #these don't appear to be required by json schema, so ignoring if missing
        streams = interval.get('streams', [])
        summary = interval.get('sum', {})

        renamed_streams = []

        for stream in streams:
            new_stream = rename_json(stream)
            renamed_streams.append(new_stream)

        renamed_summary = rename_json(summary)

        final_streams.append({
                "streams": renamed_streams,
                "summary": renamed_summary
                })


    sum_end = {}
    if 'end' in content:
       sum_end =  content['end']
    else:
        results['succeeded'] = False
        results['error'] = "iperf3 output is missing required field 'end'" 
        return results
    
    # the "summary" keys are different for UDP/TCP here
    if "sum_sent" in sum_end:
        summary = sum_end["sum_sent"]
    elif "sum" in sum_end:
        summary = sum_end['sum']
    else:
        results['succeeded'] = False
        results['error'] = "iperf3 output has neither 'sum_sent' nor 'sum' field, and one of them is required" 
        return results

    renamed_summary = rename_json(summary)

    # kind of like above, the streams summary is in a different key
    # json schema does not require, so ignore if not provided
    sum_streams = sum_end.get('streams', [])

    renamed_sum_streams = []
    for sum_stream in sum_streams:
        if "udp" in sum_stream:
            renamed_sum_streams.append(rename_json(sum_stream['udp']))
        elif "sender" in sum_stream:
            renamed_sum_streams.append(rename_json(sum_stream['sender']))

    results["intervals"] = final_streams
    results["summary"]   = {"streams": renamed_sum_streams, "summary": renamed_summary}

    return results


def rename_json(obj):
    new_obj = {}

    lookup = {
        "socket": "stream-id",
        "start": "start",
        "end": "end",
        "bytes": "throughput-bytes",
        "bits_per_second": "throughput-bits",
        "omitted": "omitted",
        "jitter_ms": "jitter",

        # only for UDP
        "packets": "sent",
        "lost_packets": "lost",

        # only for TCP
        "retransmits": "retransmits",
        "snd_cwnd": "tcp-window-size",
        "rtt": "rtt",
        "mean_rtt": "rtt"
        }

    for k,v in obj.items():
        if k in lookup:
            new_obj[lookup[k]] = v


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


    test_output = """
{
        "start":        {
                "connected":    [{
                                "socket":       4,
                                "local_host":   "150.254.208.65",
                                "local_port":   35026,
                                "remote_host":  "140.182.44.177",
                                "remote_port":  5201
                        }],
                "version":      "iperf 3.1.6",
                "system_info":  "Linux ps-4-0 4.4.0-59-generic #80~14.04.1-Ubuntu SMP Fri Jan 6 18:02:02 UTC 2017 x86_64",
                "timestamp":    {
                        "time": "Mon, 13 Feb 2017 19:14:16 GMT",
                        "timesecs":     1487013256
                },
                "connecting_to":        {
                        "host": "140.182.44.177",
                        "port": 5201
                },
                "cookie":       "ps-4-0.1487013255.986166.651993251aa",
                "tcp_mss_default":      1448,
                "test_start":   {
                        "protocol":     "TCP",
                        "num_streams":  1,
                        "blksize":      131072,
                        "omit": 0,
                        "duration":     20,
                        "bytes":        0,
                        "blocks":       0,
                        "reverse":      0
                }
        },
        "intervals":    [{
                        "streams":      [{
                                        "socket":       4,
                                        "start":        0,
                                        "end":  1.000095,
                                        "seconds":      1.000095,
                                        "bytes":        2255984,
                                        "bits_per_second":      18046155.287058,
                                        "retransmits":  0,
                                        "snd_cwnd":     350416,
                                        "rtt":  134320,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        0,
                                "end":  1.000095,
                                "seconds":      1.000095,
                                "bytes":        2255984,
                                "bits_per_second":      18046155.287058,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        1.000095,
                                        "end":  2.000278,
                                        "seconds":      1.000183,
                                        "bytes":        3598840,
                                        "bits_per_second":      28785456.088557,
                                        "retransmits":  137,
                                        "snd_cwnd":     209960,
                                        "rtt":  134534,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        1.000095,
                                "end":  2.000278,
                                "seconds":      1.000183,
                                "bytes":        3598840,
                                "bits_per_second":      28785456.088557,
                                "retransmits":  137,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        2.000278,
                                        "end":  3.000251,
                                        "seconds":      0.999973,
                                        "bytes":        1310720,
                                        "bits_per_second":      10486042.507611,
                                        "retransmits":  0,
                                        "snd_cwnd":     221544,
                                        "rtt":  134808,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        2.000278,
                                "end":  3.000251,
                                "seconds":      0.999973,
                                "bytes":        1310720,
                                "bits_per_second":      10486042.507611,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        3.000251,
                                        "end":  4.003264,
                                        "seconds":      1.003013,
                                        "bytes":        2621440,
                                        "bits_per_second":      20908519.827961,
                                        "retransmits":  0,
                                        "snd_cwnd":     318560,
                                        "rtt":  140105,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        3.000251,
                                "end":  4.003264,
                                "seconds":      1.003013,
                                "bytes":        2621440,
                                "bits_per_second":      20908519.827961,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        4.003264,
                                        "end":  5.000230,
                                        "seconds":      0.996966,
                                        "bytes":        2621440,
                                        "bits_per_second":      21035343.648278,
                                        "retransmits":  0,
                                        "snd_cwnd":     543000,
                                        "rtt":  134169,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        4.003264,
                                "end":  5.000230,
                                "seconds":      0.996966,
                                "bytes":        2621440,
                                "bits_per_second":      21035343.648278,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        5.000230,
                                        "end":  6.000112,
                                        "seconds":      0.999882,
                                        "bytes":        5242880,
                                        "bits_per_second":      41947990.584254,
                                        "retransmits":  0,
                                        "snd_cwnd":     834048,
                                        "rtt":  137125,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        5.000230,
                                "end":  6.000112,
                                "seconds":      0.999882,
                                "bytes":        5242880,
                                "bits_per_second":      41947990.584254,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        6.000112,
                                        "end":  7.000081,
                                        "seconds":      0.999969,
                                        "bytes":        9175040,
                                        "bits_per_second":      73402595.070514,
                                        "retransmits":  0,
                                        "snd_cwnd":     1274240,
                                        "rtt":  134496,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        6.000112,
                                "end":  7.000081,
                                "seconds":      0.999969,
                                "bytes":        9175040,
                                "bits_per_second":      73402595.070514,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        7.000081,
                                        "end":  8.000090,
                                        "seconds":      1.000009,
                                        "bytes":        13107200,
                                        "bits_per_second":      104856650.008607,
                                        "retransmits":  0,
                                        "snd_cwnd":     1918600,
                                        "rtt":  134377,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        7.000081,
                                "end":  8.000090,
                                "seconds":      1.000009,
                                "bytes":        13107200,
                                "bits_per_second":      104856650.008607,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        8.000090,
                                        "end":  9.000100,
                                        "seconds":      1.000010,
                                        "bytes":        19660800,
                                        "bits_per_second":      157284825.015771,
                                        "retransmits":  0,
                                        "snd_cwnd":     2735272,
                                        "rtt":  134310,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        8.000090,
                                "end":  9.000100,
                                "seconds":      1.000010,
                                "bytes":        19660800,
                                "bits_per_second":      157284825.015771,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        9.000100,
                                        "end":  10.000086,
                                        "seconds":      0.999986,
                                        "bytes":        27525120,
                                        "bits_per_second":      220204057.543572,
                                        "retransmits":  105,
                                        "snd_cwnd":     3095824,
                                        "rtt":  137908,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        9.000100,
                                "end":  10.000086,
                                "seconds":      0.999986,
                                "bytes":        27525120,
                                "bits_per_second":      220204057.543572,
                                "retransmits":  105,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        10.000086,
                                        "end":  11.000096,
                                        "seconds":      1.000010,
                                        "bytes":        14417920,
                                        "bits_per_second":      115342205.011566,
                                        "retransmits":  285,
                                        "snd_cwnd":     1849096,
                                        "rtt":  134890,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        10.000086,
                                "end":  11.000096,
                                "seconds":      1.000010,
                                "bytes":        14417920,
                                "bits_per_second":      115342205.011566,
                                "retransmits":  285,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        11.000096,
                                        "end":  12.000080,
                                        "seconds":      0.999984,
                                        "bytes":        14417920,
                                        "bits_per_second":      115345202.529433,
                                        "retransmits":  0,
                                        "snd_cwnd":     1901224,
                                        "rtt":  134602,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        11.000096,
                                "end":  12.000080,
                                "seconds":      0.999984,
                                "bytes":        14417920,
                                "bits_per_second":      115345202.529433,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        12.000080,
                                        "end":  13.000086,
                                        "seconds":      1.000006,
                                        "bytes":        14417920,
                                        "bits_per_second":      115342672.504098,
                                        "retransmits":  0,
                                        "snd_cwnd":     2106840,
                                        "rtt":  137683,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        12.000080,
                                "end":  13.000086,
                                "seconds":      1.000006,
                                "bytes":        14417920,
                                "bits_per_second":      115342672.504098,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        13.000086,
                                        "end":  14.000088,
                                        "seconds":      1.000002,
                                        "bytes":        15728640,
                                        "bits_per_second":      125828880.000458,
                                        "retransmits":  0,
                                        "snd_cwnd":     2457256,
                                        "rtt":  134995,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        13.000086,
                                "end":  14.000088,
                                "seconds":      1.000002,
                                "bytes":        15728640,
                                "bits_per_second":      125828880.000458,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        14.000088,
                                        "end":  15.000085,
                                        "seconds":      0.999997,
                                        "bytes":        19660800,
                                        "bits_per_second":      157286850.001287,
                                        "retransmits":  0,
                                        "snd_cwnd":     2930752,
                                        "rtt":  134586,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        14.000088,
                                "end":  15.000085,
                                "seconds":      0.999997,
                                "bytes":        19660800,
                                "bits_per_second":      157286850.001287,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        15.000085,
                                        "end":  16.000087,
                                        "seconds":      1.000002,
                                        "bytes":        19660800,
                                        "bits_per_second":      157286100.000572,
                                        "retransmits":  102,
                                        "snd_cwnd":     1637688,
                                        "rtt":  134678,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        15.000085,
                                "end":  16.000087,
                                "seconds":      1.000002,
                                "bytes":        19660800,
                                "bits_per_second":      157286100.000572,
                                "retransmits":  102,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        16.000087,
                                        "end":  17.000085,
                                        "seconds":      0.999998,
                                        "bytes":        11796480,
                                        "bits_per_second":      94372020.000343,
                                        "retransmits":  0,
                                        "snd_cwnd":     1647824,
                                        "rtt":  134401,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        16.000087,
                                "end":  17.000085,
                                "seconds":      0.999998,
                                "bytes":        11796480,
                                "bits_per_second":      94372020.000343,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        17.000085,
                                        "end":  18.000109,
                                        "seconds":      1.000024,
                                        "bytes":        11796480,
                                        "bits_per_second":      94369567.554721,
                                        "retransmits":  0,
                                        "snd_cwnd":     1765112,
                                        "rtt":  134668,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        17.000085,
                                "end":  18.000109,
                                "seconds":      1.000024,
                                "bytes":        11796480,
                                "bits_per_second":      94369567.554721,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        18.000109,
                                        "end":  19.000080,
                                        "seconds":      0.999971,
                                        "bytes":        14417920,
                                        "bits_per_second":      115346715.097590,
                                        "retransmits":  0,
                                        "snd_cwnd":     2031544,
                                        "rtt":  135142,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        18.000109,
                                "end":  19.000080,
                                "seconds":      0.999971,
                                "bytes":        14417920,
                                "bits_per_second":      115346715.097590,
                                "retransmits":  0,
                                "omitted":      false
                        }
                }, {
                        "streams":      [{
                                        "socket":       4,
                                        "start":        19.000080,
                                        "end":  20.000215,
                                        "seconds":      1.000135,
                                        "bytes":        11796480,
                                        "bits_per_second":      94359106.718292,
                                        "retransmits":  57,
                                        "snd_cwnd":     1122200,
                                        "rtt":  135457,
                                        "omitted":      false
                                }],
                        "sum":  {
                                "start":        19.000080,
                                "end":  20.000215,
                                "seconds":      1.000135,
                                "bytes":        11796480,
                                "bits_per_second":      94359106.718292,
                                "retransmits":  57,
                                "omitted":      false
                        }
                }],
        "end":  {
                "streams":      [{
                                "sender":       {
                                        "socket":       4,
                                        "start":        0,
                                        "end":  20.000215,
                                        "seconds":      20.000215,
                                        "bytes":        235230824,
                                        "bits_per_second":      94091317.866364,
                                        "retransmits":  686,
                                        "max_snd_cwnd": 3095824,
                                        "max_rtt":      140105,
                                        "min_rtt":      134169,
                                        "mean_rtt":     135362
                                },
                                "receiver":     {
                                        "socket":       4,
                                        "start":        0,
                                        "end":  20.000215,
                                        "seconds":      20.000215,
                                        "bytes":        221415128,
                                        "bits_per_second":      88565098.888017
                                }
                        }],
                "sum_sent":     {
                        "start":        0,
                        "end":  20.000215,
                        "seconds":      20.000215,
                        "bytes":        235230824,
                        "bits_per_second":      94091317.866364,
                        "retransmits":  686
                },
                "sum_received": {
                        "start":        0,
                        "end":  20.000215,
                        "seconds":      20.000215,
                        "bytes":        221415128,
                        "bits_per_second":      88565098.888017
                },
                "cpu_utilization_percent":      {
                        "host_total":   0.957782,
                        "host_user":    0.038625,
                        "host_system":  0.907690,
                        "remote_total": 5.297520,
                        "remote_user":  0,
                        "remote_system":        5.307290
                },
                "sender_tcp_congestion":        "htcp"
        }
}
"""

    result = parse_output(test_output.split("\n"))
    pprint.PrettyPrinter(indent=4).pprint(result)

    test_output = """
{
    "start" :    {
                "connected":	[{
				"socket":	4,
				"local_host":	"150.254.208.65",
				"local_port":	40574,
				"remote_host":	"140.182.44.177",
				"remote_port":	5201
			}],
		"version":	"iperf 3.1.6",
		"system_info":	"Linux ps-4-0 4.4.0-59-generic #80~14.04.1-Ubuntu SMP Fri Jan 6 18:02:02 UTC 2017 x86_64",
		"timestamp":	{
			"time":	"Mon, 13 Feb 2017 19:29:01 GMT",
			"timesecs":	1487014141
		},
		"connecting_to":	{
			"host":	"140.182.44.177",
			"port":	5201
		},
		"cookie":	"ps-4-0.1487014141.570141.2f10aa7723f",
		"tcp_mss_default":	1448,
		"test_start":	{
			"protocol":	"TCP",
			"num_streams":	1,
			"blksize":	131072,
			"omit":	0,
			"duration":	20,
			"bytes":	0,
			"blocks":	0,
			"reverse":	0
		}
	},
	"intervals":	[{
			"streams":	[{
					"socket":	4,
					"start":	0,
					"end":	1.000098,
					"seconds":	1.000098,
					"bytes":	2114080,
					"bits_per_second":	16910982.892177,
					"retransmits":	0,
					"snd_cwnd":	304080,
					"rtt":	134421,
					"omitted":	false
				}],
			"sum":	{
				"start":	0,
				"end":	1.000098,
				"seconds":	1.000098,
				"bytes":	2114080,
				"bits_per_second":	16910982.892177,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	1.000098,
					"end":	2.000288,
					"seconds":	1.000190,
					"bytes":	2150280,
					"bits_per_second":	17198971.858117,
					"retransmits":	35,
					"snd_cwnd":	130320,
					"rtt":	133798,
					"omitted":	false
				}],
			"sum":	{
				"start":	1.000098,
				"end":	2.000288,
				"seconds":	1.000190,
				"bytes":	2150280,
				"bits_per_second":	17198971.858117,
				"retransmits":	35,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	2.000288,
					"end":	3.000341,
					"seconds":	1.000053,
					"bytes":	1042560,
					"bits_per_second":	8340038.570728,
					"retransmits":	0,
					"snd_cwnd":	144800,
					"rtt":	133840,
					"omitted":	false
				}],
			"sum":	{
				"start":	2.000288,
				"end":	3.000341,
				"seconds":	1.000053,
				"bytes":	1042560,
				"bits_per_second":	8340038.570728,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	3.000341,
					"end":	4.000411,
					"seconds":	1.000070,
					"bytes":	1042560,
					"bits_per_second":	8339897.402759,
					"retransmits":	0,
					"snd_cwnd":	215752,
					"rtt":	138897,
					"omitted":	false
				}],
			"sum":	{
				"start":	3.000341,
				"end":	4.000411,
				"seconds":	1.000070,
				"bytes":	1042560,
				"bits_per_second":	8339897.402759,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	4.000411,
					"end":	5.000199,
					"seconds":	0.999788,
					"bytes":	2085120,
					"bits_per_second":	16684496.347688,
					"retransmits":	0,
					"snd_cwnd":	354760,
					"rtt":	133983,
					"omitted":	false
				}],
			"sum":	{
				"start":	4.000411,
				"end":	5.000199,
				"seconds":	0.999788,
				"bytes":	2085120,
				"bits_per_second":	16684496.347688,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	5.000199,
					"end":	6.000137,
					"seconds":	0.999938,
					"bytes":	3258000,
					"bits_per_second":	26065615.777040,
					"retransmits":	0,
					"snd_cwnd":	563272,
					"rtt":	133985,
					"omitted":	false
				}],
			"sum":	{
				"start":	5.000199,
				"end":	6.000137,
				"seconds":	0.999938,
				"bytes":	3258000,
				"bits_per_second":	26065615.777040,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	6.000137,
					"end":	7.000188,
					"seconds":	1.000051,
					"bytes":	5170200,
					"bits_per_second":	41359489.773652,
					"retransmits":	32,
					"snd_cwnd":	380824,
					"rtt":	134023,
					"omitted":	false
				}],
			"sum":	{
				"start":	6.000137,
				"end":	7.000188,
				"seconds":	1.000051,
				"bytes":	5170200,
				"bits_per_second":	41359489.773652,
				"retransmits":	32,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	7.000188,
					"end":	8.000114,
					"seconds":	0.999926,
					"bytes":	2621440,
					"bits_per_second":	20973070.114569,
					"retransmits":	0,
					"snd_cwnd":	390960,
					"rtt":	134016,
					"omitted":	false
				}],
			"sum":	{
				"start":	7.000188,
				"end":	8.000114,
				"seconds":	0.999926,
				"bytes":	2621440,
				"bits_per_second":	20973070.114569,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	8.000114,
					"end":	9.000442,
					"seconds":	1.000328,
					"bytes":	2621440,
					"bits_per_second":	20964647.253062,
					"retransmits":	0,
					"snd_cwnd":	480736,
					"rtt":	133858,
					"omitted":	false
				}],
			"sum":	{
				"start":	8.000114,
				"end":	9.000442,
				"seconds":	1.000328,
				"bytes":	2621440,
				"bits_per_second":	20964647.253062,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	9.000442,
					"end":	10.000102,
					"seconds":	0.999660,
					"bytes":	5242880,
					"bits_per_second":	41957304.849833,
					"retransmits":	0,
					"snd_cwnd":	695040,
					"rtt":	134062,
					"omitted":	false
				}],
			"sum":	{
				"start":	9.000442,
				"end":	10.000102,
				"seconds":	0.999660,
				"bytes":	5242880,
				"bits_per_second":	41957304.849833,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	10.000102,
					"end":	11.000162,
					"seconds":	1.000060,
					"bytes":	6553600,
					"bits_per_second":	52425650.189245,
					"retransmits":	0,
					"snd_cwnd":	986088,
					"rtt":	134923,
					"omitted":	false
				}],
			"sum":	{
				"start":	10.000102,
				"end":	11.000162,
				"seconds":	1.000060,
				"bytes":	6553600,
				"bits_per_second":	52425650.189245,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	11.000162,
					"end":	12.000334,
					"seconds":	1.000172,
					"bytes":	5242880,
					"bits_per_second":	41935821.242624,
					"retransmits":	199,
					"snd_cwnd":	279464,
					"rtt":	134194,
					"omitted":	false
				}],
			"sum":	{
				"start":	11.000162,
				"end":	12.000334,
				"seconds":	1.000172,
				"bytes":	5242880,
				"bits_per_second":	41935821.242624,
				"retransmits":	199,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	12.000334,
					"end":	13.000138,
					"seconds":	0.999804,
					"bytes":	2621440,
					"bits_per_second":	20975635.807598,
					"retransmits":	0,
					"snd_cwnd":	293944,
					"rtt":	133866,
					"omitted":	false
				}],
			"sum":	{
				"start":	12.000334,
				"end":	13.000138,
				"seconds":	0.999804,
				"bytes":	2621440,
				"bits_per_second":	20975635.807598,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	13.000138,
					"end":	14.000082,
					"seconds":	0.999944,
					"bytes":	2621440,
					"bits_per_second":	20972690.065278,
					"retransmits":	0,
					"snd_cwnd":	402544,
					"rtt":	134400,
					"omitted":	false
				}],
			"sum":	{
				"start":	13.000138,
				"end":	14.000082,
				"seconds":	0.999944,
				"bytes":	2621440,
				"bits_per_second":	20972690.065278,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	14.000082,
					"end":	15.000251,
					"seconds":	1.000169,
					"bytes":	2621440,
					"bits_per_second":	20967980.597452,
					"retransmits":	0,
					"snd_cwnd":	577752,
					"rtt":	137868,
					"omitted":	false
				}],
			"sum":	{
				"start":	14.000082,
				"end":	15.000251,
				"seconds":	1.000169,
				"bytes":	2621440,
				"bits_per_second":	20967980.597452,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	15.000251,
					"end":	16.000279,
					"seconds":	1.000028,
					"bytes":	2621440,
					"bits_per_second":	20970930.016598,
					"retransmits":	15,
					"snd_cwnd":	308424,
					"rtt":	134372,
					"omitted":	false
				}],
			"sum":	{
				"start":	15.000251,
				"end":	16.000279,
				"seconds":	1.000028,
				"bytes":	2621440,
				"bits_per_second":	20970930.016598,
				"retransmits":	15,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	16.000279,
					"end":	17.000356,
					"seconds":	1.000077,
					"bytes":	2621440,
					"bits_per_second":	20969905.124360,
					"retransmits":	0,
					"snd_cwnd":	360552,
					"rtt":	138924,
					"omitted":	false
				}],
			"sum":	{
				"start":	16.000279,
				"end":	17.000356,
				"seconds":	1.000077,
				"bytes":	2621440,
				"bits_per_second":	20969905.124360,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	17.000356,
					"end":	18.000418,
					"seconds":	1.000062,
					"bytes":	2621440,
					"bits_per_second":	20970220.080580,
					"retransmits":	0,
					"snd_cwnd":	524176,
					"rtt":	138088,
					"omitted":	false
				}],
			"sum":	{
				"start":	17.000356,
				"end":	18.000418,
				"seconds":	1.000062,
				"bytes":	2621440,
				"bits_per_second":	20970220.080580,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	18.000418,
					"end":	19.000208,
					"seconds":	0.999790,
					"bytes":	5242880,
					"bits_per_second":	41951851.850901,
					"retransmits":	0,
					"snd_cwnd":	836944,
					"rtt":	133874,
					"omitted":	false
				}],
			"sum":	{
				"start":	18.000418,
				"end":	19.000208,
				"seconds":	0.999790,
				"bytes":	5242880,
				"bits_per_second":	41951851.850901,
				"retransmits":	0,
				"omitted":	false
			}
		}, {
			"streams":	[{
					"socket":	4,
					"start":	19.000208,
					"end":	20.000146,
					"seconds":	0.999938,
					"bytes":	7864320,
					"bits_per_second":	62918460.241771,
					"retransmits":	0,
					"snd_cwnd":	1206184,
					"rtt":	135744,
					"omitted":	false
				}],
			"sum":	{
				"start":	19.000208,
				"end":	20.000146,
				"seconds":	0.999938,
				"bytes":	7864320,
				"bits_per_second":	62918460.241771,
				"retransmits":	0,
				"omitted":	false
			}
		}],
	"end":	{
		"streams":	[{
				"sender":	{
					"socket":	4,
					"start":	0,
					"end":	20.000146,
					"seconds":	20.000146,
					"bytes":	67980880,
					"bits_per_second":	27192153.616692,
					"retransmits":	281,
					"max_snd_cwnd":	1206184,
					"max_rtt":	138924,
					"min_rtt":	133798,
					"mean_rtt":	135056
				},
				"receiver":	{
					"socket":	4,
					"start":	0,
					"end":	20.000146,
					"seconds":	20.000146,
					"bytes":	63723584,
					"bits_per_second":	25489247.640428
				}
			}],
		"sum_sent":	{
			"start":	0,
			"end":	20.000146,
			"seconds":	20.000146,
			"bytes":	67980880,
			"bits_per_second":	27192153.616692,
			"retransmits":	281
		},
		"sum_received":	{
			"start":	0,
			"end":	20.000146,
			"seconds":	20.000146,
			"bytes":	63723584,
			"bits_per_second":	25489247.640428
		},
		"cpu_utilization_percent":	{
			"host_total":	0.863500,
			"host_user":	0.115875,
			"host_system":	0.753187,
			"remote_total":	1.768670,
			"remote_user":	0.083237,
			"remote_system":	1.713290
		},
		"sender_tcp_congestion":	"htcp"
	}
}
"""

    result = parse_output(test_output.split("\n"))
    pprint.PrettyPrinter(indent=4).pprint(result)


