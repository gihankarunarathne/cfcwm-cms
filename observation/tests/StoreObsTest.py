import datetime
import json
import logging
import logging.config
import os
import sys
import traceback
from os.path import join as pjoin
from subprocess import Popen, PIPE

import unittest2 as unittest


class StoreObsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root_dir = os.path.dirname(os.path.realpath(__file__))
            # config = json.loads(open(pjoin(cls.root_dir, '../config/CONFIG.json')).read())

            # Initialize Logger
            logging_config = json.loads(open(pjoin(cls.root_dir, '../config/LOGGING_CONFIG.json')).read())
            logging.config.dictConfig(logging_config)
            cls.logger = logging.getLogger('StoreObsTest')
            cls.logger.addHandler(logging.StreamHandler())
            cls.logger.info('setUpClass')

            cls.run_start_date = datetime.datetime(2017, 11, 20, 0, 0, 0)
            cls.run_end_date = datetime.datetime(2017, 11, 20, 12, 0, 0)
        except Exception as e:
            logging.error(e)
            traceback.print_exc()

    @classmethod
    def tearDownClass(cls):
        cls.logger.info('tearDownClass')

    def setUp(self):
        self.logger.info('setUp')

    def tearDown(self):
        self.logger.info('tearDown')

    def test_runScriptForAll(self):
        self.logger.info('runScriptForAll')
        execList = ['python', pjoin(self.root_dir, '../StoreObs.py')]
        execList = execList + ['-s', self.run_start_date.strftime("%Y-%m-%d")]
        execList = execList + ['-f']
        execList = execList + ['-e', self.run_end_date.strftime("%Y-%m-%d")]
        execList = execList + ['-m', 'all']
        print('*********************************************************')
        print('>>>', execList, '\n')
        process = Popen(execList, stdout=PIPE)
        process.wait()
