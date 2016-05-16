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
        
        # Recording title
        recording_name = recording["recording"]["title"]
        
        artists = []
        releases = []
        release_groups = []
        
        
        for item in recording["recording"]["artist-credit"]:
            # Condition to skip join-phrase in multi-artists recordings
            if isinstance(item, dict):
                
                # Recording artist info
                artist_id = item["artist"]["id"]
                artist_name = item["artist"]["name"]
                # Check for recording artist tag-list
                if "tag-list" in item["artist"]:
                    artist_tags = item["artist"]["tag-list"]
                    artists.append({"id": artist_id, "name": artist_name, "tag-list": artist_tags})
                else:
                    artists.append({"id": artist_id, "name": artist_name})
        
        
        for item in recording["recording"]["release-list"]:
            
            # Request for release info
            release = mb.get_release_by_id(item["id"], includes = ["artists", "release-groups", "tags"])
            
            
            # Release group info
            release_group_id = release["release"]["release-group"]["id"]
            release_group_title = release["release"]["release-group"]["title"]
            release_group_first_release_date = release["release"]["release-group"]["first-release-date"]
            
            release_artists = []
            
            for item2 in release["release"]["artist-credit"]:
                # Condition to skip join-phrase in multi-artists releases
                if isinstance(item2, dict):
                    # Release artist info
                    release_artist_id = item2["artist"]["id"]
                    release_artist_name = item2["artist"]["name"]
                    
                    # Check for artist tag-list
                    if "tag-list" in item2["artist"]:
                        release_artist_tags = item2["artist"]["tag-list"]
                        release_artists.append({"id": release_artist_id, "name": release_artist_name, "tag-list": release_artist_tags})
                    else:
                        release_artists.append({"id": release_artist_id, "name": release_artist_name})
            
            
            
            # Release group tags check and first-release-date
            if "tag-list" in release["release"]["release-group"]:
                release_group_tags = release["release"]["release-group"]["tag-list"]
                release_group = {"id": release_group_id, "title": release_group_title, "firs-release-date": release_group_first_release_date, "tag-list": release_group_tags}
            else:
                release_group = {"id": release_group_id, "title": release_group_title, "firs-release-date": release_group_first_release_date}
            
            # Check if release group already stored - eliminate dublicates
            if release_group not in release_groups:
                release_groups.append(release_group)
            
            
            # Check for release tag-list
            if "tag-list" in release["release"]:
                release_tags = release["release"]["tag-list"]
                releases.append({"id": item["id"], "title": item["title"], "artist": release_artists, "date": item["date"], "tag-list": release_tags})
            else:
                releases.append({"id": item["id"], "title": item["title"], "artist": release_artists, "date": item["date"]})


    except mb.MusicBrainzError as ex:
        raise
    
    # Final result based on the existance of recording tags
    if "tag-list" in recording["recording"]:
        recording_tags = recording["recording"]["tag-list"]
        result = {"title": recording_name, "artist": artists, "releases": releases, "realease-groups": release_groups, "tag-list": recording_tags}
    else:
        result = {"title": recording_name, "artist": artists, "releases": releases, "realease-groups": release_groups}
    
    return result
