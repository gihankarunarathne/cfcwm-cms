import copy
import logging

from curwmysqladapter import Data
from cms_utils.UtilValidation import validate_timeseries
# from ..config import Constants as con


def create_processed_timeseries(adapter, stations, duration, opts):
    start_date_time = duration.get('start_date_time', None)
    end_date_time = duration.get('end_date_time', None)
    force_insert = opts.get('force_insert', False)

    metaData = {
        'station': 'Hanwella',
        'variable': 'Precipitation',
        'unit': 'mm',
        'type': 'Observed',
        'source': 'WeatherStation',
        'name': 'WUnderground',
    }

    for station in stations:
        print('station:', station)
        #  Check whether station exists
        is_station_exists = adapter.get_station({'name': station['name']})
        if is_station_exists is None:
            logging.warning('Station %s does not exists. Continue with others', station['name'])
            continue

        meta = copy.deepcopy(metaData)
        meta['station'] = station['name']

        variables = station['variables']
        units = station['units']
        max_values = station['max_values']
        min_values = station['min_values']
        if 'run_name' in station:
            meta['name'] = station['run_name']
        for i in range(0, len(variables)):
            meta['variable'] = variables[i]
            meta['unit'] = units[i]
            # Get Existing Raw Data
            eventId = adapter.get_event_id(meta)
            opts = {
                'from': start_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'to': end_date_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            rawTimeseries = adapter.retrieve_timeseries(meta, opts)
            if len(rawTimeseries) and len(rawTimeseries[0]['timeseries']) > 0:
                rawTimeseries = rawTimeseries[0]['timeseries']
            else:
                print('INFO: Timeseries does not have any data on :', end_date_time.strftime("%Y-%m-%d"), rawTimeseries)
                continue

            validationObj = {
                'max_value': max_values[i],
                'min_value': min_values[i],
            }
            validatedTimeseries = validate_timeseries(rawTimeseries, validationObj)

            # Check whether processed timeseries exists
            new_opts = {
                'from': start_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'to': end_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                'mode': Data.processed_data,
            }
            existingTimeseries = adapter.retrieve_timeseries(meta, new_opts)
            if len(existingTimeseries) and len(existingTimeseries[0]['timeseries']) > 0 and not force_insert:
                print('\n')
                continue

            for l in validatedTimeseries[:3] + validatedTimeseries[-2:]:
                print(l)

            rowCount = \
                adapter.insert_timeseries(eventId, validatedTimeseries, upsert=force_insert, mode=Data.processed_data)
            print('%s rows inserted.\n' % rowCount)
