#!/usr/bin/python3

import sys
import traceback
import csv
import json
from datetime import datetime
import getopt
import os
import copy
import requests
import argparse

from curwmysqladapter import mysqladapter

sys.path.insert(0, '../lib')
from lib import get_timeseries
from lib import extract_single_timeseries
from lib import validate_timeseries
from .config import Constants as C

try:
    INIT_DIR = os.getcwd()
    ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
    os.chdir(ROOT_DIR)

    CONFIG = json.loads(open(os.path.join(ROOT_DIR, '../CONFIG.json')).read())

    OBS_CONFIG = "./config/StationConfig.json"
    COMMON_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

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
    parser.add_argument("-c", "--config", help="Configuration file of timeseries. Default is ./OBS_CONFIG.json.")
    parser.add_argument("-f", "--force", action="store_true", help="Force insert.")
    parser.add_argument("-m", "--mode", help="One of 'raw' | 'processed' | 'virtual'")
    args = parser.parse_args()
    print('Commandline Options:', args)

    if args.config:
        OBS_CONFIG = os.path.join(ROOT_DIR, args.config)
    forceInsert = args.force

    print('Observation data extraction:', datetime.now().strftime(C.DATE_TIME_FORMAT), 'on', ROOT_DIR)
    if forceInsert:
        print('WARNING: Force Insert enabled.')

    CON_DATA = json.loads(open(OBS_CONFIG).read())

    stations = CON_DATA['stations']


except Exception as e:
    traceback.print_stack()
