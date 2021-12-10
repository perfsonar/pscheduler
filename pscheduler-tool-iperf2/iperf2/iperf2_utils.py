###
# utility functions for the iperf2 tool
#

import pscheduler
import configparser
from iperf2_defaults import *

logger = pscheduler.Log(quiet=True)

##
# Read and return config file (or nothing if unable to)
def get_config():
    obj = {
        "server_port": DEFAULT_SERVER_PORT,
        "iperf2_cmd": DEFAULT_IPERF2_PATH
    }

    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
    except:
        logger.warning("Unable to read configuration file %s. Proceeding with defaults." % CONFIG_FILE)
        return obj

    if config.has_option("iperf2", "iperf2_cmd"):
        obj["iperf2_cmd"] = config.get("iperf2", "iperf2_cmd")

    if config.has_option("iperf2", "server_port"):
        obj["server_port"] = int(config.get("iperf2", "server_port"))

    return obj


def setup_time(rtt):

    """Setup time: How long it takes for iperf2 to set up a test.  This is
    heavily influenced by the RTT between the hosts involved.
    Measurements taken as part of #868 indicate that every 50 ms of
    latency adds about one second.  Previously, this was done with a
    static fudge factor of four seconds, which has been set as the
    default.  RTT has no influence on how long it takes to run the
    test; iperf2 will stop after the specified number of seconds
    regardless of how much data was transferred.
    The rtt is an ISO8601 duration as a string.  If None, the default
    will be used.
    Returned value is seconds, minimum 1.
    """

    delta = pscheduler.iso8601_as_timedelta(rtt or DEFAULT_LINK_RTT)
    rtt = pscheduler.timedelta_as_seconds(delta)

    # TODO: This is the same as what we do for iperf3 but may need tuning.
    return max(((rtt * 1000.0) / 50.0), 1.0)


if __name__ == "__main__":
    
    config = get_config()
    print(config)
