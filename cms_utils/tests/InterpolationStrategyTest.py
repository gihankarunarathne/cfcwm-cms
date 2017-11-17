import logging
import logging.config
import os
import json
from os.path import join as pjoin

import unittest2 as unittest
from cms_utils.UtilInterpolation import interpolate_timeseries
from cms_utils.InterpolationStrategy import InterpolationStrategy


class InterpolationStrategyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.path.dirname(os.path.realpath(__file__))
        config = json.loads(open(pjoin(cls.root_dir, '../../observation/config/CONFIG.json')).read())

        # Initialize Logger
        logging_config = json.loads(open(pjoin(cls.root_dir, '../../observation/config/LOGGING_CONFIG.json')).read())
        logging.config.dictConfig(logging_config)
        cls.logger = logging.getLogger('InterpolationStrategyTest')
        cls.logger.addHandler(logging.StreamHandler())
        cls.logger.info('setUpClass')

    @classmethod
    def tearDownClass(cls):
        cls.logger.info('tearDownClass')

    def setUp(self):
        self.logger.info('setUp')

    def tearDown(self):
        self.logger.info('tearDown')

    @staticmethod
    def test_usingAverageStrategyForLargeGaps():
        timeseries = [['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:58', 1.0], ['2017-11-16 13:36:59', 1.0],
                      ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0],
                      ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0]]
        interpolate_timeseries(InterpolationStrategy.Average, timeseries)

    @staticmethod
    def test_usingMaximumStrategy():
        timeseries = [['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:58', 1.0], ['2017-11-16 13:36:59', 1.0],
                      ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0],
                      ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0]]
        interpolate_timeseries(InterpolationStrategy.Maximum, timeseries)

    @staticmethod
    def test_usingSummationStrategy():
        timeseries = [['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:58', 1.0], ['2017-11-16 13:36:59', 1.0],
                      ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0],
                      ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0], ['2017-11-16 13:36:59', 1.0]]
        interpolate_timeseries(InterpolationStrategy.Summation, timeseries)
