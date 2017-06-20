###
# utility functions for the iperf2 tool
#

import pscheduler
import ConfigParser
from iperf2_defaults import *

logger = pscheduler.Log(quiet=True)

##
# Read and return config file (or nothing if unable to)
def get_config():
    obj = {
        "server_port": DEFAULT_SERVER_PORT,
        "iperf2_cmd": DEFAULT_IPERF3_PATH
    }

    try:
        config = ConfigParser.ConfigParser()
        config.read(CONFIG_FILE)
    except:
        logger.warning("Unable to read configuration file %s. Proceeding with defaults." % CONFIG_FILE)
        return obj

    if config.has_option("iperf2", "iperf2_cmd"):
        obj["iperf2_cmd"] = config.get("iperf2", "iperf2_cmd")

    if config.has_option("iperf2", "server_port"):
        obj["server_port"] = int(config.get("iperf2", "server_port"))

    return obj


if __name__ == "__main__":
    
    config = get_config()
    print config
