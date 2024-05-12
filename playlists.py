import os
import json
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import get_top5 as g
from collections import Counter
import top5_sentiment as ts

os.environ['SPOTIPY_CLIENT_ID']= g.cid
os.environ['SPOTIPY_CLIENT_SECRET']= g.secret
os.environ['SPOTIPY_REDIRECT_URI']='http://localhost:8888/callback'

username = ""
client_credentials_manager = SpotifyClientCredentials(client_id= g.cid, client_secret= g.secret) 
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
scope = 'user-top-read'
token = util.prompt_for_user_token(username, scope)

total_tracks = []
popularity = []
artists = []

def playlists(total_tracks, popularity, artists):

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


def read_dataset(fp):
  songs = pd.read_csv(fp)
  return songs

data = read_dataset('spotify_millsongdata.csv')


total_tracks, popularity, artists = playlists(total_tracks, popularity, artists)
most_common_artist(artists)

spotify_recs = sp.recommendations(seed_tracks=g.list_of_song_uri, limit = 25)

#print(spotify_recs)

lyrics = []

list_of_results = spotify_recs["tracks"]
list_of_artist_names = []
list_of_song_names = []

for result in list_of_results:
    this_artists_name = result["artists"][0]["name"]
    list_of_artist_names.append(this_artists_name)
    this_song_name = result["name"]
    list_of_song_names.append(this_song_name)

for i in range(len(list_of_artist_names)):
    lyrics.append(ts.scrape_lyrics(list_of_artist_names[i], list_of_song_names[i]))

lyrics = ts.lyrics_onto_frame(list_of_artist_names, list_of_song_names)

sent = ts.sentiment(lyrics)
print(sent)