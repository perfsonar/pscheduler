"""
Functions for converting numbers with SI units to integers
"""

import re

si_multipliers = {
    None: 1,
    '': 1,
    'k': 1000 ** 1,
    'm': 1000 ** 2,
    'g': 1000 ** 3,
    't': 1000 ** 4,
    'p': 1000 ** 5,
    'e': 1000 ** 6,
    'z': 1000 ** 7,
    'y': 1000 ** 8,

    'ki': 1024 ** 1,
    'mi': 1024 ** 2,
    'gi': 1024 ** 3,
    'ti': 1024 ** 4,
    'pi': 1024 ** 5,
    'ei': 1024 ** 6,
    'zi': 1024 ** 7,
    'yi': 1024 ** 8
    }

si_regex = re.compile('^(-?[0-9]+(\.[0-9]+)?)\s*([kmgtpezy][i]?)?$')

def si_as_integer(text):

    if type(text) == int:
        return text

    matches = si_regex.search(text.lower(),0)

    if matches is None:
        raise ValueError("Invalid SI value '" + text + "'")

    number = int(matches.group(1)) if matches.group(2) is None \
             else float(matches.group(1))

    unit = matches.group(3)

    multiplier = 1 if unit is None else si_multipliers.get(unit.lower(), '')

    return int(number * multiplier)


#
# Test
#

if __name__ == "__main__":

    # These should convert

    for value in [
            "1234",
            "1234K",
            "-1234ki",
            "5g", "5G", "-5Gi",
            "2y",
            "12.34",
            "123.4K",
            "106.9m",
            "3.1415P"
            ]:
        integer = si_as_integer(value)
        print value, integer

    # These should not.

    print

    for value in [
            "ki",
            "Steak",
            "123e1",
            ]:
        try:
            integer = si_as_integer(value)
            print value, integer
        except ValueError:
            print value, "-> ValueError"
