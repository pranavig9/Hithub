import os
import json
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
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
    list_of_track_ids = []

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
        track_id = result["id"]
        list_of_track_ids.append(track_id)

    top5 = pd.DataFrame(
        {'artist': list_of_artist_names,
        'artist_uri': list_of_artist_uri,
        'song': list_of_song_names,
        'song_uri': list_of_song_uri,
        'duration_ms': list_of_durations_ms,
        'explicit': list_of_explicit,
        'album': list_of_albums,
        'popularity': list_of_popularity,
        'track_id': track_id
        })

    # print(list_of_track_ids)

    all_songs_saved = top5.to_csv('output/top5_songs.csv')

def get_song_info(song_name, artist_name):
    # Initialize Spotipy client
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret) 
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Search for the song
    results = sp.search(q='track:' + song_name + ' artist:' + artist_name, type='track', limit=1)

    # Check if any tracks were found
    if len(results['tracks']['items']) == 0:
        print("No matching track found.")
        return None
    print("Don't worry, found something")
    # Extract song information
    track = results['tracks']['items'][0]
    popularity = track['popularity']
    duration_ms = track['duration_ms']
    explicit = track['explicit']

    return [popularity, duration_ms, explicit]

def create_spotify_playlist(title, playlist_content):
    # Authenticate user
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public"))

    # Create a new playlist
    playlist = sp.user_playlist_create(sp.current_user()['id'], title)
    playlist_content= list(set(playlist_content))

    # Extract track URIs from playlist content
    track_uris = []
    for artist, song in playlist_content:
        results = sp.search(q=f'track:{song} artist:{artist}', type='track', limit=1)
        if results['tracks']['items']:
            track_uris.append(results['tracks']['items'][0]['uri'])

    # Add tracks to the playlist
    sp.playlist_add_items(playlist['id'], track_uris)
    

if __name__ == "__main__":
    get_top5()
    json_to_csv()
    # print(get_song_info("espresso","Sabrina Carpenter"))