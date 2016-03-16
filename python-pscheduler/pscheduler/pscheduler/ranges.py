"""
Functions for dealing with ranges.
"""

def coalesce_ranges(ranges, duration):
    """
    Find the earliest mutually-agreeable time from lists provided by
    participants.

    The 'ranges' argument is a list of ranges is an array, with one
    element for each participant.  Each of those elements is a sorted
    list of tuples representing available time ranges.  Each tuple is
    (lower-time, upper-time).

    The 'duration' argument is the minimum length a set of times found
    to be common must be to qualify.

    Return value is a tuple of (lower-time, upper-time) if there was a
    mutually-agreeable range found, None otherwise.

    NOTES:

    This function makes no attempt to make sure the ranges
    are lower-upper, so the GIGO principle applies.

    This function was written to be used with ranges of datetimes but
    will work with anything that can be compared for sorting.
    """

    sets = len(ranges)

    if sets < 2:
        # TODO: What's a good exception to raise here?
        raise ValueError("Must have at least two sets of ranges")

    matches = []  # Ranges we came up with that matched

    for outer in ranges[0]:
        (earliest, latest) = outer

        # Weed out too-short lead proposals
        if (latest - earliest) < duration:
            continue

        matches = [ outer ]   # Ranges in non-leads that work

        # Go through each of the other sets' proposed ranges

        for inner in range(1,sets):

            for candidate in ranges[inner]:

                (lower, upper) = candidate

                # Skip ranges that clearly aren't going to work:
                #  - Non-overlapping
                #  - Too short
                if ((upper < earliest) or (lower > latest)) \
                        or ((upper - lower) < duration):
                    continue

                # Trim the candidate range to just the overlap and add
                # its tuple to our list of good ones.
                trimmed_lower = max(earliest, lower)
                trimmed_upper = min(upper, latest)
                if (trimmed_upper - trimmed_lower) >= duration:
                    matches.append( (trimmed_lower, trimmed_upper) )

        # A full set means we found a good match and can stop.
        if len(matches) == sets:
            break

    # If the loop above didn't leave us with a ranges from every
    # participant, there isn't one.
    if len(matches) < sets:
        return None

    # Trim everything to the smallest mutually-acceptable range
    (final_lower, final_upper) = matches.pop(0)
    for match in matches:
        (match_lower, match_upper) = match
        final_lower = max(final_lower, match_lower)
        final_upper = min(final_upper, match_upper)

    assert final_lower <= final_upper, "Came up with a bogus range."
    assert (final_upper - final_lower) >= duration,  "Duration %s is too short." % str(duration)

    return (final_lower, final_upper)



if __name__ == "__main__":
    # Result should be None
    print coalesce_ranges( [
            [],
            []
            ], 3)

    # Result should be None
    print coalesce_ranges( [
            [ (1, 5), (19, 23) ],
            [ (7, 10), (15, 20) ]
            ], 3)


    # Result should be (3, 7)
    print coalesce_ranges( [
            [ (1, 7), (9, 12) ],
            [ (1, 2), (3, 8) ],
            ], 3)

    # Result should be (20,30)
    print coalesce_ranges( [
            [ (1,10), (20,30) ],
            [ (5,40) ],
            [ (7,38) ]
            ], 5)
