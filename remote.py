import argparse
import json
import requests


def lookup(host, token, mbid=None):
    url = "http://{}/lookup_meta".format(host)
    if mbid:
        url = "{}/{}".format(url, mbid)
    requests.post(url,
                  headers={"Authorization": "Token {}".format(token)})


def submit(host, token, file):
    try:
        data = json.load(open(file))
    except ValueError:
        data = open(file).read().splitlines()
    requests.post("http://{}/recordings".format(host),
                  json=data,
                  headers={"Authorization": "Token {}".format(token)})


def scrape(host, token, source, mbid=None):
    url = "http://{}/scrape/{}".format(host, source)
    if mbid:
        url = "{}/{}".format(url, mbid)
    requests.post(url,
                  headers={"Authorization": "Token {}".format(token)})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", type=str, required=True, help="Access token")
    parser.add_argument("-n", type=str, required=False, default="localhost:8080", help="Hostname")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("-f", help="JSON file containing MBIDs")
    group.add_argument("-l", nargs="*", help="Look up metadata for new MBIDs")
    group.add_argument("-s", action="store_true", help="Scrape some data")

    parser.add_argument("-r", type=str, help="Source to scrape")
    parser.add_argument("-m", type=str, help="MBID to process")

    args = parser.parse_args()
    if args.f:
        submit(args.n, args.t, args.f)
    elif args.s:
        scrape(args.n, args.t, args.r, args.m)
    elif args.l:
        if len(args.l) == 0:
            mbid = None
        else:
            mbid = args.l[0]
        lookup(args.n, args.t, mbid)

if __name__ == "__main__":
    main()
