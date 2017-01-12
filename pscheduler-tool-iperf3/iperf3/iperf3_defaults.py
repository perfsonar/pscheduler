##########################################################
# Contains variables shared across iperf3 tool components
##########################################################

# Default test time
DEFAULT_DURATION = 10

# Default extra time to add on to test to wait for control packets, etc.
## iperf seems to add 3-3.5 seconds of fudge factor based on RTT during control session
DEFAULT_FUDGE_FACTOR = 4

# Default number of seconds before client will start to allow server time to boot
DEFAULT_WAIT_SLEEP = 3

# The default iperf3 control port
DEFAULT_SERVER_PORT = 5201

# The default location of the config file
CONFIG_FILE = '/etc/pscheduler/tool/iperf3.conf'

# Default install location of iperf3
DEFAULT_IPERF3_PATH = '/usr/bin/iperf3'
