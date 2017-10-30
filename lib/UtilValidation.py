def validate_timeseries(timeseries, validation=None):
    """
    Validate Timeseries against given rules
    """
    if validation is None:
        validation = {'max_value': 1000, 'min_value': 0}

    MISSING_VALUE = -999
    MAX_VALUE = float(validation.get('max_value'))
    MIN_VALUE = float(validation.get('min_value'))

    newTimeseries = []
    for t in timeseries:
        if MIN_VALUE <= t[1] and t[1] <= MAX_VALUE:
            newTimeseries.append(t)
        else:
            newTimeseries.append([t[0], MISSING_VALUE])

    return newTimeseries
