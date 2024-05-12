import os
import json
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

cid = 'a5d401307f35454584cca6ea288c0a63'
secret = '00b13f2157c64c04ac8c1e320787a107'

def get_top5():

    os.environ['SPOTIPY_CLIENT_ID']= cid
    os.environ['SPOTIPY_CLIENT_SECRET']= secret
    os.environ['SPOTIPY_REDIRECT_URI']='http://localhost:8888/callback'

    username = ""
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret) 
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    scope = 'user-top-read'
    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        results = sp.current_user_top_tracks(limit=5,offset=0,time_range='medium_term')
        for song in range(5):
            list = []
            list.append(results)
            if os.path.exists('output/top5_data.json'):
                os.remove('output/top5_data.json')
            with open('output/top5_data.json', 'w', encoding='utf-8') as f:
                json.dump(list, f, ensure_ascii=False, indent=4)
    else:
        print("Can't get token for", username)

def json_to_csv():
    with open('output/top5_data.json') as f:
        data = json.load(f)

    list_of_results = data[0]["items"]
    list_of_artist_names = []
    list_of_artist_uri = []
    list_of_song_names = []
    list_of_song_uri = []
    list_of_durations_ms = []
    list_of_explicit = []
    list_of_albums = []
    list_of_popularity = []

    for result in list_of_results:
        result["album"]
        this_artists_name = result["artists"][0]["name"]
        list_of_artist_names.append(this_artists_name)
        this_artists_uri = result["artists"][0]["uri"]
        list_of_artist_uri.append(this_artists_uri)
        list_of_songs = result["name"]
        list_of_song_names.append(list_of_songs)
        song_uri = result["uri"]
        list_of_song_uri.append(song_uri)
        list_of_duration = result["duration_ms"]
        list_of_durations_ms.append(list_of_duration)
        song_explicit = result["explicit"]
        list_of_explicit.append(song_explicit)
        this_album = result["album"]["name"]
        list_of_albums.append(this_album)
        song_popularity = result["popularity"]
        list_of_popularity.append(song_popularity)

    top5 = pd.DataFrame(
        {'artist': list_of_artist_names,
        'artist_uri': list_of_artist_uri,
        'song': list_of_song_names,
        'song_uri': list_of_song_uri,
        'duration_ms': list_of_durations_ms,
        'explicit': list_of_explicit,
        'album': list_of_albums,
        'popularity': list_of_popularity
        
        })

    all_songs_saved = top5.to_csv('output/top5_songs.csv')

if __name__ == "__main__":
    get_top5()
    json_to_csv()