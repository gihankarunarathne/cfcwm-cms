import requests
import copy
import json
import os
import logging
from datetime import datetime


# from ..config import Constants as con

def get_weather_station_data_format():
    script_path = os.path.dirname(os.path.realpath(__file__))
    return json.loads(open(os.path.join(script_path, './WeatherStation.json')).read())


def get_dialog_timeseries(station):
    # https://apps.ideabiz.lk/weather/WeatherStationData/LocationDataByMac.php?mac=3674010756837033&rows=5000
    base_url = 'https://apps.ideabiz.lk/weather/WeatherStationData/LocationDataByMac.php'
    payload = {
        'mac': station,
        'rows': 5
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
        print(item)
        # Mapping Response to common format
        new_item = copy.deepcopy(common_format)
        # -- DateUTC
        if 'paramValue10_s' in item:
            new_item['DateUTC'] = item['paramValue10_s']
        # -- TemperatureC
        if 'paramValue3_s' in item:
            new_item['TemperatureC'] = item['paramValue3_s']
        # -- PrecipitationMM
        if 'paramValue8_s' in item:
            new_item['PrecipitationMM'] = item['paramValue8_s']

        timeseries.append(new_item)

    return timeseries
    # --END get_timeseries --


def get_wu_timeseries(base_url, station, date):
    payload = {
        'ID': station,
        'day': date.day,
        'month': date.month,
        'year': date.year,
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


def extract_single_variable_timeseries(timeseries, variable, opts=None):
    """
    WUnderground Meta Data structure (1st row)
    [
        'Time', 'TemperatureC', 'DewpointC', 'PressurehPa', 'WindDirection', 'WindDirectionDegrees', 'WindSpeedKMH',
        'WindSpeedGustKMH', 'Humidity', 'HourlyPrecipMM', 'Conditions', 'Clouds', 'dailyrainMM',
        'SolarRadiationWatts/m^2', 'SoftwareType', 'DateUTC'
    ]
    Then Lines follows the data. This function will extract the given variable timeseries
    """
    if opts is None:
        opts = {'WUndergroundMeta': []}
    WUndergroundMeta = opts.get('WUndergroundMeta', [
        'Time', 'TemperatureC', 'DewpointC', 'PressurehPa', 'WindDirection', 'WindDirectionDegrees', 'WindSpeedKMH',
        'WindSpeedGustKMH', 'Humidity', 'HourlyPrecipMM', 'Conditions', 'Clouds', 'dailyrainMM',
        'SolarRadiationWatts/m^2', 'SoftwareType', 'DateUTC'
    ])

    DateUTCIndex = WUndergroundMeta.index('DateUTC')
    TemperatureCIndex = 1
    TemperatureFIndex = -1
    if 'TemperatureC' in WUndergroundMeta:
        TemperatureCIndex = WUndergroundMeta.index('TemperatureC')
    if 'TemperatureF' in WUndergroundMeta:
        TemperatureFIndex = WUndergroundMeta.index('TemperatureF')
    HourlyPrecipMMIndex = 9
    HourlyPrecipInchIndex = -1
    if 'HourlyPrecipMMIndex' in WUndergroundMeta:
        HourlyPrecipMMIndex = WUndergroundMeta.index('HourlyPrecipMM')
    if 'HourlyPrecipInchIndex' in WUndergroundMeta:
        HourlyPrecipInchIndex = WUndergroundMeta.index('HourlyPrecipInch')

    def precipitation(my_timeseries):
        print('precipitation:: HourlyPrecipMM')
        newTimeseries = []
        prevTime = datetime.strptime(timeseries[0][DateUTCIndex], '%Y-%m-%d %H:%M:%S')
        for t in my_timeseries:
            currTime = datetime.strptime(t[DateUTCIndex], '%Y-%m-%d %H:%M:%S')
            gap = currTime - prevTime
            prec = float(t[HourlyPrecipMMIndex])
            if HourlyPrecipInchIndex > -1:
                prec = float(t[HourlyPrecipInchIndex]) * 25.4

            precipitationInGap = float(prec) * gap.seconds / 3600  # If rate per Hour given, calculate for interval
            # if precipitationInGap > 0 :
            #     print('\n', float(t[HourlyPrecipMMIndex]), precipitationInGap)
            newTimeseries.append([t[DateUTCIndex], precipitationInGap])
            prevTime = currTime

        return newTimeseries

    def temperature(my_timeseries):
        print('temperature:: TemperatureC')
        newTimeseries = []
        for t in my_timeseries:
            temp = float(t[TemperatureCIndex])
            if TemperatureFIndex > -1:
                temp = (float(t[TemperatureFIndex]) - 32) * 5 / 9
            newTimeseries.append([t[DateUTCIndex], temp])
        return newTimeseries

    def default(my_timeseries):
        print('default', my_timeseries)
        return []

    variableDict = {
        'Precipitation': precipitation,
        'Temperature': temperature,
    }
    return variableDict.get(variable, default)(timeseries)
    # --END extractSingleTimeseries --


def create_raw_timeseries(adapter, stations, duration, opts):
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

    #  'https://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=IBATTARA2&month=6&day=28&year=2017&format=1'
    BASE_URL = 'https://www.wunderground.com/weatherstation/WXDailyHistory.asp'
    for station in stations:
        print('station:', station)
        #  Check whether station exists
        is_station_exists = adapter.get_station({'name': station['name']})
        if is_station_exists is None:
            logging.warning('Station %s does not exists. Continue with others', station['name'])
            continue

        WUndergroundMeta, *timeseries = get_wu_timeseries(BASE_URL, station['stationId'],
                                                          end_date_time)  # List Destructuring
        DateUTCIndex = WUndergroundMeta.index('DateUTC')

        if len(timeseries) < 1:
            print('INFO: Timeseries does not have any data on :', end_date_time.strftime("%Y-%m-%d"), timeseries)
            continue

        print(timeseries)
        print('Start Date :', timeseries[0][0])
        print('End Date :', timeseries[-1][0])
        startDateTime = datetime.strptime(timeseries[0][0], '%Y-%m-%d %H:%M:%S')
        endDateTime = datetime.strptime(timeseries[-1][0], '%Y-%m-%d %H:%M:%S')
        print(timeseries[:3])
        # continue;

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
                    print('\n')
                    continue

            extractedTimeseries = extract_single_variable_timeseries(timeseries, variables[i], {'WUndergroundMeta': WUndergroundMeta})

            for l in extractedTimeseries[:3] + extractedTimeseries[-2:]:
                print(l)

            rowCount = adapter.insert_timeseries(eventId, extractedTimeseries, force_insert)
            print('%s rows inserted.\n' % rowCount)
