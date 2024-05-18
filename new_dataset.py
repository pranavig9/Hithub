import generate_playlist as gp
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
import requests 
import playlists as p
import re
import top5_sentiment as ts


data = gp.read_dataset('spotify_millsongdata.csv')
print(data.head())

artists = data['artist'].tolist()
songs = data['song'].tolist()
lyrics = data['text'].tolist()

sentiment_scores = []
result = ts.sentiment(lyrics)
for s in result:
    print(s['compound'])
    sentiment_scores.append(s['compound'])

data_copy = data.copy()  
data_copy['Sentiment Scores'] = sentiment_scores


data_copy.to_csv('data_with_sentiment.csv', index=False)




