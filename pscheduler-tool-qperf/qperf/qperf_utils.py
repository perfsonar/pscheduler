###
# utility functions for the qperf tool
#

import pscheduler
import configparser
import qperf_defaults

logger = pscheduler.Log(quiet=True)

##
# Read and return config file (or nothing if unable to)
def get_config():
    obj = {
        'port': qperf_defaults.DEFAULT_PORT,
        'data_port': qperf_defaults.DEFAULT_DATA_PORT,
        'qperf_cmd': qperf_defaults.DEFAULT_QPERF_PATH,
        'duration': qperf_defaults.DEFAULT_DURATION,
        'link_rtt': qperf_defaults.DEFAULT_LINK_RTT,
        'wait_sleep': qperf_defaults.DEFAULT_WAIT_SLEEP,
        'server_shutdown': qperf_defaults.DEFAULT_SERVER_SHUTDOWN,
    }

    try:
        config = configparser.ConfigParser()
        config.read(qperf_defaults.CONFIG_FILE)
    except:
        logger.warning(f'Unable to read configuration file {qperf_defaults.CONFIG_FILE}. Proceeding with defaults.')
        return obj

    options = [
        'qperf_cmd',
        'port',
        'data_port',
        'duration',
        'link_rtt',
        'wait_sleep',
        'server_shutdown'
    ]

    for option in options:
        if config.has_option('qperf', option):
            obj[option] = config.get('qperf', option)

    return obj



def setup_time(rtt):
    delta = pscheduler.iso8601_as_timedelta(rtt or qperf_defaults.DEFAULT_LINK_RTT)
    rtt = pscheduler.timedelta_as_seconds(delta)

    return max(((rtt * 1000.0) / 50.0), 1.0)



if __name__ == "__main__":
    
    config = get_config()
    print(config)
