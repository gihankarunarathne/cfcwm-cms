#!/usr/bin/python3

import sys, traceback, csv, json, datetime, getopt
from os.path import join as pjoin

def usage() :
    usageText = """
Usage: ./HECHMSTORGRAPHS.py [-d date] [-h]

-h  Show usage
-d  Date in YYYY-MM. Default is current date.
"""
    print(usageText)


try :
    RGRAPHS_DIR = '/var/www/html/rgraphs'
    # RGRAPHS_DIR = './'

    DISCHARGE_FILE = 'DailyDischarge.csv'
    OBS_FLOW_FILE = './data/DIS/DailyDischargeObs.csv'
    SIM_FLOW_DIR = './data/DIS'
    SIM_FLOW_FILE = 'DailyDischarge.csv'

    OBS_META_LINES = 0
    SIM_META_LINES = 2

    d = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:", ["help", "date="])
    except getopt.GetoptError:          
        usage()                        
        sys.exit(2)                     
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                     
            sys.exit()           
        elif opt in ("-d", "--date"):
            d = arg

    # Default run for current day
    now = datetime.datetime.now()
    if d : # Or taken from first arg for the program
        now = datetime.datetime.strptime(d, '%Y-%m-%d')
    date = now.strftime("%Y-%m-%d")
    
    print('Start with ', date)

    fileName = SIM_FLOW_FILE.split('.', 1)
    fileName = "%s-%s.%s" % (fileName[0], date, fileName[1])
    SIM_FLOW_FILE_PATH = "%s/%s" % (SIM_FLOW_DIR, fileName)

    fileName1 = DISCHARGE_FILE.split('.', 1)
    fileName1 = "%s-%s.%s" % (fileName1[0], date, fileName1[1])
    RGRAPHS_FILE_PATH = "%s/%s" % (RGRAPHS_DIR, fileName1)
    RGRAPHS_CURR_FILE_PATH = "%s/%s" % (RGRAPHS_DIR, DISCHARGE_FILE)

    csvReader = csv.reader(open(SIM_FLOW_FILE_PATH, 'r'), delimiter=',', quotechar='|')
    csvList = list(csvReader)

    csvWriter = csv.writer(open(RGRAPHS_FILE_PATH, 'w'), delimiter=',', quotechar='|')
    csvWriterCurr = csv.writer(open(RGRAPHS_CURR_FILE_PATH, 'w'), delimiter=',', quotechar='|')

    csvWriter.writerow(['Annotation', 'Value' , 'Hydrograph', 'Time'])
    csvWriter.writerow(['Annotation', 'Value' , 'Hydrograph', 'Time'])

    lines = [];
    # Ref: https://support.office.com/en-us/article/DATEVALUE-function-df8b07d4-7761-4a93-bc33-b7471bbff252
    base = datetime.datetime.strptime('1900:01:01 00:00:00', '%Y:%m:%d %H:%M:%S')
    for value in csvList[SIM_META_LINES:]:
        # print('>>> ', value[0], value[1])
        str = value[0].split(' ')
        date = str[0].split(':')
        time = str[1].split(':')
        if(int(time[0]) > 23) :
            time[0] = '23'
            d = datetime.datetime.strptime(str[0] + ' ' + ':'.join(time), '%Y:%m:%d %H:%M:%S')
            d = d + datetime.timedelta(hours=1)
        else :
            d = datetime.datetime.strptime(value[0], '%Y:%m:%d %H:%M:%S')


        serialNumber = (d.timestamp() - base.timestamp())/ (24*60*60)
        # print('         >> ', serialNumber)
        csvWriter.writerow([d.strftime('%m/%d/%y %H:%M:%S'), value[1], 'Hanwella', serialNumber])
        csvWriterCurr.writerow([d.strftime('%m/%d/%y %H:%M:%S'), value[1], 'Hanwella', serialNumber])


except Exception as e :
    traceback.print_exc()
finally:
    print('Completed write ', OBS_FLOW_FILE, ' and ', SIM_FLOW_FILE)
    print('into RGRAPHS_FILE_PATH', RGRAPHS_FILE_PATH, 'RGRAPHS_CURR_FILE_PATH', RGRAPHS_CURR_FILE_PATH)