import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-modify-playback-state"
))

def play_song(song):
    tracks = sp.search(q=song, type="track", limit=1)["tracks"]["items"]

    if not tracks:
        return f"Couldn't find {song}."

    track = tracks[0]
    sp.start_playback(uris=[track["uri"]])

    return f"Playing {track['name']} by {track['artists'][0]['name']}."