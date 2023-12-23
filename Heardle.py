import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import time
import random
import requests
from PIL import Image
from io import BytesIO
import spotipy
import pandas as pd
import re
import numpy as np
from dateutil import parser
from datetime import datetime, timezone, timedelta
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from collections import Counter, defaultdict
import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials



client_id ='[Your Spotify client id here]'
client_secret = '[Your Spotify client secret here]'
scope = 'user-modify-playback-state user-library-read'
redirect_uri = 'http://localhost/'

# Initialize Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))


def get_saved_tracks_with_added_date(sp):
    saved_tracks = []
    results = sp.current_user_saved_tracks()
    while results:
        for item in results['items']:
            track = item['track']
            added_at = item['added_at']  # This is the date the track was added to your liked songs
            saved_tracks.append({
                'artist': track['artists'][0]['name'],
                'track_name': track['name'],
                'added_at': item['added_at'],
                'album': track['album']['name'],
                'release_date': track['album']['release_date'],
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity']
            })
        if results['next']:
            results = sp.next(results)
        else:
            results = None
    return saved_tracks


def get_liked_songs_track_ids(sp):
    track_ids = []
    results = sp.current_user_saved_tracks()
    while results:
        for item in results['items']:
            track = item['track']
            track_ids.append(track['id'])
        if results['next']:
            results = sp.next(results)
        else:
            results = None
    return track_ids



# Function to play a song and pause after 10 seconds
def play_and_pause_song(sp, song_uri):
    sp.pause_playback()
    one = input("Press enter to play a song for 1 second")
    sp.start_playback(uris=[song_uri], position_ms = 0)
    time.sleep(1.1)  # Wait for 10 seconds
    sp.pause_playback()  # Pause playback
    three = input("Press enter to play a song for 3 seconds")
    sp.start_playback(uris=[song_uri], position_ms = 0)
    time.sleep(3)  # Wait for 10 seconds
    sp.pause_playback()  # Pause playback
    five = input("Press enter to play a song for 5 seconds")
    sp.start_playback(uris=[song_uri], position_ms = 0)
    time.sleep(5)  # Wait for 10 seconds
    sp.pause_playback()  # Pause playback
    name, artist = get_song_name_from_uri(sp, song_uri)
    print(f"The song was {name} by {artist}")


def get_song_name_from_uri(sp, uri):
    track_info = sp.track(uri)
    return track_info['name'], track_info['artists'][0]['name']

uri_file = open(r"liked_songs_track_ids.txt").readlines()
song_uri_end = random.choice(uri_file).strip()


song_uri = f'spotify:track:{song_uri_end}'

play_and_pause_song(sp, song_uri)

file = open('liked_songs.txt', encoding = 'utf-8').read().splitlines()


def get_season(month):
    if month in [1, 2, 3]:
        return 'Q1'
    elif month in [4, 5, 6]:
        return 'Q2'
    elif month in [7, 8, 9]:
        return 'Q3'
    else:
        return 'Q4'


def displayartist(name):
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']

    if items:
        try:
            artist = items[0]
            image_url = artist['images'][0]['url']
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
        except:
            img = None
        return img
    else:
        print("Artist not found.")
        return None

def plot_most_liked_artists_timeline(most_liked_artists):
    # Setup figure
    fig, ax = plt.subplots(figsize=(15, 8))

    # Convert season-year strings to datetime objects
    season_month_mapping = {'Q1': '01', 'Q2': '04', 'Q3': '07', 'Q4': '10'}
    dates = []
    for season_year in most_liked_artists.keys():
        year, season = season_year.split('-')
        month = season_month_mapping[season]
        date = datetime.strptime(f"{year}-{month}", '%Y-%m')
        dates.append(date)

    # Display each artist's image
    for date, artist in zip(dates, most_liked_artists.values()):
        img = displayartist(artist)
        if img:
            # Convert PIL Image to numpy array and display it on the plot
            ax.imshow(img, aspect=10, extent=(mdates.date2num(date), mdates.date2num(date) + 30, 0, 1))

    # Set title and adjust layout
    ax.set_title('Most Liked Artist by Season')
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=90)
    plt.yticks([])
    plt.ylim(0, 2)

    plt.show()

def most_liked_artist_per_season(file):
    pattern = r'Artist:\s+(.*?)(?:,|$).*?Added On:\s+(\d{4}-\d{2}-\d{2})'
    data = defaultdict(list)

    for line in file:
        match = re.search(pattern, line)
        if match:
            artist, date_str = match.groups()
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            season_key = f"{date_obj.year}-{get_season(date_obj.month)}"
            data[season_key].append(artist)

    most_liked_artists = {}
    for season, artists in data.items():
        most_common_artist = Counter(artists).most_common(1)[0][0]
        most_liked_artists[season] = most_common_artist
    print(most_liked_artists)
    return most_liked_artists

#most_liked_artists = most_liked_artist_per_season(file)
#plot_most_liked_artists_timeline(most_liked_artists)
