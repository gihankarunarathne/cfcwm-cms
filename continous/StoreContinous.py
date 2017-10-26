#!/usr/bin/python3

import sys, traceback, csv, json, datetime, getopt, os, copy, requests, argparse

from curwmysqladapter import mysqladapter
from .LibContinousTimeseries import getTimeseries
from .LibContinousTimeseries import extractSigleTimeseries
from .LibContinousValidation import validateTimeseries

try:
    INIT_DIR = os.getcwd()
    ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
    os.chdir(ROOT_DIR)

    CONFIG = json.loads(open(os.path.join(ROOT_DIR, '../CONFIG.json')).read())

    CONTINOUS_CONFIG="./CONTINOUS_CONFIG.json"
    COMMON_DATE_FORMAT="%Y-%m-%d %H:%M:%S"

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

    forceInsert = False

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Configuration file of timeseries. Default is ./CONTINOUS_CONFIG.json.")
    parser.add_argument("-f", "--force", action="store_true", help="Force insert.")
    args = parser.parse_args()
    print('Commandline Options:', args)

    if args.config :
        CONTINOUS_CONFIG = os.path.join(ROOT_DIR, args.config)
    forceInsert = args.force

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
        dataLocation = station['data_location']
        timeseries = getTimeseries(dataLocation, {
            'root_dir'  : ROOT_DIR,
            'common_date_format': COMMON_DATE_FORMAT
        })

        if(len(timeseries) < 1): 
            print('INFO: Timeseries doesn\'t have any data on :', now.strftime("%Y-%m-%d"), timeseries)
            continue
        print('Start Date :', timeseries[0][0])
        print('End Date :', timeseries[-1][0])
        startDateTime = datetime.datetime.strptime(timeseries[0][0], COMMON_DATE_FORMAT)
        endDateTime = datetime.datetime.strptime(timeseries[-1][0], COMMON_DATE_FORMAT)
        print(timeseries[:3])
        # continue;

        meta = copy.deepcopy(metaData)
        meta['station'] = station['name']
        meta['type'] = station['type']
        meta['source'] = station['source']
        meta['start_date'] = startDateTime.strftime(COMMON_DATE_FORMAT)
        meta['end_date'] = endDateTime.strftime(COMMON_DATE_FORMAT)

        variables = station['variables']
        units = station['units']
        max_values = station['max_values']
        min_values = station['min_values']
        if 'run_name' in station :
            meta['name'] = station['run_name']

        for i in range(0, len(variables)) :
            meta['variable'] = variables[i]
            meta['unit'] = units[i]
            print('meta', meta)
            eventId = adapter.getEventId(meta)
            if eventId is None :
                eventId = adapter.createEventId(meta)
                print('HASH SHA256 created: ', eventId)
            else :
                print('HASH SHA256 exists: ', eventId)
                metaQuery = copy.deepcopy(metaData)
                metaQuery['station'] = station['name']
                metaQuery['type'] = station['type']
                metaQuery['source'] = station['source']
                metaQuery['variable'] = variables[i]
                metaQuery['unit'] = units[i]
                if 'run_name' in station :
                    metaQuery['name'] = station['run_name']
                opts = {
                    'from': startDateTime.strftime(COMMON_DATE_FORMAT),
                    'to': endDateTime.strftime(COMMON_DATE_FORMAT)
                }
                print('metaQuery', metaQuery)
                existingTimeseries = adapter.retrieveTimeseries(metaQuery, opts)
                if len(existingTimeseries[0]['timeseries']) > 0 and not forceInsert:
                    print('Timeseries already exists. User --force to update the existing.\n')
                    continue

            extractedTimeseries = extractSigleTimeseries(timeseries, variables[i], {
                'values': dataLocation['values']
            })
            validationObj = {
                'max_value': max_values[i],
                'min_value': min_values[i],
            }
            newTimeseries = validateTimeseries(extractedTimeseries, variables[i], validationObj)
            # continue

            for l in newTimeseries[:3] + newTimeseries[-2:] :
                print(l)

            rowCount = adapter.insertTimeseries(eventId, newTimeseries, forceInsert)
            print('%s rows inserted.\n' % rowCount)


except Exception as e :
    traceback.print_exc()
finally:
    os.chdir(INIT_DIR)
