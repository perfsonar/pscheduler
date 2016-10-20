##########################################################
# Contains variables shared across owping tool components
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
## owping seems to add 3-3.5 seconds of fudge factor based on RTT during control session
DEFAULT_FUDGE_FACTOR = 10

# Default number of seconds before client will start to allow server time to boot
DEFAULT_CLIENT_SLEEP = 1

# Default number of seconds before client will start to allow server time to boot
DEFAULT_EARLY_SERVER_STOP = 2

# The default OWAMPD control port
DEFAULT_OWAMPD_PORT = 861

# The default owampd contol port range
DEFAULT_OWAMPD_CTRL_PORTS = range(5601, 5900)

# The default owampd data port range
DEFAULT_OWAMPD_DATA_PORTS = range(8760, 9960)

#constants for working with config file
CONFIG_FILE = '/etc/pscheduler/tool/owping.conf'
CONFIG_SECTION = 'owping'
CONFIG_OPT_OWPING_CMD = 'owping_cmd'
CONFIG_OPT_DISABLE_SERVER = 'disable_server'
#CONFIG_OPT_USE_EXISTING_OWAMPD = 'use_existing_owampd'
CONFIG_OPT_CTRL_PORTS = 'control_ports'
#CONFIG_OPT_DATA_PORTS = 'data_ports'