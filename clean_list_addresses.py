import argparse
import csv
import geocoder


def geocode_row(row):

    street_key = None
    neighborhood_key = None
    zip_key = None
    city_key = None
    for k in list(row.keys()):
        if 'Street' in k:
            street_key = k
        elif 'Neighborhood' in k:
            neighborhood_key = k
        elif 'Zip' in k:
            zip_key = k
        elif 'city' in k:
            city_key = k

    address = row[street_key]
    city_or_zip = False
    if neighborhood_key:
        address += ' ' + row[neighborhood_key]
    elif city_key:
        address += ' ' + row[city_key]
        city_or_zip = True
    if row[zip_key]:
        address += ' ' + row[zip_key]
        city_or_zip = True
    # Assume Cambridge if City or Zip not given
    # This may lead to some false positives on coordinates
    if not city_or_zip:
        address += ' Cambridge, MA USA'

    # g = geocoder.google(address)
    g = geocoder.here(
        address,
        app_id=''
        app_code='')

    import ipdb; ipdb.set_trace()

    if g.status != 'OK':
        return None, None, None
    elif g.json:
        return g.json['lat'], g.json['lng'], 'Y'
    return None, None, 'F'


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("csvfile", help="csv file of mailing addresses")
    parser.add_argument("outputfile", help="name of the output csv file")

    args = parser.parse_args()

    # There are two possible formats
    # One has a Street Address, maybe Neighborhood, and Zip code
    # One has Street, City, and Zip
    updated_lines = {}

    # If spreadsheet doesn't have 'geocoded', 'updated_lat', and 'updated_lon'
    # add them
    cutoff = 10
    count = 0
    updated_rows = []
    with open(args.csvfile) as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:

            # If the spreadsheet hadn't had geocoded attempted, do it
            if ('geocoded' not in list(row.keys()) or not row['geocoded']):

                lat = None
                lon = None
                geocoded = None
                # Only geocode a smaller number to not abuse api limits
                if count < cutoff:

                    lat, lon, geocoded = geocode_row(row)
                    count += 1

                row['Geocoded Latitude'] = lat if lat else ''
                row['Geocoded Longitude'] = lon if lon else ''
                row['geocoded'] = geocoded if geocoded else ''

            updated_rows.append(row)

    # Write resulting file
    if updated_rows:
        header = updated_rows[0].keys()

        with open(args.outputfile, 'w') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=header)
            writer.writeheader()
            for r in updated_rows:
                writer.writerow(r)

    else:
        print("No rows found")
