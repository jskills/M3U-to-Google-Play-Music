#!/usr/bin/env python

import os
import re

# API to interface with Google Play Music API
from gmusicapi import Mobileclient
# https://unofficial-google-music-api.readthedocs.io/en/latest/

# API to parse MP3 tags in local files
from mutagen.easyid3 import EasyID3
# https://code.google.com/archive/p/mutagen/wikis/Tutorial.wiki

#### configuration
# the OAuth file generated from the process in the "authenticate w Google" section below
o_file = './oauth.txt'

# the file containing the ID of one of your authorized devices for Google Play Music
device_file = './dev_id.txt'

# the directory where your .m3u playlists live
playlist_dir = ''

###################


### find all local playlists
local_pls_file = [0] * 1000
local_pls_name = [0] * 1000

i = 0
for pl_file in os.listdir(playlist_dir):
    if pl_file.endswith(".m3u"):
        local_pls_name[i] = pl_file
        local_pls_file[i] = os.path.join(playlist_dir, pl_file)
        i += 1

###################


### authenticate w Google
mc = Mobileclient()

dev_id = ''

if os.path.exists(device_file):
    f = open(device_file)
    dev_id = f.read()
    dev_id.strip()
    dev_id = re.sub(r'\n', '', dev_id)
    f.close()
else:
    print "ERROR : Cannot find device ID file"
    sys.exit()
   
if os.path.exists(o_file):
    mc.oauth_login(dev_id, o_file)
else :
    # this will open a browser for you and let you follow steps
    # should only have to do this once per machine you run this on
    mc.perform_oauth(storage_filepath=o_file,open_browser=True)
    mc.oauth_login(dev_id, o_file)

###################


### get all songs in the cloud
songDict = mc.get_all_songs()

### find all cloud playlists
all_pls = mc.get_all_playlists()

### compare and find playlists we need to create
need_to_create_name = [0] * 1000
need_to_read_file = [0] * 1000

found_count = 0
cnt = 0
while (cnt < (len(local_pls_name)-1)) and (local_pls_name[cnt] != 0):
    found = 0
    # replace underscores with spaces for title of playlist comparison
    # this is a personal convention for how playlist files are named - you may not need to do this
    test_local = re.sub(r'_', ' ', str(local_pls_name[cnt]))
    test_local = re.sub(r'.m3u', '', test_local)
    file_local = str(local_pls_file[cnt])
    for p in all_pls:
        if(p['type'] == 'USER_GENERATED'):
            if str(p['name']) == test_local:
                found = 1
                break
    if found == 0:
        print "Playlist " + test_local + " does not exist in Google"
        need_to_create_name[found_count] = test_local
        need_to_read_file[found_count] = file_local
        found_count += 1
    cnt += 1

###################
    

### find each song in each new playlist, lookup song_ids in Google, add them to list, create new playlist
cnt = 0
while (cnt < len(need_to_read_file)-1) and (need_to_read_file[cnt] != 0):
    pl_songs = []
    # read local playlist
    with open(need_to_read_file[cnt]) as f:
        line = f.readline()
        while line:
            # grab each relevant line
            if not (line.startswith('#')):
                # extract title from MP3 tag
                file_lookup = playlist_dir + line
                # convert m3u file naming conventions to standard Unix
                file_lookup = re.sub(r'\\', '/', file_lookup)
                file_lookup = re.sub(r'\r', '', file_lookup)
                file_lookup = re.sub(r'\n', '', file_lookup)
                # get all mp3 tag data
                mp3 = EasyID3(file_lookup)
                #print EasyID3.valid_keys.keys()
                check_title_list = mp3["title"]
                check_title = check_title_list.pop()
                check_artist_list = mp3["artist"]
                check_artist = check_artist_list.pop()
                # scan entire songDict by name to find song_id
                sd_find = 0
                for sd in songDict:
                    if sd['title'] == check_title and sd['artist'] == check_artist:
                        # we assume if the title and artist match, that's the song we're looking for
                        # if this is too general adding "album" as an additional condition for match makes sense
                        pl_songs.append(sd["id"])
                        sd_find = 1
                        break
                if not sd_find:
                    print "Could not find " + check_title + " by " + check_artist
            line = f.readline()
        
    # create new playlist
    print 'creating playlist ' + str(need_to_create_name[cnt])
    playlist_id = mc.create_playlist(str(need_to_create_name[cnt]))
    # run through list of songs and add each song_id
    song_cnt = 0
    while(song_cnt < len(pl_songs)-1):
        mc.add_songs_to_playlist(playlist_id, str(pl_songs[song_cnt]))
        song_cnt += 1
    print str(song_cnt) + " songs added ..."

    cnt += 1

print str(cnt) + " new playlists added ..."

###################
