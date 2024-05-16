import generate_playlist as gp
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
import requests 
import re
import top5_sentiment as tp
import matplotlib.pyplot as plt


data = pd.read_csv('data_with_sentiment.csv')
scores = data['Sentiment Scores'].tolist()

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