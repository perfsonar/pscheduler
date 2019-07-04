###
# utility functions for the iperf3 tool
#

import pscheduler
import ConfigParser
from iperf3_defaults import *

logger = pscheduler.Log(quiet=True)

##
# Read and return config file (or nothing if unable to)
def get_config():
    obj = {
        "server_port": DEFAULT_SERVER_PORT,
        "iperf3_cmd": DEFAULT_IPERF3_PATH
    }

    try:
        config = ConfigParser.ConfigParser()
        config.read(CONFIG_FILE)
    except:
        logger.warning("Unable to read configuration file %s. Proceeding with defaults." % CONFIG_FILE)
        return obj

    if config.has_option("iperf3", "iperf3_cmd"):
        obj["iperf3_cmd"] = config.get("iperf3", "iperf3_cmd")

    if config.has_option("iperf3", "server_port"):
        obj["server_port"] = int(config.get("iperf3", "server_port"))

    return obj



def setup_time(rtt):

    """Setup time: How long it takes for iperf3 to set up a test.  This is
    heavily influenced by the RTT between the hosts involved.
    Measurements taken as part of #838 indicate that every 50 ms of
    latency adds about one second.  Previously, this was done with a
    static fudge factor of four seconds, which has been set as the
    default.  RTT has no influence on how long it takes to run the
    test; iperf3 will stop after the specified number of seconds
    regardless of how much data was transferred.

    The rtt is an ISO8601 duration as a string.  If None, the default
    will be used.

    Returned value is seconds, minimum 1.
    """

    delta = pscheduler.iso8601_as_timedelta(rtt or DEFAULT_LINK_RTT)
    rtt = pscheduler.timedelta_as_seconds(delta)

    return max(((rtt * 1000.0) / 50.0), 1.0)



if __name__ == "__main__":
    
    config = get_config()
    print config
