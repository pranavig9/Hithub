import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from lyricsgenius import Genius
import argparse

GENIUS_API_TOKEN='tHOsGvtPGWYle78o8rb6yQ5DZWMtcByUoopigVqRmn9Vi3KbZaSCiVrWnSwpZTXm'

def preprocess(fp):
  data = pd.read_csv(fp)
  data = data.sample(n=8000).drop('link', axis=1).reset_index(drop=True)
  data['artsong'] = data.apply(lambda row: row['artist']+row['song'],axis = 1)
  data = data.drop_duplicates('artsong')
  # data = data[['artist_name','id','track_name','danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]
  return data[['artist', 'song', 'text']]

def print_recommend(input_song, recom_song):
  rec_items = len(recom_song)

  print(f'The {rec_items} recommended songs for {input_song} are:')
  for i in range(rec_items):
      print(f"Number {i+1}:")
      print(f"{recom_song[i][1]} by {recom_song[i][2]} with {round(recom_song[i][0], 3)} similarity score") 
      print("--------------------")
        
def recommend(rec, sim_matrix):
  # Get song to find recommendations for
  song = rec['song name']
  # Get number of songs to recommend
  number_songs = rec['number_of_songs']
  # Get the number of songs most similars from matrix similarities
  recommendation = sim_matrix[song][:number_songs]
  # print each item
  print_recommend(song, recommendation)
  return recommendation

def scrape_lyrics(artistname, songname):
  genius = Genius(GENIUS_API_TOKEN)
  artist = genius.search_artist(artistname, max_songs=1, sort="title")
  song = genius.search_song(songname, artist.name)
  return song.lyrics

def recommend_songs(data, rec):
  artist = rec["artist name"]
  song = rec["song name"]
  if song not in data["song"]:
    lyrics = scrape_lyrics(artist, song)
    data.loc[len(data.index)] = [artist, song, lyrics]
  tf_idf = TfidfVectorizer(analyzer='word', stop_words='english')
  vectorized_lyrics = tf_idf.fit_transform(data['text'])
  cosine_sim = cosine_similarity(vectorized_lyrics)
  sim = {}
  for i in range(len(cosine_sim)):
    similar_indices = cosine_sim[i].argsort()[:-50:-1] 
    sim[data['song'].iloc[i]] = [(cosine_sim[i][x], data['song'][x], data['artist'][x]) for x in similar_indices][1:]

  recommend(rec, sim)
  
def recommend_playlist(input_playlist, data_fp, num_songs):
  playlist = pd.read_csv(input_playlist)
  data = preprocess(data_fp)
  recs = []
  for i in range(len(playlist)):
    rec = {}
    rec['song name'] = playlist.loc[i, 'song']
    rec['artist name'] = playlist.loc[i, 'artist']
    rec['number_of_songs'] = num_songs
    recs.append(rec)
  new_playlist = []
  for rec in recs:
    recommended_songs = recommend_songs(data, rec)
    new_playlist.append(recommend_songs)

  return new_playlist

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--top5_songs', required=True)
  parser.add_argument('--data_path', required=True)
  parser.add_argument('--num_songs', required=True)
  args = parser.parse_args()

  new_playlist = recommend_playlist(args.top5_songs, args.data_path, int(args.num_songs))
