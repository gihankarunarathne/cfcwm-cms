from enum import Enum
from .CMSError import InvalidTimeseriesCMSError


class InterpolationStrategy(Enum):
    """
    InterpolationStrategy
    """
    Average = 'Average'
    Maximum = 'Maximum'
    Summation = 'Summation'

    @staticmethod
    def get_strategy_for_larger(name):
        _nameToStrategy = {
            InterpolationStrategy.Average: InterpolationStrategy.average_larger,
            InterpolationStrategy.Maximum: InterpolationStrategy.maximum_larger,
            InterpolationStrategy.Summation: InterpolationStrategy.summation_larger
        }
        return _nameToStrategy.get(name, InterpolationStrategy.default)

    @staticmethod
    def get_strategy_for_smaller(name):
        _nameToStrategy = {
            InterpolationStrategy.Average: InterpolationStrategy.average_smaller,
            InterpolationStrategy.Maximum: InterpolationStrategy.maximum_smaller,
            InterpolationStrategy.Summation: InterpolationStrategy.summation_smaller
        }
        return _nameToStrategy.get(name, InterpolationStrategy.default)

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
    def average_smaller():
        print('15')

    """ Maximum """
    @staticmethod
    def maximum_larger():
        print('3')

    @staticmethod
    def maximum_smaller():
        print('13')

    """ Summation """
    @staticmethod
    def summation_larger():
        print('1')

    @staticmethod
    def summation_smaller():
        print('11')

    @staticmethod
    def default():
        print('0')
