import logging
import logging.config
import os
import json
from datetime import datetime, timedelta
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

    def test_average_larger(self):
        time_interval = timedelta(seconds=60)
        timeseries = [
            [datetime.strptime('2017-11-16 13:50:00', '%Y-%m-%d %H:%M:%S'), 4.0],
            [datetime.strptime('2017-11-16 13:55:00', '%Y-%m-%d %H:%M:%S'), 5.0],
            [datetime.strptime('2017-11-16 14:01:00', '%Y-%m-%d %H:%M:%S'), 6.0]
        ]
        new_timeseries = \
            InterpolationStrategy.get_strategy_for_larger(InterpolationStrategy.Average)(timeseries, time_interval)
        self.assertEqual(len(new_timeseries), 11)
