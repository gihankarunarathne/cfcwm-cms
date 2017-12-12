import requests
import copy
import json
import os
import logging
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from curwmysqladapter import Station
from cms_utils import UtilTimeseries, UtilValidation

from observation.config import Constants as Constant

sl_offset = timedelta(hours=5, minutes=30)


def get_weather_station_data_format():
    script_path = os.path.dirname(os.path.realpath(__file__))
    return json.loads(open(os.path.join(script_path, './WeatherStation.json')).read())


def get_dialog_timeseries(station, start_date_time, end_date_time, opts=None):
    if opts is None:
        opts = {}
    if 'dialog_iot_username' not in opts or 'dialog_iot_password' not in opts:
        logging.error("Need Dialog Username & Password in order get data from IoT server.")
        return []

    # https://apps.ideabiz.lk/weather/WeatherStationData/LocationDataByMac.php?mac=3674010756837033&rows=5000
    base_url = 'https://apps.ideabiz.lk/weather/WeatherStationData/getDataByMac.php'
    now = datetime.now()
    rows = int((now - start_date_time) / timedelta(seconds=15))
    print('Dialog::need to get %s rows' % rows)
    payload = {
        'mac': station['stationId'],
        'from': (start_date_time - sl_offset).strftime('%Y-%m-%dT%H:%M:%S'),
        'to': (end_date_time - sl_offset).strftime('%Y-%m-%dT%H:%M:%S'),
    }
    auth = HTTPBasicAuth(opts.get('dialog_iot_username'), opts.get('dialog_iot_password'))
    result = requests.get(base_url, params=payload, allow_redirects=False, auth=auth)
    if not result.ok or result.status_code != 200:
        logging.error("Unable to retrieve data from Dialog.")
        logging.error(result)
        return []

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
        try:
            sl_time = datetime.strptime(item['paramValue10_s'], Constant.DATE_TIME_FORMAT) + sl_offset
            if start_date_time <= sl_time <= end_date_time:
                # Mapping Response to common format
                new_item = copy.deepcopy(common_format)
                # -- DateUTC
                if 'paramValue10_s' in item:
                    new_item['DateUTC'] = item['paramValue10_s']
                # -- Time
                new_item['Time'] = sl_time.strftime(Constant.DATE_TIME_FORMAT)
                # -- TemperatureC
                if 'paramValue3_s' in item:
                    new_item['TemperatureC'] = (float(item['paramValue3_s']) - 32) * 5 / 9
                # -- PrecipitationMM
                if 'paramValue8_s' in item:
                    new_item['PrecipitationMM'] = item['paramValue8_s']

                timeseries.append(new_item)
        except Exception as e:
            logging.error("Error while reading Dialog Data. Continue with next time step.")
            logging.error(e)
            continue

    return timeseries
    # --END get_timeseries --


def get_wu_timeseries(station, start_date_time, end_date_time):
    #  'https://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=IBATTARA2&month=6&day=28&year=2017&format=1'
    base_url = 'https://www.wunderground.com/weatherstation/WXDailyHistory.asp'

    def get_wu_data(date):
        payload = {
            'ID': station['stationId'],
            'day': date.day,
            'month': date.month,
            'year': date.year,
            'format': 1
        }
        r = requests.get(base_url, params=payload)
        lines = r.text.replace('<br>', '').split('\n')

        data_lines = []
        for data_line in lines:
            lineSplit = data_line.split(',')
            if len(lineSplit) > 1:
                data_lines.append(lineSplit)

        if len(data_lines) > 1:
            WUndergroundMeta1, *new_data1 = data_lines
            return {'WUndergroundMeta': WUndergroundMeta1, 'new_data': new_data1}
        else:
            return None

    loop_date = datetime.strptime(start_date_time.strftime("%Y-%m-%d"), "%Y-%m-%d")
    data = []
    WUndergroundMeta = []
    while loop_date <= end_date_time:
        new_data = get_wu_data(loop_date)
        if new_data is not None:
            WUndergroundMeta = new_data.get('WUndergroundMeta')
            data = data + new_data.get('new_data')

        loop_date += timedelta(days=1)

    if len(data) < 1:
        logging.warning('Timeseries does not have any data for station: %s', station['name'])
        return []
    if len(WUndergroundMeta) < 1:
        logging.warning('Timeseries WU Metadata is not valid: %s', station['name'])
        return []

    print('WUndergroundMeta', WUndergroundMeta)
    common_format = get_weather_station_data_format()
    for key in common_format:
        common_format[key] = None

    DateUTCIndex = WUndergroundMeta.index('DateUTC')
    is_temp_in_F = False
    TemperatureCIndex = WUndergroundMeta.index('TemperatureC') if 'TemperatureC' in WUndergroundMeta else None
    if TemperatureCIndex is None:
        TemperatureCIndex = WUndergroundMeta.index('TemperatureF')
        is_temp_in_F = True
    is_precip_in_IN = False
    PrecipitationMMIndex = WUndergroundMeta.index('dailyrainMM') if 'dailyrainMM' in WUndergroundMeta else None
    if PrecipitationMMIndex is None:
        PrecipitationMMIndex = WUndergroundMeta.index('dailyrainin')
        is_precip_in_IN = True

    timeseries = []
    prevPrecipitationMM = float(data[0][PrecipitationMMIndex]) * 25.4 \
        if is_precip_in_IN else float(data[0][PrecipitationMMIndex])
    for line in data:
        sl_time = datetime.strptime(line[DateUTCIndex], Constant.DATE_TIME_FORMAT) + sl_offset
        if start_date_time <= sl_time <= end_date_time:
            # Mapping Response to common format
            new_item = copy.deepcopy(common_format)
            # -- DateUTC
            new_item['DateUTC'] = line[DateUTCIndex]
            # -- Time
            new_item['Time'] = sl_time.strftime(Constant.DATE_TIME_FORMAT)
            # -- TemperatureC
            new_item['TemperatureC'] = (float(line[TemperatureCIndex]) - 32) * 5 / 9 \
                if is_temp_in_F else float(line[TemperatureCIndex])
            # -- PrecipitationMM
            currPrecipitationMM = float(line[PrecipitationMMIndex]) * 25.4 \
                if is_precip_in_IN else float(line[PrecipitationMMIndex])
            if currPrecipitationMM < prevPrecipitationMM and currPrecipitationMM == 0:
                new_item['PrecipitationMM'] = 0
            else:
                new_item['PrecipitationMM'] = currPrecipitationMM - prevPrecipitationMM

            timeseries.append(new_item)
        # Save previous value
        prevPrecipitationMM = float(line[PrecipitationMMIndex]) * 25.4 \
            if is_precip_in_IN else float(line[PrecipitationMMIndex])

    return timeseries
    # --END get_timeseries --


def get_timeseries(station, start_date, end_date, opts):
    if station['run_name'] == 'WUnderground':
        return get_wu_timeseries(station, start_date, end_date)
    elif station['run_name'] == 'Dialog':
        return get_dialog_timeseries(station, start_date, end_date, opts)
    else:
        logging.warning("Unknown host to retrieve the data %s", station['run_name'])
        return []


def create_raw_timeseries(adapter, stations, duration, opts):
    """
    Create Raw Timeseries by retrieving data from given stations

    :param adapter: Instance of MySQLAdapter from curwmysqladapter
    :param stations: List of Station Meta Objects. Refer to config/StationConfig.json
    :param duration: dict(start_date_time=<Datetime>, end_date_time=<Datetime>)
    :param opts: dict of following fields,
    {
        force_insert: True/False,
        dialog_iot_username: "",
        dialog_iot_password: ""
    }
    :return:
    """
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

        timeseries = get_timeseries(station, start_date_time, end_date_time, opts)

        if len(timeseries) < 1:
            print('INFO: Timeseries does not have any data on :', end_date_time.strftime("%Y-%m-%d"), timeseries)
            continue

        print('Start Date :', timeseries[0]['Time'])
        print('End Date :', timeseries[-1]['Time'])
        startDateTime = datetime.strptime(timeseries[0]['Time'], '%Y-%m-%d %H:%M:%S')
        endDateTime = datetime.strptime(timeseries[-1]['Time'], '%Y-%m-%d %H:%M:%S')

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
                query_opts = {
                    'from': startDateTime.strftime("%Y-%m-%d %H:%M:%S"),
                    'to': endDateTime.strftime("%Y-%m-%d %H:%M:%S")
                }
                existingTimeseries = adapter.retrieve_timeseries(metaQuery, query_opts)
                if len(existingTimeseries[0]['timeseries']) > 0 and not force_insert:
                    print('Timeseries already exists. Use force insert to insert data.\n')
                    continue

            extractedTimeseries = UtilTimeseries.extract_single_variable_timeseries(timeseries, variables[i])
            validation_obj = {
                'max_value': station['max_values'][i],
                'min_value': station['min_values'][i],
            }
            extractedTimeseries = UtilValidation.handle_duplicate_values(extractedTimeseries, validation_obj)

            for l in extractedTimeseries[:3] + extractedTimeseries[-2:]:
                print(l)

            rowCount = adapter.insert_timeseries(eventId, extractedTimeseries, force_insert)
            print('%s rows inserted.\n' % rowCount)
