#!/usr/bin/python3

import argparse
import datetime
import sys
import traceback
from subprocess import Popen

try:
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--file-path", help="File name to be executed.", required=True)
    parser.add_argument("-s", "--start-date", help="Start Date in YYYY-MM.", required=True)
    parser.add_argument("--start-time", help="Start Time in HH:MM:SS.")
    parser.add_argument("-e", "--end-date", help="End Date in YYYY-MM.", required=True)
    parser.add_argument("--end-time", help="End Time in HH:MM:SS.")
    parser.add_argument("-i", "--interval", help="Time Interval between two events in hours. Default 24 hours")
    parser.add_argument("-f", "--force", action='store_true', help="Force insert.")
    parser.add_argument("-v", "--version", help="Python version. eg: python3")
    parser.add_argument("--add-start-date", action='store_true', help="Whether to add start date for params")
    parser.add_argument("--add-end-date", action='store_true', help="Whether to add end date for params")
    parser.add_argument("-m", "--mode", help="One of 'all' | 'raw' | 'processed' | 'virtual'")
    parser.add_argument("--add-mode", action='store_true', help="Whether to add mode for params")
    args = parser.parse_args()
    print('Commandline Options:', args)

    timeInterval = 24

    if args.interval:
        timeInterval = int(args.interval)

    startDate = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
    if args.start_time:
        startDate = datetime.datetime.strptime('%s %s' % (args.start_date, args.start_time), '%Y-%m-%d %H:%M:%S')
    endDate = datetime.datetime.strptime(args.end_date, '%Y-%m-%d')
    if args.end_time:
        endDate = datetime.datetime.strptime('%s %s' % (args.end_date, args.end_time), '%Y-%m-%d %H:%M:%S')

    pythonV = "python"
    if args.version:
        pythonV = args.version

    while startDate <= endDate:
        execList = [pythonV, args.file_path]
        if args.add_start_date:
            execList = execList + ['-s', startDate.strftime("%Y-%m-%d")]
            execList = execList + ['--start-time', startDate.strftime("%H:%M:%S")]
        else:
            execList = execList + ['-d', startDate.strftime("%Y-%m-%d")]

        if args.force:
            execList = execList + ['-f']
        if args.add_end_date:
            tmpEndDate = startDate + datetime.timedelta(hours=timeInterval)
            execList = execList + ['-e', tmpEndDate.strftime("%Y-%m-%d")]
            execList = execList + ['--end-time', tmpEndDate.strftime("%H:%M:%S")]
        if args.add_mode:
            execList = execList + ['-m', args.mode]
        print('*********************************************************')
        print('>>>', execList, '\n')
        proc = Popen(execList, stdout=sys.stdout)
        proc.wait()
        print('\n\n')

        startDate = startDate + datetime.timedelta(hours=timeInterval)

except ValueError:
    raise ValueError("Incorrect data format, should be YYYY-MM-DD")
except Exception as e:
    print(e)
    traceback.print_exc()
finally:
    print('Successfully run Script Repeater !.')
