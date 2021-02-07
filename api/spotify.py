import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read user-read-playback-state user-read-currently-playing user-read-recently-played user-top-read user-read-playback-position"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

__default_image_icon = "https://community.spotify.com/t5/image/serverpage/image-id/55829iC2AD64ADB887E2A5/image-size/large?v=1.0&px=999"
def get_currently_playing():
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
