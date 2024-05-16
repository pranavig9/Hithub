import generate_playlist as gp
import numpy as np
import pandas as pd
import requests 
import re
import top5_sentiment as tp
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors


data = pd.read_csv('data_with_sentiment.csv')
scores = data['Sentiment Scores'].tolist()
lyrics = data['text'].tolist()

neg = sum(1 for num in scores if num < 0)
zero = sum(1 for num in scores if num == 0)
pos = sum(1 for num in scores if num > 0)

#Total dataset
print("Number of negative songs:", neg)
print("Number of neutral songs:", zero)
print("Number of positive songs:", pos)

categories = ['negative', 'neutral', 'positive']
counts = [neg, zero, pos]
plt.bar(categories, counts, color=['red', 'blue', 'green'])
plt.xlabel('Sentiment')
plt.ylabel('Number of songs in dataset')
plt.savefig('full_dataset_songs_sentiment.png')


k = 5

sentiment_results = tp.sentiment(tp.top5_lyrics)
top_scores = []
for s in sentiment_results:
    top_scores.append(s['compound'])


top_scores = np.array(top_scores).reshape(-1, 1)
scores = np.array(scores).reshape(-1, 1)


knn_model = NearestNeighbors(n_neighbors=k, metric='euclidean')
knn_model.fit(scores)

distances, indices = knn_model.kneighbors(top_scores)

num_recommendations = 5
for i in range(len(top_scores)):
    print("Top", num_recommendations, "recommended songs for top song", i+1)
    for j in range(num_recommendations):
        recommended_song_index = indices[i, j]
        print("Recommended Song", j+1, ": Song", data['song'][recommended_song_index], "Score: ", data['Sentiment Scores'][recommended_song_index])


