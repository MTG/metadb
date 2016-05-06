"""
    This script uses the DiscogScraper Class to download style and genreinformation from discogs
    Created to use the class for the metadb project(https://github.com/MTG/metadb)
    author: Daniele Scarano
"""
import sys, os, shutil
sys.path.append('./lib')
from . import discogscraper as ds

myToken='myoEuQPZlLnuRtHokDXecKtWoeSYBzglFRKUsxcc'
TYPE = 'Weighted song styles and genres from Discogs'

def scrape(query):
    
    artist = query['artist']
    song = query['recording']
    # create the instance of the DiscogScraper object
    dso = ds.DiscogScraper(myToken, artist, song)
    # get the search results into a json file
    dso.get_url(dso.search_command())
    # get the releases and the url of the next page(for future use)
    releases, next_page = dso.releasecollect()
    if len(releases)>0:

        # create a dictionary structure with empty values
        songdict = dso.create_songdict()
        for i in releases:
            # Get each release in a separate json file
            dso.get_url(dso.release_command(i))
            # parse the json retrieved
            out = dso.chek_release(i)
            # merge the retrieved data into one dictionary
            songdict = dso.merge_song_dict(songdict,out)
    
        shutil.rmtree(os.path.join('.', dso.json_path), ignore_errors=True)
        return songdict, TYPE
    
    else:
        os.remove(dso.tempFile)
        raise ValueError('The search query returned no results!')