import subprocess, json, sys, os

class DiscogScraper():
    
    """
    Simple Class to retrieve data from the Discogs website
    It uses curl command to download the json files from the website
    """
    def __init__(self, token, artist_name, song_title):
        self.main_url = 'https://api.discogs.com/'
        self.search_url = 'database/search'
        self.release_url = 'releases/'
        self.scrape_command = 'curl'
        self.json_path = 'json_releases/'
        self.token = token
        self.artist_name = artist_name.replace(" ", "%20")
        self.artist_string = artist_name
        self.song_title = song_title.replace(" ", "%20")
        self.song_string = song_title
        self.tempFile = './' + self.json_path + self.artist_name + self.song_title + '.json'
        if not os.path.isdir(self.json_path) and not os.path.exists(self.json_path):
            # print "Create the Directory to store json files"
            os.makedirs(self.json_path)
    
    def search_command(self, artist_name='', song_title='', page=1):
        """
            This function format the curl command to retrieve data from discogs
            It uses the token authentication - pass a valid Discogs Token
            It uses the initialized artist_name and song_title
        """
        if (artist_name!='' and song_title!=''):
            self.artist_name = artist_name.replace(" ", "%20")
            self.song_title = song_title.replace(" ", "%20")
        elif (artist_name!=''):
            self.artist_name = artist_name.replace(" ", "%20")
#        else:
#            print("Use Initialization Values")
            
        #self.tempFile = './' + self.json_path + self.artist_name + self.song_title + '_' + str(page) + '.json'
        tempUrl = self.main_url + self.search_url + '?q=' + self.artist_name + '&token=' + self.token
        if self.song_title:
            tempUrl += '&track=' + self.song_title
            
        command = self.scrape_command + ' \'' + tempUrl + '\' > ' + self.tempFile
        return command
        
    def release_command(self, rel_id):
        """
            Format the curl command to retrieve a specific release from discogs
            Returns the command formatted string
            Does not execute the command!
        """
        # curl "https://api.discogs.com/releases/1117108" --user-agent "FooBarApp/3.0" >> release_1117108.json
        relfile = './' + self.json_path + str(rel_id)+'.json'
        tempurl = self.main_url + self.release_url + str(rel_id)
        cmd = self.scrape_command + ' \'' + tempurl + '\'' + ' --user-agent \'discogsBrainFeederz/0.1\' >> ' + relfile
        
        return cmd
    
    def get_url(self, command):
        """
            This function download the data from Discogs
            It just executes the commands formatted with release_command and search_command methods
        """
    
        data, error = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).communicate()
        #print data, error
        #try:
        #    with open(self.tempFile) as searchjson:
        #        json_data = json.load(searchjson)
        #        # check if not a json file
        #        return True
        #except IOError:
        #    print('File: - Not Created')
        #    return False
    
    def releasecollect(self):
        """
            Extract all the relese IDs from a returned search file
            Returns a list of IDs and the URL of the next page (useful to cycle all the result pages)
        """
        releaseids = []
        nextsong = 0
        with open(self.tempFile) as jsonfile:
            jsondata = json.load(jsonfile)
            items = jsondata['pagination']['items']
            pp = jsondata['pagination']['per_page']
            results = jsondata['results']
            
        if items>0:
            pages = jsondata['pagination']['pages']
            if 'next' in jsondata['pagination']['urls']:
                nextsong = jsondata['pagination']['urls']['next']
            
            for i in results:
                if i['type'] == 'release':
                    #print i['id']
                    releaseids.append(i['id'])
        
        return releaseids, nextsong
    
    def get_tracklist(self, rel_id):
        """
            Extract a tracklist from a release file
            Returns an array of dictionaries
        """
        tempfile = self.json_path + str(rel_id) + '.json'
        releasedictarray = []
        jdecoder = json.JSONDecoder()
        with open(tempfile) as jsonfile:
            text = jsonfile.read()
            while text:
                obj, idx = jdecoder.raw_decode(text)
                tracks = obj['tracklist']
                #print tracks
                releasedictarray.append(tracks)
                text = text[idx:].lstrip()
        return releasedictarray
    
    def chek_release(self, rel_id):
        """
            Check if a release contain a song and extract genre and style from the release
            Returns a dictionary with the retrieved informations if it find the track
        """
        tempfile = self.json_path + str(rel_id) + '.json'
        releasedictarray = []
        jdecoder = json.JSONDecoder()
        finded = False
        songdict = self.create_songdict()
        counter = 0
        with open(tempfile) as jsonfile:
            text = jsonfile.read()
            while text:
                obj, idx = jdecoder.raw_decode(text)
                tracks = obj['tracklist']                
                for i in tracks:
                    if str(self.song_string).lower() in i['title'].lower():
                        finded = True
                        counter += 1
                        songdict['release_count'] = counter
                        if counter == 1:
                            songdict['title'] = self.song_string
                            songdict['artist'] = self.artist_string
                        if 'genres' in obj:
                            self.weight_genres(songdict,obj['genres'])
                        if 'styles' in obj:
                            self.weight_styles(songdict,obj['styles'])
                        
                text = text[idx:].lstrip()
        if finded==True:
            return songdict
    
    def merge_song_dict(self, dic1, dic2):
        """
            Merges two song dictionaries keeping the genres, styles and release_count consistent
            Returns the dictionary with the merged data
        """
        if type(dic1) == type(dic2) == dict:
            if len(list(dic1.keys()))>=len(list(dic2.keys())):
                target = dic1
                source = dic2
            else:
                if len(list(dic1.keys()))==0:
                    target = dic1.copy()
                    target = target.update(dic2)
                    #return target
                else:
                    target = dic2
                    source = dic1
                
            for k in list(target.keys()):        
                if type(target[k])==list:
                    target[k] = sorted(set(target[k]+source[k]))
                elif type(target[k])==int:
                    target[k] = target[k] + source[k]
                elif type(target[k])==dict and k == 'genres':
                    self.weight_genres(target, source[k])
                elif type(target[k])==dict and k == 'styles':
                    self.weight_styles(target, source[k])
                elif k=='title' and target['title']=="":
                    target['title'] = source['title']
                elif k=='artist' and target['artist']=="":
                    target['artist'] = source['artist']
            return target
        else:
            raise ValueError("Input two dictionaries")
        
    def create_songdict(self):
        """
            Creates the song dictionary data structure
            Returns a complete dictionary with empty values
        """
        songdict = {}
        songdict['artist'] = ""
        songdict['title'] = ""
        songdict['genres'] = {}
        songdict['styles'] = {}
        songdict['release_count'] = 0
        return songdict
    
    def weight_genres(self, target, genres):
        """
            Merge the genres key of the song dictionary keeping the counters consistent
            Returns the dictionary with the merged data
        """
        if list(target['genres'].keys()) == []:
            for i in genres:
                target['genres'][str(i).lower()] = 1
        else:
            tgenres = list(target['genres'].keys())
            for i in genres:
                tmpg = str(i).lower()
                if tmpg in tgenres:
                    #target['genres'][tmpg] = (target['genres'][tmpg] + 1) / target['release_count']
                    if type(genres)==dict:
                        target['genres'][tmpg] = (target['genres'][tmpg] + genres[i])
                    else:
                        target['genres'][tmpg] = (target['genres'][tmpg] + 1)
                else:
                    #target['genres'][tmpg] = 1 / float(target['release_count'])
                    if type(genres)==dict:
                        target['genres'][tmpg] = genres[i]
                    else:
                        target['genres'][tmpg] = 1
            
        return target
    
    def weight_styles(self, target, styles):
        """
            Merge the styles key of the song dictionary keeping the counters consistent
            Returns the dictionary with the merged data
        """
        if list(target['styles'].keys()) == []:
            for i in styles:
                target['styles'][str(i).lower()] = 1
        else:
            tstyles = list(target['styles'].keys())
            for i in styles:
                tmpg = str(i).lower()
                if tmpg in tstyles:
                    #target['genres'][tmpg] = (target['genres'][tmpg] + 1) / target['release_count']
                    if type(styles)==dict:
                        target['styles'][tmpg] = (target['styles'][tmpg] + styles[i])
                    else:
                        target['styles'][tmpg] = (target['styles'][tmpg] + 1)
                else:
                    #target['genres'][tmpg] = 1 / float(target['release_count'])
                    if type(styles)==dict:
                        target['styles'][tmpg] = styles[i]
                    else:
                        target['styles'][tmpg] = 1
            
        return target