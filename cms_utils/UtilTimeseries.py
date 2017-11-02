import sys, traceback, csv, json, datetime, getopt, os, copy, requests, argparse, re


def get_timeseries(location, opts):
    location_type = location['type']

    def default():
        print('Default timeseries')
        return []

    accessDict = {
        'file': get_timeseries_from_file,
    }
    return accessDict.get(location_type, default)(location, opts)


def get_timeseries_from_file(location, opts):
    ROOT_DIR = opts['root_dir']
    COMMON_DATE_FORMAT = opts['common_date_format']
    METADATA_LINES = location['metadata_lines']
    TIMESTAMP_FORMAT = location['timestamp_format']
    UTC_OFFSET = location['utc_offset']
    offsetPattern = re.compile("[+-]\d\d:\d\d")
    match = offsetPattern.match(UTC_OFFSET)
    if match:
        UTC_OFFSET = match.group()
    else:
        print("UTC_OFFSET :", UTC_OFFSET, " not in correct format. Using +00:00")
        UTC_OFFSET = "+00:00"

    utcOffset = datetime.timedelta()
    if UTC_OFFSET[0] == "-":  # If timestamp in negtive zone, add it to current time
        offsetStr = UTC_OFFSET[1:].split(':')
        utcOffset = datetime.timedelta(hours=int(offsetStr[0]), minutes=int(offsetStr[1]))
    if UTC_OFFSET[0] == "+":  # If timestamp in positive zone, deduct it to current time
        offsetStr = UTC_OFFSET[1:].split(':')
        utcOffset = datetime.timedelta(hours=-1 * int(offsetStr[0]), minutes=-1 * int(offsetStr[1]))

    filePath = os.path.join(ROOT_DIR, location['location'])
    if not os.path.exists(filePath):
        print('Unable to find file : ', filePath)
        return []

    csvReader = csv.reader(open(filePath, 'r'), delimiter=',', quotechar='|')
    timeseries = list(csvReader)[METADATA_LINES:]

    formattedTimeseries = []
    for t in timeseries:
        dt = datetime.datetime.strptime(t[0], TIMESTAMP_FORMAT)
        dtUTC = dt + utcOffset
        value = -999
        # TODO: Read multiple values
        try:
            value = float(t[1])
        except ValueError:
            print("Not a float")

        formattedTimeseries.append([dtUTC.strftime(COMMON_DATE_FORMAT), value])
    return formattedTimeseries


def extract_single_timeseries(timeseries, variable, opts=None):
    """
    Extract Single Timeseries from Multiple values against single timeseries as below,
    ['Timestamp', 'Precipitation', 'Temperature']
    """
    if opts is None:
        opts = {'values': []}
    ValuesMeta = opts.get('values', ['Timestamp', 'Precipitation', 'Temperature'])

    DateUTCIndex = ValuesMeta.index('Timestamp')
    variableIndex = ValuesMeta.index(variable)

    newTimeseries = []
    for t in timeseries:
        newTimeseries.append([t[DateUTCIndex], t[variableIndex]])

    return newTimeseries
    # --END extractSingleTimeseries --
