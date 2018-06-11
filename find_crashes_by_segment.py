import argparse
import pyproj
from shapely.geometry import Point
import data.util as util
import os
import json
from dateutil.parser import parse


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("datadir", type=str,
                        help="Path to crash modeling data directory")
    parser.add_argument("-a", "--address", type=str,
                        help="Address you want to look up crashes for")
    parser.add_argument("-d", "--date", type=str,
                        help="Date you want to look up crashes for." +
                        "Needs either address or date")
    
    args = parser.parse_args()

    crash_items = json.load(open(os.path.join(
        args.datadir, 'processed', 'crash_joined.json')))

    if args.address:
        address = util.geocode_address(args.address)
        combined_seg, segments_index = util.read_segments(
            dirname=os.path.join(args.datadir, 'processed/maps'))

        if address:
            print(address)
            # For now, need to get the address into the record type that
            # util.find_nearest needs.  Eventually this should be cleaned up
            inproj = pyproj.Proj(init='epsg:4326')
            outproj = pyproj.Proj(init='epsg:3857')

            re_point = pyproj.transform(
                inproj, outproj, address[2], address[1])
            point = Point(re_point)

            record = [{'point': point,
                       'properties': {}}]
            util.find_nearest(record, combined_seg, segments_index, 20)

            if record[0]['properties']['near_id']:
                near_id = record[0]['properties']['near_id']

                crashes, crash_data = util.group_json_by_location(crash_items)#years=[2015, 2016, 2017], yearfield='Date Time')
                import ipdb; ipdb.set_trace()

                if str(near_id) in list(crash_data.keys()):
                    print(str(crash_data[str(near_id)]['count']) + " crashes found")

    elif args.date:
        print(parse(args.date))
        results = [crash for crash in crash_items if parse(
            crash['dateOccurred']).date() == parse(args.date).date()]
        for r in results:
            print(r['location'])

    else:
        print("Need to give either address or date")


