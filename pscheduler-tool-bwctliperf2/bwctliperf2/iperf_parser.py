import re
import pscheduler
import pprint

logger = pscheduler.Log(quiet=True)

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

        # Example lines
        # TCP window size:  244 KByte (WARNING: requested 64.0 MByte)
        # TCP window size: 19800 Byte (default)
        test = re.match('TCP window size:\s+(\d+(\.\d+)?) (\S)?Byte(.*\(WARNING:\s+requested\s+(\d+(\.\d+)?) (\S)?Byte)?', line)
        if test:
            window_size = test.group(1)
            window_si   = test.group(3)

            request_size = test.group(5)
            request_si   = test.group(7)

            if window_si:
                window_size = pscheduler.si_as_number("%s%s" % (window_size, window_si))

            if request_size:
                if request_si:
                    request_size = pscheduler.si_as_number("%s%s" % (request_size, request_si))
                results["requested-tcp-window-size"] = int(request_size)

            results["tcp-window-size"] = int(window_size)

        # Example line
        # [  3] MSS size 1448 bytes (MTU 1500 bytes, ethernet)
        test = re.match('.*MSS size (\d+) bytes \(MTU (\d+) bytes', line)
        if test:
            results['mss'] = int(test.group(1))
            results['mtu'] = int(test.group(2))


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
                throughput_bytes = pscheduler.si_as_number("%s%s" % (throughput_bytes, si_bytes))
            if si_bits:
                throughput_bits = pscheduler.si_as_number("%s%s" % (throughput_bits, si_bits))

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
                                 "throughput-bits": throughput_bits,
                                 "throughput-bytes": throughput_bytes,
                                 "start": interval_start,
                                 "end": interval_end,
                                 "stream-id": stream_id})

        

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
            if stream['stream-id'] == "SUM":
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


    logger.debug(intervals)

    # sort according to start interval
    intervals.sort(key = lambda x: x['summary']['start'])

    
    results["intervals"] = intervals
    results["summary"]   = summary_interval

    return results


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

    #result = parse_output(test_output.split("\n"))
    #pprint.PrettyPrinter(indent=4).pprint(result)



    test_output = """
------------------------------------------------------------
Client connecting to 10.0.2.4, TCP port 5001
TCP window size:  244 KByte (WARNING: requested 7.63 MByte)
------------------------------------------------------------
[  5] local 10.0.2.15 port 42309 connected with 10.0.2.4 port 5001
[  3] local 10.0.2.15 port 42307 connected with 10.0.2.4 port 5001
[  4] local 10.0.2.15 port 42308 connected with 10.0.2.4 port 5001
[ ID] Interval       Transfer     Bandwidth
[  5]  0.0- 1.0 sec  74.8 MBytes   627 Mbits/sec
[  4]  0.0- 1.0 sec  67.0 MBytes   562 Mbits/sec
[  3]  0.0- 1.0 sec  59.0 MBytes   495 Mbits/sec
[SUM]  0.0- 1.0 sec   201 MBytes  1.68 Gbits/sec
[  5]  1.0- 2.0 sec  76.4 MBytes   641 Mbits/sec
[  3]  1.0- 2.0 sec  68.1 MBytes   571 Mbits/sec
[  4]  1.0- 2.0 sec  63.8 MBytes   535 Mbits/sec
[SUM]  1.0- 2.0 sec   208 MBytes  1.75 Gbits/sec
[  5]  2.0- 3.0 sec  76.9 MBytes   645 Mbits/sec
[  3]  2.0- 3.0 sec  61.8 MBytes   518 Mbits/sec
[  4]  2.0- 3.0 sec  65.9 MBytes   553 Mbits/sec
[SUM]  2.0- 3.0 sec   204 MBytes  1.72 Gbits/sec
[  5]  3.0- 4.0 sec  72.6 MBytes   609 Mbits/sec
[  3]  3.0- 4.0 sec  68.8 MBytes   577 Mbits/sec
[  4]  3.0- 4.0 sec  60.9 MBytes   511 Mbits/sec
[SUM]  3.0- 4.0 sec   202 MBytes  1.70 Gbits/sec
[  5]  4.0- 5.0 sec  73.4 MBytes   616 Mbits/sec
[  3]  4.0- 5.0 sec  71.5 MBytes   600 Mbits/sec
[  4]  4.0- 5.0 sec  61.6 MBytes   517 Mbits/sec
[SUM]  4.0- 5.0 sec   206 MBytes  1.73 Gbits/sec
[  3]  5.0- 6.0 sec  73.2 MBytes   614 Mbits/sec
[  4]  5.0- 6.0 sec  67.0 MBytes   562 Mbits/sec
[  5]  5.0- 6.0 sec  64.5 MBytes   541 Mbits/sec
[SUM]  5.0- 6.0 sec   205 MBytes  1.72 Gbits/sec
[  5]  6.0- 7.0 sec  65.6 MBytes   551 Mbits/sec
[  3]  6.0- 7.0 sec  75.0 MBytes   629 Mbits/sec
[  4]  6.0- 7.0 sec  70.4 MBytes   590 Mbits/sec
[SUM]  6.0- 7.0 sec   211 MBytes  1.77 Gbits/sec
[  3]  7.0- 8.0 sec  77.0 MBytes   646 Mbits/sec
[  4]  7.0- 8.0 sec  65.9 MBytes   553 Mbits/sec
[  5]  7.0- 8.0 sec  63.8 MBytes   535 Mbits/sec
[SUM]  7.0- 8.0 sec   207 MBytes  1.73 Gbits/sec
[  3]  8.0- 9.0 sec  76.2 MBytes   640 Mbits/sec
[  5]  8.0- 9.0 sec  65.0 MBytes   545 Mbits/sec
[  4]  8.0- 9.0 sec  68.4 MBytes   574 Mbits/sec
[SUM]  8.0- 9.0 sec   210 MBytes  1.76 Gbits/sec
[  5]  9.0-10.0 sec  67.6 MBytes   567 Mbits/sec
[  5]  0.0-10.0 sec   701 MBytes   588 Mbits/sec
[  3]  9.0-10.0 sec  71.1 MBytes   597 Mbits/sec
[  3]  0.0-10.0 sec   702 MBytes   589 Mbits/sec
[  4]  9.0-10.0 sec  72.2 MBytes   606 Mbits/sec
[SUM]  9.0-10.0 sec   211 MBytes  1.77 Gbits/sec
[  4]  0.0-10.0 sec   663 MBytes   556 Mbits/sec
[SUM]  0.0-10.0 sec  2.02 GBytes  1.73 Gbits/sec
[  3] MSS size 1448 bytes (MTU 1500 bytes, ethernet)
"""

    result = parse_output(test_output.split("\n"))
    pprint.PrettyPrinter(indent=4).pprint(result)

    
