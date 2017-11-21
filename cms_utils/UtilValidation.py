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
        if MIN_VALUE <= t[1] <= MAX_VALUE:
            newTimeseries.append(t)
        else:
            newTimeseries.append([t[0], MISSING_VALUE])

    return newTimeseries


def handle_duplicate_values(timeseries):
    for index, step in enumerate(timeseries):
        if step in timeseries[index:min(index+3, len(timeseries))]:
            print('Duplicate:', step)

    return timeseries


def timeseries_availability(timeseries, validation=None, percentage=80):
    """
    Check the availability of values for given percentage
    """
    if validation is None:
        validation = {'max_value': 1000, 'min_value': 0}

    MAX_VALUE = float(validation.get('max_value'))
    MIN_VALUE = float(validation.get('min_value'))

    valid_points = 0
    for t in timeseries:
        if MIN_VALUE <= t[1] <= MAX_VALUE:
            valid_points += 1

    return valid_points / len(timeseries) * 100 >= percentage
