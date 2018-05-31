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
        print lat
        print lon
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

#        import ipdb; ipdb.set_trace()

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
    with open(args.csvfile) as f:
        csv_reader = csv.DictReader(f)
        for r in csv_reader:

            count += 1

            location = r['Location']
            lines = location.split('\n')
            latitude = ''
            longitude = ''

            address = lines[0]
            latitude = r['Y']
            longitude = r['X']

            cyclist = ''
            pedestrian = ''
            if r['P2 Non Motorist Desc'] == 'CYCLIST' \
               or ['P1 Non Motorist Desc'] == 'CYCLIST' \
               or r['V1 Most Harmful Event'] == 'COLLISION WITH PEDALCYCLE' \
               or r['First Harmful Event'] == 'COLLISION WITH PEDALCYCLE' \
               or r['V1 First Event'] == 'COLLISION WITH PEDALCYCLE' \
               or r['P1 Non Motorist Location'] == 'CYCLIST':
                cyclist = 'Y'
            elif r['P2 Non Motorist Desc'] == 'PEDESTRIAN' or r['P2 Non Motorist Desc'] == 'PEDESTRIAN' or r['V1 Most Harmful Event'] == 'COLLISION WITH PEDESTRIAN' or r['V1 First Event'] == 'COLLISION WITH PEDESTRIAN' or r['First Harmful Event'] == 'COLLISION WITH PEDESTRIAN' or r['P1 Non Motorist Location'] == 'PEDESTRIAN':
                pedestrian = 'Y'
            import ipdb; ipdb.set_trace()
            record = r
            record['location'] = {'latitude': latitude, 'longitude': longitude}
            records.append(Record({
                'location': {'latitude': latitude, 'longitude': longitude},
                'address': address,
                'bk': location,
                'date': r['Date Time'],
                'cyclist': cyclist,
                'pedestrian': pedestrian,
            }))

    print street_address_count

    matches = []
    getcount = 0

    header = ['address', 'date', 'X', 'Y', 'cyclist', 'pedestrian']
    with open(args.outputfile, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()

        for record in records:
            if (record.point).intersects(buffer):
                print record.properties['bk']
                print record.properties['date']
                getcount += 1
                import ipdb; ipdb.set_trace()

                row = copy.deepcopy(record.properties)
                row.pop('bk')
                loc = row.pop('location')
                row['Y'] = loc['latitude']
                row['X'] = loc['longitude']
                writer.writerow(row)

#                feats.append(geojson.Feature(
#                    geometry=geojson.Point([float(row['X']), float(row['Y'])]),
#                    properties={}
#                ))
#            import ipdb; ipdb.set_trace()

    
#        record_buffer_bounds = record_point.buffer(tolerance).bounds
#        nearby_segments = segments_index.intersection(record_buffer_bounds)

#    print "fixed:" + str(fixed_count)
#    print "poor:" + str(poor_details)
    print getcount

#    featcoll = geojson.FeatureCollection(feats)
#    with open('buff.geojson', 'w') as outfile:
#        geojson.dump(featcoll, outfile)