from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import pandas as pd
from nltk.corpus import stopwords
import string
import re
from lyricsgenius import Genius

GENIUS_API_TOKEN='tHOsGvtPGWYle78o8rb6yQ5DZWMtcByUoopigVqRmn9Vi3KbZaSCiVrWnSwpZTXm'

def tokenize(text):
    """Returns a list of words that make up the text.
    
    Note: for simplicity, lowercase everything.
    Requirement: Use Regex to satisfy this function
    
    Params: {text: String}
    Returns: List
    """
    # YOUR CODE HERE
    return re.findall(r'[a-z]+', text.lower())

def word_stats(data, stops=None, n=20):
    data_lower = Counter()
    for key in data.keys():
        data_lower[key.lower()] += data[key] #lowercase
    if stops:
        for stop in stops:
            del data_lower[stop] # remove any stopwords
    # print("\nTotal words:", sum(data_lower.values())) # print wordcount
    # print(f"\nTop {n} words by frequency: ") 
    # for word in data_lower.most_common(n):
    #     print(f"{word[0]}\t{word[1]}") # print most frequent words
    return data_lower

def scrape_lyrics(artistname, songname):
  genius = Genius(GENIUS_API_TOKEN)
  artist = genius.search_artist(artistname, max_songs=1, sort="title")
  song = genius.search_song(songname, artist.name)
  return song.lyrics

def compare(song_name_in, artist_name_in, song_name_output, artist_name_output):
  data = pd.read_csv("spotify_millsongdata.csv")
  stopwords_lyrics = stopwords.words('english')
  stopwords_lyrics = set(stopwords_lyrics).union(set(string.punctuation)).union(set(string.digits)).union(set(string.ascii_lowercase))
  custom_stops = [ "`", "``","''", "'s", "n't", "''",  "’", "wan", "'ll" , "'ve", "``", "n't", "'s", "oh", "na", "'m", "like", "'re", "'d", "'", "(", ")"]
  stopwords_lyrics = stopwords_lyrics.union(set(custom_stops))
  lyrics = data.iloc[data.index[(data["song"] == song_name_output) & (data["artist"] == artist_name_output)]]["text"]
  lyrics = lyrics.values[0]
  lyrics_tokens = tokenize(lyrics)
  song_best = word_stats(Counter(lyrics_tokens), stopwords_lyrics, 10)

  input_lyrics = data.iloc[data.index[(data["song"] == song_name_in) & (data["artist"] == artist_name_in)]]["text"]
  input_lyrics = input_lyrics.values[0]
  lyrics_tokens2 = tokenize(input_lyrics)
  song_best2 = word_stats(Counter(lyrics_tokens2), stopwords_lyrics, 10)

  most_common = set(lyrics_tokens) & set(lyrics_tokens2)
  for word in list(most_common):
    if word in stopwords_lyrics:
          most_common.remove(word)
  return most_common