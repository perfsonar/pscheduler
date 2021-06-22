"""
Functions for converting numbers with SI units to integers
"""

import copy
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


def si_as_number(text):
    """Convert a string containing an SI value to an integer or return an
    integer if that is what was passed in."""

    if isinstance(text, int):
        return text

    if not isinstance(text, str):
        raise ValueError("Source value must be string or integer")

    matches = si_regex.search(text.lower(), 0)

    if matches is None:
        raise ValueError("Invalid SI value '" + text + "'")

    number = int(matches.group(1)) if matches.group(2) is None \
        else float(matches.group(1))

    unit = matches.group(3)

    multiplier = 1 if unit is None else si_multipliers.get(unit.lower(), '')

    return number * multiplier


def number_as_si(number, places=2, base=10):
    """Convert a number to the largest possible SI
    representation of that number"""

    # Try to cast any input to a float to make
    # division able to get some deci places
    number = float(number)

    if base not in [2, 10]:
        raise ValueError("base must be either 2 or 10")

    # Ensure we get all the things in the correct order
    sorted_si = sorted(list(si_multipliers.items()),
                       key=lambda x: x[1], reverse=True)

    number_format = "{0:.%sf}" % places

    for unit, value in sorted_si:

        # Make string ops later happy
        if unit is None:
            unit = ""

        # Kind of hacky, depending on what base we're in
        # we need to skip either all the base 2 or base 10 entries
        if base == 10 and unit.endswith("i"):
            continue
        if base == 2 and not unit.endswith("i"):
            continue

        if number >= value:
            return number_format.format(number / value) + unit.title()

    # no matches, must be less than anything so just return number
    return number_format.format(number / value)


def si_range(value, default_lower=0):
    """Convert a range of SI numbers to a range of integers.

    The 'value' is a dict containing members 'lower' and 'upper', each
    being an integer or string suitable for si_as_number().  If
    'value' is not a dict, it will be passed directly to
    si_as_number() and treated as a non-range (see below).  If there
    is no 'lower' member and 'default_lower' has been provided, that
    value will be used for the lower number.

    Returns a dict containing memebers 'lower' and 'upper', both
    integers.  For non-ranges, both will be identical.

    Raises ValueError if something doesn't make sense.

    """

    if isinstance(value, str) or isinstance(value, int):
        result = si_as_number(value)
        return {"lower": result, "upper": result}

    if not isinstance(default_lower, int):
        raise ValueError("Default lower value must be integer")

    # TODO: Complain about anything else in the input?

    result = {}

    if "lower" not in value:
        # Copy this because altering it would clobber the original (not cool)
        vrange = copy.copy(value)
        vrange["lower"] = default_lower
        value = vrange

    for member in ["lower", "upper"]:
        try:
            result[member] = si_as_number(value[member])
        except KeyError:
            raise ValueError("Missing '%s' in input" % member)

    if result['lower'] > result['upper']:
        raise ValueError("Lower value must be less than upper value")

    return result


#
# Test
#

if __name__ == "__main__":

    # These should convert

    print("Simple:")
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
        integer = si_as_number(value)
        print(value, integer)

    # These should not.

    print()
    print("Simple, should throw exceptions:")

    for value in [
            "ki",
            "Steak",
            "123e1",
            3.1415
    ]:
        try:
            integer = si_as_number(value)
            print(value, integer)
        except ValueError:
            print(value, "-> ValueError")

    print()
    print("Ranges:")

    for value in [
            15,
            "16ki",
            {"upper": 1000},
            {"lower": 1000, "upper": 2000},
            {"lower": 1000, "upper": "2k"},
            {"lower": "1k", "upper": 2000},
            {"lower": "1k", "upper": "2k"},
            {"lower": "2k", "upper": "1k"}
    ]:
        try:
            returned = si_range(value, default_lower=0)
            print(value, "->", returned)
        except Exception as ex:
            print(value, "-> Exception:", ex)

    # Convert to SI
    print()
    print("Convert from number to SI representation:")
    for value in [
        1000,
        1000 ** 3,
        1234567890,
        "9.8",
        0
    ]:
        result = number_as_si(value)
        print("%s -> %s (base 10)" % (value, result))

        result = number_as_si(value, base=2)
        print("%s -> %s (base 2)" % (value, result))

        result = number_as_si(value, places=3)
        print("%s -> %s (3 places)" % (value, result))
