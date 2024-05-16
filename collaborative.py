from bs4 import BeautifulSoup
import requests
import csv
import time
import re
from urllib.parse import urlparse, parse_qs

def scrape_data(artistname, songname):
    artistname2 = str(artistname.replace(' ','-')) if ' ' in artistname else str(artistname)
    # songname2 = str(songname.replace(' ','-')) if ' ' in songname else str(songname)
    songname2 = str(re.sub(r'[^a-zA-Z0-9\s]', '', songname).lower().replace(" ", "-")) if ' ' in songname else str(songname)
    page = requests.get('https://genius.com/'+ artistname2 + '-' + songname2 + '-' + 'lyrics')
    # print('https://genius.com/'+ artistname2 + '-' + songname2 + '-' + 'lyrics')
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics_divs = html.find_all('div', {'data-lyrics-container': 'true'})
    if lyrics_divs:
        lyrics_text = [div.get_text(strip=False) for div in lyrics_divs]
    lyrics = ' '.join(lyrics_text)
    metadata = html.find("div", class_="MetadataStats__Container-sc-1t7d8ac-0 cDJyol")
    release_date = None
    views_text = None
    producers = None
    producers_div = html.find("div", class_="HeaderCredits__List-wx7h8g-3 cTzqde")
    if producers_div:
        producers = [a.get_text(strip=True) for a in producers_div.find_all("a", class_="StyledLink-sc-3ea0mt-0 iegxRM")]
    if metadata:
        views_span = metadata.find("span", class_="LabelWithIcon__Label-hjli77-1 hgsvkF", string=lambda text: "views" in text)
        release_span = metadata.find("span", class_="LabelWithIcon__Label-hjli77-1 hgsvkF")
        if views_span:
            views_text = views_span.get_text(strip=True)
        if release_span:
            release_date = release_span.get_text(strip=True)
    views = string_to_number(views_text[:-6])
    with open("songdata.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([artistname, songname, lyrics, views, release_date, producers])


def string_to_number(s):
    # Define a dictionary to map suffixes to multiplier values
    suffixes = {'K': 1000, 'M': 1000000, 'B': 1000000000}
    numeric_part = s[:-1]
    suffix = s[-1]
    number = float(numeric_part)
    if suffix in suffixes:
        number *= suffixes[suffix]
    return number



# scrape_data("Taylor Swift", "cardigan")
# print(scrape_lyrics("Kendrick Lamar", "Not Like Us"))
# scrape_data("Kendrick Lamar", "Not Like Us")
# scrape_data("Olivia Rodrigo", "bad idea right?"