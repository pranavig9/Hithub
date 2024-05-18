import generate_playlist as gp
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
import requests 
import re
import nltk
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')
from nltk.corpus import words
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
nltk.download('opinion_lexicon') 


df = pd.read_csv('output/top5_songs.csv')
data = gp.read_dataset('spotify_millsongdata.csv')

artists5 = df['artist'].tolist()
songs5 = df['song'].tolist()

#list of lyrics of the top 5 songs

def scrape_lyrics(artistname, songname):
    artistname2 = str(artistname.replace(' ','-')) if ' ' in artistname else str(artistname)
    songname2 = str(songname.replace(' ','-')) if ' ' in songname else str(songname)
    page = requests.get('https://genius.com/'+ artistname2 + '-' + songname2 + '-' + 'lyrics')
    html = BeautifulSoup(page.text, 'html.parser')

    # lyrics1 = html.find("div", class_="lyrics")
    # lyrics2 = html.find("div", class_="Lyrics__Container-sc-1ynbvzw-2 jgQsqn")

    lyrics1 = html.select("div[class*=Lyrics__Container]")
    # lyrics2 = html.select("div[class*=lyrics]")
    # print(lyrics2)
    lyrics1_text = ""

    for element in lyrics1:
        lyrics1_text += element.get_text() + "\n"

    return lyrics1_text

def lyrics_onto_frame(artists, songs):
    lyrics = []
    for i in range(len(artists)):
        test = scrape_lyrics(artists[i], songs[i])
        lyrics.append(test)
    return lyrics

top5_lyrics = lyrics_onto_frame(artists5, songs5)


def is_english(word):
    english = set(words.words())
    return word.lower() in english

def expand_contractions(text):
    contractions = {
    "n't": " not", "gon": "going", "na": "to", "'re": " are", "'s": " is", "'d": " would", "'ll": " will", "ca": "can ",
    "'t": " not","'ve": " have", "'m": " am", "wan": "want"
    }
    pattern = re.compile('({})'.format('|'.join(contractions.keys())), flags=re.IGNORECASE)
    return pattern.sub(lambda match: contractions[match.group(0).lower()], text)


def process_lyrics(lyrics):
 
    lyrics = re.sub(r'\[.*?\]', '', lyrics)
    
    lyrics = lyrics.replace('\n', ' ')

    
    lyrics = lyrics.lower()

    lyrics = expand_contractions(lyrics)
    
    sentences = re.split(r'(?<=[.!?])\s+', lyrics)
    
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    
    lines = []
    
    for s in sentences:
        s = re.sub(r'\([^()]*\)', '', s).strip()
        if not s:
            continue
        
        words = word_tokenize(s)
        
        new_words = [
            lemmatizer.lemmatize(word) for word in words if word not in stop_words
        ]

        new_words = [word for word in new_words if is_english(word)]

        
        new_sentence = ' '.join(new_words)
        
        if new_sentence:  
            new_sentence = new_sentence.capitalize()   #capitalize first letters


            if not new_sentence.endswith((".", "?", "!")): #punctuation
                new_sentence += "."    
                        
            lines.append(new_sentence + ' ')
    
    text = ''.join(lines)

    return text

def sentiment(lyrics):

    for i in range(len(lyrics)):
        lyrics[i] = process_lyrics(lyrics[i])

    analyzer = SentimentIntensityAnalyzer()

    def analyzing_sentiment(text):
        sentiment_dict = analyzer.polarity_scores(text)
        if sentiment_dict['compound'] >= 0.1:
            sentiment = 'positive'
        elif sentiment_dict['compound'] <= -0.1:
            sentiment = "negative"
        else: 
            sentiment = "neutral"
        sentiment_dict['Overall sentiment'] = sentiment
        
        return sentiment_dict

    avg = 0
    count = 0
    sentiment_results = []
    for i in lyrics:
        sentiment_result = analyzing_sentiment(i)
        print("Sentiment Analysis Result:", sentiment_result)
        sentiment_results.append(sentiment_result)
        avg += sentiment_result['compound']
        count += 1

    avg_sentiment = avg/count
    print("Average sentiment of top 5 songs:", avg_sentiment)

    return sentiment_results

def own_sentiment():

    nltk_lexicon = {
    'positive' : set(nltk.corpus.opinion_lexicon.positive()), # Why cast to a set?
    'negative' : set(nltk.corpus.opinion_lexicon.negative())
    }

    


def graph_sentiment(sentiment_results):

    compound_scores = [sentiment['compound'] for sentiment in sentiment_results]
    overall_sentiments = [sentiment['Overall sentiment'] for sentiment in sentiment_results]

    colors = ['limegreen' if sentiment == 'positive' else 'crimson' if sentiment == 'negative' else 'lightgrey' for sentiment in overall_sentiments]

    plt.figure(figsize=(10, 6))
    plt.bar(range(1, len(compound_scores) + 1), compound_scores, color=colors, edgecolor='black', width=0.6)

    for i, score in enumerate(compound_scores):
        if score == 0:
            plt.hlines(y=score, xmin=i + 0.7, xmax=i + 1.3, color='black', linestyle='-', linewidth=1)

    #labels
    for i, score in enumerate(compound_scores):
        plt.text(i + 1, score + 0.05, f'{score:.2f}', ha='center', fontsize=8)

    plt.xlabel('Song')
    plt.ylabel('Sentiment Score')
    plt.title('Sentiment Analysis of Top 5 Songs Listened to by User') 
    plt.xticks(range(1, len(compound_scores) + 1), songs5, fontsize=8)

    #labels
    plt.yticks(np.arange(-1, 1.1, 0.5), ['-1 (Negative)', '-0.5', '0 (Neutral)', '0.5', '1 (Positive)'])

    plt.tight_layout() 
    plt.savefig('top5_sentiment_analysis.png')


if __name__ == "__main__":
    sentiment_results = sentiment(top5_lyrics)
    graph_sentiment(sentiment_results)