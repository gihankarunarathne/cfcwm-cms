import logging
import logging.config
import os
import json
from os.path import join as pjoin
from datetime import datetime, timedelta

import unittest2 as unittest
from cms_utils.UtilInterpolation import interpolate_timeseries, \
    get_minimum_time_step, \
    fill_timeseries_missing_with_values
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

    def test_usingAverageStrategyForLargeGaps(self):
        timeseries = [['2017-11-16 13:35:00', 1.0], ['2017-11-16 13:40:00', 2.0], ['2017-11-16 13:45:00', 3.0],
                      ['2017-11-16 13:50:00', 4.0], ['2017-11-16 13:55:00', 5.0], ['2017-11-16 14:00:00', 6.0],
                      ['2017-11-16 14:06:00', 7.0], ['2017-11-16 14:11:00', 8.0], ['2017-11-16 14:16:00', 9.0]]
        new_timeseries = \
            interpolate_timeseries(InterpolationStrategy.Average, convert_timeseries_to_datetime(timeseries))
        print('Result::')
        for t in new_timeseries:
            print(t)
        self.assertEqual(len(new_timeseries), 42)
        self.assertListEqual(new_timeseries[40], [datetime.strptime('2017-11-16 14:15:00', '%Y-%m-%d %H:%M:%S'), 8.0])

    def test_usingMaximumStrategyForLargeGaps(self):
        timeseries = [['2017-11-16 13:35:00', 1.0], ['2017-11-16 13:40:00', 2.0], ['2017-11-16 13:45:00', -999],
                      ['2017-11-16 13:50:00', 4.0], ['2017-11-16 13:55:00', 5.0],
                      ['2017-11-16 14:06:00', 7.0], ['2017-11-16 14:11:00', 8.0], ['2017-11-16 14:16:00', 9.0]]
        new_timeseries = \
            interpolate_timeseries(InterpolationStrategy.Maximum, convert_timeseries_to_datetime(timeseries))
        print('Result::')
        for t in new_timeseries:
            print(t)
        self.assertEqual(len(new_timeseries), 42)
        self.assertListEqual(new_timeseries[40], [datetime.strptime('2017-11-16 14:15:00', '%Y-%m-%d %H:%M:%S'), 8.0])

    def test_usingSummationStrategyForLargeGaps(self):
        timeseries = [['2017-11-16 13:35:00', 1.0], ['2017-11-16 13:40:00', 2.0], ['2017-11-16 13:45:00', 3.0],
                      ['2017-11-16 13:50:00', 4.0], ['2017-11-16 13:55:00', 5.0], ['2017-11-16 14:00:00', 6.0],
                      ['2017-11-16 14:06:00', 7.0], ['2017-11-16 14:11:00', 8.0], ['2017-11-16 14:16:00', 9.0]]
        new_timeseries = \
            interpolate_timeseries(InterpolationStrategy.Summation, convert_timeseries_to_datetime(timeseries))
        print('Result::')
        for t in new_timeseries:
            print(t)
        self.assertEqual(len(new_timeseries), 42)
        self.assertListEqual(new_timeseries[40], [datetime.strptime('2017-11-16 14:15:00', '%Y-%m-%d %H:%M:%S'), 1.6])

    def test_usingAverageStrategyForSmallerGaps(self):
        timeseries = [['2017-11-15 00:00:00', 1.0], ['2017-11-15 00:00:16', 2.0], ['2017-11-15 00:00:32', -999],
                      ['2017-11-15 00:00:48', 4.0], ['2017-11-15 00:01:04', -999], ['2017-11-15 00:01:20', 6.0],
                      ['2017-11-15 00:01:36', -999], ['2017-11-15 00:01:52', 7.0], ['2017-11-15 00:02:08', 8.0],
                      ['2017-11-15 00:02:24', 9.0]]
        new_timeseries = \
            interpolate_timeseries(InterpolationStrategy.Average, convert_timeseries_to_datetime(timeseries))
        print('Result::')
        for t in new_timeseries:
            print(t)
        self.assertEqual(len(new_timeseries), 3)
        self.assertListEqual(new_timeseries[1], [datetime.strptime('2017-11-15 0:01:00', '%Y-%m-%d %H:%M:%S'), 6.5])

    def test_usingMaximumStrategyForSmallerGaps(self):
        timeseries = [['2017-11-15 00:00:00', 1.0], ['2017-11-15 00:00:16', 2.0], ['2017-11-15 00:00:32', -999],
                      ['2017-11-15 00:00:48', 4.0], ['2017-11-15 00:01:04', -999], ['2017-11-15 00:01:20', 6.0],
                      ['2017-11-15 00:01:36', -999], ['2017-11-15 00:01:52', 7.0], ['2017-11-15 00:02:08', 8.0],
                      ['2017-11-15 00:02:24', 9.0]]
        new_timeseries = \
            interpolate_timeseries(InterpolationStrategy.Maximum, convert_timeseries_to_datetime(timeseries))
        print('Result::')
        for t in new_timeseries:
            print(t)
        self.assertEqual(len(new_timeseries), 3)
        self.assertListEqual(new_timeseries[1], [datetime.strptime('2017-11-15 0:01:00', '%Y-%m-%d %H:%M:%S'), 7.0])

    def test_usingSummationStrategyForSmallerGaps(self):
        timeseries = [['2017-11-15 00:00:00', 1.0], ['2017-11-15 00:00:16', 2.0], ['2017-11-15 00:00:32', -999],
                      ['2017-11-15 00:00:48', 4.0], ['2017-11-15 00:01:04', -999], ['2017-11-15 00:01:20', 6.0],
                      ['2017-11-15 00:01:36', -999], ['2017-11-15 00:01:52', 7.0], ['2017-11-15 00:02:08', 8.0],
                      ['2017-11-15 00:02:24', 9.0]]
        new_timeseries = \
            interpolate_timeseries(InterpolationStrategy.Summation, convert_timeseries_to_datetime(timeseries))
        print('Result::')
        for t in new_timeseries:
            print(t)
        self.assertEqual(len(new_timeseries), 3)
        self.assertListEqual(new_timeseries[1], [datetime.strptime('2017-11-15 0:01:00', '%Y-%m-%d %H:%M:%S'), 13.0])

    def test_fill_timeseries_missing_with_values(self):
        timeseries = [['2017-11-16 00:00:00', 1.0], ['2017-11-16 00:10:00', 2.0], ['2017-11-16 00:15:00', 3.0],
                      ['2017-11-16 00:20:00', 4.0], ['2017-11-16 00:35:00', 5.0], ['2017-11-16 01:00:00', 6.0],
                      ['2017-11-16 01:06:00', 7.0], ['2017-11-16 01:11:00', 8.0], ['2017-11-16 01:16:00', 9.0]]
        new_timeseries = \
            fill_timeseries_missing_with_values(InterpolationStrategy.Average,
                                                convert_timeseries_to_datetime(timeseries), timedelta(minutes=5), 3)
        print(new_timeseries)
        self.assertEqual(len(new_timeseries), 16)
        self.assertListEqual(new_timeseries[1], [datetime.strptime('2017-11-16 00:05:00', '%Y-%m-%d %H:%M:%S'), 1.0])
        self.assertListEqual(new_timeseries[5], [datetime.strptime('2017-11-16 00:25:00', '%Y-%m-%d %H:%M:%S'), 4.0])
        self.assertListEqual(new_timeseries[9], [datetime.strptime('2017-11-16 00:45:00', '%Y-%m-%d %H:%M:%S'), -999])

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
