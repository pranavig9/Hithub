import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

tfidf = TfidfVectorizer(analyzer='word', stop_words='english')
songs = pd.read_csv("spotify_millsongdata.csv")
# print(cosine_similarities)
def find_similar_songs(song_index, num_similar=15):
    # Vectorize the lyrics using TF-IDF
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(songs['text'].values.astype('U'))

    # Compute the similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix[song_index], tfidf_matrix)

    # Get indices of similar songs (excluding the input song itself)
    similar_song_indices = similarity_matrix.argsort()[0][-num_similar-1:-1][::-1]

    # Return similar songs
    similar_songs = songs.iloc[similar_song_indices]
    return similar_songs

chosen_songs = ['Soldiers', 'Sleigh Ride', 'Shimmy Down The Chimney (Fill Up My Stocking)', 'Winter Things', 'A Very Bieber Christmas']

# Find similar songs for each chosen song
for song_name in chosen_songs:
    try:
        # if song name is not there then, use a song from the same artist, else levenstein distance metric closest song in dataset
        song_index = songs[songs['song'] == song_name].index[0]

        similar_songs = find_similar_songs(song_index)
        print(f"Similar songs for '{song_name}':")
        print(similar_songs[['artist', 'song', 'link']])
        print("\n")
    except:
        print("No songs for this one")