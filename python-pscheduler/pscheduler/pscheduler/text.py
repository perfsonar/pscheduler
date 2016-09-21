#
# Text-related utilities
#

import os
import sys
import textwrap

def terminal_size():
    """
    Return the number of terminal columns and rows, defaulting to
    80x24 if the standard output is not a TTY.

    NOTE THAT THIS ONLY WORKS ON UNIX.
    """
    if sys.stdout.isatty():
        # TODO: This only works on Unix.
        rows, columns = [ int(x) for x in
                          os.popen('stty size', 'r').read().split() ]
    else:
        rows = 24
        columns = 80

    return rows, columns

def prefixed_wrap(prefix, text, width=None, indent=0):
    """
    Wrap text with a prefix and optionally indenting the second and
    later lines.  If the width is None, the terminal size will be
    used.  (See terminal_size() for details.)
    """

    if width is None:
        height, width = terminal_size()

    wrapped = textwrap.wrap(text, width-len(prefix))
    leader = " " * (len(prefix) + indent)
    lines = [ wrapped.pop(0) ]
    lines.extend([ "%s%s" % (leader, line)
                   for line in wrapped])

    return "%s%s" % (prefix, "\n".join(lines))
