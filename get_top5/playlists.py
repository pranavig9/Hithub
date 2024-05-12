import os
import json
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import get_top5 as g
from collections import Counter

os.environ['SPOTIPY_CLIENT_ID']= g.cid
os.environ['SPOTIPY_CLIENT_SECRET']= g.secret
os.environ['SPOTIPY_REDIRECT_URI']='http://localhost:8888/callback'

username = ""
client_credentials_manager = SpotifyClientCredentials(client_id= g.cid, client_secret= g.secret) 
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
scope = 'user-top-read'
token = util.prompt_for_user_token(username, scope)

def playlists():

    total_tracks = []
    popularity = []
    artists = []

    playlists = sp.current_user_playlists(limit=50, offset=0)
    for i in playlists['items']:
        t, p, a = get_songs(username, i['id'], sp)
        total_tracks += t 
        popularity += p 
        artists += a 
    
    return total_tracks, popularity, artists


def get_songs(username, playlist_id, sp):

    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = []
    pop = []
    a = [] 
    for i in results['items']:
        if i['track'] is not None:
            tracks.append(i['track']['name'])
            pop.append(i['track']['popularity'])
            a.append(i['track']['artists'][0]['name'])

    return tracks, pop, a


def most_common_artist(artists): 
    most_common_element, count = Counter(artists).most_common(1)[0]
    print(most_common_element, count)


if __name__ == "__main__":
    total_tracks, popularity, artists = playlists()
    most_common_artist(artists)
