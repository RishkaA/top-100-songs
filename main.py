from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDIRECT_URI = "http://example.com"
USERNAME = os.environ["USER"]

class Playlist():
    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.redirect = REDIRECT_URI
        self.username = USERNAME
        self.artist_title_dict = {}
        self.user_id = ""
        self.song_uris = []
        self.date = ""
        self.new_playlist_id = ""

    def get_user_access(self):
        """
        getting authorisation to add a playlist to user's spotify account
        """
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect,
            scope="playlist-modify-private",
            show_dialog=True,
            cache_path="token.txt",
            username=self.username
        ))

        self.user_id = self.sp.current_user()["id"]

        self.top_songs()

    def top_songs(self):
        """
        getting top 100 songs from the specified date and their uris
        """
        url = "https://www.billboard.com/charts/hot-100/"

        self.date = input("Which year would you like to travel to? Type the date in this format YYYY-MM-DD: ")

        response = requests.get(url + self.date)
        soup = BeautifulSoup(response.text, "html.parser")
        all_titles = soup.select("li ul li h3")
        all_artists = soup.select("li ul li h3 + span ")

        # lists of all titles and all artists
        titles_list = [title.getText().strip() for title in all_titles]
        artists_list = [artist.getText().strip() for artist in all_artists]

        # creating a dictionary containing artist-song key value pairs
        self.artist_title_dict = {key: value for key, value in zip(artists_list, titles_list)}

        # getting required songs' uris
        for key, value in self.artist_title_dict.items():
            song = self.sp.search(q=F"track:{value} artist:{key}", type="track", limit=1)
            try:
                uri = song["tracks"]["items"][0]["id"]
                self.song_uris.append(uri)
            except IndexError:
                print(f"{value} not found. Onto the next one.")

        self.create_playlist()

    def create_playlist(self):
        """
        creates a new playlist in user's spotify account
        """
        new_playlist = self.sp.user_playlist_create(user=self.user_id, name=f"{self.date} Billboard 100", public=False,
                                                    description="Top 100 from the date")
        self.new_playlist_id = new_playlist["id"]

        self.add_songs()

    def add_songs(self):
        """
        adds found top 100 songs from the specified date into the newly created playlist
        """
        self.sp.playlist_add_items(playlist_id=self.new_playlist_id, items=self.song_uris)


a = Playlist()
a.get_user_access()