#
# Text-related utilities
#

import jinja2
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
        return random.randint(0, below-1)

    def secrets_choice(charset):
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



def jinja2_format(template, info, strip=True):
    """
    Format a string template and dict using Jinja2.  Adds an
    error('msg') function that makes this function raise a
    RuntimeError (e.g.: {{ error('Something went wrong') }}) and an
    unspec(var) to return var or 'Not Specified' if it isn't defined.
    """
    assert isinstance(template, str)
    assert isinstance(info, dict)

    def error_helper(message):
        raise RuntimeError(message)

    HEADER = '''
{% macro unspec(arg) -%}
{{ arg if arg is defined else 'Not Specified' }}
{%- endmacro %}
    '''

    def unspec_helper(value):
        if value:
            return value
        return 'Unspecified'

    j2 = jinja2.Environment()
    j2.globals.update(
        error=error_helper,
        unspec=unspec_helper
        )
    finished = j2.from_string(HEADER + template).render(info)

    return finished.strip() if strip else finished
