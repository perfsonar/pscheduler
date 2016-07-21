def format_si(number, places=2):
    if number > 10**9:
        return ("{0:.%sf} G" % places).format(number / 10**9)

    if number > 10**6:
        return ("{0:.%sf} M" % places).format(number / 10**6)

    if number > 10**3:
        return ("{0:.%sf} K" % places).format(number / 10**3)

    return ("{0:.%sf}" % places).format(number)    

def format_stream_output(stream_list):
    output = ""

    output += "%s%s%s%s\n" % ("{0:<15}".format("Interval"),
                              "{0:<15}".format("Throughput"),
                              "{0:<15}".format("Sent/Lost"),
                              "{0:<15}".format("Jitter"))
    
    for block in stream_list:
        
        formatted_throughput = format_si(block["throughput-bits"])
        formatted_throughput += "bps"
        
        interval   = "{0:<15}".format("%s - %s" % (block["start"], block["end"]))
        throughput = "{0:<15}".format(formatted_throughput)
        loss       = "{0:<15}".format("%s / %s" % (block["sent"], block["lost"]))
        jitter     = "{0:<15}".format(block["jitter"])
        
        output += "%s%s%s%s\n" % (interval, throughput, loss, jitter)
        
    return output


if __name__ == "__main__":

    print format_si(10 ** 12)
    print format_si(10 ** 4)
    print format_si(10 ** 7)
    print format_si(10 ** 9)
