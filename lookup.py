from argparse import ArgumentParser
import importlib
import sys
import csv
import json
import os.path
import time
import concurrent.futures

from metadb import util
from metadb import log


def _get_module_by_path(modulepath):
    try:
        package = importlib.import_module(modulepath)
        return package
    except ImportError:
        raise Exception("Cannot load module %s" % modulepath)


def save(result, outfile):
    dirname = os.path.dirname(outfile)
    util.mkdir_p(dirname)
    with open(outfile, 'w') as f:
        json.dump(result, f)


def process_items(items, module, save, numworkers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=numworkers) as executor:
        future_to_row = {}

        for i in items:
            if 'module' not in i:
                i['module'] = module
            if 'save' not in i:
                i['save'] = save

            future_to_row[executor.submit(process, i)] = i

        for future in concurrent.futures.as_completed(future_to_row):
            i = future_to_row[future]
            try:
                result = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (i, exc))

def process_file(module, filename, numworkers, save=False):
    data = []
    with open(filename) as csvfile:
        for query in csv.DictReader(csvfile):
            data.append(query)

    total = len(data)
    starttime = time.time()
    done = 0
    CHUNK_SIZE = 100

    for items in util.chunks(data, CHUNK_SIZE):
        process_items(items, module, save, numworkers)
        done += CHUNK_SIZE
        durdelta, remdelta = util.stats(done, total, starttime)
        log.info("Done %s/%s in %s; %s remaining", done, total, str(durdelta), str(remdelta))


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
        outfile = os.path.join(query['module'], mbid[:2], "{}.json".format(mbid))
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
        save(result, outfile)
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
    parser.add_argument('-n', help="Number of workers", type=int, default=1)

    args = parser.parse_args()

    if args.csv:
        if args.artist or args.recording or args.release or args.mbid:
            print('Performing queries using data in ', args.csv, ' file; --artist/--recording/--release/--mbid flags will be ignored')
        process_file(args.module, args.csv, args.n, args.save)

    else:
        process(args.__dict__)
