import spotipy
import json
import re
import keyboard
import time
from colorama import init, Fore, Style

from spotipy.oauth2 import SpotifyOAuth

cachedTracks = []
config = json.load(open('config.json', "r"))
init(autoreset=True)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=config["app-settings"]["client_id"],
                                               client_secret=config["app-settings"]["client_secret"],
                                               scope=config["app-settings"]["scope"],
                                               redirect_uri=config["app-settings"]["redirectURL"]))


GREEN = Fore.GREEN
CYAN = Fore.CYAN
LIGHTCYAN = Fore.LIGHTCYAN_EX
RED = Fore.RED
RESET = Style.RESET_ALL
LIGHTBLUE = Fore.LIGHTBLUE_EX


def check_config():
    if len(config["user-settings"]["playlistID"]) == 0:
        print(f"{RED}Please provide a link to your playlist.{RESET}\n"
              f"{RED}Example{RESET}: {CYAN}spotify:playlist:1CQXW3KFWFxObIxdmh8o1k")

        uri = input()
        playlistID = uri[17:]
        config["user-settings"]["playlistID"] = playlistID

        json.dump(config, open("config.json", "w"))

        print(f"{RED}Playlist ID{RESET} {GREEN}successfully{RESET} saved.")


def collect_tracks():
    start_time = time.time()
    print(f"Start {RED}caching...")
    playlist = sp.playlist_items(playlist_id=config["user-settings"]["playlistID"])

    for i in playlist["items"]:
        cachedTracks.append(i["track"]["id"])

    while True:
        if playlist["next"] is None:
            break

        offset = re.search(r'offset=(\d+)', playlist["next"]).group(1)
        playlist = sp.playlist_items(playlist_id=config["user-settings"]["playlistID"],
                                     offset=offset)

        for i in playlist["items"]:
            cachedTracks.append(i["track"]["id"])

    execTime = round(time.time() - start_time, 3)
    print(f"Took: {execTime}s. | {GREEN}Successfully{RESET} {RED}cache{RESET} all tracks.")


def add_track():
    start_time = time.time()
    playlist = sp.playlist_items(playlist_id=config["user-settings"]["playlistID"])

    if playlist["total"] != 0 and len(cachedTracks) == 0:
        print(f"Please {RED}wait{RESET} for {RED}caching.")
        return

    currentPlaying = sp.currently_playing()

    if currentPlaying is None:
        print(f"Please {RED}start{RESET} {LIGHTCYAN}listening{RESET} any track.")
        return

    artist = currentPlaying['item']['artists'][0]['name']
    trackName = currentPlaying['item']['name']
    trackId = currentPlaying["item"]["id"]
    trackUri = currentPlaying["item"]["uri"]

    if currentPlaying["item"]["id"] in cachedTracks:
        execTime = round(time.time() - start_time, 3)
        timePart = f"Took: {execTime}s."
        message = f"{timePart} | {LIGHTBLUE}{artist} - {trackName}{RESET} {LIGHTCYAN}already{RESET} in playlist."
        print(message)
        return

    sp.playlist_add_items(playlist_id=config["user-settings"]["playlistID"], items=[trackUri])

    cachedTracks.append(trackId)

    execTime = round(time.time() - start_time, 3)
    timePart = f"Took: {execTime}s."
    message = f"{timePart} | {LIGHTBLUE}{artist} - {trackName}{RESET} was {GREEN}added{RESET} to your playlist."
    print(message)


def main():
    check_config()
    collect_tracks()
    keyboard.add_hotkey('alt+0', add_track)

    print(Fore.RED + 'PRESS "alt + -" to stop program.')

    keyboard.wait("alt+-")


if __name__ == '__main__':
    main()
