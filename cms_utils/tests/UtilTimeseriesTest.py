import logging
import logging.config
import os
import json
from os.path import join as pjoin
from datetime import datetime, timedelta

import unittest2 as unittest
from cms_utils.UtilTimeseries import convert_timeseries_to_datetime


class UtilTimeseriesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.path.dirname(os.path.realpath(__file__))
        # config = json.loads(open(pjoin(cls.root_dir, '../../observation/config/CONFIG.json')).read())

        # Initialize Logger
        logging_config = json.loads(open(pjoin(cls.root_dir, '../../observation/config/LOGGING_CONFIG.json')).read())
        logging.config.dictConfig(logging_config)
        cls.logger = logging.getLogger('UtilTimeseriesTest')
        cls.logger.addHandler(logging.StreamHandler())
        cls.logger.info('setUpClass')

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass')

    def setUp(self):
        self.logger.info('setUp')

    def tearDown(self):
        self.logger.info('tearDown')

    def test_convertTimeseriesToDatetime(self):
        timeseries = [['2017-11-16 13:35:00', 1.0], ['2017-11-16 13:40:00', 2.0], ['2017-11-16 13:45:00', 3.0],
                      ['2017-11-16 13:50:00', 4.0], ['2017-11-16 13:55:00', 5.0], ['2017-11-16 14:00:00', 6.0],
                      ['2017-11-16 14:06:00', 7.0], ['2017-11-16 14:11:00', 8.0], ['2017-11-16 14:16:00', 9.0]]
        new_timeseries = convert_timeseries_to_datetime(timeseries)
        print(new_timeseries)
        self.assertTrue(isinstance(new_timeseries[0][0], datetime))
