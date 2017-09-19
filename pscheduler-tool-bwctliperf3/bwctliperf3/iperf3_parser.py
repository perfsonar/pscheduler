import re
import pscheduler
import pprint
import json

logger = pscheduler.Log(prefix='tool-bwctliperf3', quiet=True)

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
    if content.has_key('intervals'):
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

        # iperf3 doesn't report the "socket" field for the summary, but we need
        # it to fit the validation for throughput
        summary['socket'] = "SUM"
        
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
    if content.has_key('end'):
       sum_end =  content['end']
    else:
        results['succeeded'] = False
        results['error'] = "iperf3 output is missing required field 'end'" 
        return results
    
    # the "summary" keys are different for UDP/TCP here
    if sum_end.has_key("sum_sent"):
        summary = sum_end["sum_sent"]
    elif sum_end.has_key("sum"):
        summary = sum_end['sum']
    else:
        results['succeeded'] = False
        results['error'] = "iperf3 output has neither 'sum_sent' nor 'sum' field, and one of them is required" 
        return results

    # same as above manual socket setting
    summary["socket"] = "SUM"

    renamed_summary = rename_json(summary)

    # kind of like above, the streams summary is in a different key
    # json schema does not require, so ignore if not provided
    sum_streams = sum_end.get('streams', [])

    renamed_sum_streams = []
    for sum_stream in sum_streams:
        if sum_stream.has_key("udp"):
            renamed_sum_streams.append(rename_json(sum_stream['udp']))
        elif sum_stream.has_key("sender"):
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

    for k,v in obj.iteritems():
        if lookup.has_key(k):
            new_obj[lookup[k]] = v


    return new_obj

 
if __name__ == "__main__":

    # Test "regular" output
    test_output = """
{
    "start": {
"connected": [{
    "socket": 15,
    "local_host": "10.0.2.15",
    "local_port": 50657,
    "remote_host": "10.0.2.4",
    "remote_port": 5460
}],
"version": "iperf 3.1.6",
"system_info": "Linux ps-test1 2.6.32-642.3.1.el6.x86_64 #1 SMP Tue Jul 12 18:30:56 UTC 2016 x86_64",
"timestamp": {
    "time": "Tue, 19 Sep 2017 16:34:14 GMT",
    "timesecs": 1505838854
},
"connecting_to": {
    "host": "10.0.2.4",
    "port": 5460
},
"cookie": "ps-test1.1505838854.405897.2ccf82e77",
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
    "socket": 15,
    "start": 0,
    "end": 1.000032,
    "seconds": 1.000032,
    "bytes": 248951744,
    "bits_per_second": 1.991550e+09,
    "retransmits": 45,
    "snd_cwnd": 204168,
    "rtt": 1875,
    "omitted": false
}],
"sum": {
    "start": 0,
    "end": 1.000032,
    "seconds": 1.000032,
    "bytes": 248951744,
    "bits_per_second": 1.991550e+09,
    "retransmits": 45,
    "omitted": false
}
    }, {
"streams": [{
    "socket": 15,
    "start": 1.000032,
    "end": 2.000028,
    "seconds": 0.999996,
    "bytes": 298107000,
    "bits_per_second": 2.384866e+09,
    "retransmits": 0,
    "snd_cwnd": 222992,
    "rtt": 1875,
    "omitted": false
}],
"sum": {
    "start": 1.000032,
    "end": 2.000028,
    "seconds": 0.999996,
    "bytes": 298107000,
    "bits_per_second": 2.384866e+09,
    "retransmits": 0,
    "omitted": false
}
    }, {
"streams": [{
    "socket": 15,
    "start": 2.000028,
    "end": 3.000136,
    "seconds": 1.000108,
    "bytes": 296608320,
    "bits_per_second": 2.372610e+09,
    "retransmits": 0,
    "snd_cwnd": 237472,
    "rtt": 1875,
    "omitted": false
}],
"sum": {
    "start": 2.000028,
    "end": 3.000136,
    "seconds": 1.000108,
    "bytes": 296608320,
    "bits_per_second": 2.372610e+09,
    "retransmits": 0,
    "omitted": false
}
    }, {
"streams": [{
    "socket": 15,
    "start": 3.000136,
    "end": 4.000212,
    "seconds": 1.000076,
    "bytes": 284488560,
    "bits_per_second": 2.275735e+09,
    "retransmits": 45,
    "snd_cwnd": 176656,
    "rtt": 1875,
    "omitted": false
}],
"sum": {
    "start": 3.000136,
    "end": 4.000212,
    "seconds": 1.000076,
    "bytes": 284488560,
    "bits_per_second": 2.275735e+09,
    "retransmits": 45,
    "omitted": false
}
    }, {
"streams": [{
    "socket": 15,
    "start": 4.000212,
    "end": 5.000281,
    "seconds": 1.000069,
    "bytes": 206361720,
    "bits_per_second": 1.650780e+09,
    "retransmits": 0,
    "snd_cwnd": 189688,
    "rtt": 1875,
    "omitted": false
}],
"sum": {
    "start": 4.000212,
    "end": 5.000281,
    "seconds": 1.000069,
    "bytes": 206361720,
    "bits_per_second": 1.650780e+09,
    "retransmits": 0,
    "omitted": false
}
    }, {
"streams": [{
    "socket": 15,
    "start": 5.000281,
    "end": 6.000186,
    "seconds": 0.999905,
    "bytes": 260145160,
    "bits_per_second": 2.081359e+09,
    "retransmits": 0,
    "snd_cwnd": 205616,
    "rtt": 1875,
    "omitted": false
}],
"sum": {
    "start": 5.000281,
    "end": 6.000186,
    "seconds": 0.999905,
    "bytes": 260145160,
    "bits_per_second": 2.081359e+09,
    "retransmits": 0,
    "omitted": false
}
    }, {
"streams": [{
    "socket": 15,
    "start": 6.000186,
    "end": 7.000029,
    "seconds": 0.999843,
    "bytes": 293545800,
    "bits_per_second": 2.348735e+09,
    "retransmits": 0,
    "snd_cwnd": 221544,
    "rtt": 1875,
    "omitted": false
}],
"sum": {
    "start": 6.000186,
    "end": 7.000029,
    "seconds": 0.999843,
    "bytes": 293545800,
    "bits_per_second": 2.348735e+09,
    "retransmits": 0,
    "omitted": false
}
    }, {
"streams": [{
    "socket": 15,
    "start": 7.000029,
    "end": 8.000111,
    "seconds": 1.000082,
    "bytes": 299756648,
    "bits_per_second": 2.397857e+09,
    "retransmits": 0,
    "snd_cwnd": 234576,
    "rtt": 1875,
    "omitted": false
}],
"sum": {
    "start": 7.000029,
    "end": 8.000111,
    "seconds": 1.000082,
    "bytes": 299756648,
    "bits_per_second": 2.397857e+09,
    "retransmits": 0,
    "omitted": false
}
    }, {
"streams": [{
    "socket": 15,
    "start": 8.000111,
    "end": 9.000176,
    "seconds": 1.000065,
    "bytes": 207990720,
    "bits_per_second": 1.663817e+09,
    "retransmits": 45,
    "snd_cwnd": 182448,
    "rtt": 1875,
    "omitted": false
}],
"sum": {
    "start": 8.000111,
    "end": 9.000176,
    "seconds": 1.000065,
    "bytes": 207990720,
    "bits_per_second": 1.663817e+09,
    "retransmits": 45,
    "omitted": false
}
    }, {
"streams": [{
    "socket": 15,
    "start": 9.000176,
    "end": 10.000068,
    "seconds": 0.999892,
    "bytes": 214506720,
    "bits_per_second": 1.716239e+09,
    "retransmits": 0,
    "snd_cwnd": 196928,
    "rtt": 1875,
    "omitted": false
}],
"sum": {
    "start": 9.000176,
    "end": 10.000068,
    "seconds": 0.999892,
    "bytes": 214506720,
    "bits_per_second": 1.716239e+09,
    "retransmits": 0,
    "omitted": false
}
    }],
    "end": {
"streams": [{
    "sender": {
"socket": 15,
"start": 0,
"end": 10.000068,
"seconds": 10.000068,
"bytes": 2610462392,
"bits_per_second": 2.088356e+09,
"retransmits": 135,
"max_snd_cwnd": 237472,
"max_rtt": 1875,
"min_rtt": 1875,
"mean_rtt": 1875
    },
    "receiver": {
"socket": 15,
"start": 0,
"end": 10.000068,
"seconds": 10.000068,
"bytes": 2610117072,
"bits_per_second": 2.088079e+09
    }
}],
"sum_sent": {
    "start": 0,
    "end": 10.000068,
    "seconds": 10.000068,
    "bytes": 2610462392,
    "bits_per_second": 2.088356e+09,
    "retransmits": 135
},
"sum_received": {
    "start": 0,
    "end": 10.000068,
    "seconds": 10.000068,
    "bytes": 2610117072,
    "bits_per_second": 2.088079e+09
},
"cpu_utilization_percent": {
    "host_total": 5.752723,
    "host_user": 0.644603,
    "host_system": 5.166739,
    "remote_total": 32.130235,
    "remote_user": 0.032946,
    "remote_system": 32.133588
},
"sender_tcp_congestion": "cubic",
"receiver_tcp_congestion": "cubic"
    }
}
"""


    result = parse_output(test_output.split("\n"))
    pprint.PrettyPrinter(indent=4).pprint(result)

