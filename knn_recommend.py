import generate_playlist as gp
import numpy as np
import pandas as pd
import requests 
import re
import top5_sentiment as tp
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors


def returnRecommendSongs(data):
    scores = data['sentiment'].tolist()
    lyrics = data['lyrics'].tolist()
    popularity = data['popularity'].tolist()
    duration_ms = data['duration_ms'].tolist()
    explicit = data['explicit'].tolist()
    k = 10
    sentiment_results = tp.sentiment(tp.top5_lyrics)
    top_scores = []
    for s in sentiment_results:
        top_scores.append(s['compound'])
    top_scores = np.array(top_scores).reshape(-1, 1)
    scores = np.array(scores).reshape(-1, 1)
    features = np.column_stack((scores, popularity, duration_ms, explicit))
    # print(features.shape())
    knn_model = NearestNeighbors(n_neighbors=k, metric='euclidean')
    knn_model.fit(features)
    distances, indices = knn_model.kneighbors(features)
    num_recommendations = 10
    playlist_content = []
    for i in range(len(top_scores)):
        # print("Top", num_recommendations, "recommended songs for top song", i+1)
        for j in range(num_recommendations):
            recommended_song_index = indices[i, j]
            recsong = data['song'][recommended_song_index]
            recartist = data['artist'][recommended_song_index]
            playlist_content.append((recartist,recsong))

            # print("Recommended Song", j+1, ": Song", data['song'][recommended_song_index], "Score: ", data['sentiment'][recommended_song_index])

    return playlist_content






