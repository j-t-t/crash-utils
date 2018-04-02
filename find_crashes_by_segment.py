import argparse
import pyproj
from shapely.geometry import Point
import data.util as util
import os

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("datadir", type=str,
                        help="Path to crash modeling data directory")
    parser.add_argument("address", type=str,
                        help="Address you want to look up crashes for")
    
    args = parser.parse_args()

    address = util.geocode_address(args.address)
    combined_seg, segments_index = util.read_segments(
        dirname=os.path.join(args.datadir, 'processed/maps'))

    if address:
        print address
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
            crashes, crash_data = util.group_json_by_location(
                os.path.join(args.datadir, 'processed', 'crash_joined.json'),
                years=[2016], yearfield='Date Time')
            
            if str(near_id) in crash_data.keys():
                print str(crash_data[str(near_id)]['count']) + " crashes found"




