#!/usr/bin/python3

import argparse
import json
import os
import traceback
import logging
from datetime import datetime, timedelta

from curwmysqladapter import MySQLAdapter

from observation.config import Constants as Constant
from observation.obs_processed_data import ObsProcessedData
from observation.obs_raw_data import ObsRawData
from observation.obs_virtual import ObsVirtual

try:
    INIT_DIR = os.getcwd()
    ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
    os.chdir(ROOT_DIR)

    CONFIG = json.loads(open(os.path.join(ROOT_DIR, './config/CONFIG.json')).read())

    OBS_CONFIG = "./config/StationConfig.json"

    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_DB = "curw"
    MYSQL_PASSWORD = ""

    if 'OBS_CONFIG' in CONFIG:
        OBS_CONFIG = CONFIG['OBS_CONFIG']

    if 'MYSQL_HOST' in CONFIG:
        MYSQL_HOST = CONFIG['MYSQL_HOST']
    if 'MYSQL_USER' in CONFIG:
        MYSQL_USER = CONFIG['MYSQL_USER']
    if 'MYSQL_DB' in CONFIG:
        MYSQL_DB = CONFIG['MYSQL_DB']
    if 'MYSQL_PASSWORD' in CONFIG:
        MYSQL_PASSWORD = CONFIG['MYSQL_PASSWORD']

    force_insert = False

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start-date", help="Start Date in YYYY-MM-DD.")
    parser.add_argument("--start-time", help="Start Time in HH:MM:SS.")
    parser.add_argument("-b", "--back-start", help="Set start date with respect to end-date in hours")
    parser.add_argument("-e", "--end-date", help="End Date in YYYY-MM.")
    parser.add_argument("--end-time", help="End Time in HH:MM:SS.")
    parser.add_argument("-c", "--config", help="Configuration file of timeseries. "
                                               "Default is ./config/StationConfig.json.")
    parser.add_argument("-f", "--force", action="store_true", help="Force insert.")
    parser.add_argument("-m", "--mode", choices=['raw', 'processed', 'virtual', 'virtual_kub', 'virtual_klb', 'all'],
                        default='raw', type=str,
                        help="One of 'all' | 'raw' | 'processed' | 'virtual' | 'virtual_kub' | 'virtual_klb'. "
                             "Default is 'raw'")
    args = parser.parse_args()
    print('Commandline Options:', args)

    if args.config:
        OBS_CONFIG = os.path.join(ROOT_DIR, args.config)
    force_insert = args.force

    # Default End Date is current date
    end_date_time = datetime.now()
    if args.end_date:
        end_date_time = datetime.strptime(args.end_date, '%Y-%m-%d')
    if args.end_time:
        end_date_time = datetime.strptime("%s %s" % (end_date_time.strftime("%Y-%m-%d"), args.end_time),
                                          Constant.DATE_TIME_FORMAT)

    if args.back_start:
        start_date_time = (end_date_time - timedelta(hours=int(args.back_start)))
    elif args.start_date:
        start_date_time = datetime.strptime(args.start_date, '%Y-%m-%d')
    else:
        # Default Start & End date time gap is one hour
        start_date_time = (end_date_time - timedelta(hours=1))

    if args.start_time:
        start_date_time = datetime.strptime("%s %s" % (start_date_time.strftime("%Y-%m-%d"), args.start_time), Constant.DATE_TIME_FORMAT)

    print('Observation data extraction starts on:', datetime.now().strftime(Constant.DATE_TIME_FORMAT), 'at', ROOT_DIR)
    if force_insert:
        print('WARNING: Force Insert enabled.')

    CON_DATA = json.loads(open(OBS_CONFIG).read())

    stations = CON_DATA['stations']

    adapter = MySQLAdapter(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)


    def create_virtual_timeseries(my_adapter, my_stations, my_duration, my_opts):
        ObsVirtual.create_kub_timeseries(my_adapter, my_stations, my_duration, my_opts)
        ObsVirtual.create_klb_timeseries(my_adapter, my_stations, my_duration, my_opts)

    def create_all_timeseries(my_adapter, my_stations, my_duration, my_opts):
        ObsRawData.create_raw_timeseries(my_adapter, my_stations, my_duration, my_opts)
        ObsProcessedData.create_processed_timeseries(my_adapter, my_stations, my_duration, my_opts)
        create_virtual_timeseries(my_adapter, my_stations, my_duration, my_opts)

    modeDict = {
        'all': create_all_timeseries,
        'raw': ObsRawData.create_raw_timeseries,
        'processed': ObsProcessedData.create_processed_timeseries,
        'virtual_kub': ObsVirtual.create_kub_timeseries,
        'virtual_klb': ObsVirtual.create_klb_timeseries,
        'virtual': create_virtual_timeseries
    }


    def default():
        print('default mode')
        return []


    duration = dict(start_date_time=start_date_time, end_date_time=end_date_time)
    opts = dict(force_insert=force_insert)
    if 'DIALOG_IOT_USERNAME' in CONFIG:
        opts['dialog_iot_username'] = CONFIG['DIALOG_IOT_USERNAME']
    if 'DIALOG_IOT_PASSWORD' in CONFIG:
        opts['dialog_iot_password'] = CONFIG['DIALOG_IOT_PASSWORD']
    print('Duration::', duration, 'Opts::', opts)

    modeDict.get(args.mode, default)(adapter, stations, duration, opts)

except Exception as e:
    logging.error(e)
    print(e)
    traceback.print_stack()
