import requests
import base64
from dotenv import load_dotenv
import os
import pandas as pd

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

# Function to fetch audio features for a list of track IDs
def fetch_audio_features(track_ids):
    # Get the access token
    access_token = get_access_token(client_id, client_secret)
    if not access_token:
        return None

    headers = {"Authorization": f"Bearer {access_token}"}
    features = []  # To store audio features

    # Fetch audio features for each track
    for track_id in track_ids:
        track_url = f"https://api.spotify.com/v1/audio-features/{track_id}"
        response = requests.get(track_url, headers=headers)
        if response.status_code == 200:
            features.append(response.json())  # Add track audio features
        else:
            print(f"Error fetching audio features for {track_id}: {response.status_code} - {response.text}")
    
    return pd.DataFrame(features)  # Return DataFrame with all features

# Example usage (This part can be removed if you want to use it strictly as a module)
if __name__ == "__main__":
    example_track_ids = ["6rqhFgbbKwnb9MLmUQDhG6", "4uLU6hMCjMI75M1A2tKUQC"]  # Replace with actual track IDs
    features_df = fetch_audio_features(example_track_ids)
    print(features_df)
