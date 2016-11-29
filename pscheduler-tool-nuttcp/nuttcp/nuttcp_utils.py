###
# utility functions for the nuttcp tool
#

import pscheduler
import ConfigParser
from nuttcp_defaults import *

logger = pscheduler.Log(quiet=True)

##
# Read and return config file (or nothing if unable to)
def get_config():
    obj = {
        "server_port": DEFAULT_SERVER_PORT,
        "nuttcp_cmd": DEFAULT_NUTTCP_PATH,
        "data_port_start": DEFAULT_DATA_PORT_START
    }

    try:
        config = ConfigParser.ConfigParser()
        config.read(CONFIG_FILE)
    except:
        logger.warn("Unable to read configuration file %s. Proceeding with defaults." % CONFIG_FILE)
        return obj

    if config.has_option("nuttcp", "nuttcp_cmd"):
        obj["nuttcp_cmd"] = config.get("nuttcp", "nuttcp_cmd")

    if config.has_option("nuttcp", "server_port"):
        obj["server_port"] = int(config.get("nuttcp", "server_port"))

    if config.has_option("nuttcp", "data_port_start"):
        obj["server_port"] = int(config.get("nuttcp", "data_port_start"))

    return obj


if __name__ == "__main__":
    
    config = get_config()
    print config


