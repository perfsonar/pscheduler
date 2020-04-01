##########################################################
# Contains variables shared across iperf tool components
##########################################################

# Default time between packets (in seconds) if not specified by user
DEFAULT_DURATION = 10

# Default link RTT in seconds.  This is a rough approximation of RTT
# for the longest possible terrestrial path.
DEFAULT_LINK_RTT = "PT0.200S"

# Default number of seconds before client will start to allow server time to boot
DEFAULT_WAIT_SLEEP = 1

# How long to wait for the server to shut down
DEFAULT_SERVER_SHUTDOWN = 1

# The default iperf2 control port
DEFAULT_SERVER_PORT = 5001

# The default location of the config file
CONFIG_FILE = '/etc/pscheduler/tool/iperf2.conf'

# Default install location of iperf2
DEFAULT_IPERF2_PATH = '/usr/bin/iperf'
