import get_top5 as pull
import pandas as pd
import generate_playlist as get_data
import name_generation as ldatm
import knn_recommend as song_recs
import top5_sentiment as ts

# print(ts.sentiment(["Happy days woohoo"]))

if __name__ == "__main__":
    pull.get_top5()
    pull.json_to_csv()

    usertop5 = pd.read_csv('output/top5_songs.csv')
    track_data = pd.read_csv("consolidated_data.csv")
    song_names = []
    print("Pulled top 5 songs")
    for _, song in usertop5.iterrows():
        artist = song['artist']
        songname = song['song']
        song_names.append(songname)
        match = track_data[(track_data['artist'] == artist) & (track_data['song'] == songname)]
        print("Updating Dataset as needed")
        # print(match)
        if len(match)==0:
            pop = song['popularity']
            dur = song['duration_ms']
            expl = song['explicit']
            lyrics = get_data.scrape_lyrics(artist,songname)
            ##ADD THIS
            if not lyrics:
                lyrics = songname
            sentiment = ts.sentiment([lyrics])
            # print(sentiment)
            sentiment = sentiment[0]['compound']
            new_row = {'artist':[artist],'song':[songname],'sentiment':[sentiment],'popularity':[pop], 'duration_ms':[dur],'explicit':[expl],'lyrics':[lyrics]}
            new_row_df = pd.DataFrame(new_row)
            new_row_df.to_csv('consolidated_data.csv', mode='a', header=False, index=False)
        ##USE KNN recommender to generate song titles
    print("Beginning Recommending Songs")
    playlist_content = song_recs.returnRecommendSongs(track_data)
    # print(playlist_content)
        ##USE LDA TOPIC MODELING TO GET LYRICS 
    print("Creating playlist title")
    title = ldatm.generateDaylistTitle(song_names, track_data)
    print(title)
        ##CREATE PLAYLIST
    print("Creating Playlist")
    pull.create_spotify_playlist(title, playlist_content)

