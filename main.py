import spotipy
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
import os
import json
import http.client
import requests

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"

RECCOBEATS_BASE = "https://api.reccobeats.com/v1"
DEFAULT_TIME_RANGE = "long_term"
DEFAULT_LIMIT = 10

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope="user-top-read"))
  

def get_top_artists(limit = DEFAULT_LIMIT, time_range = DEFAULT_TIME_RANGE):
    return sp.current_user_top_artists(limit=limit, time_range=time_range)

def get_top_songs(limit = DEFAULT_LIMIT, time_range = DEFAULT_TIME_RANGE):
    return sp.current_user_top_tracks(limit=limit, time_range=time_range)


def show(llist):
    for i, item in enumerate(llist["items"], start=1):
        print(f"{i}. {item['name']}")

 
#  RoccoBeats integration
class ReccoBeatsClient:
    def __init__(self, timeout = 10):
        self.timeout = timeout
        self._spotify_to_rb_cache: Dict[str, Optional[str]] = {}

    def spotify_to_reccobeats_id(self, spotify_id) -> Optional[str]:
        if spotify_id in self._spotify_to_rb_cache:
            return self._spotify_to_rb_cache[spotify_id]

        url = f"{RECCOBEATS_BASE}/track"
        r = requests.get(url, params={"ids": spotify_id}, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()

        content = data.get("content", [])
        rb_id = content[0].get("id") if content else None
        self._spotify_to_rb_cache[spotify_id] = rb_id
        return rb_id

    def audio_features(self, spotify_track_id) -> Optional[Dict[str, Any]]:
        rb_id = self.spotify_to_reccobeats_id(spotify_track_id)
        if not rb_id:
            return None

        url = f"{RECCOBEATS_BASE}/track/{rb_id}/audio-features"
        r = requests.get(url, headers={"Accept": "application/json"}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

@dataclass
class TrackVibe:
    name: str
    artist: str
    energy: Optional[float]
    danceability: Optional[float]
    valence: Optional[float]
    tempo: Optional[float]


def top_track_vibes(
    rb,
    limit = DEFAULT_LIMIT,
    time_range = DEFAULT_TIME_RANGE,
) -> List[TrackVibe]:
    top = get_top_songs()

    vibes: List[TrackVibe] = []
    for t in top.get("items", []):
        
        track_id = t.get("id")
        if not track_id:
            continue

        features = rb.audio_features(track_id)
        vibes.append(
            TrackVibe(
                name=t.get("name", "Unknown"),
                artist=(t.get("artists") or [{}])[0].get("name", "Unknown"),
                energy=(features or {}).get("energy"),
                danceability=(features or {}).get("danceability"),
                valence=(features or {}).get("valence"),
                tempo=(features or {}).get("tempo"),
            )
        )
    return vibes

def get_avg_element(elem, data):
    total = 0
    count = 0

    for n in data:
        val = getattr(n, elem, None)

        if val is not None:
            total += val
            count += 1

    return total / count if count else None

               
def average_song_stats(rb):
    song_list = top_track_vibes(rb)

    return (
        get_avg_element("energy", song_list),
        get_avg_element("danceability", song_list),
        get_avg_element("valence", song_list),
        get_avg_element("tempo", song_list),
    )

rb = ReccoBeatsClient()

num = int((input("How many songs and artists?\n")))
term = input("\nshort, medium or long term?\n")

if term == "short":
    term = "short_term"
elif term == "medium":
    term = "medium_term"
elif term == "long":
    term = DEFAULT_TIME_RANGE
else:
    print("invalid term")
 
print("Top Artists:")
show(get_top_artists(num, term))
print("\nTop Tracks:")

show(get_top_songs(num, term))

avg = average_song_stats(rb)
print("\nAverages:", avg)