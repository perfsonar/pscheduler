###
# utility functions for the Ethr tool
#

import pscheduler
import configparser
from ethr_defaults import *

logger = pscheduler.Log(quiet=True)

##
# Read and return config file (or nothing if unable to)
def get_config():
    obj = {
        'server_port': DEFAULT_SERVER_PORT,
        'ethr_cmd': DEFAULT_ETHR_PATH
    }

    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
    except:
        logger.warning('Unable to read configuration file %s. Proceeding with defaults.' % CONFIG_FILE)
        return obj

    if config.has_option('ethr', 'ethr_cmd'):
        obj['ethr_cmd'] = config.get('ethr', 'ethr_cmd')

    if config.has_option('ethr', 'server_port'):
        obj['server_port'] = int(config.get('ethr', 'server_port'))

    return obj



def setup_time(rtt):

    '''Setup time: How long it takes for ethr to set up a test.  This is
    heavily influenced by the RTT between the hosts involved.
    Measurements taken as part of #838 indicate that every 50 ms of
    latency adds about one second.  Previously, this was done with a
    static fudge factor of four seconds, which has been set as the
    default.  RTT has no influence on how long it takes to run the
    test; ethr will stop after the specified number of seconds
    regardless of how much data was transferred.

    The rtt is an ISO8601 duration as a string.  If None, the default
    will be used.

    Returned value is seconds, minimum 1.
    '''

    delta = pscheduler.iso8601_as_timedelta(rtt or DEFAULT_LINK_RTT)
    rtt = pscheduler.timedelta_as_seconds(delta)

    return max(((rtt * 1000.0) / 50.0), 1.0)





if __name__ == '__main__':    
    config = get_config()
    print(config)
