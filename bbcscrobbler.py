#! /usr/bin/python
# Author: Amr Hassan <amr.hassan@gmail.com>

# Enable (uncomment) one of these radio_stations
STATION = "bbc6music"
#STATION = "bbcradio1"
#STATION = "bbcradio2"
#STATION = "bbc1xtra"


# Do not edit anything below this line

import pylast, os, time

API_KEY = "8fe0d07b4879e9cd6f8d78d86a8f447c"
API_SECRET = "debb11ad5da3be07d06fddd8fe95cc42"

network = pylast.get_lastfm_network(API_KEY, API_SECRET)
station = network.get_user(STATION)

if not os.path.exists(".session_key"):
    skg = pylast.SessionKeyGenerator(network)
    url = skg.get_web_auth_url()
    
    print("Please authorize the scrobbler to scrobble to your account: %s\n" %url)
    
    authorized = False
    while not authorized:
        try:
            session_key = skg.get_web_auth_session_key(url)
            authorized = True
            fp = open(".session_key", "w")
            fp.write(session_key)
            fp.close()
        except pylast.WSError:
            time.sleep(1)
else:
    session_key = open(".session_key").read()

network = pylast.get_lastfm_network(API_KEY, API_SECRET, session_key)
station = network.get_user(STATION)

print("Tuned in to %s\n----------------------" %STATION)

playing_track = None
playing_track_scrobbled = False
while True:
    
    try:
        new_track = station.get_recent_tracks(1)[0]
    
        if new_track != playing_track:
            
            if playing_track and not playing_track_scrobbled:
                network.scrobble(playing_track.track.artist.name, playing_track.track.title, playing_track.timestamp)
                playing_track_scrobbled = True
                print("Scrobbled: %s" %playing_track.track)
            
            network.update_now_playing(new_track.track.artist.name, new_track.track.title, duration = str(int(new_track.track.get_duration()/1000)))
            print("Now playing: %s" %new_track.track)
            
            playing_track = new_track
            playing_track_scrobbled = False
        
        if playing_track and not playing_track_scrobbled and (time.time() - int(playing_track.timestamp)) >= int(playing_track.track.get_duration())/2000:
            network.scrobble(playing_track.track.artist.name, playing_track.track.title, playing_track.timestamp)
            print("Scrobbled: %s" %playing_track.track)
            playing_track_scrobbled = True
            
    except Exception as e:
        print ("Error: %s" %repr(e))
        continue
    
    time.sleep(10)

for item in station.get_recent_tracks():
    print(item.track)
    print(item.timestamp)
