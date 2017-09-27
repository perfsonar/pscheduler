#!/usr/bin/python

import pscheduler

def format_stream_output(stream_list, udp=False, summary=False):
    output = ""

    output += "%s%s%s" % ("{0:<15}".format("Interval"),
                          "{0:<15}".format("Throughput"),
                          "{0:<18}".format("Transferred")
    )

    if udp:
        output += "{0:<15}".format("Lost / Sent")
    else:
        output += "{0:<15}".format("Retransmits")

        if not summary:
            output += "{0:<15}".format("Current Window")
                            
    output += "\n"

    for block in stream_list:
        
        formatted_throughput = pscheduler.number_as_si(block["throughput-bits"], spaces=1)
        formatted_throughput += "bps"

        formatted_volume     = pscheduler.number_as_si(block["throughput-bytes"], spaces=1)
        formatted_volume    += "bytes"

        # tools like iperf3 report time with way more precision than we need to report,
        # so make sure it's cut down to 1 decimal spot
        start = "{0:.1f}".format(block["start"])
        end   = "{0:.1f}".format(block["end"])
       
        interval   = "{0:<15}".format("%s - %s" % (start, end))
        throughput = "{0:<15}".format(formatted_throughput)
        volume     = "{0:<18}".format(formatted_volume)

        jitter  = block.get("jitter")

        output += "%s%s%s" % (interval, throughput, volume)

        if udp:
            sent    = block.get("sent")
            lost    = block.get("lost")

            if sent == None:
                loss = "{0:<15}".format("Not Reported")
            else:
                if lost == None:
                    loss = "{0:<15}".format("%s sent" % sent)
                else:
                    loss = "{0:<15}".format("%s / %s" % (lost, sent))


            output += loss

        else:
            retrans = block.get('retransmits')

            if retrans == None:
                retransmits = "{0:<15}".format("Not Reported")
            else:
                retransmits = "{0:<15}".format(retrans)
    
            output += retransmits


            if not summary:
                window = block.get('tcp-window-size')

                if window == None:
                    tcp_window = "{0:<15}".format("Not Reported")
                else:
                    window = pscheduler.number_as_si(window, spaces=1) + "Bytes"
                    tcp_window = "{0:<15}".format(window)

                output += tcp_window


        jitter = block.get('jitter')
        if jitter != None:
            output += "{0:<20}".format("Jitter: %s ms" % jitter)

        if block.get('omitted'):
            output += " (omitted)"

        output += "\n"
        
    return output


if __name__ == "__main__":
    pass
