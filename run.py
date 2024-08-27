import os
from create_playlist import app, create_spotify_playlist, add_tracks_to_playlist, get_user_id
from get_songs import get_playlist_track_ids
from get_data import fetch_audio_features
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import threading
import time

def main(playlist_id):
    # Start the Flask app in a separate thread
    threading.Thread(target=lambda: app.run(port=8080, use_reloader=False)).start()

    # Wait for the user to authenticate and store the access token
    print("Please authenticate in the browser window that opens...")
    time.sleep(5)  # Wait for a few seconds to allow the Flask app to start

    input("Press Enter after you have authenticated and closed the browser...")

    # Read the access token from the file
    if not os.path.exists("access_token.txt"):
        print("Access token file not found. Authentication failed.")
        return
    
    with open("access_token.txt", "r") as file:
        access_token = file.read().strip()

    # Step 2: Fetch track IDs using get_playlist_track_ids
    track_ids = get_playlist_track_ids(playlist_id)
    
    if not track_ids:
        print("Failed to retrieve track IDs or no tracks found in the playlist.")
        return

    # Step 3: Fetch audio features for these track IDs using fetch_audio_features
    features = fetch_audio_features(track_ids)
    
    if features is None or features.empty:
        print("Failed to retrieve audio features for the provided track IDs.")
        return

    # Step 4: Perform clustering
   # Updated feature_columns to include all relevant audio features
    feature_columns = [
        'danceability', 'energy', 'loudness', 'mode', 'speechiness',
        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'
    ]

    X = features[feature_columns]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    optimal_k = 5
    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    features['cluster'] = kmeans.fit_predict(X_scaled)

    # Step 5: Generate and create playlists based on clusters
    user_id = get_user_id(access_token)
    if not user_id:
        print("Failed to retrieve user ID.")
        return

    for cluster in range(optimal_k):
        cluster_songs = features[features['cluster'] == cluster]['id'].tolist()
        playlist_name = f"Cluster {cluster + 1} Playlist"
        playlist_id = create_spotify_playlist(user_id, playlist_name, access_token)
        
        if playlist_id:
            add_tracks_to_playlist(playlist_id, cluster_songs, access_token)
            print(f"Playlist '{playlist_name}' created and tracks added successfully!")
        else:
            print(f"Failed to create playlist '{playlist_name}'.")

if __name__ == "__main__":
    playlist_id = "37HONfm4BNcj4lBewfvp4M"  # Replace with your actual playlist ID
    main(playlist_id)
