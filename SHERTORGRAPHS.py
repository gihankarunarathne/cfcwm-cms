#!/usr/bin/python3

import sys, traceback, csv, json, datetime, getopt

def usage() :
    usageText = """
Usage: ./SHERTORGRAPHS.py [-s Start_Date_time] [-e End_Date_Time] [-h]

-h  Show usage
-s  Start Date in YYYY-MM-DD:HH-MM. Required
-e  End Date in YYYY-MM-DD:HH-MM. Required
"""
    print(usageText)


try :
    OBS_FLOW_FILE = './SHER/ObsFlowHanwella-2016.csv'
    SIM_FLOW_FILE = './SHER/ComFlowHanwella-2016.csv'

    try:
        startDateTime = '';               
        endDateTime = '';

        opts, args = getopt.getopt(sys.argv[1:], "hs:e:", ["help", "start=", "end="])
    except getopt.GetoptError:          
        usage()                        
        sys.exit(2)                     
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                     
            sys.exit()                
        elif opt in ("-s", "--start"):
            startDateTime = arg
        elif opt in ("-e", "--end"):
            endDateTime = arg

    print('Start with ', startDateTime, endDateTime)

except Exception as e :
    traceback.print_exc()
finally:
    print('Completed ', OBS_FLOW_FILE, ' and ', SIM_FLOW_FILE)