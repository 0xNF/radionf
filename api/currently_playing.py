from datetime import datetime, timedelta
import time
import api.spotify as spotify
import hello.models
import json

Currently_Playing = None
Kind = None
Progress_Ms = 0
Duration_Ms = 0
Is_Playing = False
PlayedAt = 0 # timestamp in ms


# Datetime of the last check of Spotify
Last_Spotify_Check = datetime.min
Check_Every = timedelta(seconds=10)

# because history can be a bit finnicky, we add some extra checks before adding to history
# check most recent history song. If same as current song...
#   check if (played_at + duration_ms) <= now
#       if so, don't add. Because The old song couldn't finished playing, and its the same song, so just ignore it.
def check_add_history(song, timestamp, duration_ms):
    h = hello.models.History.objects.order_by("-Timestamp").first()
    if h is not None:
        if h.Timestamp == timestamp:
            print(f"Not adding {song.Id} to history because of a Timestamp conflict.")
            return
        if h.Song.Id == song.Id:
            # most recent history item is the same as this one, so check the time info
            td = timedelta(milliseconds=duration_ms) 
            if (h.Timestamp + td) >= datetime.now():
                print(f"Not adding {song.Id} to history because it didn't pass the history time-check")
                return
    h = hello.models.History.objects.create(Timestamp=timestamp, Song=song)
    h.save()
    print(f"Inserted into history at timestamp {timestamp}")
    return


# Tries to add the Spotify song to the database, and place it in the history table too
# Skips adding to history if the Played AT timestamp was already seen
def add_spotify_to_history(spot):
    played = datetime.fromtimestamp(int(spot["timestamp"] / 1000))
    songId = spot["item"]["id"]
    jdump = json.dumps(spot["item"])
    # first try to add the basic song info to the Songs table
    msong = song_get_or_create(songId, "spotify", jdump)
    # next, try to add it to the History table
    check_add_history(msong, played, spot["item"]["duration_ms"])
    return

def add_song(obj):
    global Currently_Playing, Kind, Progress_Ms, Duration_Ms, PlayedAt, Is_Playing
    if obj["kind"] == "youtube":
        ytPlayed = int(obj["timestamp"])
        ytId = obj["item"]["id"]
        ytPlaying = obj["is_playing"]

        oldId = Currently_Playing["item"]["id"] if Currently_Playing is not None else ""

        if Kind == "spotify" and not ytPlaying:
            print("Tried to replace a spotify track with a youtube one, but youtube was paused. Skipping")
            return
        # only set PlayedAt if the song actually changed.
        if oldId != ytId:
            PlayedAt = ytPlayed
            played = datetime.fromtimestamp(ytPlayed)
        jdump = json.dumps(obj["item"])
        Is_Playing = ytPlaying
        Kind = "youtube"
        Duration_Ms = obj["item"]["duration_ms"]
        Progress_Ms = obj["progress_ms"]
        Currently_Playing = obj
        msong = song_get_or_create(ytId, "youtube", jdump)
        # only add to history if we actually play the video and its a different song
        if ytPlaying and oldId != ytId:
            check_add_history(msong, played, obj["item"]["duration_ms"])
    return

def song_get_or_create(id, kind, jdata):
    song = hello.models.Song.objects.filter(Id=id, Kind=kind).first()
    if not song:
        song = hello.models.Song.objects.create(Id=id, Kind=kind, JsonData=jdata)
    return song

def get_currently_playing() -> int:
    global Currently_Playing, Kind, Progress_Ms, Duration_Ms, PlayedAt, Last_Spotify_Check, Is_Playing
    now = datetime.now()
    # Prioritize returning any currently playing Spotify song
    if (Currently_Playing is None) or ((Last_Spotify_Check + Check_Every) <= now):
        print("Spotify hasn't been checked recently...")
        song_spot = spotify.get_currently_playing()
        if song_spot is not None:
            # only override the currently playing if the received song is playing. if it is paused, return currently playing
            if Kind == "spotify" or song_spot["is_playing"]:
                Is_Playing = song_spot["is_playing"]
                add_spotify_to_history(song_spot)
                print("Spotify was playing something. It has Priority.")
                Currently_Playing = song_spot
                Kind = "spotify"
                Last_Spotify_Check = now
                PlayedAt = int(song_spot["timestamp"] / 1000) # Spotify gives us something that Datetime cant work with
                print("played at: " + datetime.fromtimestamp(PlayedAt).strftime("%I:%M:%S"))
                Progress_Ms = song_spot["progress_ms"]
                Duration_Ms = song_spot["item"]["duration_ms"]
                return {
                    "song": song_spot,
                    "kind": "spotify"
                }
            elif not song_spot["is_playing"]:
                print("Got a spotify song, but it wasn't playing. Returning currently playing instead.")

    # Next, check if our currently playing song is still valid (i.e., a youtube video)
    if Currently_Playing is not None:
        dtPlayedat = datetime.fromtimestamp(PlayedAt)
        tdelta = timedelta(milliseconds=(Duration_Ms))
        expiry = dtPlayedat + tdelta
        if expiry >= now: # we may come into the video halfway through, so subtract our progress
            # song is still valid
            print("Currently Playing is still valid")
            cp = Currently_Playing
            if Kind != "spotify":
                if Is_Playing:
                    cp["progress_ms"] = cp["progress_ms"] + int((datetime.now() - datetime.fromtimestamp(PlayedAt)).total_seconds())
            return {
                "song": cp,
                "kind": Kind,
            }
        else:
            if Progress_Ms < Duration_Ms and Is_Playing:
                print("Song should be expired, but user seems to have gone backwards on it.")
                return {
                    "song": Currently_Playing,
                    "kind": Kind,
                }
            else:
                print("datetime playedat: " + dtPlayedat.strftime("%I:%M:%S"))
                print("timedelta (dms - progms): " + str(timedelta(milliseconds=(Duration_Ms - Progress_Ms))))
                print("Time to expiry: " + expiry.strftime("%I:%M:%S"))
                print("Currently playing song has expired")

    print("Radio NF is offline - nothing from youtube, currently_playing, or Spotify")
    return None

# NF TODO what is up with signing shit?

def get_history(previous=50):
    hist = []
    skip = 0
    if Currently_Playing is not None:
        skip = 1
    for history in hello.models.History.objects.all().order_by("-Timestamp")[skip:previous]: # skip most recent
        h = {
            "timestamp": int(time.mktime(history.Timestamp.timetuple())),
            "song": {
                "kind": history.Song.Kind,
                "item": json.loads(history.Song.JsonData)
            }
        }
        hist.append(h)
    return hist