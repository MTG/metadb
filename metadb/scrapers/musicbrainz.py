# import getpass as gt
import sys
import musicbrainzngs as mb

# Username and password promting
# username = raw_input('Enter MusicBrainz Username: ')
# password = gt.getpass('Password for {}: '.format(username))
# mb.auth(username,password)

mb.set_useragent(
    "python-metadb-musicbrainz-scrape",
    "0.1",
    "https://github.com/MTG/metadb")



def scrape(mbid):
    try:
        result = mb.get_recording_by_id(mbid, includes=["artists", "releases", "tags"])

        artists = list()
        artists_mbid = list()

        for item in result["recording"]["artist-credit"]:
            if isinstance(item, dict):
        
                artists.append(item["artist"]["name"])
                artists_mbid.append(item["artist"]["id"])

        
        #resultArtist = mb.search_artists(artist=artist, limit = 10, strict = True)
    
        #resultTitle = mb.search_recordings(recording=title, limit = 10, strict = True)

    except mb.MusicBrainzError as ex:
        raise
    
    return artists,artists_mbid
