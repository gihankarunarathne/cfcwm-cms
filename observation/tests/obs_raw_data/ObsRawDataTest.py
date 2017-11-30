import datetime
import json
import logging
import logging.config
import os
import traceback
from os.path import join as pjoin

import unittest2 as unittest
from curwmysqladapter import MySQLAdapter

from observation.obs_raw_data.ObsRawData import \
    get_dialog_timeseries, \
    get_wu_timeseries, \
    create_raw_timeseries
from cms_utils.UtilTimeseries import extract_single_variable_timeseries


class ObsRawDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root_dir = os.path.dirname(os.path.realpath(__file__))
            cls.config = json.loads(open(pjoin(cls.root_dir, '../../config/CONFIG.json')).read())

            # Initialize Logger
            logging_config = json.loads(open(pjoin(cls.root_dir, '../../config/LOGGING_CONFIG.json')).read())
            logging.config.dictConfig(logging_config)
            cls.logger = logging.getLogger('MySQLAdapterTest')
            cls.logger.addHandler(logging.StreamHandler())
            cls.logger.info('setUpClass')

            MYSQL_HOST = "localhost"
            MYSQL_USER = "root"
            MYSQL_DB = "curw"
            MYSQL_PASSWORD = ""

            if 'MYSQL_HOST' in cls.config:
                MYSQL_HOST = cls.config['MYSQL_HOST']
            if 'MYSQL_USER' in cls.config:
                MYSQL_USER = cls.config['MYSQL_USER']
            if 'MYSQL_DB' in cls.config:
                MYSQL_DB = cls.config['MYSQL_DB']
            if 'MYSQL_PASSWORD' in cls.config:
                MYSQL_PASSWORD = cls.config['MYSQL_PASSWORD']

            cls.adapter = MySQLAdapter(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)
            cls.eventIds = []
        except Exception as e:
            print(e)
            traceback.print_exc()

    @classmethod
    def tearDownClass(cls):
        cls.logger.info('tearDownClass')

    def setUp(self):
        self.logger.info('setUp')

    def tearDown(self):
        self.logger.info('tearDown')

    def test_createRawDataForLastHour(self):
        self.logger.info('createRawDataForLastHour')
        OBS_CONFIG = pjoin(self.root_dir, "../../config/StationConfig.json")
        CON_DATA = json.loads(open(OBS_CONFIG).read())
        stations = CON_DATA['stations']
        self.logger.debug('stations %s', stations)
        start_date_time = datetime.datetime(2017, 11, 20, 0, 0, 0)
        end_date_time = datetime.datetime(2017, 11, 20, 12, 0, 0)
        duration = dict(start_date_time=start_date_time, end_date_time=end_date_time)
        opts = dict(forceInsert=False)

        create_raw_timeseries(self.adapter, stations, duration, opts)

    def test_getDialogTimeseries(self):
        self.logger.info('getDialogTimeseries')
        start_date_time = datetime.datetime(2017, 11, 21, 0, 0, 0)
        end_date_time = datetime.datetime(2017, 11, 21, 1, 0, 0)
        username = self.config['DIALOG_IOT_USERNAME'] if 'DIALOG_IOT_USERNAME' in self.config else None
        password = self.config['DIALOG_IOT_PASSWORD'] if 'DIALOG_IOT_PASSWORD' in self.config else None
        opts = dict(dialog_iot_username=username, dialog_iot_password=password)
        station = {'stationId': '3674010756837033'}
        dialog_timeseries = get_dialog_timeseries(station, start_date_time, end_date_time, opts)
        print('Length:', len(dialog_timeseries))
        print(dialog_timeseries[10:])
        self.assertGreater(len(dialog_timeseries), 0)

    def test_getDialogTimeseriesWithoutAuth(self):
        self.logger.info('test_getDialogTimeseriesWithoutAuth')
        start_date_time = datetime.datetime(2017, 11, 21, 0, 0, 0)
        end_date_time = datetime.datetime(2017, 11, 21, 1, 0, 0)
        dialog_timeseries = get_dialog_timeseries({'stationId': '3674010756837033'}, start_date_time, end_date_time)
        print('Length:', len(dialog_timeseries))
        print(dialog_timeseries)
        self.assertEqual(len(dialog_timeseries), 0)

    def test_getWUndergroundTimeseries(self):
        self.logger.info('getWUndergroundTimeseries')
        start_date_time = datetime.datetime(2017, 10, 1, 0, 0, 0)
        end_date_time = datetime.datetime(2017, 10, 1, 23, 0, 0)
        wu_timeseries = get_wu_timeseries({'stationId': 'IBATTARA3'}, start_date_time, end_date_time)
        print(wu_timeseries)
        self.assertGreater(len(wu_timeseries), 0)

    def test_getWUndergroundTimeseriesYatiwawala(self):
        self.logger.info('getWUndergroundTimeseries')
        start_date_time = datetime.datetime(2017, 11, 1, 23, 0, 0)
        end_date_time = datetime.datetime(2017, 11, 2, 1, 0, 0)
        wu_timeseries = get_wu_timeseries({'stationId': 'Yatiwawala', 'name': 'Yatiwawala'}, start_date_time, end_date_time)
        print('wu_timeseries', wu_timeseries)
        self.assertGreater(len(wu_timeseries), 0)

    def test_extractSinglePrecipitationDialogTimeseries(self):
        self.logger.info('test_extractSinglePrecipitationDialogTimeseries')
        start_date_time = datetime.datetime(2017, 10, 20, 0, 0, 0)
        end_date_time = datetime.datetime(2017, 10, 20, 23, 0, 0)
        dialog_timeseries = get_dialog_timeseries({'stationId': '3674010756837033'}, start_date_time, end_date_time)
        print(dialog_timeseries)
        self.assertGreater(len(dialog_timeseries), 0)
        extractedTimeseries = extract_single_variable_timeseries(dialog_timeseries, 'Precipitation')
        print(extractedTimeseries)
        self.assertTrue(isinstance(extractedTimeseries[0], list))
        self.assertEqual(len(extractedTimeseries[0]), 2)

    def test_extractSinglePrecipitationWUndergroundTimeseries(self):
        self.logger.info('test_extractSinglePrecipitationWUndergroundTimeseries')
        start_date_time = datetime.datetime(2017, 10, 1, 0, 0, 0)
        end_date_time = datetime.datetime(2017, 10, 1, 23, 0, 0)
        wu_timeseries = get_wu_timeseries({'stationId': 'IBATTARA3'}, start_date_time, end_date_time)
        print(wu_timeseries)
        self.assertGreater(len(wu_timeseries), 0)
        extractedTimeseries = extract_single_variable_timeseries(wu_timeseries, 'Precipitation')
        print(extractedTimeseries)
        self.assertTrue(isinstance(extractedTimeseries[0], list))
        self.assertEqual(len(extractedTimeseries[0]), 2)
