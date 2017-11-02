#!/usr/bin/python3

import argparse
import json
import os
import traceback
from datetime import datetime

from curwmysqladapter import MySQLAdapter

from observation.config import Constants as C
from observation.obs_processed_data import ObsProcessedData
from observation.obs_raw_data import ObsRawData
from observation.obs_virtual import ObsVirtual

try:
    INIT_DIR = os.getcwd()
    ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
    os.chdir(ROOT_DIR)

    CONFIG = json.loads(open(os.path.join(ROOT_DIR, '../CONFIG.json')).read())

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

    forceInsert = False

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start-date", help="Start Date in YYYY-MM-DD.", required=True)
    parser.add_argument("--start-time", help="Start Time in HH:MM:SS.")
    parser.add_argument("-e", "--end-date", help="End Date in YYYY-MM.")
    parser.add_argument("--end-time", help="End Time in HH:MM:SS.")
    parser.add_argument("-c", "--config", help="Configuration file of timeseries. Default is ./OBS_CONFIG.json.")
    parser.add_argument("-f", "--force", action="store_true", help="Force insert.")
    parser.add_argument("-m", "--mode", choices=['raw', 'processed', 'virtual', 'virtual_kub', 'virtual_klb'],
                        default='raw', type=str,
                        help="One of 'raw' | 'processed' | 'virtual' | 'virtual_kub' | 'virtual_klb'. Default is 'raw'")
    args = parser.parse_args()
    print('Commandline Options:', args)

    if args.config:
        OBS_CONFIG = os.path.join(ROOT_DIR, args.config)
    forceInsert = args.force

    start_date_time = datetime.strptime(args.start_date, '%Y-%m-%d')
    # Default End Date is current date
    end_date_time = datetime.now()
    if args.end_date:
        end_date_time = datetime.strptime(args.end_date, '%Y-%m-%d')
    if args.start_time:
        start_date_time = datetime.strptime("%s %s" % (start_date_time, args.start_time), '%Y-%m-%d %H:%M:%S')
    if args.end_time:
        end_date_time = datetime.strptime("%s %s" % (end_date_time.strftime("%Y-%m-%d"), args.end_time),
                                          '%Y-%m-%d %H:%M:%S')

    print('Observation data extraction:', datetime.now().strftime(C.DATE_TIME_FORMAT), 'on', ROOT_DIR)
    if forceInsert:
        print('WARNING: Force Insert enabled.')

    CON_DATA = json.loads(open(OBS_CONFIG).read())

    stations = CON_DATA['stations']

    adapter = MySQLAdapter(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)


    def create_virtual_timeseries(my_adapter, my_stations, my_duration, my_opts):
        ObsVirtual.create_kub_timeseries(my_adapter, my_stations, my_duration, my_opts)
        ObsVirtual.create_klb_timeseries(my_adapter, my_stations, my_duration, my_opts)


    modeDict = {
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
    opts = dict(forceInsert=forceInsert)

    modeDict.get(args.mode, default)(adapter, stations, duration, opts)

except Exception as e:
    traceback.print_stack()
