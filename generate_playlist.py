import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from lyricsgenius import Genius
import nltk
from nltk.corpus import stopwords
import argparse
from evaluate_perf_cont import compare

GENIUS_API_TOKEN='tHOsGvtPGWYle78o8rb6yQ5DZWMtcByUoopigVqRmn9Vi3KbZaSCiVrWnSwpZTXm'

def preprocess(fp):
  data = pd.read_csv(fp)
  if 'link' in data.columns:
    data = data.drop('link', axis=1).reset_index(drop=True)
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
  stopwords_lyrics = stopwords.words('english')
  artist = rec["artist name"]
  song = rec["song name"]
  if song not in data["song"]:
    lyrics = scrape_lyrics(artist, song)
    data.loc[len(data.index)] = [artist, song, lyrics]
  lyrics_vectorizer = TfidfVectorizer(
    encoding='utf-8',
    strip_accents='unicode',
    lowercase=True,
    stop_words=stopwords_lyrics,
    min_df=2,
    max_df=0.9,
    binary=False,
    norm='l2',
    use_idf=False,
    max_features=5000
)
  vectorized_lyrics = lyrics_vectorizer.fit_transform(data['text'])
  cosine_sim = cosine_similarity(vectorized_lyrics)
  sim = {}
  for i in range(len(cosine_sim)):
    similar_indices = cosine_sim[i].argsort()[:-50:-1][1:]
    sim[data['song'].iloc[i]] = [(cosine_sim[i][x], data['song'][x], data['artist'][x]) for x in similar_indices][1:]

  return recommend(rec, sim), data
  
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
    recommended_songs, new_data = recommend_songs(data, rec)
    new_playlist.append(recommended_songs)

  new_data.to_csv('spotify_millsongdata.csv')

  return new_playlist

def update_format(output_playlist, num_songs):
  final_playlist = []
  for i in range(len(output_playlist)):
    for j in range(num_songs):
      artist = output_playlist[i][j][2]
      song = output_playlist[i][j][1]
      final_tuple = (artist, song)
      final_playlist.append(final_tuple)

  return final_playlist

def evaluate_playlist(input_playlist, outputted_playlist, num_songs):
  playlist = pd.read_csv(input_playlist)
  for i in range(len(playlist)):
    song = playlist.loc[i, 'song']
    artist = playlist.loc[i, 'artist']
    print(f"Song: {song}")
    print(f"Artist: {artist}")
    for j in range(num_songs):
      output_song = outputted_playlist[i][j][1]
      output_artist = outputted_playlist[i][j][2]
      print(f"Recommened Song: {output_song}")
      most_common_words = compare(song, artist, output_song, output_artist)
      print(f"Most Common Words: {' '.join(most_common_words)}")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--top5_songs', required=True)
  parser.add_argument('--data_path', required=True)
  parser.add_argument('--num_songs', required=True)
  args = parser.parse_args()

  new_playlist = recommend_playlist(args.top5_songs, args.data_path, int(args.num_songs))
  # new_playlist = [[(0.6090642393449999, 'Chiquita', 'Aerosmith'), (0.6035552437489646, 'For You To Love', 'Luther Vandross'), (0.5934304589578079, 'Love Is Dangerous', 'Fleetwood Mac')], [(0.5612663413205756, "You Don't Love Me (No, No, No)", 'Rihanna'), (0.5310446240737012, 'But You Know I Love You', 'Waylon Jennings'), (0.5284001118749688, 'Yes I Do', 'Rascal Flatts')], [(0.8975209606514932, 'Somebody Loves You', 'Marianne Faithfull'), (0.8853818401504832, 'Birthday Song', 'Madonna'), (0.8702737247476661, 'I Believe In You', 'Dusty Springfield')], [(0.6548001287515242, 'Upsetter', 'Grand Funk Railroad'), (0.6530754106590009, 'Locked Out Of Heaven', 'Bruno Mars'), (0.6253150949974127, "I've Got A Feeling", 'Pearl Jam')], [(0.8497257782985548, 'plot twist', 'TWS'), (0.8067483457693106, 'Somebody Loves You', 'Marianne Faithfull'), (0.7890071357555971, 'Birthday Song', 'Madonna')]]
  evaluate_playlist(args.top5_songs, new_playlist, int(args.num_songs))
