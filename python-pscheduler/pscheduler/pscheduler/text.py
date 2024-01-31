#
# Text-related utilities
#

import jinja2
import os
import string
import sys
import textwrap

from .exitstatus import fail
from .exitstatus import succeed
from .psjson import json_load
from .psjson import json_strip_hyphens

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
    Format a string template and dict using Jinja2.

    This functions Adds the following utilities to Jinja2:

    error(msg) - Raises a RuntimeError (e.g.: {{ error('Something went
    wrong') }})

    siformat(val) - Formats a number as an SI number (e.g., 1000 -> 1k).

    unspec(var) - Returns return var or 'Not Specified' if it isn't
    defined.
    """
    assert isinstance(template, str)
    assert isinstance(info, dict)

    def error_helper(message):
        raise RuntimeError(message)

    HEADER = '''
{%- macro siformat(arg) -%}
{{ arg | filesizeformat | replace('B','') }}
{%- endmacro -%}
{% macro unspec(arg) -%}
{{ arg if arg is defined else 'Not Specified' }}
{%- endmacro -%}
    '''

    j2 = jinja2.Environment()
    j2.globals.update(
        error=error_helper
        )
    finished = j2.from_string(HEADER + template).render(info)

    return finished.strip() if strip else finished


def _format_method(template,
                   mime_type=None,
                   max_schema=None,
                   pick=None,
                   validator=None
                   ):
    """Carry out most of what the spec-format and result-format text
    plugin methods do:

     - Load a JSON file from standard input
     - Check it against a maximum schema value in max_schema
     - Validate the structure of the JSON using a validator function
     - Format it with a Jinja2 template
     - Print the result to standard output and exit successfully
     - Fail with a message to standard error if any step along the way fails

    Arguments:

    template - A Jinja2 template to be applied to the input data.  See
    'Template Notes' below.

    mime_type - Passed to the template as the variable _mime_type,
    used in making decisions about formatting.  If None, it will be
    taken from sys.argv[1] or defaulted to 'text/plain'.

    max_schema - The maximum value for the input's 'schema' pair or
    None (the default) to skip checking.

    pick - A function to pick out the desired part of the input for
    validation.  For result-format methods, the usual value would be
    lambda v: v['result'].

    validator = A callable that takes the input data as an argument
    and returns a tuple of (bool, str), where the bool indicates
    validity and the str is an error message, if any.  If None, no
    validation will be done.

    Template Notes:

    Because Jinja2 cannot support dictionaries with hyphens in the
    keys, all hyphens will be removed from keys after validation.
    E.g., the key 'foo-bar' will be changed to 'foobar'.  Templates
    should use that accordingly.

    See jinja2_format for a list of utility functions added to Jinja2.

    """

    assert isinstance(template, str)

    if mime_type is None:
        try:
            mime_type = sys.argv[1]
        except IndexError:
            mime_type = 'text/plain'

    json_in = json_load(exit_on_error=True, max_schema=max_schema)

    if validator is not None:
        assert callable(validator)

        if pick is not None:
            assert callable(pick)
            json_val = pick(json_in)
        else:
            json_val = json_in

        valid, message = validator(json_val)
        if not valid:
            fail(message)

    json_stripped = json_strip_hyphens(json_in)
    json_stripped['_mime_type'] = mime_type

    try:
        succeed(jinja2_format(template, json_stripped, strip=True))
    except RuntimeError as ex:
        fail(str(ex))
    except jinja2.TemplateError as ex:
        fail(f'Template error: {ex}')



def spec_format_method(template, max_schema=None, validator=None):
    """
    Implement a result-format method.  See _format_method() for more information.
    """
    return _format_method(template,
                         max_schema=max_schema,
                         validator=validator)


def result_format_method(template, max_schema=None, validator=None):
    """
    Implement a result-format method.  See _format_method() for more information.
    """
    return _format_method(template,
                         max_schema=max_schema,
                         pick=lambda v: v['result'],
                         validator=validator)
