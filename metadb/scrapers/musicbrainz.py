import getpass as gt
import sys
import musicbrainzngs as mb

#username = raw_input('Enter MusicBrainz Username: ')
#password = gt.getpass('Password for {}: '.format(username))
#mb.auth(username,password)

mb.set_useragent(
    "python-metadb-musicbrainz-scrape",
    "0.1",
    "https://github.com/MTG/metadb")



def scrape(mbid):
    try:
        result = mb.get_recording_by_id(mbid, includes=["artists", "releases", "tags"])
	
	recordingName = result["recording"]["title"] #recording title
	
	artist = list()
	artist_mbid = list()

	for item in result["recording"]["artist-credit"]:
    		if isinstance(item, dict): 
        		artist.append(item["artist"]["name"])
        		artist_mbid.append(item["artist"]["id"])
			

        release_mbid = list()
	release_title = list()

	for item in result["recording"]["release-list"]:
    		release_mbid.append(item["id"])
    		release_title.append(item["title"])



    except mb.MusicBrainzError as ex:
        raise
    
return recordingName, artist, artist_mbid, release_mbid, release_title