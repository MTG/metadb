from argparse import ArgumentParser
import importlib
import sys
import csv
import json
import os.path


def _get_module_by_path(modulepath):
    try:
        package = importlib.import_module(modulepath)
        return package
    except ImportError:
        raise Exception("Cannot load module %s" % modulepath)


def save(result, outfile):
    with open(outfile, 'w') as f:
        json.dump(result, f)


def process_file(module, filename, save=False):
    with open(filename) as csvfile:
        for query in csv.DictReader(csvfile):
            if not 'module' in query:
                query['module'] = module
            if not 'save' in query:
                query['save'] = save


            if not 'year' in query:
                query['year'] = None
            if not 'artist' in query:
                query['artist'] = None
            if not 'recording' in query:
                query['recording'] = None
            if not 'mbid' in query:
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
        outfile = query['mbid'] + '.json'
        if os.path.exists(outfile):
            return

    result, result_type = module.scrape(query)
    
    if not result:
        return 
        
    result = {
                'type': result_type,
                'mbid': query['mbid'],
                'scraper': query['module'],
                'result': result
             }

    if query['save']:
        save(result, outfile)
    else:
        print result
        print


if __name__ == "__main__":
    parser = ArgumentParser(description = """
MetaDB metadata scraper.
""")
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
            print 'Performing queries using data in ', args.csv, 'file; --artist/--recording/--release/--mbid flags will be ignored'
        process_file(args.module, args.csv, args.save)

    else:
        process(args.__dict__)
