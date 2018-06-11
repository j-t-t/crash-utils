import csv
import argparse
import re
import data.util as util

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
            if count == 0 and 'X' not in list(r.keys()):
                header = list(r.keys()) + ['X', 'Y']

            location = r['Location']
            lines = location.split('\n')
            latitude = ''
            longitude = ''

            # If it's not a numbered street address, need to parse address
            if not re.match('[0-9]+', lines[0]):
                street1 = None
                street2 = None
                if ' &amp; ' in lines[0]:
                    street1, street2 = lines[0].split(' &amp; ')
                elif r['Street Name'] and r['Cross Street']:
                    street1 = r['Street Name']
                    street2 = r['Cross Street']
                else:
                    pass
                if street1 and street2:
                    if count < 200:
                        address = util.geocode_address(
                            street1 + " & " + street2 + " Cambridge, MA")
                        latitude = address[1]
                        longitude = address[2]
                        print(address)
                        print(count)
                    count += 1
            else:
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

