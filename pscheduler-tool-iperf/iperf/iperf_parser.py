import re
import pscheduler
import pprint

logger = pscheduler.Log()

# A whole bunch of pattern matching against the output of the "iperf" tool
# client output. Builds up an object of interesting bits from it.
def parse_output(lines):
    results = {}
    results['succeeded'] = True

    seen_header = False
    streams    = {}

    dest_ip   = None
    dest_port = None
    src_ip    = None
    src_port  = None

    for line in lines:

        # ignore bogus sessions
        if re.match('\(nan%\)', line):
            results["succeeded"] = False
            results["error"]    = "Found NaN result";
            break;

        if re.match('read failed: Connection refused', line):
            results["succeeded"] = False
            results["error"]     = "Connection refused"
            break


        test = re.match('local ([^ ]+) port (\d+) connected with ([^ ]+) port (\d+)', line)
        if test:
            dest_ip   = test.group(1)
            dest_port = test.group(2)
            src_ip    = test.group(3)
            src_port  = test.group(4)


        stream_id        = None
        interval_start   = None
        throughput_bytes = None
        si_bytes         = None
        throughput_bits  = None
        si_bits          = None
        jitter           = None
        lost             = None
        sent             = None

        # Example line
        # [  3] 16.0-17.0 sec  37355520 Bytes  298844160 bits/sec
        test = re.match('\[\s*(\d+|SUM)\s*\]\s+([0-9\.]+)\s*\-\s*([0-9\.]+)\s+sec\s+(\d+(\.\d+)?)\s+(P|T|G|M|K)?Bytes\s+(\d+(\.\d+)?)\s+(P|T|G|M|K)?bits\/sec(\s+([0-9\.]+)\s+ms\s+(\d+)\/\s*(\d+)\s+)?', line)
        if test:
            stream_id         = test.group(1)
            interval_start    = float(test.group(2))
            interval_end      = float(test.group(3))
            throughput_bytes  = float(test.group(4))
            si_bytes          = test.group(6)
            throughput_bits   = float(test.group(7))
            si_bits           = test.group(9)
            
            # these may or may not be present depending on versions
            jitter = test.group(11)
            lost   = test.group(12)
            send   = test.group(13)

            # If the output was in say GBytes convert back to regular Bytes for ease
            # of things later
            if si_bytes:
                throughput_bytes = convert(throughput_bytes, si_bytes)
            if si_bits:
                throughput_bits = convert(throughput_bits, si_bits)

        # if we found a matching line, we can add this info to our streams
        if stream_id:

            key = "%s-%s" % (interval_start, interval_end)

            # there has to be a better way than this...
            if interval_end - interval_start > 5:
                key = "summary"

            if not streams.has_key(key):
                streams[key] = []

            streams[key].append({"jitter": jitter,
                                 "lost": lost,
                                 "sent": sent,
                                 "throughput_bits": throughput_bits,
                                 "throughput_bytes": throughput_bytes,
                                 "start": interval_start,
                                 "end": interval_end,
                                 "stream_id": stream_id})

        

    if len(streams.keys()) == 0:
        results["succeeded"] = False
        results["error"] = "No results found"
        return results


    summary_interval = None
    intervals        = []

    for interval in streams.keys():

        summary_stream = None

        interval_streams = []

        # try to find the SUM if possible
        for stream in streams[interval]:
            if stream['stream_id'] == "SUM":
                summary_stream = stream
            else:
                interval_streams.append(stream)
                
 
        # if we couldn't find it, there was probably
        # just the one line so use that
        if not summary_stream and len(interval_streams) == 1:
            summary_stream = interval_streams[0]

        finalized = {
            "streams": interval_streams,
            "summary": summary_stream
        }

        if interval == "summary":
            summary_interval = finalized
        else:
            intervals.append(finalized)


    # sort according to start interval
    intervals.sort(key = lambda x: x['summary']['start'])

    
    results["intervals"] = intervals
    results["summary"]   = summary_interval

    return results


def convert(number, si):

    rates = {
        'P': 15,
        'T': 12,
        'G': 9,
        'M': 6,
        'K': 3    
    }

    return number * (10 ** rates[si])



if __name__ == "__main__":

    # Test a "regular" output
    test_output = """
------------------------------------------------------------
Client connecting to 10.0.2.15, TCP port 5001
TCP window size: 19800 Byte (default)
------------------------------------------------------------
[  3] local 10.0.2.4 port 50338 connected with 10.0.2.15 port 5001
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec  224788480 Bytes  1798307840 bits/sec
[  3]  1.0- 2.0 sec  222298112 Bytes  1778384896 bits/sec
[  3]  2.0- 3.0 sec  150339584 Bytes  1202716672 bits/sec
[  3]  3.0- 4.0 sec  210501632 Bytes  1684013056 bits/sec
[  3]  4.0- 5.0 sec  218759168 Bytes  1750073344 bits/sec
[  3]  5.0- 6.0 sec  222298112 Bytes  1778384896 bits/sec
[  3]  6.0- 7.0 sec  233177088 Bytes  1865416704 bits/sec
[  3]  7.0- 8.0 sec  230686720 Bytes  1845493760 bits/sec
[  3]  8.0- 9.0 sec  229638144 Bytes  1837105152 bits/sec
[  3]  9.0-10.0 sec  226492416 Bytes  1811939328 bits/sec
[  3]  0.0-10.0 sec  2169110528 Bytes  1735167481 bits/sec
"""

    result = parse_output(test_output.split("\n"))

    pprint.PrettyPrinter(indent=4).pprint(result)




    
