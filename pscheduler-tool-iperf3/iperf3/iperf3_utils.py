###
# utility functions for the iperf3 tool
#

import pscheduler
import ConfigParser
from iperf3_defaults import *

logger = pscheduler.Log()

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
        logger.warn("Unable to read configuration file %s. Proceeding with defaults." % CONFIG_FILE)
        return obj

    if config.has_option("iperf3", "iperf3_cmd"):
        obj["iperf3_cmd"] = config.get("iperf3", "iperf3_cmd")

    if config.has_option("iperf3", "server_port"):
        obj["server_port"] = int(config.get("iperf3", "server_port"))

    return obj


if __name__ == "__main__":
    
    config = get_config()
    print config
