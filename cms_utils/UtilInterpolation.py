import logging
from datetime import timedelta

from .CMSError import InvalidTimeseriesCMSError, InvalidInterpolateStrategyCMSError
from .InterpolationStrategy import InterpolationStrategy

maximum_time_step = timedelta(hours=1)  # Possible maximum time step is 1 hour
missing_value = -999


def interpolate_timeseries(strategy, timeseries, time_interval_sec=0, time_interval_min=0):
    if len(timeseries) < 2:
        logging.error('Timeseries should have at least two points to proceed')
        raise InvalidTimeseriesCMSError('Timeseries should have at least two points to proceed')

    time_interval = timedelta(seconds=60)  # Default time interval is 60 seconds
    if time_interval_sec != 0 and time_interval_min != 0:
        time_interval = timedelta(minutes=time_interval_min, seconds=time_interval_sec)

    if isinstance(strategy, InterpolationStrategy):
        prev_step = timeseries[0]
        prev_time = prev_step[0]
        for step in timeseries[1:]:
            curr_time = step[0]
            is_time_step = is_time_step_larger(prev_time, curr_time, time_interval)
            if is_time_step == 1:
                strategy.get_strategy_for_smaller(strategy)()
            elif is_time_step == 3:
                strategy.get_strategy_for_larger(strategy)()
            else:
                logging.error('Time step difference have an issue: %s', is_time_step)
            prev_step = step
            prev_time = curr_time
    else:
        raise InvalidInterpolateStrategyCMSError('Invalid Interpolate Strategy')


def fill_timeseries_missing_with_values(strategy, timeseries, time_step, max_filling_period=5):
    new_timeseries = []
    prev_step = timeseries[0]
    for step in timeseries[1:]:
        if step[0] - prev_step[0] < time_step * 2:
            new_timeseries.append(prev_step)
        elif step[0] - prev_step[0] <= time_step * max_filling_period:
            sub_timeseries = InterpolationStrategy.get_strategy_for_fill_missing(strategy)(prev_step, step, time_step)
            new_timeseries.extend(sub_timeseries)
        else:
            sub_timeseries = \
                InterpolationStrategy.get_strategy_for_fill_missing(strategy)(prev_step, step, time_step, missing_value)
            new_timeseries.extend(sub_timeseries)
        prev_step = step

    # Add last step
    new_timeseries.append(timeseries[-1])

    return new_timeseries


def is_time_step_larger(time1, time2, time_interval=timedelta(seconds=60)):
    """
    :param time1:
    :param time2:
    :param time_interval:
    :return: Int which indicate the difference between given time steps
    -1 - time1 is greater than time2
    0 - time1 and time2 values are equal
    1 - difference between time1 and time2 are less than given time interval
    2 - difference between time1 and time2 are equal to given time interval
    3 - difference between time1 and time2 are greater than given time interval
    """
    if time1 < time2:
        diff = time2 - time1
        if diff > time_interval:
            return 3
        elif diff < time_interval:
            return 1
        else:
            return 2
    elif time1 == time2:
        return 0
    else:
        return -1


def get_minimum_time_step(timeseries):
    """
    Get the minimum time step of given timeseries
    :param timeseries: List of List s.t.
    [
        ['2017-11-15 08:20:29', 1.0, 2.0],
        ...
    ]
    :return: timedelta instance of time step gap. None if time gap is higher than maximum_time_step
    """
    minimum = maximum_time_step
    prev_time = timeseries[0][0]
    for time, value in timeseries[1:]:
        diff = time - prev_time
        if timedelta() < diff < minimum:
            minimum = diff

    if minimum < maximum_time_step:
        return minimum
    else:
        return None
