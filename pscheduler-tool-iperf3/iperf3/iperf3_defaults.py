##########################################################
# Contains variables shared across iperf3 tool components
##########################################################

# Default test time
DEFAULT_DURATION = 10

# Default link RTT in seconds.  This is a rough approximation of RTT
# for the longest possible terrestrial path.
DEFAULT_LINK_RTT = "PT0.200S"


# Default number of seconds before client will start to allow server time to boot
DEFAULT_WAIT_SLEEP = 3

# Default number of seconds to let the server spin down
DEFAULT_SERVER_SHUTDOWN = 2

# The default iperf3 control port
DEFAULT_SERVER_PORT = 5201

# The default location of the config file
CONFIG_FILE = '/etc/pscheduler/tool/iperf3.conf'

# Default install location of iperf3
DEFAULT_IPERF3_PATH = '/usr/bin/iperf3'
