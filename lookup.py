import argparse
import importlib
import sys
import csv


def _get_module_by_path(modulepath):
    try:
        package = importlib.import_module(modulepath)
        return package
    except ImportError:
        raise Exception("Cannot load module %s" % modulepath)


def process_file(module, filename):
    r = csv.reader(open(filename))
    for line in r:
        process(module, line[0], line[1], line[2])

def process(module, mbid, artist, title):
    if not hasattr(module, "scrape"):
        raise Exception("module %s must have a .scrape method" % module)

    print module.scrape(mbid, artist, title)



if __name__ == "__main__":
    if len(sys.argv) < 4:
        print >>sys.stderr, "Usage: %s <module> <mbid> <artist> <title>" % sys.argv[0]
        print >>sys.stderr, "       %s <module> -f filename" % sys.argv[0]
        print >>sys.stderr, "       filename contains in csv format <mbid>,<artist>,<title>"
        print >>sys.stderr, "       module is a python path, e.g. metadb.scrapers.lastfm"
        sys.exit(1)

    module = _get_module_by_path(sys.argv[1])
    if sys.argv[2] == "-f":
        process_file(module, sys.argv[3])
    else:
        process(module, sys.argv[2], sys.argv[3], sys.argv[4])
