#!/usr/bin/python3

import argparse
import copy
import datetime
import json
import os
import traceback

from curwmysqladapter import MySQLAdapter, Station

from continous.LibContinousTimeseries import extractSigleTimeseries
from continous.LibContinousTimeseries import getTimeseries
from continous.LibContinousValidation import validateTimeseries

try:
    INIT_DIR = os.getcwd()
    ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
    os.chdir(ROOT_DIR)

    CONFIG = json.loads(open(os.path.join(ROOT_DIR, '../CONFIG.json')).read())

    CONTINUOUS_CONFIG= "./CONTINUOUS_CONFIG.json"
    COMMON_DATE_FORMAT="%Y-%m-%d %H:%M:%S"

    MYSQL_HOST="localhost"
    MYSQL_USER="root"
    MYSQL_DB="curw"
    MYSQL_PASSWORD=""

    if 'CONTINOUS_CONFIG' in CONFIG :
        CONTINUOUS_CONFIG = CONFIG['CONTINOUS_CONFIG']

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
    parser.add_argument("-c", "--config", help="Configuration file of timeseries. Default is ./CONTINUOUS_CONFIG.json.")
    parser.add_argument("-f", "--force", action="store_true", help="Force insert.")
    args = parser.parse_args()
    print('Commandline Options:', args)

    if args.config :
        CONTINUOUS_CONFIG = os.path.join(ROOT_DIR, args.config)
    forceInsert = args.force

    print('Continuous data extraction:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'on', ROOT_DIR)
    if forceInsert:
        print('WARNING: Force Insert enabled.')

    CON_DATA = json.loads(open(CONTINUOUS_CONFIG).read())

    stations = CON_DATA['stations']

    metaData = {
        'station': '',
        'variable': '',
        'unit': '',
        'type': '',
        'source': '',
        'name': '',
    }
    adapter = MySQLAdapter(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)

    for station in stations :
        print('station:', station)
        #  Check whether station exists
        is_station_exists = adapter.get_station({'name': station['name']})
        if is_station_exists is None:
            print('Station %s does not exists.', station['name'])
            if 'station_meta' in station and 'station_type' in station:
                station_meta = station['station_meta']
                station_meta.insert(0, Station.getType(station['station_type']))
                row_count = adapter.create_station(station_meta)
                if row_count > 0:
                    print('Created new station %s', station_meta)
                    is_station_exists = adapter.get_station({'name': station['name']})
                else:
                    print("Unable to create station %s", station_meta)
                    continue
            else:
                print("Could not find station meta data or station_type to create new ", station['name'])
                continue

        dataLocation = station['data_location']
        timeseries = getTimeseries(dataLocation, {
            'root_dir': ROOT_DIR,
            'common_date_format': COMMON_DATE_FORMAT
        })

        if len(timeseries) < 1:
            print('INFO: Timeseries does not have any data.')
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
        if 'run_name' in station:
            meta['name'] = station['run_name']

        for i in range(0, len(variables)):
            meta['variable'] = variables[i]
            meta['unit'] = units[i]
            print('meta', meta)
            eventId = adapter.get_event_id(meta)
            if eventId is None :
                eventId = adapter.create_event_id(meta)
                print('HASH SHA256 created: ', eventId)
            else :
                print('HASH SHA256 exists: ', eventId)
                metaQuery = copy.deepcopy(metaData)
                metaQuery['station'] = station['name']
                metaQuery['type'] = station['type']
                metaQuery['source'] = station['source']
                metaQuery['variable'] = variables[i]
                metaQuery['unit'] = units[i]
                if 'run_name' in station:
                    metaQuery['name'] = station['run_name']
                opts = {
                    'from': startDateTime.strftime(COMMON_DATE_FORMAT),
                    'to': endDateTime.strftime(COMMON_DATE_FORMAT)
                }
                print('metaQuery', metaQuery)
                existingTimeseries = adapter.retrieve_timeseries(metaQuery, opts)
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

            rowCount = adapter.insert_timeseries(eventId, newTimeseries, forceInsert)
            print('%s rows inserted.\n' % rowCount)


except Exception as e:
    traceback.print_exc()
    print(e)
finally:
    os.chdir(INIT_DIR)
