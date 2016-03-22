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
        recording = mb.get_recording_by_id(mbid, includes=["artists", "releases", "tags"])
        
        recording_name = recording["recording"]["title"] #recording title
        
        artists = []
        
        for item in recording["recording"]["artist-credit"]:
            if isinstance(item, dict):
                artists.append({"id": item["artist"]["id"], "name": item["artist"]["name"]})
        
        releases = []
        release_groups = []
        
        for item in recording["recording"]["release-list"]:
            releases.append({"id": item["id"], "title": item["title"], "date": item["date"]})
            
            #Request for retrieving release info
            release = mb.get_release_by_id(item["id"], includes = ["artists", "release-groups"])
            release_group = {"id": release["release"]["release-group"]["id"], "title": release["release"]["release-group"]["title"]}
            
            #Check if release group already exists in the list in order to eliminate duplicate instances
            if release_group not in release_groups:
                release_groups.append(release_group)
            
    except mb.MusicBrainzError as ex:
        raise
    
    return {"title": recording_name, "artist": artists, "releases": releases, "realease-groups": release_groups}