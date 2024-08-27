import os
import requests
import base64
from urllib.parse import urlencode
from dotenv import load_dotenv
from flask import Flask, request, redirect, session, url_for

# Load environment variables from .env file
load_dotenv()

# Spotify API credentials from environment variables
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:8080/callback"

# Flask setup
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global variable to store access token
access_token = None

@app.route('/')
def login():
    scopes = "playlist-modify-public playlist-modify-private"
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scopes
    }
    return redirect(f"{auth_url}?{urlencode(params)}")

@app.route('/callback')
def callback():
    global access_token
    code = request.args.get('code')
    
    token_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token
        with open("access_token.txt", "w") as file:
            file.write(access_token)
        return "User authenticated successfully! You can now close this browser tab and return to the console."
    else:
        return f"Error fetching access token: {response.status_code} - {response.text}"

def get_user_id(access_token):
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("id")
    else:
        print(f"Error fetching user ID: {response.status_code} - {response.text}")
        return None

def create_spotify_playlist(user_id, playlist_name, access_token):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "name": playlist_name,
        "description": "Playlist created automatically with Python script.",
        "public": False  # Set to False if you want the playlist to be private
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        return response.json().get("id")
    else:
        print(f"Error creating playlist: {response.status_code} - {response.text}")
        return None

def add_tracks_to_playlist(playlist_id, track_ids, access_token):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"uris": [f"spotify:track:{track_id}" for track_id in track_ids]}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print("Tracks added successfully.")
    else:
        print(f"Error adding tracks: {response.status_code} - {response.text}")

def refresh_access_token(refresh_token):
    token_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        new_tokens = response.json()
        return new_tokens.get('access_token')
    else:
        print(f"Error refreshing access token: {response.status_code} - {response.text}")
        return None

if __name__ == '__main__':
    app.run(port=8080)
