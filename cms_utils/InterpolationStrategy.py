import math
from enum import Enum

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
    def average_smaller(timeseries, time_interval):
        print('average_smaller')
        if len(timeseries) > 1:
            curr_tick = timeseries[0][0]
            next_tick = curr_tick + time_interval
            curr_value = timeseries[0][1]
            total = curr_value
            count = 1
            new_timeseries = []
            for index, step in enumerate(timeseries[1:]):
                if step[0] < next_tick:
                    if step[1] > -1:
                        if total > -1:
                            total += step[1]
                            count += 1
                        else:
                            total = step[1]
                    if index == len(timeseries) - 2:
                        new_timeseries.append([curr_tick, total / count])
                else:
                    new_timeseries.append([curr_tick, total / count])
                    total = step[1]
                    count = 1
                    curr_tick += time_interval
                    next_tick += time_interval

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
            next_tick = curr_tick + time_interval
            curr_value = timeseries[0][1]
            maximum = curr_value
            new_timeseries = []
            for index, step in enumerate(timeseries[1:]):
                if step[0] < next_tick:
                    maximum = max(maximum, step[1])
                    if index == len(timeseries) - 2:
                        new_timeseries.append([curr_tick, maximum])
                else:
                    new_timeseries.append([curr_tick, maximum])
                    maximum = step[1]
                    curr_tick += time_interval
                    next_tick += time_interval

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
                    factor = (next_time - prev_time) / time_interval if curr_value > -1 else 1
                    new_timeseries.append([start_time, curr_value / factor])
                else:
                    curr_index += 1
                    if curr_index + 1 < len(timeseries):
                        prev_time = timeseries[curr_index][0]
                        next_time = timeseries[curr_index + 1][0]
                    curr_value = timeseries[curr_index][1]
                    factor = (next_time - prev_time) / time_interval if curr_value > -1 else 1
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
            next_tick = curr_tick + time_interval
            curr_value = timeseries[0][1]
            total = curr_value if curr_value > -1 else 0
            new_timeseries = []
            for index, step in enumerate(timeseries[1:]):
                if step[0] < next_tick:
                    total += step[1] if step[1] > -1 else 0
                    if index == len(timeseries) - 2:
                        new_timeseries.append([curr_tick, total])
                else:
                    new_timeseries.append([curr_tick, total])
                    total = step[1] if step[1] > -1 else 0
                    curr_tick += time_interval
                    next_tick += time_interval

            return new_timeseries
        else:
            raise InvalidTimeseriesCMSError('Time series should have at least two steps: %s' % len(timeseries))

    @staticmethod
    def default():
        print('0')

    @staticmethod
    def get_strategy_for_fill_missing(name):
        _name_to_strategy_fill = {
            InterpolationStrategy.Average: InterpolationStrategy.same_fill,
            InterpolationStrategy.Maximum: InterpolationStrategy.same_fill,
            InterpolationStrategy.Summation: InterpolationStrategy.spread_fill
        }
        return _name_to_strategy_fill.get(name, InterpolationStrategy.default_fill)

    @staticmethod
    def same_fill(step1, step2, time_step, missing_value=None):
        start_time, start_value = step1
        end_time, end_value = step2
        diff = end_time - start_time
        occurrence = int(math.ceil(diff / time_step))
        new_step = diff / occurrence
        new_timeseries = []
        for i in range(0, occurrence):
            if missing_value is not None and i:
                start_value = missing_value
            new_timeseries.append([start_time, start_value])
            start_time += new_step

        return new_timeseries

    @staticmethod
    def spread_fill(step1, step2, time_step, missing_value=None):
        start_time, start_value = step1
        end_time, end_value = step2
        diff = end_time - start_time
        occurrence = int(math.ceil(diff / time_step))
        new_step = diff / occurrence
        new_timeseries = []
        for i in range(0, occurrence):
            value = start_value / occurrence
            if missing_value is not None and i:
                value = missing_value
            new_timeseries.append([start_time, value])
            start_time += new_step

        return new_timeseries

    @staticmethod
    def default_fill(step1, step2):
        return [step1, step2]
