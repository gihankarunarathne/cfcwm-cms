#!/usr/bin/python3

import sys, traceback, csv, json, datetime, getopt, os, copy, requests, argparse

from curwmysqladapter import mysqladapter
from LibContinousTimeseries import getTimeseries
from LibContinousValidation import validateTimeseries

try:
    INIT_DIR = os.getcwd()
    ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
    os.chdir(ROOT_DIR)

    CONFIG = json.loads(open(os.path.join(ROOT_DIR, '../CONFIG.json')).read())

    CONTINOUS_CONFIG="./CONTINOUS_CONFIG.json"

    MYSQL_HOST="localhost"
    MYSQL_USER="root"
    MYSQL_DB="curw"
    MYSQL_PASSWORD=""

    if 'CONTINOUS_CONFIG' in CONFIG :
        CONTINOUS_CONFIG = CONFIG['CONTINOUS_CONFIG']

    if 'MYSQL_HOST' in CONFIG :
        MYSQL_HOST = CONFIG['MYSQL_HOST']
    if 'MYSQL_USER' in CONFIG :
        MYSQL_USER = CONFIG['MYSQL_USER']
    if 'MYSQL_DB' in CONFIG :
        MYSQL_DB = CONFIG['MYSQL_DB']
    if 'MYSQL_PASSWORD' in CONFIG :
        MYSQL_PASSWORD = CONFIG['MYSQL_PASSWORD']

    date = ''
    forceInsert = False

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", help="Date in YYYY-MM-DD. Default is current date.")
    parser.add_argument("-c", "--config", help="Configuration file of timeseries. Default is ./CONTINOUS_CONFIG.json.")
    parser.add_argument("-f", "--force", action="store_true", help="Force insert.")
    args = parser.parse_args()
    print('Commandline Options:', args)
    
    if args.date :
        date = args.date
    if args.config :
        CONTINOUS_CONFIG = os.path.join(ROOT_DIR, args.config)
    forceInsert = args.force

    # Default run for current day
    now = datetime.datetime.now()
    if date :
        now = datetime.datetime.strptime(date, '%Y-%m-%d')

    print('Continous data extraction:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'on', ROOT_DIR)
    if forceInsert :
        print('WARNING: Force Insert enabled.')

    CON_DATA = json.loads(open(CONTINOUS_CONFIG).read())

    stations = CON_DATA['stations']

    metaData = {
        'station': '',
        'variable': '',
        'unit': '',
        'type': '',
        'source': '',
        'name': '',
    }
    adapter = mysqladapter(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)

    for station in stations :
        print('station:', station)



except Exception as e :
    traceback.print_exc()
finally:
    os.chdir(INIT_DIR)
