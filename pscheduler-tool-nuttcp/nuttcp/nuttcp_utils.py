###
# utility functions for the nuttcp tool
#

import pscheduler
import ConfigParser
from nuttcp_defaults import *

logger = pscheduler.Log()

##
# Read and return config file (or nothing if unable to)
def get_config():
    config = None
    try:
        config = ConfigParser.ConfigParser()
        config.read(CONFIG_FILE)
    except:
        logger.warn("Unable to read configuration file %s. Proceeding with defaults." % CONFIG_FILE)
    
    return config

