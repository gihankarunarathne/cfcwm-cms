from enum import Enum


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

    @staticmethod
    def average_larger():
        print('5')

    @staticmethod
    def average_smaller():
        print('15')

    @staticmethod
    def maximum_larger():
        print('3')

    @staticmethod
    def maximum_smaller():
        print('13')

    @staticmethod
    def summation_larger():
        print('1')

    @staticmethod
    def summation_smaller():
        print('11')

    @staticmethod
    def default():
        print('0')
