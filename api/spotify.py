import spotipy
import os, json
from spotipy.oauth2 import SpotifyOAuth
import sys
import time, datetime

scope = "user-library-read user-read-playback-state user-read-currently-playing user-read-recently-played user-top-read user-read-playback-position"

last_known_expires_at = datetime.datetime.min
last_known_refresh_token = ""

sp = None
# Reads in the Refresh Token environment variable and saves it to the .cache file so Spotipy can refresh our access token.
# As this is a single-user architecture, idgaf that no one else can log into this site.
def load_token():
    global last_known_expires_at, last_known_refresh_token, sp

    # only Min before a Refresh has been attempted, so this requires a file read
    if last_known_expires_at > datetime.datetime.now():
        print(f"Tried to refresh spotipy token, but cached expiry date wasn't yet expired: {last_known_expires_at}")
        return

    refresh = ""
    j = {}

    # Token has never been loaded (because last known is dt.min), so load it from the file
    if last_known_expires_at <= datetime.datetime.min:
        j = load_token_file()
        last_known_expires_at = datetime.datetime.fromtimestamp(j["expires_at"])

    # Try to laod the refresh token from the environment variable
    try:
        refresh = os.environ["RADIO_REFRESH_TOKEN"]
    except KeyError:
        print("RADIO_REFRESH_TOKEN wasn't found, RadioNF cannot run.", file=sys.stderr)
        return

    if len(j) == 0:
        # only re-read the file if we didn't read it before
        j = load_token_file()

    # Check if we need to write a new .cache file
    if refresh != last_known_refresh_token:
        print("The refresh token user wants to use has changed - writing the new one to the .cache file and reloading Spotipy")
        j["refresh_token"] = refresh
        write_token_file(j)
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    last_known_refresh_token = refresh
    last_known_expires_at = datetime.datetime.fromtimestamp(j["expires_at"])
    
    return

def load_token_file():
    j = {}
    try:
        with open('.cache', 'r') as f:
            j = json.load(f)
    except FileNotFoundError:
        print("Tried to open the Spotipy .cache file but none existed. Creating a new one.")
        j["expires_at"] = 1612779211
        j["scope"] = "user-library-read user-read-currently-playing user-read-playback-position user-read-playback-state user-read-recently-played user-top-read"
        j["expires_in"] = 3600
        j["token_type"] = "Bearer"
        j["access_token"] = ""
    return j

def write_token_file(j):
    with open('.cache', 'w') as f:
        json.dump(j, f)
    return


__default_image_icon = "https://community.spotify.com/t5/image/serverpage/image-id/55829iC2AD64ADB887E2A5/image-size/large?v=1.0&px=999"
def get_currently_playing():
    load_token()
    song = sp.current_user_playing_track()
    if song is None:
        print("User is not currently playing any tracks")
        return None
    else:
        si = song["item"]
        item = {
            "id": si["id"],
            "name": si["name"],
            "is_local": si["is_local"],
            "href": si["href"],
            "preview_url": si["preview_url"],
            "duration_ms": si["duration_ms"],
            "album": si["album"],
            "artists": si["artists"],
            "main_image": __default_image_icon,
            "main_link": None
        }


        d = {
            "timestamp": song["timestamp"],
            "progress_ms": song["progress_ms"],
            "is_playing": song["is_playing"],
            "item": item,
        }

        if not si["is_local"]:
            a = si["album"]
            item["main_image"] = a["images"][0]["url"]
            item["main_link"] = si["external_urls"]["spotify"]
            item["album"] = {
                "id": a["id"],
                "images": a["images"],
                "name": a["name"],
            }
            item["artists"] = [
                {"id": x["id"], "name": x["name"], "href":x["href"]}  for x in si["artists"]
            ]
        else:
            item["id"] = f"{item['name']}{str(item['duration_ms'])}" # default is local id

        return d


# results = sp.current_user_saved_tracks()
# for idx, item in enumerate(results['items']):
#     track = item['track']
#     print(idx, track['artists'][0]['name'], " – ", track['name']) 
