
def strip_zeroes(series):
    """
    Remove leading zero values from a frequency series (e.g. if a word
    begins in 1950, removes all the 1750-1940 zero values).
    """
    series_stripped = series[:]
    while series_stripped and series_stripped[0][1] == 0:
        series_stripped.pop(0)

    # Add back in a single zero value immediately before the first non-zero
    # value, so that the first value doesn't appear to spring from nowhere.
    if series_stripped and series_stripped != series:
        first_date = series_stripped[0][0]
        series_stripped.insert(0, (first_date-10, 0))
    return series_stripped
