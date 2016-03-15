from argparse import ArgumentParser
import importlib
import sys
import csv
import json
import os
import errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def _get_module_by_path(modulepath):
    try:
        package = importlib.import_module(modulepath)
        return package
    except ImportError as e:
        raise Exception("Cannot load module %s (%s)" % (modulepath, e))


def save_result(result, outfile):
    with open(outfile, 'w') as f:
        json.dump(result, f)


def process_file(module, filename, save=False):
    with open(filename) as csvfile:
        for row in csv.DictReader(csvfile):
            if not 'year' in row:
                row['year'] = None
            if not 'artist' in row:
                row['artist'] = None
            if not 'recording' in row:
                row['recording'] = None
            if not 'mbid' in row:
                row['mbid'] = None

            process(module, row, save)


def process(module_path, data, save):
    if not module_path:
        raise Exception("Missing module information")

    module = _get_module_by_path(module_path)

    if not hasattr(module, "scrape"):
        raise Exception("Module %s must have a .scrape method" % module)

    if not data['mbid']:
        raise Exception("Missing MBID for the query", json.dumps(data))

    outdir = os.path.join(module_path, data['mbid'][:2])
    outfile = os.path.join(outdir, '%s.json' % data['mbid'])
    if save:
        # Check if result file already exists
        if os.path.exists(outfile):
            print "File", outfile, "found, skipping query"
            return
    try:
        result, result_type = module.scrape(data)
    except Exception, e:
        print str(e)
        return

    result = {
                'type': result_type,
                'mbid': data['mbid'],
                'scraper': module_path,
                'result': result
             }

    if save:
        mkdir_p(outdir)
        save_result(result, outfile)
    else:
        print result
        print


if __name__ == "__main__":
    parser = ArgumentParser(description = """
MetaDB metadata scraper.
""")
    parser.add_argument('--module', help='Scraper module python path, e.g. metadb.scrapers.lastfm', required=True)
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
            print 'Performing queries using data in ', args.csv, 'file; --artist/--recording/--release/--mbid flags will be ignored'
        process_file(args.module, args.csv, args.save)

    else:
        query = {"mbid": args.mbid,
                 "recording": args.recording,
                 "release": args.release,
                 "year": args.year,
                 "artist": args.artist
                }
        process(args.module, query, args.save)
