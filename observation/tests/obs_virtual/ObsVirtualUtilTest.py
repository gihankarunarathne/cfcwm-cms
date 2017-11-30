import datetime
import json
import logging
import logging.config
import os
import traceback
from os.path import join as pjoin

import unittest2 as unittest

from observation.obs_virtual.ObsVirtualUtils import is_unique_points


class ObsVirtualTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root_dir = os.path.dirname(os.path.realpath(__file__))
            # config = json.loads(open(pjoin(cls.root_dir, '../../config/CONFIG.json')).read())

            # Initialize Logger
            logging_config = json.loads(open(pjoin(cls.root_dir, '../../config/LOGGING_CONFIG.json')).read())
            logging.config.dictConfig(logging_config)
            cls.logger = logging.getLogger('MySQLAdapterTest')
            cls.logger.addHandler(logging.StreamHandler())
            cls.logger.info('setUpClass')

        except Exception as e:
            cls.logger.error(e)
            traceback.print_exc()

    @classmethod
    def tearDownClass(self):
        self.logger.info('tearDownClass')

    def setUp(self):
        self.logger.info('setUp')

    def tearDown(self):
        self.logger.info('tearDown')

    def test_is_unique_points(self):
        points = {
            'IBATTARA2': [79.86, 6.892],
            'IBATTARA3': [79.86, 6.893],
            'Borella': [79.86, 6.93],
            'Kompannaveediya': [79.85, 6.92],
            'Angurukaramulla': [79.86, 7.21],
            'Hirimbure': [80.221, 6.054],
            'Yatiwawala': [80.613, 7.329],
        }
        is_unique = is_unique_points(points)
        self.assertTrue(is_unique)

        points2 = {
            'IBATTARA2': [79.86, 6.89],
            'IBATTARA3': [79.86, 6.89],
            'Borella': [79.86, 6.93],
            'Kompannaveediya': [79.85, 6.92],
            'Angurukaramulla': [79.86, 7.21],
            'Hirimbure': [80.221, 6.054],
            'Yatiwawala': [80.613, 7.329],
        }
        is_unique = is_unique_points(points2)
        self.assertFalse(is_unique)
