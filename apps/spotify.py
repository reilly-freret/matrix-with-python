from apps.App import App
from os import getenv
from PIL import Image, ImageDraw
import base64
from requests import post
from utils.scroller import Scroller


class SpotifyApp(App):
    def __init__(self, image_setter, data_refresh_rate=10) -> None:
        super().__init__(image_setter, data_refresh_rate)

        # for debugging: use an access token from the env file
        access_token = getenv("SPOTIFY_ACCESS_TOKEN")
        if access_token is None:
            # need to get a new access token, probably
            cid = getenv("SPOTIFY_CLIENT_ID")
            cs = getenv("SPOTIFY_CLIENT_SECRET")
            rt = getenv("SPOTIFY_REFRESH_TOKEN")
            encoded_creds = base64.b64encode(f"{cid}:{cs}".encode()).decode()
            headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + encoded_creds
            }
            form_data = {
                "grant_type": 'refresh_token',
                "refresh_token": rt
            }
            access_response = post(
                'https://accounts.spotify.com/api/token',
                headers=headers,
                data=form_data
            )
            access_token = access_response.json()['access_token']
            print(f"got new access_token: {access_token}")
        else:
            print(f"using env access token: {access_token}")

        # got access token, instantiate class
        self.__api_headers__ = {
            'Authorization': f"Bearer {access_token}"
        }
        self.__api_url__ = "https://api.spotify.com/v1/me/player/currently-playing"

        self.__last_song_id__ = None
        self.__canvas__ = Image.new("RGB", (64, 32), (0, 0, 0))
        self.__title_scroller__ = Scroller(self.__canvas__, 1, 1, 62, "")
        self.__artist_scroller__ = Scroller(self.__canvas__, 1, 8, 62, "")

    def __render_update__(self):

        # clear canvas
        self.__canvas__.paste(
            (0, 0, 0), (0, 0, self.__canvas__.size[0], self.__canvas__.size[1]))

        if self.__data__ is None:
            self.__draw_text__(self.__canvas__, (1, 1), "loading")
            self.__draw_text__(self.__canvas__, (1, 8), "spotify...")
        elif 'item' in self.__data__:
            highlight_color = 'pink' if self.__data__[
                'is_playing'] else 'white'

            if self.__data__['item']['id'] != self.__last_song_id__:
                self.__title_scroller__.update_text(
                    self.__data__['item']['name'])
                self.__artist_scroller__.update_text(self.__data__[
                    'item']['artists'][0]['name'])
                self.__last_song_id__ = self.__data__['item']['id']

            self.__title_scroller__.update_color(highlight_color)
            self.__artist_scroller__.update_color((180, 180, 180))
            self.__title_scroller__.incr()
            self.__artist_scroller__.incr()

            draw = ImageDraw.Draw(self.__canvas__)
            progress_as_pixel = int(
                self.__data__['progress_ms'] / self.__data__['item']['duration_ms'] * 62)
            draw.rectangle((1, 18, 62, 18), fill='gray')
            draw.rectangle((1, 18, 1 + progress_as_pixel, 18),
                           fill=highlight_color)
        elif "err_code" in self.__data__:
            self.__draw_text__(self.__canvas__, (1, 8), "not playing")

        self.__image_setter__(self.__canvas__)

    def stop(self):
        # self.t.stop()
        return super().stop()
