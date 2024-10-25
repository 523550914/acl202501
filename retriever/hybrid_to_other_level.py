import argparse
import json


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=str)
    parser.add_argument('--input_file', type=str)
    parser.add_argument('--hybrid_file')
    parser.add_argument('--output_file', type=str)
    args = parser.parse_args()
    with open(args.input_file, 'r') as in_f:
        data = json.load(in_f)
    with open(args.hybrid_file, 'r') as orig_f:
        hybrid_data = json.load(orig_f)
    print("hybrid data length: ",len(hybrid_data))
    print("data length: ",len(data))
    for d in data:
        id = d['id']
        for orig_d in hybrid_data:
            if orig_d['id'] == id:
                orig_d['query'] = d[args.type]
                break
    with open(args.output_file, 'w') as out_f:
        json.dump(hybrid_data, out_f, indent=4)

    print('Done!')