from datetime import timedelta, datetime
import logging
from .InterpolationStrategy import InterpolationStrategy
from .CMSError import InvalidTimeseriesCMSError, InvalidInterpolateStrategyCMSError


def interpolate_timeseries(strategy, timeseries, time_interval_sec=0, time_interval_min=0):
    if len(timeseries) < 2:
        logging.error('Timeseries should have at least two points to proceed')
        raise InvalidTimeseriesCMSError('Timeseries should have at least two points to proceed')

    time_interval = timedelta(seconds=60) # Default time interval is 60 seconds
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
