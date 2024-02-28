import re
import pscheduler

logger = pscheduler.Log(quiet=True)

def _finalize_interval(streams):
    '''
    Prepare a final interval, figuring out what the summary should be
    based on iperf's output.
    '''
    assert isinstance(streams,list)
    assert len(streams) > 0

    if len(streams) == 1:
        # Sole stream
        summary = streams[0]
    else:
        # Multi-stream, last one is the summary
        summary = streams.pop()
        assert summary['stream-id'] == 'SUM'

    return {
        'streams': streams,
        'summary': summary
    }



def parse_output(lines, expect_udp=False):
    '''
    A whole bunch of pattern matching against the output of the
    "iperf" tool client output. Builds up an object of interesting bits
    from it.

    Developed against iperf version 2.1.9 (14 March 2023) pthreads

    Note that this assumes iperf was invoked with '--format b' so there
    are no SI units to be converted and -m so MSS is displayed.
    '''


    results = {
        'succeeded': True
    }



    intervals = []
    current_interval = []
    current_interval_key = None

    has_summaries = False

    longest_interval = 0
    longest_interval_key = None

    streams = {}


    for line in lines:

        # Bogus numbers

        if re.match('\(nan%\)', line):
            return {
                'succeeded': False,
                'error': 'Found NaN result'
            }

        # Connection failures

        if re.match('read failed: Connection refused', line):
            return {
                'succeeded': False,
                'error': 'Connection refused'
            }

        # Initial connection message

        # Example lines:
        # Client connecting to localhost, TCP port 5001 with pid 119661 (1 flows)
        # Client connecting to localhost, UDP port 5001 with pid 119686 (1 flows)

        test = re.match('^Client connecting to .*, (TCP|UDP) port', line)
        if test:
            protocol = test.group(1)
            if (protocol == 'TCP' and expect_udp) or (protocol == 'UDP' and not expect_udp):
                return {
                    "succeeded": False,
                    "error": f'Protocol mismatch: was not expecting {protocol}.'
                }
            # Anything else is okay.
            continue

        # TCP Window Size

        # Example line:
        # TCP window size: 2626560 Byte (default)
        # TCP window size: 425984 Byte (WARNING: requested 1000000 Byte)

        test = re.match('^TCP window size:\s+(\d+) Byte (\(WARNING: requested (\d+) Byte\))?', line)
        if test:
            assert not expect_udp
            results['tcp-window-size'] = int(test.group(1))
            requested_size = test.group(3)
            if requested_size:
                results['requested-tcp-window-size'] = int(requested_size)


        # MSS

        # Example line:
        # [  1] local 127.0.0.1%lo port 58260 connected with 127.0.0.1 port 5001 (sock=3) (icwnd/mss/irtt=319/32741/38) (ct=0.11 ms) on 2024-02-22 15:54:35.781 (UTC)

        # Note that this will be matched and overwritten once per
        # stream.  This shouldn't matter because, in theory, they
        # should all be the same.

        test = re.match('^\[\s*\d+\].*\(icwnd/mss/irtt=\d+/(\d+)/\d+\)', line)
        if test:
            assert not expect_udp
            results['mss'] = int(test.group(1))


        # If we start seeing server reports, we've seen everything
        # from the client side.  Treat it as EOF.
        if re.match('^\[\s*(\d+|SUM) Server Report:', line):
            break

        # Interval

        # Single parsed record
        stream_interval = None
        interval_start = None
        interval_end = None

        if expect_udp:

            # Example line (with annotations):
            # [ ID] Interval        Transfer     Bandwidth      Write/Err  PPS
            # [  1] 4.00-6.00 sec  263130 Bytes  1052520 bits/sec  179/0       89 pps

            test = re.match(
                '^\[\s*(\d+|SUM)\]'   # 1 - Stream ID
                '\s+(\d+\.\d+)'       # 2 - Interval start
                '-(\d+\.\d+) sec'     # 3 - Interval end
                '\s+(\d+) Bytes'      # 4 - Bytes transferred
                '\s+(\d+) bits/sec'   # 5 - Bandwidth
                '\s+(\d+)'            # 6 - Writes
                '/(\d+)'              # 7 - Errors
                '\s+(\d+) pps$'       # 8 - Packets per second
                , line)

            if not test:
                continue

            stream_id = test.group(1)
            interval_start = float(test.group(2))
            interval_end = float(test.group(3))

            stream_interval = {
                'throughput-bits': int(test.group(5)),
                'throughput-bytes': int(int(test.group(5)) / 8),
                'sent': int(test.group(6)),
                'stream-id': test.group(1),
                'start': interval_start,
                'end': interval_end
            }

            # Use the text as matched rather than the Python-parsed
            # floats.  If it's a summary, don't change the key because
            # the numbers are usually off.
            if stream_id != 'SUM':
                key = f'{test.group(2)}-{test.group(3)}'


        else:

            # Example line (with annotations):
            # [ ID] Interval        Transfer    Bandwidth       Write/Err  Rtry     Cwnd/RTT(var)        NetPwr
            # [  1] 2.00-4.00 sec  11173888000 Bytes  44695552000 bits/sec  85250/0        10     1470K/33(4) us  169301333

            test = re.match(
                '^\[\s*(\d+|SUM)\]'   # 1 - Stream ID
                '\s+(\d+\.\d+)'       # 2 - Interval start
                '-(\d+\.\d+) sec'     # 3 - Interval end
                '\s+(\d+) Bytes'      # 4 - Bytes transferred
                '\s+(\d+) bits/sec'   # 5 - Bandwidth
                '\s+(\d+)'            # 6 - Writes
                '/(\d+)'              # 7 - Errors
                '\s+(\d+)'            # 8 - Retransmits
                '('                   # 9 - Begin optional stuff
                '\s+(\d+K)'           # 10 - Window size in SI units
                '/(\d+)'              # 11 - RTT
                '\((\d+)\) us'        # 12 - RTT Variance(?)
                '\s*(\d+)'            # 13 - Net Power (Experimental)
                ')?'
                '\s*$'
                , line)
            
            if not test:
                continue

            stream_id = test.group(1)
            interval_start = float(test.group(2))
            interval_end = float(test.group(3))

            stream_interval = {
                'throughput-bits': int(test.group(5)),
                'throughput-bytes': int(int(test.group(5)) / 8),
                'sent': int(test.group(6)),
                'stream-id': test.group(1),
                'start': interval_start,
                'end': interval_end,
                'retransmits': int(test.group(8))
            }

            if test.group(10) is not None:
                stream_interval['tcp-window-size'] = pscheduler.si_as_number(test.group(10))

            if test.group(11) is not None:
                stream_interval['rtt'] = int(test.group(11))

            # Use the text as matched rather than the Python-parsed
            # floats.  If it's a summary, don't change the key because
            # the numbers are usually off.
            if stream_id != 'SUM':
                key = f'{test.group(2)}-{test.group(3)}'

        assert interval_start is not None
        assert interval_end is not None

        if key != current_interval_key:
            if current_interval:
                intervals.append(_finalize_interval(current_interval))
            current_interval = []
            current_interval_key = key

        current_interval.append(stream_interval)

    # Push anything left onto the list.
    if current_interval:
        intervals.append(_finalize_interval(current_interval))
                

    if not intervals:
        return {
            'succeeded': False,
            'error': 'No results found'
        }


    if len(intervals) == 1:
        # The summary is the same as the sole interval
        summary_interval = intervals[0]
    else:        
        # The last interval is the summary interval.
        summary_interval = intervals.pop()

    results['intervals'] = intervals
    results['summary'] = summary_interval

    return results


if __name__ == "__main__":

    TEST_OUTPUTS = [

        {
            'label': 'TCP Single-Stream',
            'expect_udp': False,
            'text': '''
iperf -c localhost -e  --format b -i 2 -t 6
------------------------------------------------------------
Client connecting to localhost, TCP port 5001 with pid 157041 (1 flows)
Write buffer size: 131072 Byte
TOS set to 0x0 (Nagle on)
TCP window size: 2626560 Byte (default)
------------------------------------------------------------
[  1] local 127.0.0.1%lo port 47358 connected with 127.0.0.1 port 5001 (sock=3) (icwnd/mss/irtt=319/32741/35) (ct=0.09 ms) on 2024-02-26 22:16:25.887 (UTC)
[ ID] Interval        Transfer    Bandwidth       Write/Err  Rtry     Cwnd/RTT(var)        NetPwr
[  1] 0.00-2.00 sec  10924589116 Bytes  43698356464 bits/sec  83348/0        11     3645K/36(7) us  151730404
[  1] 2.00-4.00 sec  11269832704 Bytes  45079330816 bits/sec  85982/0         4     3645K/38(6) us  148287272
[  1] 4.00-6.00 sec  11097866240 Bytes  44391464960 bits/sec  84670/0         2     3645K/32(5) us  173404160
[  1] 0.00-6.01 sec  33292419132 Bytes  44297878100 bits/sec  254001/0        17     3645K/1575(3097) us  3515705
'''
        },

        {
            'label': 'TCP Multi-Stream',
            'expect_udp': False,
            'text': '''
iperf -c localhost -e  --format b -i 2 -t 6 -P 2
------------------------------------------------------------
Client connecting to localhost, TCP port 5001 with pid 133581 (2 flows)
Write buffer size: 131072 Byte
TOS set to 0x0 (Nagle on)
TCP window size: 2626560 Byte (default)
------------------------------------------------------------
[  1] local 127.0.0.1%lo port 55778 connected with 127.0.0.1 port 5001 (sock=3) (icwnd/mss/irtt=319/32741/39) (ct=0.11 ms) on 2024-02-23 15:51:57.435 (UTC)
[  2] local 127.0.0.1%lo port 55790 connected with 127.0.0.1 port 5001 (sock=4) (icwnd/mss/irtt=319/32741/58) (ct=0.11 ms) on 2024-02-23 15:51:57.435 (UTC)
[ ID] Interval        Transfer    Bandwidth       Write/Err  Rtry     Cwnd/RTT(var)        NetPwr
[  1] 0.00-2.00 sec  9784655932 Bytes  39138623728 bits/sec  74651/0         0     2110K/34(2) us  143891999
[  2] 0.00-2.00 sec  9957408828 Bytes  39829635312 bits/sec  75969/0         1     4220K/34(1) us  146432483
[SUM] 0.00-2.00 sec  19742064760 Bytes  78968259040 bits/sec  150620/0         1
[  1] 2.00-4.00 sec  9664200704 Bytes  38656802816 bits/sec  73732/0         0     2877K/39(5) us  123900009
[  2] 2.00-4.00 sec  10205396992 Bytes  40821587968 bits/sec  77861/0         0     4220K/38(4) us  134281539
[SUM] 2.00-4.00 sec  19869597696 Bytes  79478390784 bits/sec  151593/0         0
[  1] 4.00-6.00 sec  8287682560 Bytes  33150730240 bits/sec  63230/0         0     2877K/36(7) us  115106702
[  2] 4.00-6.00 sec  10189537280 Bytes  40758149120 bits/sec  77740/0         2     4220K/35(2) us  145564818
[SUM] 4.00-6.00 sec  18477219840 Bytes  73908879360 bits/sec  140970/0         2
[  1] 0.00-6.02 sec  27737194556 Bytes  36857799987 bits/sec  211618/0         1     2877K/408(745) us  11292218
[  2] 0.00-6.02 sec  30352474172 Bytes  40332659745 bits/sec  231571/0         3     4220K/2574(5082) us  1958657
[SUM] 0.00-6.00 sec  58089668728 Bytes  77452452740 bits/sec  443189/0         4
[ CT] final connect times (min/avg/max/stdev) = 0.106/0.106/0.107/0.707 ms (tot/err) = 2/0
'''
        },

        {
            'label': 'UDP Single-Stream',
            'expect_udp': True,
            'text': '''
iperf -c localhost -e  --format b -i 2 -t 6 -u
------------------------------------------------------------
Client connecting to localhost, UDP port 5001 with pid 157309 (1 flows)
TOS set to 0x0 (Nagle on)
Sending 1470 byte datagrams, IPG target: 11215.21 us (kalman adjust)
UDP buffer size: 212992 Byte (default)
------------------------------------------------------------
[  1] local 127.0.0.1%lo port 49449 connected with 127.0.0.1 port 5001 (sock=3) on 2024-02-26 22:22:07.973 (UTC)
[ ID] Interval        Transfer     Bandwidth      Write/Err  PPS
[  1] 0.00-2.00 sec  264600 Bytes  1058400 bits/sec  179/0       90 pps
[  1] 2.00-4.00 sec  261660 Bytes  1046640 bits/sec  178/0       89 pps
[  1] 4.00-6.00 sec  261660 Bytes  1046640 bits/sec  178/0       89 pps
[  1] 0.00-6.01 sec  790860 Bytes  1052461 bits/sec  537/0       90 pps
[  1] Sent 539 datagrams
[  1] Server Report:
[ ID] Interval       Transfer     Bandwidth        Jitter   Lost/Total Datagrams
[  1] 0.00-6.01 sec  790860 Bytes  1052469 bits/sec   0.013 ms 0/538 (0%)
'''         
        },

        {
            'label': 'UDP Multi-Stream',
            'expect_udp': True,
            'text': '''
iperf -c localhost -e  --format b -i 2 -t 6 -P 2 -u
------------------------------------------------------------
Client connecting to localhost, UDP port 5001 with pid 133597 (2 flows)
TOS set to 0x0 (Nagle on)
Sending 1470 byte datagrams, IPG target: 11215.21 us (kalman adjust)
UDP buffer size: 212992 Byte (default)
------------------------------------------------------------
[  1] local 127.0.0.1%lo port 42613 connected with 127.0.0.1 port 5001 (sock=3) on 2024-02-23 15:52:44.280 (UTC)
[  2] local 127.0.0.1%lo port 50674 connected with 127.0.0.1 port 5001 (sock=4) on 2024-02-23 15:52:44.281 (UTC)
[ ID] Interval        Transfer     Bandwidth      Write/Err  PPS
[  2] 0.00-2.00 sec  264600 Bytes  1058400 bits/sec  179/0       90 pps
[  1] 0.00-2.00 sec  264600 Bytes  1058400 bits/sec  179/0       90 pps
[SUM] 0.00-2.00 sec  529200 Bytes  2116800 bits/sec  358/0     180 pps
[  2] 2.00-4.00 sec  261660 Bytes  1046640 bits/sec  178/0       89 pps
[  1] 2.00-4.00 sec  261660 Bytes  1046640 bits/sec  178/0       89 pps
[SUM] 2.00-4.00 sec  523320 Bytes  2093280 bits/sec  356/0     178 pps
[  2] 4.00-6.00 sec  261660 Bytes  1046640 bits/sec  178/0       89 pps
[  1] 4.00-6.00 sec  261660 Bytes  1046640 bits/sec  178/0       89 pps
[SUM] 4.00-6.00 sec  523320 Bytes  2093280 bits/sec  356/0     178 pps
[  2] 0.00-6.01 sec  790860 Bytes  1052473 bits/sec  537/0       90 pps
[  2] Sent 539 datagrams
[  1] 0.00-6.01 sec  790860 Bytes  1052455 bits/sec  537/0       90 pps
[  1] Sent 539 datagrams
[SUM] 0.00-6.01 sec  1581720 Bytes  2104909 bits/sec  1074/0     179 pps
[SUM-2] Sent 1078 datagrams
[  2] Server Report:
[ ID] Interval       Transfer     Bandwidth        Jitter   Lost/Total Datagrams
[  2] 0.00-5.99 sec  789390 Bytes  1053488 bits/sec   0.006 ms 1/538 (0.19%)
[  1] Server Report:
[ ID] Interval       Transfer     Bandwidth        Jitter   Lost/Total Datagrams
[  1] 0.00-6.01 sec  792330 Bytes  1054424 bits/sec   0.008 ms 0/538 (0%)
[  1] 0.00-6.01 sec  1 datagrams received out-of-order
'''
            }
    ]


    for test in TEST_OUTPUTS:
        print(f'''\n{test['label']}\n''')
        print(
            pscheduler.json_dump(
                parse_output(
                    test['text'].split('\n'),
                    expect_udp=test['expect_udp']
                ),
                pretty=True)
    )
