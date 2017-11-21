import requests
import copy
import json
import os
import logging
from datetime import datetime, timedelta
from curwmysqladapter import Station
from cms_utils import UtilTimeseries, UtilValidation

from observation.config import Constants as Constant


def get_weather_station_data_format():
    script_path = os.path.dirname(os.path.realpath(__file__))
    return json.loads(open(os.path.join(script_path, './WeatherStation.json')).read())


def get_dialog_timeseries(station, start_date_time, end_date_time):
    # https://apps.ideabiz.lk/weather/WeatherStationData/LocationDataByMac.php?mac=3674010756837033&rows=5000
    base_url = 'https://apps.ideabiz.lk/weather/WeatherStationData/LocationDataByMac.php'
    now = datetime.now()
    rows = int((now - start_date_time) / timedelta(seconds=15))
    print('Dialog::need to get %s rows' % rows)
    payload = {
        'mac': station['stationId'],
        'rows': rows
    }
    result = requests.get(base_url, params=payload, allow_redirects=False)
    result = result.text.strip()
    if result.startswith("<pre>") and result.endswith("</pre>"):
        result = result[5:-6]

    try:
        result = json.loads(result)
    except ValueError as e:
        logging.error(e)
        return []

    result = result['response']['docs']
    common_format = get_weather_station_data_format()
    for key in common_format:
        common_format[key] = None
    timeseries = []
    for item in result:
        item_time = datetime.strptime(item['paramValue10_s'], Constant.DATE_TIME_FORMAT)
        if start_date_time <= item_time <= end_date_time:
            # Mapping Response to common format
            new_item = copy.deepcopy(common_format)
            # -- DateUTC
            if 'paramValue10_s' in item:
                new_item['DateUTC'] = item['paramValue10_s']
            # -- TemperatureC
            if 'paramValue3_s' in item:
                new_item['TemperatureC'] = (float(item['paramValue3_s']) - 32) * 5 / 9
            # -- PrecipitationMM
            if 'paramValue8_s' in item:
                new_item['PrecipitationMM'] = item['paramValue8_s']

            timeseries.append(new_item)

    return timeseries
    # --END get_timeseries --


def get_wu_timeseries(station, start_date_time, end_date_time):
    #  'https://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=IBATTARA2&month=6&day=28&year=2017&format=1'
    base_url = 'https://www.wunderground.com/weatherstation/WXDailyHistory.asp'
    payload = {
        'ID': station['stationId'],
        'day': end_date_time.day,
        'month': end_date_time.month,
        'year': end_date_time.year,
        'format': 1
    }
    r = requests.get(base_url, params=payload)
    lines = r.text.replace('<br>', '').split('\n')

    data_lines = []
    for line in lines:
        lineSplit = line.split(',')
        if len(lineSplit) > 1:
            data_lines.append(lineSplit)

    WUndergroundMeta, *data = data_lines
    if len(data) < 1:
        logging.warning('Timeseries does not have any data for station: %s', station['name'])
        return []

    common_format = get_weather_station_data_format()
    for key in common_format:
        common_format[key] = None

    DateUTCIndex = WUndergroundMeta.index('DateUTC')
    TemperatureCFactor = False
    TemperatureCIndex = WUndergroundMeta.index('TemperatureC') if 'TemperatureC' in WUndergroundMeta else None
    if TemperatureCIndex is None:
        TemperatureCIndex = WUndergroundMeta.index('TemperatureF')
        TemperatureCFactor = True
    PrecipitationMMFactor = False
    PrecipitationMMIndex = WUndergroundMeta.index('dailyrainMM') if 'dailyrainMM' in WUndergroundMeta else None
    if PrecipitationMMIndex is None:
        PrecipitationMMIndex = WUndergroundMeta.index('dailyrainInch')
        PrecipitationMMFactor = True

    timeseries = []
    prevPrecipitationMM = float(data[0][PrecipitationMMIndex]) * 25.4 \
        if PrecipitationMMFactor else float(data[0][PrecipitationMMIndex])
    for line in data:
        line_time = datetime.strptime(line[DateUTCIndex], Constant.DATE_TIME_FORMAT)
        if start_date_time <= line_time <= end_date_time:
            # Mapping Response to common format
            new_item = copy.deepcopy(common_format)
            # -- DateUTC
            new_item['DateUTC'] = line[DateUTCIndex]
            # -- TemperatureC
            new_item['TemperatureC'] = (float(line[TemperatureCIndex]) - 32) * 5 / 9 \
                if TemperatureCFactor else float(line[TemperatureCIndex])
            # -- PrecipitationMM
            new_item['PrecipitationMM'] = float(line[PrecipitationMMIndex]) * 25.4 - prevPrecipitationMM \
                if PrecipitationMMFactor else float(line[PrecipitationMMIndex]) - prevPrecipitationMM
            prevPrecipitationMM = float(line[PrecipitationMMIndex]) * 25.4 \
                if PrecipitationMMFactor else float(line[PrecipitationMMIndex])

            timeseries.append(new_item)

    return timeseries
    # --END get_timeseries --


def get_timeseries(station, start_date, end_date):
    if station['run_name'] == 'WUnderground':
        return get_wu_timeseries(station, start_date, end_date)
    elif station['run_name'] == 'Dialog':
        return get_dialog_timeseries(station, start_date, end_date)
    else:
        logging.warning("Unknown host to retrieve the data %s", station['run_name'])
        return []


def create_raw_timeseries(adapter, stations, duration, opts):
    print("""
    *********************************************************
    *   Create Raw Data                                     *
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
        print('station:', station['name'], '(%s)' % station['run_name'])
        #  Check whether station exists
        is_station_exists = adapter.get_station({'name': station['name']})
        if is_station_exists is None:
            logging.warning('Station %s does not exists.', station['name'])
            if 'station_meta' in station:
                station_meta = station['station_meta']
                station_meta.insert(0, Station.CUrW)
                row_count = adapter.create_station(station_meta)
                if row_count > 0:
                    logging.warning('Created new station %s', station_meta)
                else:
                    continue
            else:
                logging.warning('Continue with others', station['name'])
                continue

        timeseries = get_timeseries(station, start_date_time, end_date_time)

        if len(timeseries) < 1:
            print('INFO: Timeseries does not have any data on :', end_date_time.strftime("%Y-%m-%d"), timeseries)
            continue

        print('Start Date :', timeseries[0]['DateUTC'])
        print('End Date :', timeseries[-1]['DateUTC'])
        startDateTime = datetime.strptime(timeseries[0]['DateUTC'], '%Y-%m-%d %H:%M:%S')
        endDateTime = datetime.strptime(timeseries[-1]['DateUTC'], '%Y-%m-%d %H:%M:%S')

        meta = copy.deepcopy(metaData)
        meta['station'] = station['name']
        meta['start_date'] = startDateTime.strftime("%Y-%m-%d %H:%M:%S")
        meta['end_date'] = endDateTime.strftime("%Y-%m-%d %H:%M:%S")

        variables = station['variables']
        units = station['units']
        if 'run_name' in station:
            meta['name'] = station['run_name']
        for i in range(0, len(variables)):
            meta['variable'] = variables[i]
            meta['unit'] = units[i]
            eventId = adapter.get_event_id(meta)
            if eventId is None:
                eventId = adapter.create_event_id(meta)
                print('HASH SHA256 created: ', eventId)
            else:
                print('HASH SHA256 exists: ', eventId)
                metaQuery = copy.deepcopy(metaData)
                metaQuery['station'] = station['name']
                metaQuery['variable'] = variables[i]
                metaQuery['unit'] = units[i]
                if 'run_name' in station:
                    metaQuery['name'] = station['run_name']
                opts = {
                    'from': startDateTime.strftime("%Y-%m-%d %H:%M:%S"),
                    'to': endDateTime.strftime("%Y-%m-%d %H:%M:%S")
                }
                existingTimeseries = adapter.retrieve_timeseries(metaQuery, opts)
                if len(existingTimeseries[0]['timeseries']) > 0 and not force_insert:
                    print('Timeseries already exists. Use force insert to insert data.\n')
                    continue

            extractedTimeseries = UtilTimeseries.extract_single_variable_timeseries(timeseries, variables[i])
            validation_obj = {
                'max_value': station['max_values'][i],
                'min_value': station['min_values'][i],
            }
            extractedTimeseries = UtilValidation.handle_duplicate_values(extractedTimeseries, validation_obj)
            if station['run_name'] == 'Dialog':
                print('Dialog::')
                print(extractedTimeseries)

            for l in extractedTimeseries[:3] + extractedTimeseries[-2:]:
                print(l)

            rowCount = adapter.insert_timeseries(eventId, extractedTimeseries, force_insert)
            print('%s rows inserted.\n' % rowCount)
