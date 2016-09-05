##########################################################
# Contains variables shared across iperf3 tool components
##########################################################

# Default test time
DEFAULT_DURATION = 10

# Default extra time to add on to test to wait for control packets, etc.
## BWCTL needs a lot becuause it takes time to schedule test
DEFAULT_FUDGE_FACTOR = 60

# Default number of seconds before client will start to allow server time to boot
DEFAULT_WAIT_SLEEP = 1

# The default iperf3 control port
DEFAULT_SERVER_PORT = 5201
