#!/usr/bin/python3

import sys, traceback, csv, json, datetime, getopt, os, copy, requests
from curwmysqladapter import mysqladapter

def usage() :
    usageText = """
Usage: ./HECHMSTORGRAPHS.py [-d date] [-h]

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
    # --END getTimeseries --

def extractSigleTimeseries(timeseries, variable, opts={'WUndergroundMeta': []}) :
    '''
    WUnderground Meta Data structure (1st row)
    ['Time', 'TemperatureC', 'DewpointC', 'PressurehPa', 'WindDirection', 'WindDirectionDegrees', 'WindSpeedKMH', 'WindSpeedGustKMH', 'Humidity', 'HourlyPrecipMM', 'Conditions', 'Clouds', 'dailyrainMM', 'SolarRadiationWatts/m^2', 'SoftwareType', 'DateUTC']
    '''
    WUndergroundMeta = opts.get('WUndergroundMeta', [])
    print('MMMM', WUndergroundMeta)
    DateUTCIndex = WUndergroundMeta.index('DateUTC')
    TemperatureCIndex = 1
    TemperatureFIndex = 0
    if 'TemperatureC' in WUndergroundMeta :
        TemperatureCIndex = WUndergroundMeta.index('TemperatureC')
    if 'TemperatureF' in WUndergroundMeta :
        TemperatureFIndex = WUndergroundMeta.index('TemperatureF')
    HourlyPrecipMMIndex = WUndergroundMeta.index('HourlyPrecipMM')

    def Precipitation(myTimeseries):
        print('Precipitation:: HourlyPrecipMM')
        newTimeseries = []
        prevTime = datetime.datetime.strptime(timeseries[0][DateUTCIndex], '%Y-%m-%d %H:%M:%S')
        for t in myTimeseries :
            currTime = datetime.datetime.strptime(t[DateUTCIndex], '%Y-%m-%d %H:%M:%S')
            gap = currTime - prevTime
            precipitationInGap = float(t[HourlyPrecipMMIndex]) * gap.seconds / 3600 # If rate per Hour given, calculate for interval
            # if precipitationInGap > 0 :
            #     print('\n', float(t[HourlyPrecipMMIndex]), precipitationInGap)
            newTimeseries.append([t[DateUTCIndex], precipitationInGap])
            prevTime = currTime

        return newTimeseries

    def Temperature(myTimeseries):
        print('Temperature:: TemperatureC')
        newTimeseries = []
        for t in myTimeseries :
            temp = t[TemperatureCIndex]
            if TemperatureFIndex :
                temp = (temp - 32) * 5 / 9
            newTimeseries.append([t[DateUTCIndex], temp])
        return newTimeseries

    def default(myTimeseries):
        print('default')

    variableDict = {
        'Precipitation': Precipitation,
        'Temperature': Temperature,
    }
    return variableDict.get(variable, default)(timeseries)
    # --END extractSingleTimeseries --

try:
    CONFIG = json.loads(open('CONFIG.json').read())
    INIT_DIR = os.getcwd()
    # E.g. 'https://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=IBATTARA2&month=6&day=28&year=2017&format=1'
    BASE_URL = 'https://www.wunderground.com/weatherstation/WXDailyHistory.asp'

    MYSQL_HOST="localhost"
    MYSQL_USER="root"
    MYSQL_DB="curw"
    MYSQL_PASSWORD=""

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
    if date :
        now = datetime.datetime.strptime(date, '%Y-%m-%d')

    ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
    os.chdir(ROOT_DIR)

    print('WUnderground data extraction:', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'on', ROOT_DIR)
    if forceInsert :
        print('WARNING: Force Insert enabled')

    stations = ['IBATTARA2', 'IBATTARA3', 'IBATTARA4']
    variables = ['Precipitation', 'Temperature']
    units = ['mm', 'oC']

    metaData = {
        'station': 'Hanwella',
        'variable': 'Precipitation',
        'unit': 'mm',
        'type': 'Observed',
        'source': 'WeatherStation',
        'name': 'Baththaramulla',
    }
    adapter = mysqladapter(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)

    for station in stations :
        WUndergroundMeta, *timeseries = getTimeseries(BASE_URL, station, now) # List Destructuring
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
        meta['station'] = station
        meta['start_date'] = startDateTime.strftime("%Y-%m-%d %H:%M:%S")
        meta['end_date'] = endDateTime.strftime("%Y-%m-%d %H:%M:%S")

        for i in range(0, len(variables)) :
            meta['variable'] = variables[i]
            meta['unit'] = units[i]
            eventId = adapter.getEventId(meta)
            if eventId is None :
                eventId = adapter.createEventId(meta)
                print('HASH SHA256 created: ', eventId)
            else :
                print('HASH SHA256 exists: ', eventId)
                metaQuery = copy.deepcopy(metaData)
                metaQuery['station'] = station
                opts = {
                    'from': startDateTime.strftime("%Y-%m-%d %H:%M:%S"),
                    'to': endDateTime.strftime("%Y-%m-%d %H:%M:%S")
                }
                existingTimeseries = adapter.retrieveTimeseries(metaQuery, opts)
                if len(existingTimeseries[0]['timeseries']) > 0 and not forceInsert:
                    print('\n')
                    continue

            newTimeseries = extractSigleTimeseries(timeseries, variables[i], {'WUndergroundMeta': WUndergroundMeta})
            # print(newTimeseries)
            # continue

            for l in newTimeseries[:3] + newTimeseries[-2:] :
                print(l)

            rowCount = adapter.insertTimeseries(eventId, newTimeseries, forceInsert)
            print('%s rows inserted.\n' % rowCount)


except Exception as e :
    traceback.print_exc()
finally:
    os.chdir(INIT_DIR)