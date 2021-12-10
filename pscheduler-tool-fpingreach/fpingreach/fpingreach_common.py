#
# Common data for netreach
#

import os

DEFAULT_TIMEOUT = 'PT3S'

# Additional seconds of slop for fping to operate
FPING_RUN_SLOP = 1.0


def max_args_per_run(network):
    """
    Figure out how many arguments we can fit on a command line based
    on the address family
    """

    # Length of a single argument.
    if network.version == 4:
        arg_len = 16  # len('111.111.111.111 ')
    elif network.version == 6:
        arg_len = 50  # len('0000:0000:0000:0000:0000:0000:0000:0000 ')
    else:
        assert False, "Unsupported address family"

    # Chop 200 from the maximum for non-address arguments
    max_args_per_run = int((os.sysconf('SC_ARG_MAX') - 200) / arg_len)

    return int((os.sysconf('SC_ARG_MAX') - 200) / arg_len)
