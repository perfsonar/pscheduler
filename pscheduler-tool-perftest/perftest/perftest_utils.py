###
# utility functions for the perftest tool
#

import pscheduler
import configparser
from perftest_defaults import *

logger = pscheduler.Log(prefix='tool-perftest', quiet=True)

def get_config():
    obj = {
        'server_port': DEFAULT_SERVER_PORT,
        'ib_write_bw_cmd': DEFAULT_IB_WRITE_BW_PATH
    }

    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
    except:
        logger.warning(f'Unable to read configuration file {CONFIG_FILE}. Proceeding with defaults.')
        return obj

    if config.has_option('perftest', 'ib_write_bw_cmd'):
        obj['ib_write_bw_cmd'] = config.get('perftest', 'ib_write_bw_cmd')

    if config.has_option('perftest', 'server_port'):
        obj['server_port'] = int(config.get('perftest', 'server_port'))

    return obj


def setup_time(rtt):
    delta = pscheduler.iso8601_as_timedelta(rtt or DEFAULT_LINK_RTT)
    rtt = pscheduler.timedelta_as_seconds(delta)
    return max(((rtt * 1000.0) / 50.0), 1.0)

if __name__ == '__main__':
    config = get_config()
    print(config)
