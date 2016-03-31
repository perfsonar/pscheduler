##########################################################
# Contains variables shared across owping tool components
##########################################################

# Default time between packets (in seconds) if not specified by user
DEFAULT_PACKET_INTERVAL = .1

# Default number of packets if not specified by user
DEFAULT_PACKET_COUNT = 100

# Default time to wait for packet (in seconds) before declaring lost
DEFAULT_PACKET_TIMEOUT = 0

# Default extra time to add on to test to wait for control packets, etc.
## owping seems to add 3-3.5 seconds of fudge factor based on RTT during control session
DEFAULT_FUDGE_FACTOR = 4

# Default number of seconds before client will start to allow server time to boot
DEFAULT_CLIENT_SLEEP = 1

# Default number of seconds before client will start to allow server time to boot
DEFAULT_EARLY_SERVER_STOP = 2

# The default OWAMPD control port
DEFAULT_OWAMPD_PORT = 861