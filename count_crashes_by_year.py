from dateutil.parser import parse
import csv
import argparse
import json


def count_csv(csvfile, datecol, start_year, end_year):
    count = 0
    with open(csvfile) as f:
        csv_reader = csv.DictReader(f)
        for r in csv_reader:
            if r[datecol]:
                year = parse(r[datecol]).year
                if (not start_year or year >= int(start_year)) \
                   and (not end_year or year <= int(end_year)):
                    count += 1
    print "count for " + csvfile + ":" + str(count)


def count_json(jsonfile, datecol, start_year, end_year):
    count = 0
    with open(jsonfile) as data_file:
        data = json.load(data_file)
        for d in data:
            
            if d[datecol]:
                year = parse(d[datecol]).year
                if (not start_year or year >= int(start_year)) \
                   and (not end_year or year <= int(end_year)):
                    count += 1
    print "count for " + jsonfile + ":" + str(count)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("csvfile", help="csv crash file")
    parser.add_argument("jsonfile", help="json crash file")
    parser.add_argument("datecol", help="name of the column with date")
    parser.add_argument("-s", "--start_year")
    parser.add_argument("-e", "--end_year")

    args = parser.parse_args()
    count_csv(args.csvfile, args.datecol, args.start_year, args.end_year)
    count_json(args.jsonfile, args.datecol, args.start_year, args.end_year)
