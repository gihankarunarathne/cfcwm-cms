#!/usr/bin/python3

import sys, traceback, csv, json, datetime, getopt, os, copy, requests
from curwmysqladapter import MySQLAdapter

def usage() :
    usageText = """
Usage: ./WUnderground.py [-d date] [-h]

-h  --help      Show usage
-d  --date      Date in YYYY-MM. Default is current date.
-b  --backDays  Run forecast specified backDays with respect to current date. Expect an integer.
                When -d is specified, counting from that date.
"""
    print(usageText)

def getTimeseries(BASE_URL, station, date) :
    payload = {
        'ID': station,
        'day': date.day,
        'month': date.month,
        'year': date.year,
        'format': 1
    }
    r = requests.get(BASE_URL, params=payload)
    lines = r.text.replace('<br>', '').split('\n')
    timeseries = []
    for line in lines :
        lineSplit = line.split(',')
        if(len(lineSplit) > 1) :
            timeseries.append(lineSplit)
    # print('>>>> >>>')
    # print(timeseries)
    return timeseries
    # --END get_timeseries --

def extractSigleTimeseries(timeseries, variable, opts={'WUndergroundMeta': []}) :
    '''
    WUnderground Meta Data structure (1st row)
    ['Time', 'TemperatureC', 'DewpointC', 'PressurehPa', 'WindDirection', 'WindDirectionDegrees', 'WindSpeedKMH', 'WindSpeedGustKMH', 'Humidity', 'HourlyPrecipMM', 'Conditions', 'Clouds', 'dailyrainMM', 'SolarRadiationWatts/m^2', 'SoftwareType', 'DateUTC']
    '''
    WUndergroundMeta = opts.get('WUndergroundMeta', ['Time', 'TemperatureC', 'DewpointC', 'PressurehPa', 'WindDirection', 'WindDirectionDegrees', 'WindSpeedKMH', 'WindSpeedGustKMH', 'Humidity', 'HourlyPrecipMM', 'Conditions', 'Clouds', 'dailyrainMM', 'SolarRadiationWatts/m^2', 'SoftwareType', 'DateUTC'])

    DateUTCIndex = WUndergroundMeta.index('DateUTC')
    TemperatureCIndex = 1
    TemperatureFIndex = -1
    if 'TemperatureC' in WUndergroundMeta :
        TemperatureCIndex = WUndergroundMeta.index('TemperatureC')
    if 'TemperatureF' in WUndergroundMeta :
        TemperatureFIndex = WUndergroundMeta.index('TemperatureF')
    HourlyPrecipMMIndex = 9
    HourlyPrecipInchIndex = -1
    if 'HourlyPrecipMMIndex' in WUndergroundMeta:
        HourlyPrecipMMIndex = WUndergroundMeta.index('HourlyPrecipMM')
    if 'HourlyPrecipInchIndex' in WUndergroundMeta:
        HourlyPrecipInchIndex = WUndergroundMeta.index('HourlyPrecipInch')

    def Precipitation(myTimeseries):
        print('Precipitation:: HourlyPrecipMM')
        newTimeseries = []
        prevTime = datetime.datetime.strptime(timeseries[0][DateUTCIndex], '%Y-%m-%d %H:%M:%S')
        for t in myTimeseries :
            currTime = datetime.datetime.strptime(t[DateUTCIndex], '%Y-%m-%d %H:%M:%S')
            gap = currTime - prevTime
            prec = float(t[HourlyPrecipMMIndex])
            if HourlyPrecipInchIndex > -1 :
                prec = float(t[HourlyPrecipInchIndex]) * 25.4

            precipitationInGap = float(prec) * gap.seconds / 3600 # If rate per Hour given, calculate for interval
            # if precipitationInGap > 0 :
            #     print('\n', float(t[HourlyPrecipMMIndex]), precipitationInGap)
            newTimeseries.append([t[DateUTCIndex], precipitationInGap])
            prevTime = currTime

        return newTimeseries

    def Temperature(myTimeseries):
        print('Temperature:: TemperatureC')
        newTimeseries = []
        for t in myTimeseries :
            temp = float(t[TemperatureCIndex])
            if TemperatureFIndex > -1 :
                temp = (float(t[TemperatureFIndex]) - 32) * 5 / 9
            newTimeseries.append([t[DateUTCIndex], temp])
        return newTimeseries

    def default(myTimeseries):
        print('default')
        return []

    variableDict = {
        'Precipitation': Precipitation,
        'Temperature': Temperature,
    }
    return variableDict.get(variable, default)(timeseries)
    # --END extractSingleTimeseries --

def validateTimeseries(timeseries, variable, validation={'max_value': 1000, 'min_value': 0}) :
    '''
    Validate Timeseries against given rules
    '''
    MISSING_VALUE = -999
    MAX_VALUE = float(validation.get('max_value'))
    MIN_VALUE = float(validation.get('min_value'))
    def Precipitation(myTimeseries) :
        print('Precipitation:: Validation')
        newTimeseries = []
        for t in myTimeseries :
            if MIN_VALUE <= t[1] and t[1] <= MAX_VALUE :
                newTimeseries.append(t)
            else :
                newTimeseries.append([t[0], MISSING_VALUE])
        return newTimeseries

    def Temperature(myTimeseries) :
        print('Precipitation:: Validation')
        newTimeseries = []
        for t in myTimeseries :
            if MIN_VALUE <= t[1] and t[1] <= MAX_VALUE :
                newTimeseries.append(t)
            else :
                newTimeseries.append([t[0], MISSING_VALUE])
        return newTimeseries

    def default(myTimeseries) :
        print('default validation')
        return []

    validationDict = {
        'Precipitation': Precipitation,
        'Temperature': Temperature,
    }
    return validationDict.get(variable, default)(timeseries)
    # --END extractSingleTimeseries --


INIT_DIR = './'
try:
    INIT_DIR = os.getcwd()
    ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
    os.chdir(ROOT_DIR)

    CONFIG = json.loads(open(os.path.join(ROOT_DIR, 'CONFIG.json')).read())

    # E.g. 'https://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=IBATTARA2&month=6&day=28&year=2017&format=1'
    BASE_URL = 'https://www.wunderground.com/weatherstation/WXDailyHistory.asp'

    WU_CONFIG="./WU_CONFIG.json"

    MYSQL_HOST="localhost"
    MYSQL_USER="root"
    MYSQL_DB="curw"
    MYSQL_PASSWORD=""

    if 'WU_CONFIG' in CONFIG :
        WU_CONFIG = CONFIG['WU_CONFIG']

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
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:b:f", ["help", "date=", "backDays=", "force"])
    except getopt.GetoptError:          
        usage()                        
        sys.exit(2)                     
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                     
            sys.exit()           
        elif opt in ("-d", "--date"):
            date = arg
        elif opt in ("-b", "--backDays"):
            backDays = int(arg)
        elif opt in ("-f", "--force"):
            forceInsert = True

    # Default run for current day
    now = datetime.datetime.now()
    if date:
        now = datetime.datetime.strptime(date, '%Y-%m-%d')

    print('WUnderground data extraction:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'on', ROOT_DIR)
    if forceInsert:
        print('WARNING: Force Insert enabled')

    WU_DATA = json.loads(open(WU_CONFIG).read())

    stations = WU_DATA['stations']

    metaData = {
        'station': 'Hanwella',
        'variable': 'Precipitation',
        'unit': 'mm',
        'type': 'Observed',
        'source': 'WeatherStation',
        'name': 'WUnderground',
    }
    adapter = MySQLAdapter(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)

    for station in stations :
        print('station:', station)
        WUndergroundMeta, *timeseries = getTimeseries(BASE_URL, station['stationId'], now)  # List Destructuring
        DateUTCIndex = WUndergroundMeta.index('DateUTC')

        if(len(timeseries) < 1): 
            print('INFO: Timeseries doesn\'t have any data on :', now.strftime("%Y-%m-%d"), timeseries)
            continue
        print('Start Date :', timeseries[0][0])
        print('End Date :', timeseries[-1][0])
        startDateTime = datetime.datetime.strptime(timeseries[0][0], '%Y-%m-%d %H:%M:%S')
        endDateTime = datetime.datetime.strptime(timeseries[-1][0], '%Y-%m-%d %H:%M:%S')
        print(timeseries[:3])
        # continue;

        meta = copy.deepcopy(metaData)
        meta['station'] = station['name']
        meta['start_date'] = startDateTime.strftime("%Y-%m-%d %H:%M:%S")
        meta['end_date'] = endDateTime.strftime("%Y-%m-%d %H:%M:%S")

        variables = station['variables']
        units = station['units']
        max_values = station['max_values']
        min_values = station['min_values']
        if 'run_name' in station :
            meta['name'] = station['run_name']
        for i in range(0, len(variables)) :
            meta['variable'] = variables[i]
            meta['unit'] = units[i]
            eventId = adapter.get_event_id(meta)
            if eventId is None :
                eventId = adapter.create_event_id(meta)
                print('HASH SHA256 created: ', eventId)
            else :
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
                if len(existingTimeseries[0]['timeseries']) > 0 and not forceInsert:
                    print('\n')
                    continue

            extractedTimeseries = extractSigleTimeseries(timeseries, variables[i], {'WUndergroundMeta': WUndergroundMeta})
            validationObj = {
                'max_value': max_values[i],
                'min_value': min_values[i],
            }
            newTimeseries = validateTimeseries(extractedTimeseries, variables[i], validationObj)
            # print(newTimeseries[:20])
            # continue

            for l in newTimeseries[:3] + newTimeseries[-2:] :
                print(l)

            rowCount = adapter.insert_timeseries(eventId, newTimeseries, forceInsert)
            print('%s rows inserted.\n' % rowCount)


except Exception as e :
    traceback.print_exc()
finally:
    os.chdir(INIT_DIR)
