import pandas as pd
import get_top5 as gt5
import csv
 
sentiment_data = pd.read_csv("data_with_sentiment.csv")

# consol = pd.read_csv("consolidated_data.csv")
# print(len(consol))

# clumns = ['artist', 'song', 'sentiment', 'popularity', 'duration_ms', 'explicit', 'lyrics']
# total_data = pd.DataFrame(columns=clumns)

for i in range(17701, len(sentiment_data)):
    track = sentiment_data.iloc[i]
    artist = track['artist']
    song = track['song']
    sentiment = track['Sentiment Scores']
    lyrics = track['text']
    link = track['link']
    metadata = gt5.get_song_info(song,artist)
    if metadata:
        pop = metadata[0]
        dur = metadata[1]
        expl=metadata[2]
    else:
        pop=0
        dur =0
        expl = False
    new_row = {'artist':[artist],'song':[song],'sentiment':[sentiment],'popularity':[pop], 'duration_ms':[dur],'explicit':[expl],'lyrics':[lyrics]}
    new_row_df = pd.DataFrame(new_row)
    new_row_df.to_csv('consolidated_data.csv', mode='a', header=False, index=False)
    
# total_data.to_csv('data.csv', index=False)



# file_name = 'consolidated_data.csv'
# with open(file_name, 'w', newline='') as csv_file:
#     writer = csv.DictWriter(csv_file, fieldnames=clumns)

#     # Write the header
#     writer.writeheader()
