##########################################################
# Contains variables shared across perftest tool components
##########################################################

# Default test time
DEFAULT_DURATION = 10

# Default link RTT in seconds.  This is a rough approximation of RTT
# for the longest possible terrestrial path.
DEFAULT_LINK_RTT = 'PT0.200S'


# Default number of seconds before client will start to allow server time to boot
DEFAULT_WAIT_SLEEP = 3

# Default number of seconds to let the server spin down
DEFAULT_SERVER_SHUTDOWN = 2

# The default perftest control port
DEFAULT_SERVER_PORT = 18515

# The default location of the config file
CONFIG_FILE = '/etc/pscheduler/tool/perftest.conf'

# Default install location of binaries
DEFAULT_IB_WRITE_BW_PATH = '/usr/bin/ib_write_bw'
