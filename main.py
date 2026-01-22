import spotipy
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
from dotenv import load_dotenv
import os
import json
import http.client
import requests

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"

def spotify_auth(SCOPE):
      sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope=SCOPE))
      
      return sp
  

def get_top_artists():

    sp = spotify_auth("user-top-read")
    top_artists = sp.current_user_top_artists(limit = 10, time_range = 'long_term')
    return top_artists

def get_top_songs():
    
    sp = spotify_auth("user-top-read")
    top_songs = sp.current_user_top_tracks(limit = 10, time_range = 'long_term')

    return top_songs

def show(llist):
    for i, item in enumerate(llist["items"], start=1):
        print(f"{i}. {item['name']}")

 
def get_reccobeats_features(track_id):
    
    conn = http.client.HTTPSConnection("api.reccobeats.com")

    headers = {
        "Accept": "application/json"
    }
    
    rocco_track_id = spotify_to_roccobeatsID(track_id)
    conn.request(
        "GET",
        f"/v1/track/{rocco_track_id}/audio-features",
        headers=headers
    )

    res = conn.getresponse()
    data = res.read().decode("utf-8")

    return json.loads(data)

def spotify_to_roccobeatsID(spotify_id):
    url = "https://api.reccobeats.com/v1/track"
    r = requests.get(url, params={"ids": spotify_id})
    r.raise_for_status()

    data = r.json()

    content = data.get("content", [])
    if not content:
        return None

    return content[0]["id"]


def get_song_vibe():
    
    songs = get_top_songs()
    track_id = [t["id"] for t in songs["items"]]
    
    vibes = []
    for t in songs["items"]:
        track_id = t["id"]
        if not track_id:
            continue
            
        features = get_reccobeats_features(track_id)

        vibes.append({
            "name": t["name"],
            "artist": t["artists"][0]["name"],
            "energy": features.get("energy"),
            "danceability": features.get("danceability"),
            "valence": features.get("valence"),
            "tempo": features.get("tempo"),
        })
    return vibes

def get_avg_element(elem, json_data):
    total = 0
    count = 0
    
    for n in json_data:
        val = n.get(elem)
        
        if(val is not None):
            total += val
            count += 1
    return total / count if count > 0 else None
               
def average_song_stats():
   song_list =  get_song_vibe()
   
   avg_energy = get_avg_element("energy", song_list)
   avg_dancebility = get_avg_element("danceability", song_list)
   avg_valence = get_avg_element("valence", song_list)
   avg_tempo = get_avg_element("tempo", song_list)
   
   print(avg_tempo,avg_dancebility,avg_valence,avg_energy)
   
average_song_stats()