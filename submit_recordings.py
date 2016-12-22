import argparse
import json
import requests


def submit(host, token, file):
    data = json.load(open(file))
    requests.post("http://{}/recordings".format(host),
                  json=data,
                  headers={"Authorization": "Token {}".format(token)})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", type=str, required=True, help="Access token")
    parser.add_argument("-n", type=str, required=False, default="localhost:8080", help="Hostname")
    parser.add_argument("file", type=str, help="JSON file containing MBIDs")

    args = parser.parse_args()
    submit(args.n, args.t, args.file)

if __name__ == "__main__":
    main()