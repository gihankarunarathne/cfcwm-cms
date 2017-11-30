import copy
import logging

from curwmysqladapter import Data
from cms_utils.UtilValidation import validate_timeseries
from cms_utils.UtilInterpolation import interpolate_timeseries
from cms_utils.InterpolationStrategy import InterpolationStrategy
# from ..config import Constants as con


def get_interpolated_timeseries(timeseries, variable):
    if variable == 'Precipitation':
        return interpolate_timeseries(InterpolationStrategy.Summation, timeseries)
    elif variable == 'Temperature':
        return interpolate_timeseries(InterpolationStrategy.Average, timeseries)
    else:
        logging.error('Unable to handle variable type: %s', variable)
        return []


def create_processed_timeseries(adapter, stations, duration, opts):
    print("""
    *********************************************************
    *   Create Processed Data                               *
    *********************************************************
    """)
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
        print('\n**************** STATION **************')
        print('station:', station['name'])
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
            validated_timeseries = validate_timeseries(rawTimeseries, validationObj)
            filled_timeseries = get_interpolated_timeseries(validated_timeseries, variables[i])

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

            print('Interpolated Timeseries::')
            for l in filled_timeseries[:2] + filled_timeseries[-2:]:
                print(l)

            rowCount = \
                adapter.insert_timeseries(eventId, filled_timeseries, upsert=force_insert, mode=Data.processed_data)
            print('%s rows inserted.\n' % rowCount)
