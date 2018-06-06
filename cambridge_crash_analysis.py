import csv
import argparse
import data.util as util
from data.record import Record
import copy
from shapely.geometry import Polygon
import geojson

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("csvfile", help="csv crash file")
    parser.add_argument("outputfile", help="output csv crash file")

    parser.add_argument("-a", "--address", type=str,
                        help="Address you want to look up crashes for")
    parser.add_argument("-latlon", "--latlon", type=str,
                        help="latitude and longitude, comma separated," +
                        "can be used instead of address")

    # Can use minx, miny, maxx, maxy args for bounding box instead of address
    # Example for Inman Square bounding box
    # minx: -71.102359
    # maxx: -71.099945
    # miny: 42.373203
    # maxy: 42.374416
    parser.add_argument("-minx", "--minx", type=str)
    parser.add_argument("-miny", "--miny", type=str)
    parser.add_argument("-maxx", "--maxx", type=str)
    parser.add_argument("-maxy", "--maxy", type=str)
    args = parser.parse_args()

    feats = []
    # Get a large buffer around the intersection address
    intersection = None
    if args.address:
        address = None
        if args.latlon:
            lat, lon = args.latlon.split(',')
            address = args.address, lat, lon
        else:
            address, lat, lon = util.geocode_address(
                args.address)
            
        intersection = Record({
            'location': {'latitude': lat, 'longitude': lon},
            'address': address
        })
        buffer = (intersection.point).buffer(250)

    else:
        # Convert to 3857 projection and get the bounding box
        minx = float(args.minx)
        miny = float(args.miny)
        maxx = float(args.maxx)
        maxy = float(args.maxy)

        poly = geojson.Polygon([[
            [minx, miny],
            [maxx, miny],
            [maxx, maxy],
            [minx, maxy],
            [minx, miny]
        ]])
        feats.append(geojson.Feature(geometry=poly, properties={}))

        p1 = Record({
            'location': {'latitude': miny, 'longitude': minx},
        })
        p2 = Record({
            'location': {'latitude': miny, 'longitude': maxx},
        })
        p3 = Record({
            'location': {'latitude': maxy, 'longitude': maxx},
        })
        p4 = Record({
            'location': {'latitude': maxy, 'longitude': minx},
        })

        buffer = Polygon([
            [p1.point.x, p1.point.y],
            [p2.point.x, p2.point.y],
            [p3.point.x, p3.point.y],
            [p4.point.x, p3.point.y]
        ])

    results = []
    count = 0
    unfixed_count = 0

    street_address_count = 0
    records = []
    fields = []
    with open(args.csvfile) as f:
        csv_reader = csv.DictReader(f)
        for r in csv_reader:

            count += 1

            lat = float(r['Y'])
            lon = float(r['X'])
            records.append(Record({
                'location': {'latitude': lat, 'longitude': lon},
                'address': r['Address'],
                'date': r['DateTime'],
                'type': r['Type'],
                'EMS': r['EMS']
            }))
    fields = records[0].properties.keys()
    print street_address_count

    matches = []
    getcount = 0

    fields = fields + ['X', 'Y']

    with open(args.outputfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fields)
        writer.writeheader()

        for record in records:
            if (record.point).intersects(buffer):
                getcount += 1

                row = copy.deepcopy(record.properties)

                loc = row.pop('location')
                row['Y'] = loc['latitude']
                row['X'] = loc['longitude']
                writer.writerow(row)

    print getcount

