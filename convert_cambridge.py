import csv
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("csvfile", help="csv crash file")
    parser.add_argument("outputfile", help="output csv crash file")
    args = parser.parse_args()

    results = []
    header = []
    count = 0
    with open(args.csvfile) as f:
        csv_reader = csv.DictReader(f)
        for r in csv_reader:
            if count == 0:
                header = r.keys() + ['X', 'Y']
            count += 1
            location = r['Location']
            lines = location.split('\n')
            latlong = lines[len(lines)-1]
            latitude, longitude = lines[-1][1:-1].split(', ')

            r['X'] = longitude
            r['Y'] = latitude

            results.append(r)

    with open(args.outputfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
