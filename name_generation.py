from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import nltk 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import pandas as pd


nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

songs = pd.read_csv("consolidated_data.csv")

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def generateDaylistTitle(song_names, songs):
    preprocessed_songs = []
    for sname in song_names:
        try:
            lyrics = songs[songs['song']==sname]['lyrics'].value[0]
        except:
            lyrics = sname
        words = word_tokenize(lyrics.lower())
        filtered_words = [lemmatizer.lemmatize(word) for word in words if word.isalpha() and word not in stop_words]
        preprocessed_songs.append(" ".join(filtered_words))
    vectorizer = CountVectorizer(max_features=1000)
    X = vectorizer.fit_transform(preprocessed_songs)
    num_topics = 5  
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(X)
    feature_names = vectorizer.get_feature_names_out()
    topic_words = []
    for topic_idx, topic in enumerate(lda.components_):
        top_words_idx = topic.argsort()[:-6:-1]  
        top_words = [feature_names[i] for i in top_words_idx]
        topic_words.append(top_words)
    representative_words = set()
    for words in topic_words:
        representative_words.update(words)
    title = ' '.join(list(representative_words)[:5])
    return title

# song_names = ['Sleigh Ride', 'How About Me?', 'Soft Parachutes', 'Bridge Over Troubled Water' , 'Lifelong Passion']
# print(generateDaylistTitle(song_names,songs))
