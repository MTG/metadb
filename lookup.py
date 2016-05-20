from argparse import ArgumentParser
import importlib
import sys
import csv
import json
import os.path

from metadb import util


def _get_module_by_path(modulepath):
    try:
        package = importlib.import_module(modulepath)
        return package
    except ImportError:
        raise Exception("Cannot load module %s" % modulepath)


def save(result, modulepath, outfile):
    outfile = os.path.join(modulepath, outfile)
    dirname = os.path.dirname(outfile)
    util.mkdir_p(dirname)
    with open(outfile, 'w') as f:
        json.dump(result, f)


def process_file(module, filename, save=False):
    with open(filename) as csvfile:
        for query in csv.DictReader(csvfile):
            if 'module' not in query:
                query['module'] = module
            if 'save' not in query:
                query['save'] = save


            if 'year' not in query:
                query['year'] = None
            if 'artist' not in query:
                query['artist'] = None
            if 'recording' not in query:
                query['recording'] = None
            if 'mbid' not in query:
                query['mbid'] = None

            process(query)


def process(query):

    if not 'module' in query or not query['module']:
        raise Exception("Missing module information for the query", json.dumps(query))

    module = _get_module_by_path(query['module'])

    if not hasattr(module, "scrape"):
        raise Exception("Module %s must have a .scrape method" % module)

    if not query['mbid']:
        raise Exception("Missing MBID for the query", json.dumps(query))

    if query['save']:
        # Check if result file already exists
        mbid = query['mbid']
        outfile = os.path.join(mbid[:2], "{}.json".format(mbid))
        if os.path.exists(outfile):
            return

    try:
        result = module.scrape(query)
    except Exception as e:
        raise
        print(str(e))
        return

    result_type = result["type"]
    data = result.get("data")
    response = result.get("response")
    if data:
        result = {
                    'type': result_type,
                    'mbid': query['mbid'],
                    'scraper': query['module'],
                    'result': data
                 }
    elif response:
        result = response

    if query['save']:
        save(result, query['module'], outfile)
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = ArgumentParser(description = """MetaDB metadata scraper.""")
    parser.add_argument('--module', help='Scraper module python path, e.g. metadb.scrapers.lastfm', required=False)
    parser.add_argument('--csv', help='Use input csv file for queries', required=False)
    parser.add_argument('--artist', help='Artist name', required=False)
    parser.add_argument('--recording', help='Recording title', required=False)
    parser.add_argument('--release', help='Release title', required=False)
    parser.add_argument('--year', help='Year', required=False)
    parser.add_argument('--mbid', help='Associated (artist/recording/release) MBID to store data for', required=False)
    parser.add_argument('--save', help="Save to file", action='store_true', default=False)

    args = parser.parse_args()

    if args.csv:
        if args.artist or args.recording or args.release or args.mbid:
            print('Performing queries using data in ', args.csv, 'file; --artist/--recording/--release/--mbid flags will be ignored')
        process_file(args.module, args.csv, args.save)

    else:
        process(args.__dict__)
