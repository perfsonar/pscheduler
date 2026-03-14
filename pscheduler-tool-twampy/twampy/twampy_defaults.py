##########################################################
# Contains variables shared across twampy tool components
##########################################################

# Version of the latency schema used
LATENCY_SCHEMA_VERSION = 1

# Default time between packets (in seconds) if not specified by user
DEFAULT_PACKET_INTERVAL = 0.1

# Default number of packets if not specified by user
DEFAULT_PACKET_COUNT = 100

# Default time to wait for packet (in seconds) before declaring lost
DEFAULT_PACKET_TIMEOUT = 0

# Default extra time to add on to test to wait for control packets, etc.
DEFAULT_FUDGE_FACTOR = 10

# Default number of seconds before client will start
DEFAULT_CLIENT_SLEEP = 1

# Default STAMP reflector port (IANA assigned for STAMP)
DEFAULT_STAMP_PORT = 862

# Time scale for millisecond conversions
TIME_SCALE = 0.001

# Number of digits to round delay buckets
DELAY_BUCKET_DIGITS = 2
DELAY_BUCKET_FORMAT = '%.2f'

# Number of digits to round clock error
CLOCK_ERROR_DIGITS = 2

# Default raw output setting
DEFAULT_RAW_OUTPUT = False

# Default bucket width (in ms)
DEFAULT_BUCKET_WIDTH = TIME_SCALE

# Config file constants
CONFIG_FILE = '/etc/pscheduler/tool/twampy.conf'
CONFIG_SECTION = 'twampy'
CONFIG_OPT_TWAMPY_CMD = 'twampy_cmd'
