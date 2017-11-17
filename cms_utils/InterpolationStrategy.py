from enum import Enum
import math
from .CMSError import InvalidTimeseriesCMSError


class InterpolationStrategy(Enum):
    """
    InterpolationStrategy

    NOTE: Assume that there isn't any gaps in the timeseries.
    Gaps need to be fulfill before going to feed into the functions.
    """
    Average = 'Average'
    Maximum = 'Maximum'
    Summation = 'Summation'

    @staticmethod
    def get_strategy_for_larger(name):
        _name_to_strategy_larger = {
            InterpolationStrategy.Average: InterpolationStrategy.average_larger,
            InterpolationStrategy.Maximum: InterpolationStrategy.maximum_larger,
            InterpolationStrategy.Summation: InterpolationStrategy.summation_larger
        }
        return _name_to_strategy_larger.get(name, InterpolationStrategy.default)

    @staticmethod
    def get_strategy_for_smaller(name):
        _name_to_strategy_smaller = {
            InterpolationStrategy.Average: InterpolationStrategy.average_smaller,
            InterpolationStrategy.Maximum: InterpolationStrategy.maximum_smaller,
            InterpolationStrategy.Summation: InterpolationStrategy.summation_smaller
        }
        return _name_to_strategy_smaller.get(name, InterpolationStrategy.default)

    """ Average """
    @staticmethod
    def average_larger(timeseries, time_interval):
        print('average_larger')
        if len(timeseries) > 1:
            start_time = timeseries[0][0]
            end_time = timeseries[-1][0]

            curr_index = 0
            curr_value = timeseries[curr_index][1]
            next_time = timeseries[curr_index+1][0]
            new_timeseries = []
            while start_time <= end_time:
                if start_time < next_time:
                    new_timeseries.append([start_time, curr_value])
                else:
                    curr_index += 1
                    if curr_index+1 < len(timeseries):
                        next_time = timeseries[curr_index + 1][0]
                    curr_value = timeseries[curr_index][1]
                    new_timeseries.append([start_time, curr_value])
                # Increment tick
                start_time += time_interval
            return new_timeseries
        else:
            raise InvalidTimeseriesCMSError('Time series should have at least two steps: %s' % len(timeseries))

    @staticmethod
    def average_smaller(timeseries, time_interval):
        print('average_smaller')
        if len(timeseries) > 1:
            curr_tick = timeseries[0][0]
            curr_value = timeseries[0][1]
            total = curr_value
            count = 1
            new_timeseries = []
            for index, step in enumerate(timeseries[1:]):
                if step[0] < curr_tick:
                    total += step[1]
                    count += 1
                    if index == len(timeseries) - 2:
                        new_timeseries.append([curr_tick, total / count])
                else:
                    new_timeseries.append([curr_tick, total/count])
                    total = step[1]
                    count = 1
                    curr_tick += time_interval

            return new_timeseries
        else:
            raise InvalidTimeseriesCMSError('Time series should have at least two steps: %s' % len(timeseries))

    """ Maximum """
    @staticmethod
    def maximum_larger(timeseries, time_interval):
        print('maximum_larger')
        if len(timeseries) > 1:
            start_time = timeseries[0][0]
            end_time = timeseries[-1][0]

            curr_index = 0
            curr_value = timeseries[curr_index][1]
            next_time = timeseries[curr_index + 1][0]
            new_timeseries = []
            while start_time <= end_time:
                if start_time < next_time:
                    new_timeseries.append([start_time, curr_value])
                else:
                    curr_index += 1
                    if curr_index + 1 < len(timeseries):
                        next_time = timeseries[curr_index + 1][0]
                    curr_value = timeseries[curr_index][1]
                    new_timeseries.append([start_time, curr_value])
                # Increment tick
                start_time += time_interval
            return new_timeseries
        else:
            raise InvalidTimeseriesCMSError('Time series should have at least two steps: %s' % len(timeseries))

    @staticmethod
    def maximum_smaller(timeseries, time_interval):
        print('maximum_smaller')
        if len(timeseries) > 1:
            curr_tick = timeseries[0][0]
            curr_value = timeseries[0][1]
            maximum = curr_value
            new_timeseries = []
            for index, step in enumerate(timeseries[1:]):
                if step[0] < curr_tick:
                    maximum = max(maximum, step[1])
                    if index == len(timeseries) - 2:
                        new_timeseries.append([curr_tick, maximum])
                else:
                    new_timeseries.append([curr_tick, maximum])
                    maximum = step[1]
                    curr_tick += time_interval

            return new_timeseries
        else:
            raise InvalidTimeseriesCMSError('Time series should have at least two steps: %s' % len(timeseries))

    """ Summation """
    @staticmethod
    def summation_larger(timeseries, time_interval):
        print('summation_larger')
        if len(timeseries) > 1:
            start_time = timeseries[0][0]
            end_time = timeseries[-1][0]

            curr_index = 0
            curr_value = timeseries[curr_index][1]
            prev_time = timeseries[curr_index][0]
            next_time = timeseries[curr_index + 1][0]
            new_timeseries = []
            while start_time <= end_time:
                if start_time < next_time:
                    factor = (next_time - prev_time) / time_interval
                    new_timeseries.append([start_time, curr_value / factor])
                else:
                    curr_index += 1
                    if curr_index + 1 < len(timeseries):
                        prev_time = timeseries[curr_index][0]
                        next_time = timeseries[curr_index + 1][0]
                    curr_value = timeseries[curr_index][1]
                    factor = (next_time - prev_time) / time_interval
                    new_timeseries.append([start_time, curr_value / factor])
                # Increment tick
                start_time += time_interval
            return new_timeseries
        else:
            raise InvalidTimeseriesCMSError('Time series should have at least two steps: %s' % len(timeseries))

    @staticmethod
    def summation_smaller(timeseries, time_interval):
        print('summation_smaller')
        if len(timeseries) > 1:
            curr_tick = timeseries[0][0]
            curr_value = timeseries[0][1]
            total = curr_value
            count = 1
            new_timeseries = []
            for index, step in enumerate(timeseries[1:]):
                if step[0] < curr_tick:
                    total += step[1]
                    count += 1
                    if index == len(timeseries) - 2:
                        new_timeseries.append([curr_tick, total])
                else:
                    new_timeseries.append([curr_tick, total])
                    total = step[1]
                    count = 1
                    curr_tick += time_interval

            return new_timeseries
        else:
            raise InvalidTimeseriesCMSError('Time series should have at least two steps: %s' % len(timeseries))

    @staticmethod
    def default():
        print('0')
