#
# Text-related utilities
#

import os
import string
import sys
import textwrap

# This is not available on Debian 9, so if it isn't, roll our own.
# DEBIAN: Go back to using secrets directly when Debian 9 goes away.
try:

    import secrets
    SECRETS_CHOICE = secrets.choice
    SECRETS_RANDBELOW = secrets.randbelow
    
except ImportError:

    import random

    def secrets_randbelow(below):
        # TODO: Implement this.
        return random.randint(0, below-1)

    def secrets_choice(charset):
        # TODO: Implement this.
        return charset[secrets_randbelow(len(charset)-1)]


    SECRETS_CHOICE = secrets_choice
    SECRETS_RANDBELOW = secrets_randbelow


def terminal_size():
    """
    Return the number of terminal columns and rows, defaulting to
    80x24 if the standard output is not a TTY.

    NOTE THAT THIS ONLY WORKS ON UNIX.
    """
    if sys.stdout.isatty():
        # PORT: This only works on Unix.
        rows, columns = [int(x) for x in
                         os.popen('stty size', 'r').read().split()]
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

    wrapped = textwrap.wrap(text, width - len(prefix))
    leader = " " * (len(prefix) + indent)
    lines = [wrapped.pop(0)]
    lines.extend(["%s%s" % (leader, line)
                  for line in wrapped])

    return "%s%s" % (prefix, "\n".join(lines))



def indent(
        text,      # Text to indent
        char=' ',  # Character to use in indenting
        indent=2   # Repeats of char
):
    """
    Indent single- or multi-lined text.
    """
    prefix = char * indent
    return "\n".join([prefix + s for s in text.split("\n")])




def random_string(length, randlength=False, safe=False):
    """Return a random string of length 'length'

    Set 'randlength' True to pick a random length between half of
    'length' and 'length'.

    Set 'safe' True to onlu include alphanumeric characters.
    """

    if randlength:
        length = length - SECRETS_RANDBELOW(int(length/2))

    charset = string.digits + string.ascii_letters
    if not safe:
        charset += string.punctuation
    charset_len = len(charset)

    characters = [
        SECRETS_CHOICE(charset)
        for _ in range(0, length)
    ]

    return "".join(characters)
