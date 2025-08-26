#
# Utilities
#

import os
import stat

def file_ok(path):
    """
    Determine if a local file is safe to read and return a list of
    reasons why not.
    """

    reasons = []

    # No relative paths
    if list(filter(lambda p: p in ['.', '..'], path.split(os.sep))):
        reasons.append('Invalid path')

    real_path = os.path.realpath(path)

    # No peeking at system stuff
    for forbidden in [ '/dev/', '/etc/', '/media/', '/proc/', '/run/', '/srv/', '/sys/', '/var/' ]:
        if real_path.startswith(forbidden):
            reasons.append('Invalid path')
            break

    # No looking at anything but plain or missing files.  This will be
    # double-checked at runtime.
    try:
        filestat = os.stat(real_path)
        if not stat.S_ISREG(filestat.st_mode):
            reasons.append('Invalid path')
    except (FileNotFoundError, NotADirectoryError):
        pass

    # The set/list conversion removes duplicates
    return list(set(reasons))
