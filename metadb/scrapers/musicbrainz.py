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
        
        recording_name = result["recording"]["title"] #recording title
        
        artists = []
        
        for item in result["recording"]["artist-credit"]:
            if isinstance(item, dict):
                artists.append({"id": item["artist"]["id"], "name": item["artist"]["name"]})
        
        releases = []
        release_groups = []
        
        for item in result1["recording"]["release-list"]:
            releases.append({"id": item["id"], "Title": item["title"], "Date": item["date"]})
            
            #Request for retrieving release info
            rel = mb.get_release_by_id(item["id"], includes = ["artists", "release-groups"])
            
            #Check if release group already exists in the list in order to eliminate dublicate instances
            if not ({"id": rel["release"]["release-group"]["id"], "Title": rel["release"]["release-group"]["title"]}) in release_groups:
                release_groups.append({"id": rel["release"]["release-group"]["id"], "Title": rel["release"]["release-group"]["title"]})
            else:
                print "Release-group already exists in the list!"
  
    except mb.MusicBrainzError as ex:
        raise
    
return {"Title": recording_name, "Artist": artists, "Releases": releases, "Realease-groups": release_groups}