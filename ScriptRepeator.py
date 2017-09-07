#!/usr/bin/python3

import sys, datetime, subprocess, argparse
from subprocess import Popen

try :
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="File name to be executed.")
    parser.add_argument("-s", "--start-date", help="Start Date in YYYY-MM.")
    parser.add_argument("-e", "--end-date", help="End Date in YYYY-MM.")
    args = parser.parse_args()
    print('Commandline Options:', args)

    if not args.file and args.startDate and args.endDate :
        print('All fields required.')
        sys.exit(2)

    startDate = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
    endDate = datetime.datetime.strptime(args.end_date, '%Y-%m-%d')

    while(startDate <= endDate) :
        execList = ["python", args.file]
        execList = execList + ['-d' , startDate.strftime("%Y-%m-%d")]
        print('*********************************************************')
        print('>>>', execList, '\n')
        proc = Popen(execList, stdout=sys.stdout)
        proc.wait()
        print('\n\n')

        startDate = startDate + datetime.timedelta(days=1)

except ValueError:
    raise ValueError("Incorrect data format, should be YYYY-MM-DD")
except Exception as e :
    traceback.print_exc()
finally:
    print('Successfully run Script Repeator !.')