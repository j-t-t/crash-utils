import argparse
import json

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("jsonfile", help="json see click fix file")
    args = parser.parse_args()

    count = 0
    with open(args.jsonfile) as data_file:
        data = json.load(data_file)
        for d in data:

            if 'title' in list(d['request_type'].keys()) and d[
                    'request_type']['title'] == 'Icy or Snowy Bike Lane':
                print(d)
                print("\n")

                count += 1
    print(count)


