import sys
import datetime
import json
import os
import logging, logging.config
import traceback
from glob import glob
from os.path import join as pjoin

import unittest2 as unittest
from curwmysqladapter import MySQLAdapter

sys.path.insert(0, '../../obs_virtual')
from observation.obs_virtual.ObsVirtual import create_klb_timseries, create_kub_timeseries


class ObsVirtualTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            root_dir = os.path.dirname(os.path.realpath(__file__))
            config = json.loads(open(pjoin(root_dir, '../../config/CONFIG.json')).read())

            # Initialize Logger
            logging_config = json.loads(open(pjoin(root_dir, '../../config/LOGGING_CONFIG.json')).read())
            logging.config.dictConfig(logging_config)
            cls.logger = logging.getLogger('MySQLAdapterTest')
            cls.logger.addHandler(logging.StreamHandler())
            cls.logger.info('setUpClass')

            MYSQL_HOST = "localhost"
            MYSQL_USER = "root"
            MYSQL_DB = "curw"
            MYSQL_PASSWORD = ""

            if 'MYSQL_HOST' in config:
                MYSQL_HOST = config['MYSQL_HOST']
            if 'MYSQL_USER' in config:
                MYSQL_USER = config['MYSQL_USER']
            if 'MYSQL_DB' in config:
                MYSQL_DB = config['MYSQL_DB']
            if 'MYSQL_PASSWORD' in config:
                MYSQL_PASSWORD = config['MYSQL_PASSWORD']

            cls.adapter = MySQLAdapter(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)
            cls.eventIds = []
        except Exception as e:
            traceback.print_exc()

    @classmethod
    def tearDownClass(self):
        self.logger.info('tearDownClass')

    def setUp(self):
        self.logger.info('setUp')

    def tearDown(self):
        self.logger.info('tearDown')

    def test_createKUBForLastHour(self):
        self.logger.info('createKUBForLastHour')

        create_kub_timeseries()

    def test_createKLBForLastHour(self):
        self.logger.info('createKLBForLastHour')
        create_klb_timseries()
