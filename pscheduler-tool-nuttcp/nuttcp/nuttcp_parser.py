import re
import pscheduler
import pprint
import json
import sys

logger = pscheduler.Log(quiet=True)

# A whole bunch of pattern matching against the output of the "nuttcp" tool
# client output. Builds up an object of interesting bits from it.
def parse_output(lines):
    results = {}
    results['succeeded'] = True

    intervals = []
    summary_view = {}

    current_interval_start = 0
    for line in lines:

        # Example line:
        # 216.8125 MB /   1.00 sec = 1817.8571 Mbps    45 retrans    206 KB-cwnd
        test = re.match('^\s*(\d+(\.\d+)?) MB\s*\/\s*(\d+)\.\d+ sec \=\s*(\d+(\.\d+)?) (\S)bps\s*(\d+) retrans(\s*(\d+)\s*(\S)\S\-cwnd)?', line)
        if test:
            volume  = float(test.group(1))
            spacing = int(test.group(3))
            value   = test.group(4)
            si      = test.group(6)
            retrans = int(test.group(7))
            cwnd    = test.group(9)
            cwnd_si = test.group(10)

            value = pscheduler.si_as_number("%s%s" % (value, si))
            cwnd  = pscheduler.si_as_number("%s%s" % (cwnd, cwnd_si))

            # volume always seems to be reported in MB, need to standardize to just B
            volume *= 10**6;
            
            data = {
                "start": current_interval_start,
                "end": current_interval_start + spacing,
                "stream-id": 1, # nuttcp won't report separate streams as best as I can tell, so just fudge it
                "throughput-bits": value,
                "throughput-bytes": volume,
                "tcp-window-size": cwnd,
                "retransmits": retrans
                }

            # since it doesn't report 1-2, 3-4, etc we have to keep track of where we are ourselves
            current_interval_start += spacing

            # in nuttcp there's only ever one reported and it's the summary so
            # just double it up
            intervals.append({"summary": data,
                              "streams": [data]})
            

        # Example UDP line
        #     5.9609 MB /   1.00 sec =   49.9993 Mbps     0 /  6104 ~drop/pkt  0.00 ~%loss 0.8362 msMaxJitter
        # 25.1572 MB /   1.00 sec =  211.0065 Mbps    62 / 25823 ~drop/pkt  0.24 ~%loss 4.8672 msMaxJitter
        test = re.match('^\s*(\d+(\.\d+)?) MB\s*\/\s*(\d+)\.\d+ sec \=\s*(\d+(\.\d+)?) (\S)bps\s*(\d+)\s*/\s*(\d+) ~drop/pkt\s*(\d+\.\d+) ~%loss\s*(\d+\.\d+) msMaxJitter', line)
        if test:
            volume  = float(test.group(1))
            spacing = int(test.group(3))
            value   = test.group(4)
            si      = test.group(6)
            lost    = int(test.group(7))
            sent    = int(test.group(8))
            loss    = test.group(9)
            jitter  = float(test.group(10))

            value = pscheduler.si_as_number("%s%s" % (value, si))

            # volume always seems to be reported in MB, need to standardize to just B
            volume *= 10**6
            
            data = {
                "start": current_interval_start,
                "end": current_interval_start + spacing,
                "stream-id": 1, # nuttcp won't report separate streams as best as I can tell, so just fudge it
                "throughput-bits": value,
                "throughput-bytes": volume,
                "sent": sent,
                "lost": lost,
                "jitter": jitter
                }

            # since it doesn't report 1-2, 3-4, etc we have to keep track of where we are ourselves
            current_interval_start += spacing

            # in nuttcp there's only ever one reported and it's the summary so
            # just double it up
            intervals.append({"summary": data,
                              "streams": [data]})
        
        # Example summary line:
        # 2197.0657 MB /  10.00 sec = 1842.3790 Mbps 8 %TX 90 %RX 90 retrans 237 KB-cwnd 0.50 msRTT
        test = re.match('^\s*(\d+(\.\d+)?) MB\s*\/\s*(\d+)\.\d+ sec =\s*(\d+(\.\d+)?) (\S)bps \d+ %TX \d+ %RX (\d+) retrans(\s*(\d+)\s*(\S)\S\-cwnd)?', line)
        if test:
            volume   = float(test.group(1))
            duration = int(test.group(3))
            value    = test.group(4)
            si       = test.group(6)
            retrans  = int(test.group(7))
            cwnd     = test.group(9)
            cwnd_si  = test.group(10)
           
            value = pscheduler.si_as_number("%s%s" % (value, si))
            cwnd  = pscheduler.si_as_number("%s%s" % (cwnd, cwnd_si))

            # volume always seems to be reported in MB, need to standardize to just B
            volume *= 10**6

            summary_view = {
                "start": 0,
                "end": duration,
                "stream-id": 1, # nuttcp won't report separate streams as best as I can tell, so just fudge it
                "throughput-bits": value,
                "throughput-bytes": volume,
                "tcp-window-size": cwnd,
                "retransmits": retrans
                }


        # Example UDP summary line
        #   252.0586 MB /  10.00 sec =  211.4462 Mbps 99 %TX 50 %RX 1485 / 259593 drop/pkt 0.57 %loss 37.2012 msMaxJitter
        test = re.match('^\s*(\d+(\.\d+)?) MB\s*\/\s*(\d+)\.\d+ sec \=\s*(\d+(\.\d+)?) (\S)bps\s*(\d+) %TX (\d+) %RX (\d+)\s*/\s*(\d+) drop/pkt\s*(\d+\.\d+) %loss\s*(\d+\.\d+) msMaxJitter', line)
        if test:
            volume   = float(test.group(1))
            duration = int(test.group(3))
            value    = test.group(4)
            si       = test.group(6)
            lost     = int(test.group(9))
            sent     = int(test.group(10))
            loss     = test.group(11)
            jitter   = float(test.group(12))

            value = pscheduler.si_as_number("%s%s" % (value, si))

            # volume always seems to be reported in MB, need to standardize to just B
            volume *= 10**6
            
            summary_view = {
                "start": 0,
                "end": duration,
                "stream-id": 1, # nuttcp won't report separate streams as best as I can tell, so just fudge it
                "throughput-bits": value,
                "throughput-bytes": volume,
                "sent": sent,
                "lost": lost,
                "jitter": jitter
                }
            

    results["intervals"] = intervals
    results["summary"]   = {"summary": summary_view,
                            "streams": [summary_view]}

    return results

 
if __name__ == "__main__":

    # Test "regular" output
    test_output = """
  216.8125 MB /   1.00 sec = 1817.8571 Mbps    45 retrans    206 KB-cwnd
  217.6875 MB /   1.00 sec = 1826.5444 Mbps     0 retrans    227 KB-cwnd
  217.2500 MB /   1.00 sec = 1822.5107 Mbps     0 retrans    240 KB-cwnd
  215.2500 MB /   1.00 sec = 1805.6569 Mbps     0 retrans    248 KB-cwnd
  213.8750 MB /   1.00 sec = 1794.3001 Mbps     0 retrans    253 KB-cwnd
  218.1875 MB /   1.00 sec = 1829.2157 Mbps    45 retrans    196 KB-cwnd
  225.8125 MB /   1.00 sec = 1894.3302 Mbps     0 retrans    206 KB-cwnd
  224.7500 MB /   1.00 sec = 1885.1247 Mbps     0 retrans    216 KB-cwnd
  225.8750 MB /   1.00 sec = 1895.0459 Mbps     0 retrans    227 KB-cwnd
  218.0000 MB /   1.00 sec = 1828.4496 Mbps     0 retrans    237 KB-cwnd

 2197.0657 MB /  10.00 sec = 1842.3790 Mbps 8 %TX 90 %RX 90 retrans 237 KB-cwnd 0.50 msRTT
"""
    result = parse_output(test_output.split("\n"))
    pprint.PrettyPrinter(indent=4).pprint(result)


    test_output = """
   25.1572 MB /   1.00 sec =  211.0065 Mbps    62 / 25823 ~drop/pkt  0.24 ~%loss 4.8672 msMaxJitter
   25.2119 MB /   1.00 sec =  211.5030 Mbps   123 / 25940 ~drop/pkt  0.47 ~%loss 5.8452 msMaxJitter
   25.2695 MB /   1.00 sec =  211.9700 Mbps    13 / 25889 ~drop/pkt 0.05021 ~%loss 3.2322 msMaxJitter
   24.8672 MB /   1.00 sec =  208.5727 Mbps    60 / 25524 ~drop/pkt  0.24 ~%loss 4.8782 msMaxJitter
   25.4121 MB /   1.00 sec =  213.2157 Mbps    37 / 26059 ~drop/pkt  0.14 ~%loss 3.5862 msMaxJitter
   25.3184 MB /   1.00 sec =  212.3745 Mbps     0 / 25926 ~drop/pkt  0.00 ~%loss 3.0762 msMaxJitter
   24.3955 MB /   1.00 sec =  204.5846 Mbps  1135 / 26116 ~drop/pkt  4.35 ~%loss 37.2012 msMaxJitter
   25.4688 MB /   1.00 sec =  213.7010 Mbps     0 / 26080 ~drop/pkt  0.00 ~%loss 2.4122 msMaxJitter
   25.5693 MB /   1.00 sec =  214.4933 Mbps    16 / 26199 ~drop/pkt 0.06107 ~%loss 2.8272 msMaxJitter

  252.0586 MB /  10.00 sec =  211.4462 Mbps 99 %TX 50 %RX 1485 / 259593 drop/pkt 0.57 %loss 37.2012 msMaxJitter
"""
    result = parse_output(test_output.split("\n"))
    pprint.PrettyPrinter(indent=4).pprint(result)


    test_output = """
    68.7253 MB /  10.15 sec =   56.7987 Mbps 7 %TX 6 %RX 0 retrans 94 KB-cwnd 4.79 msRTT
"""
    result = parse_output(test_output.split("\n"))
    pprint.PrettyPrinter(indent=4).pprint(result)
