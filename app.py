import os
import requests
import time
import shutil
import json
import re
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the environment
load_dotenv()

# Environment variables
EMBY_URL = os.getenv("EMBY_URL")
EMBY_API_KEY = os.getenv("EMBY_API_KEY")
TRAKT_CLIENT_ID = os.getenv("TRAKT_CLIENT_ID")
MOVIE_FOLDER_NAME = os.getenv("MOVIE_FOLDER_NAME", "movies-hd")
TV_FOLDER_NAME = os.getenv("TV_FOLDER_NAME", "tv")
MOVIES_LIMIT = int(os.getenv("MOVIES_LIMIT", 6))
SHOWS_LIMIT = int(os.getenv("SHOWS_LIMIT", 3))

TOP_PICKS_PATH = Path("/media")

# Ensure required variables are set
if not (EMBY_URL and EMBY_API_KEY and TRAKT_CLIENT_ID):
    raise EnvironmentError("EMBY_URL, EMBY_API_KEY, and TRAKT_CLIENT_ID must be set in environment variables.")

# HTTP session setup
session = requests.Session()
session.headers.update({
    "accept": "application/json",
    "Content-Type": "application/json",
})
params = {"api_key": EMBY_API_KEY}

def fetch_plugin_id(plugin_name):
    """Fetch the plugin ID by name."""
    response = session.get(f"{EMBY_URL}/emby/Plugins", params=params)
    plugins = response.json()
    return next((plugin["Id"] for plugin in plugins if plugin["Name"] == plugin_name), None)

def update_plugin_configuration(plugin_id, media):
    """Update the plugin configuration with top picks."""
    response = session.get(f"{EMBY_URL}/emby/Plugins/{plugin_id}/Configuration", params=params)
    plugin_data = response.json()
    
    for index, item in enumerate(plugin_data.get("SpotlightItems", [])):
        if index < len(media):
            item["InternalId"] = media[index]
    
    binary_data = json.dumps(plugin_data).encode("utf-8")
    response = session.post(f"{EMBY_URL}/emby/Plugins/{plugin_id}/Configuration", params=params, 
                            headers={"Content-Type": "application/octet-stream"}, data=binary_data)
    return response.status_code

def get_trending_media():
    """Fetch trending movies and shows from Trakt."""
    urls = [
        "https://api.trakt.tv/movies/trending",
        "https://api.trakt.tv/shows/trending"
    ]
    headers = {
        "Content-Type": "application/json",
        "trakt-api-version": "2",
        "trakt-api-key": TRAKT_CLIENT_ID,
    }
    movies, shows = [], []
    
    try:
        for page in range(1, 3):
            for url in urls:
                response = requests.get(url, headers=headers, params={"page": page})
                response.raise_for_status()
                for item in response.json():
                    if "movie" in item:
                        movies.append(item["movie"]["ids"]["tmdb"])
                    elif "show" in item:
                        shows.append(item["show"]["ids"]["tmdb"])
        return movies + shows
    except requests.RequestException as e:
        print(f"Error fetching trending media: {e}")
        return []

def get_emby_media(tmdb_ids):
    """Retrieve Emby media IDs by TMDb IDs."""
    items = {"movies": [], "shows": []}
    try:
        for tmdb_id in tmdb_ids:
            response = session.get(f"{EMBY_URL}/emby/Items", params={
                **params,
                "Fields": "Path",
                "AnyProviderIdEquals": f"tmdb.{tmdb_id}",
                "Recursive": "true",
            })
            response.raise_for_status()
            media_items = response.json().get("Items", [])
            if media_items:
                path = media_items[0].get("Path")
                if path:
                    if MOVIE_FOLDER_NAME in path:
                        items["movies"].append(media_items[0]["Id"])
                    elif TV_FOLDER_NAME in path:
                        items["shows"].append(media_items[0]["Id"])
        return items
    except requests.RequestException as e:
        print(f"Error fetching Emby media: {e}")
        return items

def trigger_task(task_name):
    """Run a scheduled task by name."""
    response = session.get(f"{EMBY_URL}/emby/ScheduledTasks", params=params)
    tasks = response.json()
    task_id = next((task["Id"] for task in tasks if task["Name"] == task_name), None)

    if not task_id:
        raise ValueError(f"Task '{task_name}' not found.")
    
    response = session.post(f"{EMBY_URL}/emby/ScheduledTasks/Running/{task_id}", params=params)
    return response.status_code

def organize_metadata_files():
    """Organize metadata files in the specified directory."""
    def extract_season_number(path):
        match = re.search(r"(\d+)x", str(path))
        return int(match.group(1)) if match else None

    start_time = time.time()
    while time.time() - start_time < 60:
        files_to_move = []
        for nfo_file in TOP_PICKS_PATH.rglob("*.nfo"):
            season_number = extract_season_number(nfo_file)
            if season_number and "Season" not in str(nfo_file):
                season_dir = nfo_file.parent / f"Season {season_number}"
                season_dir.mkdir(exist_ok=True)
                target_path = season_dir / nfo_file.name
                if not target_path.exists():
                    files_to_move.append((nfo_file, target_path))
        
        for src, dest in files_to_move:
            if src.exists():
                shutil.move(str(src), str(dest))
                print(f"Moved {src.name} to {dest}\n")
        
        time.sleep(1)

def process_top_picks():
    """Process top picks and organize metadata."""
    trending_ids = get_trending_media()
    emby_media = get_emby_media(trending_ids)
    
    media_list = []
    for i in range(9):
        if  i < MOVIES_LIMIT and i < len(emby_media["movies"]):
            media_list.append(emby_media["movies"][i])
        if  i < SHOWS_LIMIT and i < len(emby_media["shows"]):
            media_list.append(emby_media["shows"][i])
    
    plugin_id = fetch_plugin_id("Top Picks")
    if plugin_id:
        update_plugin_configuration(plugin_id, media_list)
        trigger_task("Update Top Picks")
        organize_metadata_files()
        print("Complete!")
    else:
        print("Top Picks plugin not found.")

if __name__ == "__main__":
    process_top_picks()
