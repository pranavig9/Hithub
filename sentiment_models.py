import generate_playlist as gp
import numpy as np
import pandas as pd
import requests 
import re
import top5_sentiment as tp
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.express as px
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import silhouette_score



data = pd.read_csv('data_with_sentiment.csv')
scores = data['Sentiment Scores'].tolist()
lyrics = data['text'].tolist()

#length of song titles and lyrics
data['song_title_word_count'] = data['song'].str.split().str.len()
data['lyrics_word_count'] = data['text'].str.split().str.len()

"---------------------------------------------------------------------------------"

neg = sum(1 for num in scores if num < 0)
zero = sum(1 for num in scores if num == 0)
pos = sum(1 for num in scores if num > 0)

#overall analysis of dataframe with sentiment score data (mean, std, etc.)
print("Overall Song Sentiment Data")
print(data['Sentiment Scores'].describe())
print()

#Total dataset counts and graph of it
print("Number of negative songs:", neg)
print("Number of neutral songs:", zero)
print("Number of positive songs:", pos)
vals = ['negative', 'neutral', 'positive']
plt.bar(vals, [neg, zero, pos], color=['red', 'blue', 'green'])
plt.xlabel('Sentiment')
plt.ylabel('Number of songs')
plt.title('Number of Songs per Sentiment Classification')
plt.savefig('full_dataset_songs_sentiment.png')

"---------------------------------------------------------------------------------"

#Histogram of Lyric Count versus Sentiment Score (-1 is the lowest, 1 is the highest)
plt.clf()  
plt.hist(data['Sentiment Scores'], bins=20, color='gray')
plt.xlabel('Sentiment Score')
plt.ylabel('Frequency')
plt.title('Distribution of Sentiment Scores')
plt.savefig('sentiment_histogram_with_wordcount.png')

"---------------------------------------------------------------------------------"

#Sentiment scores for the top 5 songs by user 
sentiment_results = tp.sentiment(tp.top5_lyrics)
top_scores = []
for s in sentiment_results:
    top_scores.append(s['compound'])


top_scores = np.array(top_scores).reshape(-1, 1)
scores = np.array(scores).reshape(-1, 1)

"---------------------------------------------------------------------------------"

#K-Nearest Neighbors with 5 neighbors (5 songs per recommendation)
k = 5
knn_model = NearestNeighbors(n_neighbors=k, metric='euclidean')
knn_model.fit(scores)

distances, indices = knn_model.kneighbors(top_scores)

print('K-Nearest-Neighbors Recommended Songs: ')
print(' ')
num_recommendations = 5
for i in range(len(top_scores)):
    print("Top", num_recommendations, "recommended songs by knn for song", i+1)
    for j in range(num_recommendations):
        indx = indices[i, j]
        print(" Song", j+1, " ", data['song'][indx], "; Score: ", data['Sentiment Scores'][indx])

print()

"---------------------------------------------------------------------------------"

#K-means with 5 clusters
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(scores)

cluster_labels = kmeans.labels_

def kmeans_recommend(top_scores, k=5):
    recs = []
    for score in top_scores:

        best = kmeans.predict(np.array(score).reshape(1, -1))[0]  
        
        cluster_i = np.where(cluster_labels == best)[0]
        
        scores_arr = np.array(scores).reshape(-1, 1)  

        cluster_i = np.setdiff1d(cluster_i, np.where(np.isin(scores_arr, score))[0])

        len_clusteri = len(cluster_i)
        
        rec_indices = np.random.choice(cluster_i, size=min(k, len_clusteri), replace=False)
        
        recs.append(data.iloc[rec_indices])
    
    return recs

recommended_songs = kmeans_recommend(top_scores)

for i, songs in enumerate(recommended_songs):
    print(f"Top {i+1} Recommended Songs:")
    print(songs[['song', 'artist', 'Sentiment Scores']])

print()


sil = silhouette_score(scores, cluster_labels)
print(f"Silhouette Score for K-means clustering with 5 clusters: {sil}")

print()
"---------------------------------------------------------------------------------"

print("Naive Bayes: ")

sentiment_labels = []

for i in scores: 
    if i<0:
        sentiment_labels.append('negative')
    elif i==0:
        sentiment_labels.append('neutral')
    else:
        sentiment_labels.append('positive')


#can't be negative so apply Laplace Smoothing
scores = scores +1
top_scores = top_scores +1

X_train, X_test, y_train, y_test = train_test_split(scores, sentiment_labels, test_size=0.2, random_state=42, stratify=sentiment_labels)

nb_classifier = MultinomialNB(class_prior=None, fit_prior=True)
nb_classifier.fit(X_train, y_train)
y_pred = nb_classifier.predict(X_test)

print()


#Evaluating Naive Bayes
print("Naive Bayes classification report:", classification_report(y_test, y_pred, zero_division=1))
accuracy = accuracy_score(y_test, y_pred)
print("Naive Bayes Accuracy:", accuracy)


print()

def recommend(top_scores, classifier, k=5):
    recommendations = []
    for score in top_scores:
        sentiment_label = classifier.predict(np.array(score).reshape(1, -1))[0]  # Predict sentiment label

        indices = np.where(np.array(sentiment_labels) == sentiment_label)[0]

        data_recs = data.iloc[indices] 
        recommended_songs = data_recs.sample(min(k, len(data_recs)))
        
        recommendations.append(recommended_songs)
    
    return recommendations


naive_recs = recommend(top_scores, nb_classifier)

for i, songs in enumerate(naive_recs):
    print(f"Top {i+1} Recommended Songs:")
    print(songs[['song', 'artist', 'Sentiment Scores']])


scores = scores - 1
top_scores = top_scores - 1

print()

"---------------------------------------------------------------------------------"

print("Logistic model")

X_train, X_test, y_train, y_test = train_test_split(scores, sentiment_labels, test_size=0.2, random_state=42, stratify=sentiment_labels)


logistic_classifier = LogisticRegression(max_iter=1000)  

logistic_classifier.fit(X_train, y_train)
y_pred = logistic_classifier.predict(X_test)

print()

#Evaluating Logistic
print("Logistic classification report:", classification_report(y_test, y_pred))
accuracy = accuracy_score(y_test, y_pred)
print("Logistic Regression Accuracy:", accuracy)
 

print()

logistic_recs = recommend(top_scores, logistic_classifier)

for i, songs in enumerate(logistic_recs):
    print(f"Top {i+1} Recommended Songs:")
    print(songs[['song', 'artist', 'Sentiment Scores']])


print()

"---------------------------------------------------------------------------------"

