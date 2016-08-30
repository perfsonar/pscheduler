def format_si(number, places=2):
    number = float(number)
    if number > 10**9:
        return ("{0:.%sf} G" % places).format(number / 10**9)

    if number > 10**6:
        return ("{0:.%sf} M" % places).format(number / 10**6)

    if number > 10**3:
        return ("{0:.%sf} K" % places).format(number / 10**3)

    return ("{0:.%sf}" % places).format(number)    

def format_stream_output(stream_list, udp=False):
    output = ""

    output += "%s%s" % ("{0:<15}".format("Interval"),
                        "{0:<15}".format("Throughput")
                        )

    if udp:
        output += "{0:<15}".format("Sent/Lost")
    else:
        output += "{0:<15}".format("Retransmits")
                            
    output += "\n"

    for block in stream_list:
        
        formatted_throughput = format_si(block["throughput-bits"])
        formatted_throughput += "bps"

        # tools like iperf3 report time with way more precision than we need to report,
        # so make sure it's cut down to 1 decimal spot
        start = "{0:.1f}".format(block["start"])
        end   = "{0:.1f}".format(block["end"])
       
        interval   = "{0:<15}".format("%s - %s" % (start, end))
        throughput = "{0:<15}".format(formatted_throughput)

        jitter  = block.get("jitter")

        output += "%s%s" % (interval, throughput)

        if udp:
            sent    = block.get("sent")
            lost    = block.get("lost")

            if sent == None:
                loss = "{0:<15}".format("Not Reported")
            else:
                loss = "{0:<15}".format("%s / %s" % (sent, lost))

            output += loss

        else:
            retrans = block.get('retransmits')

            if retrans == None:
                retransmits = "{0:<15}".format("Not Reported")
            else:
                retransmits = "{0:<15}".format(retrans)
    
            output += retransmits


        if block.get('omitted'):
            output += " (omitted)"

        output += "\n"
        
    return output


if __name__ == "__main__":

    print format_si(10 ** 12)
    print format_si(10 ** 4)
    print format_si(10 ** 7)
    print format_si(10 ** 9)
