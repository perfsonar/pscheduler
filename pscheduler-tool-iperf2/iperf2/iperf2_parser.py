import re
import pscheduler


def _finalize_interval(streams, debug):
    '''
    Prepare a final interval, figuring out what the summary should be
    based on iperf's output.
    '''
    assert isinstance(streams,list)
    assert len(streams) > 0

    debug(f'''Finalizing {streams[0]['start']}-{streams[0]['end']}''')

    if len(streams) == 1:
        # Sole stream
        summary = streams[0]
    else:
        # Multi-stream, last one is the summary
        summary = streams.pop()
        assert summary['stream-id'] == 'SUM'

    # Put the streams into a reasonable order with the summary last.
    streams.sort(key=lambda v: int(v['stream-id']))

    return {
        'streams': streams,
        'summary': summary
    }



def parse_output(lines, expect_udp=False, logger=None):
    '''
    A whole bunch of pattern matching against the output of the
    "iperf" tool client output. Builds up an object of interesting bits
    from it.

    Developed against iperf version 2.1.9 (14 March 2023) pthreads

    Note that this assumes iperf was invoked with '--format b' so there
    are no SI units to be converted and -m so MSS is displayed.
    '''

    debug = logger.debug if logger is not None else lambda m: None


    results = {
        'succeeded': True
    }



    intervals = []
    current_interval = []
    current_interval_key = None

    streams = {}

    # These are used in detecting and correcting the time stamps on
    # what should be the last interval.

    last_start = 0
    highest_end = 0
    highest_end_string = '0.0'
    in_final_summary = False

    for line in lines:

        debug(f'Line {line}')

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
            interval_start = test.group(2)
            interval_end = test.group(3)

            stream_interval = {
                'throughput-bits': int(test.group(5)),
                'throughput-bytes': int(int(test.group(5)) / 8),
                'sent': int(test.group(6)),
                'stream-id': test.group(1),
                'start': interval_start,
                'end': interval_end
            }

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
            interval_start = test.group(2)
            interval_end = test.group(3)

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


        assert interval_start is not None
        assert interval_end is not None

        interval_start_float = float(interval_start)
        interval_end_float = float(interval_end)

        if not in_final_summary:

            if interval_start_float < last_start:
                # Start of summary interval, e.g., went from 8.00-10.00 to 0.00-10.00
                debug(f'Start final summary: Start dropeed from {last_start} -> {interval_start_float}')
                in_final_summary = True
                interval_end = highest_end_string
                debug(f'Adjusted interval end to {interval_end}')
            else:
                last_start = interval_start_float
                if interval_end_float > highest_end:
                    highest_end = interval_end_float
                    highest_end_string = interval_end
                    debug(f'New high {interval_end}')

        else:

            # Inside the final summary, force the end of the interval
            # to the end of the last interval to avoid complications
            # from iperf2's wrong concept of when the last measurement
            # interval ended.
            interval_end = highest_end_string
            debug(f'Adjusted final interval end to {interval_end}')

        if stream_id != 'SUM':
            key = f'{interval_start}-{interval_end}'

        stream_interval['start'] = float(interval_start)
        stream_interval['end'] = float(interval_end)

        if key != current_interval_key:
            debug(f'New interval: {current_interval_key} -> {key}')
            if current_interval:
                intervals.append(_finalize_interval(current_interval, debug))
            current_interval = []
            current_interval_key = key

        current_interval.append(stream_interval)

    # Push anything left onto the list.
    if current_interval:
        intervals.append(_finalize_interval(current_interval, debug))
                

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
        },
        {
            'label': 'Uneven final interval',
            'expect_udp': False,
            'text': '''
------------------------------------------------------------
Client connecting to denv.ps.internet2.edu, TCP port 5001 with pid 188114 (4 flows)
Write buffer size: 131072 Byte
MSS size 536 bytes
TOS set to 0x0 (Nagle on)
TCP window size: 16384 Byte (default)
------------------------------------------------------------
[  3] local 10.88.0.116%eth0 port 54908 connected with 163.253.16.23 port 5001 (sock=3) (icwnd/mss/irtt=14/1460/31343) (ct=31.43 ms) on 2024-02-29 20:24:26.026 (UTC)
[  1] local 10.88.0.116%eth0 port 54916 connected with 163.253.16.23 port 5001 (sock=5) (icwnd/mss/irtt=14/1460/31149) (ct=31.26 ms) on 2024-02-29 20:24:26.026 (UTC)
[  4] local 10.88.0.116%eth0 port 54912 connected with 163.253.16.23 port 5001 (sock=4) (icwnd/mss/irtt=14/1460/31210) (ct=31.33 ms) on 2024-02-29 20:24:26.026 (UTC)
[  2] local 10.88.0.116%eth0 port 54932 connected with 163.253.16.23 port 5001 (sock=6) (icwnd/mss/irtt=14/1460/31083) (ct=31.18 ms) on 2024-02-29 20:24:26.026 (UTC)
[ ID] Interval        Transfer    Bandwidth       Write/Err  Rtry     Cwnd/RTT(var)        NetPwr
[  4] 0.00-2.00 sec  34078780 Bytes  136315120 bits/sec  260/0       387       58K/1107(145) us  15392
[  2] 0.00-2.00 sec  27000892 Bytes  108003568 bits/sec  206/0       254       41K/1451(36) us  9304
[  3] 0.00-2.00 sec  31326268 Bytes  125305072 bits/sec  239/0       562       69K/1024(210) us  15296
[  1] 0.00-2.00 sec  29491260 Bytes  117965040 bits/sec  225/0       444       54K/3966(192) us  3718
[SUM] 0.00-2.00 sec  121897200 Bytes  487588800 bits/sec  930/0      1647
[  1] 2.00-4.00 sec  28049408 Bytes  112197632 bits/sec  214/0       111       25K/2323(352) us  6037
[  4] 2.00-4.00 sec  33161216 Bytes  132644864 bits/sec  253/0       272       65K/2349(46) us  7059
[  2] 2.00-4.00 sec  29884416 Bytes  119537664 bits/sec  228/0       128       65K/1550(65) us  9640
[  3] 2.00-4.00 sec  32505856 Bytes  130023424 bits/sec  248/0       193       65K/1621(157) us  10026
[SUM] 2.00-4.00 sec  123600896 Bytes  494403584 bits/sec  943/0       704
[  1] 4.00-6.00 sec  31850496 Bytes  127401984 bits/sec  243/0       647       22K/1545(58) us  10308
[  3] 4.00-6.00 sec  32112640 Bytes  128450560 bits/sec  245/0       334       14K/1866(129) us  8605
[  4] 4.00-6.00 sec  38797312 Bytes  155189248 bits/sec  296/0       568       57K/1798(8) us  10789
[  2] 4.00-6.00 sec  29491200 Bytes  117964800 bits/sec  225/0       526       27K/1683(55) us  8761
[SUM] 4.00-6.00 sec  132251648 Bytes  529006592 bits/sec  1009/0      2075
[  3] 6.00-8.00 sec  39452672 Bytes  157810688 bits/sec  301/0       230       72K/2468(225) us  7993
[  4] 6.00-8.00 sec  40763392 Bytes  163053568 bits/sec  311/0        77       68K/2218(142) us  9189
[  2] 6.00-8.00 sec  34865152 Bytes  139460608 bits/sec  266/0       509       48K/1181(106) us  14761
[  1] 6.00-8.00 sec  36438016 Bytes  145752064 bits/sec  278/0       168       67K/920(164) us  19803
[SUM] 6.00-8.00 sec  151519232 Bytes  606076928 bits/sec  1156/0       984
[  1] 8.00-10.00 sec  38010880 Bytes  152043520 bits/sec  290/0       157       59K/2268(289) us  8380
[  3] 8.00-10.00 sec  39583744 Bytes  158334976 bits/sec  302/0        44       67K/2700(92) us  7330
[  4] 8.00-10.00 sec  42598400 Bytes  170393600 bits/sec  325/0        18       67K/1622(60) us  13131
[  2] 8.00-10.00 sec  36175872 Bytes  144703488 bits/sec  276/0       253       38K/2034(207) us  8893
[SUM] 8.00-10.00 sec  156368896 Bytes  625475584 bits/sec  1193/0       472
[  2] 0.00-10.14 sec  157548604 Bytes  124306045 bits/sec  1202/0      1670       38K/458(18) us  33926
[  3] 0.00-10.19 sec  175112252 Bytes  137469482 bits/sec  1336/0      1363       67K/1805(283) us  9520
[  4] 0.00-10.19 sec  189530172 Bytes  148792118 bits/sec  1446/0      1322       67K/897(131) us  20735
[  1] 0.00-10.21 sec  163971132 Bytes  128471237 bits/sec  1251/0      1527       62K/2821(112) us  5693
[SUM] 0.00-10.01 sec  686162160 Bytes  548236045 bits/sec  5235/0      5882
[ CT] final connect times (min/avg/max/stdev) = 31.182/31.303/31.434/107.410 ms (tot/err) = 4/0
'''
        }
    ]

    logger = pscheduler.Log(debug=True, verbose=True)

    # Enable this to test a specific element
    # TEST_OUTPUTS = [ TEST_OUTPUTS[-1] ]

    for test in TEST_OUTPUTS:
        print(f'''\n{test['label']}\n''')
        result = parse_output(
            test['text'].split('\n'),
            expect_udp=test['expect_udp'],
            logger=logger
        )
        print(pscheduler.json_dump(result, pretty=True))
