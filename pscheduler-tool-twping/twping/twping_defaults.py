##########################################################
# Contains variables shared across twping tool components
##########################################################

#Version of the latency schema used
LATENCY_SCHEMA_VERSION = 1 

# Default time between packets (in seconds) if not specified by user
DEFAULT_PACKET_INTERVAL = .1

# Default number of packets if not specified by user
DEFAULT_PACKET_COUNT = 100

# Default time to wait for packet (in seconds) before declaring lost
DEFAULT_PACKET_TIMEOUT = 0

# Default extra time to add on to test to wait for control packets, etc.
## twping seems to add 3-3.5 seconds of fudge factor based on RTT during control session
DEFAULT_FUDGE_FACTOR = 10

# Default number of seconds before client will start to allow server time to boot
DEFAULT_CLIENT_SLEEP = 1

# Default number of seconds before client will start to allow server time to boot
DEFAULT_EARLY_SERVER_STOP = 2

# The default TWAMPD control port
DEFAULT_TWAMPD_PORT = 862

# The default twampd contol port range
DEFAULT_TWAMPD_CTRL_PORTS = list(range(5601, 5900))

# The default twampd data port range
DEFAULT_TWAMPD_DATA_PORTS = list(range(8760, 9960))

#constants for working with config file
CONFIG_FILE = '/etc/pscheduler/tool/twping.conf'
CONFIG_SECTION = 'twping'
CONFIG_OPT_TWPING_CMD = 'twping_cmd'
CONFIG_OPT_DISABLE_SERVER = 'disable_server'
#CONFIG_OPT_USE_EXISTING_TWAMPD = 'use_existing_twampd'
CONFIG_OPT_CTRL_PORTS = 'control_ports'
#CONFIG_OPT_DATA_PORTS = 'data_ports'
