import requests
import base64
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Step 1: Get the client_id and client_secret from environment variables
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Function to fetch the access token
def get_access_token(client_id, client_secret):
    # Encode your credentials
    credentials = f"{client_id}:{client_secret}"
    credentials_b64 = base64.b64encode(credentials.encode()).decode()

    # Request access token
    auth_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {credentials_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(auth_url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error fetching access token: {response.status_code} - {response.text}")
        return None

# Function to get all track IDs from a playlist
def get_playlist_track_ids(playlist_id):
    # Get the access token
    access_token = get_access_token(client_id, client_secret)
    if not access_token:
        print("Access token retrieval failed.")
        return None

    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "fields": "items(track(id,name,artists(name))),next",
        "limit": 100
    }
    
    all_track_ids = []
    track_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    # Fetch tracks in pages
    while track_url:
        response = requests.get(track_url, headers=headers, params=params)
        
        if response.status_code == 200:
            playlist_data = response.json()
            tracks = playlist_data['items']
            for item in tracks:
                track = item['track']
                track_id = track['id']
                track_name = track['name']
                artists = ", ".join(artist['name'] for artist in track['artists'])
                print(f"Found track: {track_name} by {artists}")  # Debug: Print track details
                all_track_ids.append(track_id)  # Collect track ID
            
            # Move to next set of tracks if available
            track_url = playlist_data['next']
        else:
            print(f"Error fetching tracks: {response.status_code} - {response.text}")
            break

    return all_track_ids

if __name__ == "__main__":
    # Example playlist ID
    playlist_id = "7vN3ueHmJS4Z5BHAKEW1f1"  # Replace with your actual playlist ID

    # Fetch track IDs from the playlist
    track_ids = get_playlist_track_ids(playlist_id)

    # Check if track IDs were successfully retrieved
    if track_ids:
        print("Tracks in Playlist:")
        for idx, track_id in enumerate(track_ids, start=1):
            print(f"{idx}. {track_id}")
    else:
        print("Failed to retrieve track IDs or no tracks found in the playlist.")
