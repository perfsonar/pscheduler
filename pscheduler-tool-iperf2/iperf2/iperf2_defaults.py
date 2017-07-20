##########################################################
# Contains variables shared across iperf tool components
##########################################################

# Default time between packets (in seconds) if not specified by user
DEFAULT_DURATION = 10

# Default extra time to add on to test to wait for control packets, etc.
## iperf seems to add 3-3.5 seconds of fudge factor based on RTT during control session
DEFAULT_FUDGE_FACTOR = 4

# Default number of seconds before client will start to allow server time to boot
DEFAULT_WAIT_SLEEP = 1

# The default iperf2 control port
DEFAULT_SERVER_PORT = 5001

# The default location of the config file
CONFIG_FILE = '/etc/pscheduler/tool/iperf2.conf'

# Default install location of iperf2
DEFAULT_IPERF3_PATH = '/usr/bin/iperf'
