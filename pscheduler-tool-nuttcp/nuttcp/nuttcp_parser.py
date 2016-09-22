import re
import pscheduler
import pprint
import json
import sys

logger = pscheduler.Log()

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
        test = re.match('^.*(\d+)\.\d+ sec \=\s*(\d+(\.\d+)?) (\S)bps\s*(\d+) retrans(\s*(\d+)\s*(\S)\S\-cwnd)?', line)
        if test:
            spacing = int(test.group(1))
            value   = test.group(2)
            si      = test.group(4)
            retrans = int(test.group(5))
            cwnd    = test.group(7)
            cwnd_si = test.group(8)

            value = pscheduler.si_as_number("%s%s" % (value, si))
            cwnd  = pscheduler.si_as_number("%s%s" % (cwnd, cwnd_si))

            data = {
                "start": current_interval_start,
                "end": current_interval_start + spacing,
                "stream-id": 1, # nuttcp won't report separate streams as best as I can tell, so just fudge it
                "throughput-bits": value,
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
        # 25.1572 MB /   1.00 sec =  211.0065 Mbps    62 / 25823 ~drop/pkt  0.24 ~%loss 4.8672 msMaxJitter
        test = re.match('^.*(\d+)\.\d+ sec \=\s*(\d+(\.\d+)?) (\S)bps\s*(\d+) / (\d+) ~drop/pkt\s*(\d+\.\d+) ~%loss\s*(\d+\.\d+) msMaxJitter', line)
        if test:
            spacing = int(test.group(1))
            value   = test.group(2)
            si      = test.group(4)
            lost    = int(test.group(5))
            sent    = int(test.group(6))
            loss    = test.group(7)
            jitter  = float(test.group(8))

            value = pscheduler.si_as_number("%s%s" % (value, si))

            data = {
                "start": current_interval_start,
                "end": current_interval_start + spacing,
                "stream-id": 1, # nuttcp won't report separate streams as best as I can tell, so just fudge it
                "throughput-bits": value,
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
        test = re.match('^.*(\d+)\.\d+ sec = (\d+(\.\d+)?) (\S)bps \d+ %TX \d+ %RX (\d+) retrans(\s*(\d+)\s*(\S)\S\-cwnd)?', line)
        if test:
            duration = int(test.group(1))
            value    = test.group(2)
            si       = test.group(4)
            retrans  = test.group(5)
            cwnd     = test.group(7)
            cwnd_si  = test.group(8)
           
            value = pscheduler.si_as_number("%s%s" % (value, si))
            cwnd  = pscheduler.si_as_number("%s%s" % (cwnd, cwnd_si))

            summary_view = {
                "start": 0,
                "end": duration,
                "stream-id": 1, # nuttcp won't report separate streams as best as I can tell, so just fudge it
                "throughput-bits": value,
                "tcp-window-size": cwnd,
                "retransmits": retrans
                }


        # Example UDP summary line
        #   252.0586 MB /  10.00 sec =  211.4462 Mbps 99 %TX 50 %RX 1485 / 259593 drop/pkt 0.57 %loss 37.2012 msMaxJitter
        test = re.match('^.*(\d+)\.\d+ sec \=\s*(\d+(\.\d+)?) (\S)bps\s*(\d+) %TX (\d+) %RX (\d+) / (\d+) drop/pkt\s*(\d+\.\d+) %loss\s*(\d+\.\d+) msMaxJitter', line)
        if test:
            duration = int(test.group(1))
            value    = test.group(2)
            si       = test.group(4)
            lost     = int(test.group(5))
            sent     = int(test.group(6))
            loss     = test.group(7)
            jitter   = float(test.group(8))

            value = pscheduler.si_as_number("%s%s" % (value, si))

            summary_view = {
                "start": 0,
                "end": duration,
                "stream-id": 1, # nuttcp won't report separate streams as best as I can tell, so just fudge it
                "throughput-bits": value,
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
