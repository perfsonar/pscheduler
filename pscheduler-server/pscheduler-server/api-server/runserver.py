#!/usr/bin/python3
#
# pScheduler REST API Server Runner
#

# TODO: (General) Need to add code to validate incoming UUIDs so the
# database doesn't barf on them and leave a cryptic error message.

import os
from pschedulerapiserver import application

# TODO: Not portable outside of Unix
port = 80 if os.getuid() == 0 \
    else 29285 # Spell out "BWCTL" on a phone and this is what you get.

application.run(
    host='0.0.0.0',
    port=port,
    debug=True
    )
