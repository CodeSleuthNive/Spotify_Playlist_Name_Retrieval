#!/usr/bin/env python
# coding: utf-8

"""
Spotify Tamil Playlist Scraper
Author: Nivetha (Optimized Version)
Description:
    This script reads queries from an Excel file and retrieves Spotify playlists
    related to those queries in Tamil language using the Spotipy API.

Features:
    ✅ Reads search terms from Queries.xlsx
    ✅ Filters playlists for Tamil relevance
    ✅ Saves results to playlist_name_scraping.xlsx
    ✅ Handles errors and merges with existing data
"""

import os
import re
import time
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")


# ----------------------------------------
# Spotify Credentials (Add your own)
# ----------------------------------------
SPOTIFY_CLIENT_ID = ""   # <-- Add your Spotify API client ID here
SPOTIFY_CLIENT_SECRET = ""  # <-- Add your Spotify API client secret here


# ----------------------------------------
# Initialize Spotify Client
# ----------------------------------------
cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=".spotify_cache")
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        cache_handler=cache_handler
    )
)


# ----------------------------------------
# Tamil Playlist Retrieval Function
# ----------------------------------------
def fetch_tamil_playlists(queries):
    """
    Retrieves playlists from Spotify that are relevant to Tamil searches.
    """
    if not isinstance(queries, list):
        raise ValueError("Queries must be provided as a list.")

    tamil_keywords = ['tamil', 'kollywood', 'chennai', 'madras', 'tamizh']
    playlist_records = []

    # Create timestamp
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create storage directory
    base_dir = os.path.join(os.getcwd(), "Spotify_Playlist_Retrieval")
    os.makedirs(base_dir, exist_ok=True)

    output_path = os.path.join(base_dir, "playlist_name_scraping.xlsx")

    # Load existing file if it exists
    if os.path.exists(output_path):
        existing_data = pd.read_excel(output_path)
    else:
        existing_data = pd.DataFrame()

    try:
        for search_term in queries:
            search_results = sp.search(q=search_term, type='playlist', market='IN', limit=10)

            for playlist in search_results['playlists']['items']:
                playlist_id = playlist.get('id')
                playlist_name = playlist.get('name', '')
                total_tracks = playlist['tracks']['total']

                # Match Tamil keywords in playlist name
                if re.search(r'\b(?:' + '|'.join(tamil_keywords) + r')\b', playlist_name, re.IGNORECASE):
                    playlist_records.append({
                        'PlaylistID': playlist_id,
                        'PlaylistName': playlist_name,
                        'NumSongs': total_tracks,
                        'Query': search_term,
                        'Language': 'Tamil',
                        'Timestamp': current_timestamp
                    })

        # Combine old and new data
        updated_df = pd.concat([existing_data, pd.DataFrame(playlist_records)], ignore_index=True)

        # Save to Excel
        updated_df.to_excel(output_path, index=False)
        print(f"[{current_timestamp}] ✅ Tamil playlist data saved successfully.")

        return updated_df

    except Exception as e:
        print(f"❌ Error during playlist retrieval: {e}")
        return None


# ----------------------------------------
# Main Function
# ----------------------------------------
def run_tamil_playlist_scraper():
    """
    Main entry point for the Tamil playlist retrieval process.
    Reads queries from 'Queries.xlsx' and triggers Spotify search.
    """
    try:
        queries_file = os.path.join(os.getcwd(), "Queries.xlsx")

        if not os.path.exists(queries_file):
            raise FileNotFoundError(f"Queries.xlsx not found in {os.getcwd()}")

        df_queries = pd.read_excel(queries_file)

        if 'Queries' not in df_queries.columns:
            raise KeyError("The Excel file must have a column named 'Queries'.")

        queries = df_queries['Queries'].dropna().tolist()

        print(f"🔍 Starting Tamil playlist retrieval for {len(queries)} queries...")
        result_df = fetch_tamil_playlists(queries)

        if result_df is not None:
            print("✅ Playlist scraping completed successfully.")
        else:
            print("⚠️ No playlists retrieved or an error occurred.")

    except Exception as e:
        print("❌ An unexpected error occurred while running the scraper.")
        print(f"Error: {e}")


# ----------------------------------------
# Entry Point
# ----------------------------------------
if __name__ == "__main__":
    run_tamil_playlist_scraper()
