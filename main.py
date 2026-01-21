import spotipy
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"


def get_top_artists():
    
    SCOPE = "user-top-read"
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope=SCOPE))
    
    top_artists = sp.current_user_top_artists(limit = 10, time_range = 'long_term')
    for i, artist in enumerate(top_artists["items"], start=1):
        print(f"{i}. {artist['name']}")

    return top_artists

