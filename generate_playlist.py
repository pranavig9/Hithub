import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
import requests

class ContentBasedRecommender:
    def __init__(self, matrix):
        self.matrix_similar = matrix

    def _print_message(self, song, recom_song):
        rec_items = len(recom_song)
        
        print(f'The {rec_items} recommended songs for {song} are:')
        for i in range(rec_items):
            print(f"Number {i+1}:")
            print(f"{recom_song[i][1]} by {recom_song[i][2]} with {round(recom_song[i][0], 3)} similarity score") 
            print("--------------------")
        
    def recommend(self, recommendation):
        # Get song to find recommendations for
        song = recommendation['song']
        # Get number of songs to recommend
        number_songs = recommendation['number_songs']
        # Get the number of songs most similars from matrix similarities
        recom_song = self.matrix_similar[song][:number_songs]
        # print each item
        self._print_message(song=song, recom_song=recom_song)

def read_dataset(fp):
  songs = pd.read_csv(fp)
  return songs

def scrape_lyrics(artistname, songname):
    artistname2 = str(artistname.replace(' ','-')) if ' ' in artistname else str(artistname)
    songname2 = str(songname.replace(' ','-')) if ' ' in songname else str(songname)
    page = requests.get('https://genius.com/'+ artistname2 + '-' + songname2 + '-' + 'lyrics')
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics1 = html.find("div", class_="lyrics")
    lyrics2 = html.find("div", class_="Lyrics__Container-sc-1ynbvzw-2 jgQsqn")
    if lyrics1:
        lyrics = lyrics1.get_text()
    elif lyrics2:
        lyrics = lyrics2.get_text()
    elif lyrics1 == lyrics2 == None:
        lyrics = None
    return lyrics

def recommend_songs(data, rec):
  artist = rec["artist name"]
  song = rec["song"]
  if song not in data["song"]:
    lyrics = scrape_lyrics(artist, song)
    data.loc[len(data.index)] = [artist, song, None, lyrics]
  tf_idf = TfidfVectorizer(analyzer='word', stop_words='english')
  vectorized_lyrics = tf_idf.fit_transform(data['text'])
  cosine_sim = cosine_similarity(vectorized_lyrics)
  sim = {}
  for i in range(len(cosine_sim)):
    similar_indices = cosine_sim[i].argsort()[:-50:-1] 
    sim[data['song'].iloc[i]] = [(cosine_sim[i][x], data['song'][x], data['artist'][x]) for x in similar_indices][1:]

  recs = ContentBasedRecommender(sim)

  recs.recommend(rec)
  
if __name__ == "__main__":
  data = read_dataset('spotify_millsongdata.csv')
  rec = {
    "song": data['song'].iloc[10],
    "artist name": "",
    "number_songs": 3
  }
  recommended_songs = recommend_songs(data, rec)
  print(recommended_songs)
