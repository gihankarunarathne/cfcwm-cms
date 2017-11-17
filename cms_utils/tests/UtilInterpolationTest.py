import logging
import logging.config
import os
import json
from os.path import join as pjoin

import unittest2 as unittest
from cms_utils.UtilInterpolation import interpolate_timeseries
from cms_utils.InterpolationStrategy import InterpolationStrategy


class UtilInterpolationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.path.dirname(os.path.realpath(__file__))
        # config = json.loads(open(pjoin(cls.root_dir, '../../observation/config/CONFIG.json')).read())

        # Initialize Logger
        logging_config = json.loads(open(pjoin(cls.root_dir, '../../observation/config/LOGGING_CONFIG.json')).read())
        logging.config.dictConfig(logging_config)
        cls.logger = logging.getLogger('UtilInterpolationTest')
        cls.logger.addHandler(logging.StreamHandler())
        cls.logger.info('setUpClass')

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass')

    def setUp(self):
        self.logger.info('setUp')

    def tearDown(self):
        self.logger.info('tearDown')

    @staticmethod
    def test_usingAverageStrategyForLargeGaps():
        timeseries = [['2017-11-16 13:35:00', 1.0], ['2017-11-16 13:40:00', 2.0], ['2017-11-16 13:45:00', 3.0],
                      ['2017-11-16 13:50:00', 4.0], ['2017-11-16 13:55:00', 5.0], ['2017-11-16 14:00:00', 6.0],
                      ['2017-11-16 14:06:00', 7.0], ['2017-11-16 14:11:00', 8.0], ['2017-11-16 14:16:00', 9.0]]
        interpolate_timeseries(InterpolationStrategy.Average, timeseries)

    @staticmethod
    def test_usingMaximumStrategyForLargeGaps():
        timeseries = [['2017-11-16 13:35:00', 1.0], ['2017-11-16 13:40:00', 2.0], ['2017-11-16 13:45:00', 3.0],
                      ['2017-11-16 13:50:00', 4.0], ['2017-11-16 13:55:00', 5.0], ['2017-11-16 14:00:00', 6.0],
                      ['2017-11-16 14:06:00', 7.0], ['2017-11-16 14:11:00', 8.0], ['2017-11-16 14:16:00', 9.0]]
        interpolate_timeseries(InterpolationStrategy.Maximum, timeseries)

    @staticmethod
    def test_usingSummationStrategyForLargeGaps():
        timeseries = [['2017-11-16 13:35:00', 1.0], ['2017-11-16 13:40:00', 2.0], ['2017-11-16 13:45:00', 3.0],
                      ['2017-11-16 13:50:00', 4.0], ['2017-11-16 13:55:00', 5.0], ['2017-11-16 14:00:00', 6.0],
                      ['2017-11-16 14:06:00', 7.0], ['2017-11-16 14:11:00', 8.0], ['2017-11-16 14:16:00', 9.0]]
        interpolate_timeseries(InterpolationStrategy.Summation, timeseries)
