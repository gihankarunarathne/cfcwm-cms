#!/usr/bin/python3

import sys, traceback, csv, json, datetime, getopt, os, copy, requests, argparse

def getTimeseries(location, opts) :
    locationType = location['type']

    def default(metadata) :
        print('Default timeseries')
        return []

    accessDict = {
        'file': getTimeseriesFromFile,
    }
    return accessDict.get(locationType, default)(location, opts)

def getTimeseriesFromFile(location, opts) :
    ROOT_DIR = opts['root_dir']
    COMMON_DATE_FORMAT = opts['common_date_format']
    METADATA_LINES = location['metadata_lines']
    TIMESTAMP_FORMAT = location['timestamp_format']

    filePath = os.path.join(ROOT_DIR, location['location'])
    if not os.path.exists(filePath):
        print('Unable to find file : ', filePath)
        return []

    csvReader = csv.reader(open(filePath, 'r'), delimiter=',', quotechar='|')
    timeseries = list(csvReader)[METADATA_LINES:]

    formattedTimeseries = []
    for t in timeseries :
        dt = datetime.datetime.strptime(t[0], TIMESTAMP_FORMAT)
        value = -999
        # TODO: Read multiple values
        try:
            value = float(t[1])
        except ValueError:
            print("Not a float")

        formattedTimeseries.append([dt.strftime(COMMON_DATE_FORMAT), value])
    return formattedTimeseries

def extractSigleTimeseries(timeseries, variable, opts={'values': []}) :
    '''
    Extract Single Timeseries from Multiple values against single timeseries as below,
    ['Timestamp', 'Precipitation', 'Temperature']
    '''
    ValuesMeta = opts.get('values', ['Timestamp', 'Precipitation', 'Temperature'])

    DateUTCIndex = ValuesMeta.index('Timestamp')
    variableIndex = ValuesMeta.index(variable)

    newTimeseries = []
    for t in timeseries :
        newTimeseries.append([t[DateUTCIndex], t[variableIndex]])

    return newTimeseries
    # --END extractSingleTimeseries --
