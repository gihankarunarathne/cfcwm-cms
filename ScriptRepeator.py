#!/usr/bin/python3

import sys, datetime, traceback, argparse
from subprocess import Popen

try:
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--file-path", help="File name to be executed.")
    parser.add_argument("-s", "--start-date", help="Start Date in YYYY-MM.")
    parser.add_argument("-e", "--end-date", help="End Date in YYYY-MM.")
    parser.add_argument("-i", "--interval", help="Time Interval between two events in hours. Default 24 hours")
    parser.add_argument("-f", "--force", action='store_true', help="Force insert.")
    parser.add_argument("-v", "--version", help="Python version. eg: python3")
    parser.add_argument("--add-end-date", action='store_true', help="Whether to add end date for params")
    parser.add_argument("-m", "--mode", help="One of 'raw' | 'processed' | 'virtual'")
    parser.add_argument("--add-mode", action='store_true', help="Whether to add mode for params")
    args = parser.parse_args()
    print('Commandline Options:', args)

    timeInterval = 24

    if not args.file_path and args.start_date:
        print('All fields required.')
        sys.exit(2)
    if args.interval:
        timeInterval = int(args.interval)

    startDate = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
    endDate = datetime.datetime.strptime(args.end_date, '%Y-%m-%d')

    pythonV = "python"
    if args.version:
        pythonV = args.version

    while startDate <= endDate:
        execList = [pythonV, args.file_path]
        execList = execList + ['-d', startDate.strftime("%Y-%m-%d")]
        if args.force:
            execList = execList + ['-f']
        if args.add_end_date:
            tmpEndDate = startDate + datetime.timedelta(hours=timeInterval-1)
            execList = execList + ['-e', tmpEndDate.strftime("%Y-%m-%d")]
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
    traceback.print_exc()
finally:
    print('Successfully run Script Repeater !.')
