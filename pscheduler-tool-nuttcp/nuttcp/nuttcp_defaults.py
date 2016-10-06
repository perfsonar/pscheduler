##########################################################
# Contains variables shared across nuttcp tool components
##########################################################

# Default test time
DEFAULT_DURATION = 10

# Default extra time to add on to test to wait for control packets, etc.
DEFAULT_FUDGE_FACTOR = 4

# Default number of seconds before client will start to allow server time to boot
DEFAULT_WAIT_SLEEP = 2

# The default nuttcp ports
DEFAULT_SERVER_PORT     = 5000
DEFAULT_DATA_PORT_START = 5101

# The default location of the config file
CONFIG_FILE = '/etc/pscheduler/tool/nuttcp.conf'

# Default install location of nuttcp
DEFAULT_NUTTCP_PATH = '/usr/bin/nuttcp'
