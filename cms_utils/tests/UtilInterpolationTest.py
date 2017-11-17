import logging
import logging.config
import os
import json
from os.path import join as pjoin
from datetime import datetime, timedelta

import unittest2 as unittest
from cms_utils.UtilInterpolation import interpolate_timeseries, get_minimum_time_step
from cms_utils.InterpolationStrategy import InterpolationStrategy
from cms_utils.UtilTimeseries import convert_timeseries_to_datetime


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

    def test_getMinimumTimeStep(self):
        timeseries1 = [['2017-11-16 13:35:00', 1.0], ['2017-11-16 13:40:00', 2.0], ['2017-11-16 13:45:00', 3.0],
                       ['2017-11-16 13:50:00', 4.0], ['2017-11-16 13:55:00', 5.0], ['2017-11-16 14:00:00', 6.0],
                       ['2017-11-16 14:06:00', 7.0], ['2017-11-16 14:11:00', 8.0], ['2017-11-16 14:16:00', 9.0]]
        time_step = get_minimum_time_step(convert_timeseries_to_datetime(timeseries1))
        self.assertEqual(time_step, timedelta(minutes=5))

        timeseries2 = [['2017-11-15 08:20:29', 1.0], ['2017-11-15 08:20:45', 2.0], ['2017-11-15 08:21:01', 3.0],
                       ['2017-11-15 08:21:17', 4.0], ['2017-11-15 08:21:33', 5.0], ['2017-11-15 08:21:49', 6.0],
                       ['2017-11-15 08:22:05', 7.0], ['2017-11-15 08:22:21', 8.0], ['2017-11-15 08:22:37', 9.0]]
        time_step = get_minimum_time_step(convert_timeseries_to_datetime(timeseries2))
        self.assertEqual(time_step, timedelta(seconds=16))

        timeseries3 = [['2017-11-16 13:35:00', 1.0], ['2017-11-16 14:40:00', 2.0], ['2017-11-16 15:45:00', 3.0]]
        time_step = get_minimum_time_step(convert_timeseries_to_datetime(timeseries3))
        self.assertEqual(time_step, None)
