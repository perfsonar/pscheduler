##########################################################
# Contains variables shared across powstream tool components
##########################################################

#Version of the latency schema used
LATENCY_SCHEMA_VERSION = 1 

# Default time between packets (in seconds) if not specified by user
DEFAULT_PACKET_INTERVAL = .1

# Default number of packets if not specified by user
DEFAULT_PACKET_COUNT = 600

# Default duration for test. Defaults to 100 years.
DEFAULT_DURATION = "PT24H"

# Default number of seconds before checking if powstream booted properly
DEFAULT_CLIENT_SLEEP = 3

# Default number of seconds to wait before trying to restart powstream when it fails to start
DEFAULT_RESTART_SLEEP = 30

# Default number of seconds to wait before looking for a result again
DEFAULT_RETRY_SLEEP = 5

# The maximum number of tries to get a result before giving up on powstream. 
DEFAULT_MAX_RETRIES = 24

# Convenience value, changing this alters nothing except error messages
# The number of seconds pscheduler will wait for a result before declating powstream dead
DEFAULT_MAX_WAIT_TIME = DEFAULT_RETRY_SLEEP * DEFAULT_MAX_RETRIES

# The default OWAMPD control port
DEFAULT_OWAMPD_PORT = 861

# The default owampd contol port range
DEFAULT_OWAMPD_CTRL_PORTS = list(range(5601, 5900))

# The default owampd data port range
DEFAULT_OWAMPD_DATA_PORTS = list(range(8760, 9960))

# Use for millisecond conversions
TIME_SCALE = .001 

#Number of times it will try to start powstream before giving-up
MAX_POWSTREAM_START_ATTEMPTS = 20

#constants for working with config file
CONFIG_FILE = '/etc/pscheduler/tool/powstream.conf'
CONFIG_SECTION = 'powstream'
CONFIG_OPT_POWSTREAM_CMD = 'powstream_cmd'
CONFIG_OPT_OWSTATS_CMD = 'owstats_cmd'
CONFIG_OPT_PKILL_CMD = 'pkill_cmd'
CONFIG_OPT_LOG_LEVEL = 'log_level'
CONFIG_OPT_DATA_DIR = 'data_dir'
CONFIG_OPT_KEEP_DATA_FILES = 'keep_data_files'
CONFIG_OPT_CTRL_PORTS = 'control_ports'
#CONFIG_OPT_USE_EXISTING_OWAMPD = 'use_existing_owampd'
#CONFIG_OPT_DATA_PORTS = 'data_ports'