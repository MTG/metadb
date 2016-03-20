import getpass as gt
import sys
import musicbrainzngs as mb

username = raw_input('Enter MusicBrainz Username: ')
password = gt.getpass('Password for {}: '.format(username))
mb.auth(username,password)

mb.set_useragent(
    "python-metadb-musicbrainz-scrape",
    "0.1",
    "https://github.com/MTG/metadb")



def scrape(mbid, artist, title):
    try:
        resultID = mb.get_recording_by_id(mbid,
                                          includes=["artists", "releases", "annotation", "tags"],
                                          release_status=["official"],
                                          release_type=["album", "single", "ep", "broadcast", "other", "compilation"])
        
        resultArtist = mb.search_artists(artist=artist,
                                         limit = 10,
                                         strict = True)
    
        resultTitle = mb.search_recordings(recording=title,
                                           limit = 10,
                                           strict = True)
    except mb.MusicBrainzError as ex:
        raise
    
    return resultID, resultArtist, resultTitle