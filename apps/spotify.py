from apps.App import App
from os import getenv
from PIL import Image, ImageDraw
import base64
from requests import post, get
from utils.scroller import Scroller
from utils.color import ColorThiefFromImage
import colorsys
from utils.timer import setInterval
from utils.logging import get_logger
logger = get_logger(__name__)

ALBUM_PLACEHOLDER = Image.new("RGB", (16, 16), (150, 150, 150))
d = ImageDraw.Draw(ALBUM_PLACEHOLDER)
d.ellipse([(2, 2), (13, 13)], fill=(0, 0, 0))
d.ellipse([(6, 6), (9, 9)], fill=(150, 150, 150))


def scale_lightness(rgb, scale_l):
    # convert rgb to hls
    h, l, s = colorsys.rgb_to_hls(*rgb)
    # manipulate h, l, s values and return as rgb
    r, g, b = colorsys.hls_to_rgb(h, min(1, l * scale_l), s=s)
    return tuple((int(r * 255), int(g * 255), int(b * 255)))


class SpotifyApp(App):
    def __test_access_tokan__(self, token):
        test_res = get("https://api.spotify.com/v1/me",
                       headers={"Authorization": f"Bearer {token}"})
        try:
            j = test_res.json()
            if 'error' in j:
                if j['error']['status'] == 401:
                    # api token is invalid
                    return False
                # return false anyway, but keep the scaffolding for future error codes
                return False
            else:
                return True
        except Exception:
            logger.error("unknown failure in spotify init")
            raise Exception("CRITIAL FAILURE")

    def __get_new_access_token__(self) -> str:
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
        logger.debug(access_response.json())
        access_token = access_response.json()['access_token']
        logger.info(f"got new access_token: {access_token}")
        return access_token

    def __set_new_access_token_inplace__(self):
        logger.info("refreshing access token")
        access_token = self.__get_new_access_token__()
        logger.info(f"new token: {access_token}")
        self.__api_headers__ = {
            'Authorization': f"Bearer {access_token}"
        }
        self.__api_url__ = "https://api.spotify.com/v1/me/player/currently-playing"

    def __init__(self, image_setter, data_refresh_rate=10) -> None:
        super().__init__(image_setter, data_refresh_rate)

        # for debugging: use an access token from the env file
        access_token = getenv("SPOTIFY_ACCESS_TOKEN")
        if access_token is None:
            # need to get a new access token, probably
            access_token = self.__get_new_access_token__()
        else:
            logger.info(f"testing env access token")
            logger.info(f"token to test: {access_token}")
            if not self.__test_access_tokan__(access_token):
                logger.warn("access token too old; getting new one")
                access_token = self.__get_new_access_token__()
            else:
                logger.info("env token valid")

        # got access token, instantiate class
        self.__api_headers__ = {
            'Authorization': f"Bearer {access_token}"
        }
        self.__api_url__ = "https://api.spotify.com/v1/me/player/currently-playing"

        # get a new access token every 58 minutes
        self.__token_refresher__ = setInterval(
            58 * 60, self.__set_new_access_token_inplace__)

        self.__top_padding__ = 4
        self.__last_song_id__ = None
        self.__last_album_id__ = None
        self.__accent_color__ = None
        self.__album_art__ = ALBUM_PLACEHOLDER
        self.__album_art_cache__ = {}
        self.__canvas__ = Image.new("RGB", (64, 32), (0, 0, 0))
        self.__title_scroller__ = Scroller(
            self.__canvas__, 19, self.__top_padding__ + 2, 44, "")
        self.__artist_scroller__ = Scroller(
            self.__canvas__, 19, self.__top_padding__ + 2 + 7, 44, "")

        self.__play_icon__ = Image.open('imgs/play.png')
        self.__pause_icon__ = Image.open('imgs/pause.png')

        self.__GRAY__ = (180, 180, 180)
        self.__DARK_GRAY__ = (100, 100, 100)

    def stop(self):
        self.__token_refresher__.cancel()
        return super().stop()

    def __data_update__(self):
        super().__data_update__()
        # update album art, if necessary
        try:
            new_album_id = self.__data__['item']['album']['id']
        except Exception:
            pass
        if (self.__data__ is not None) and ('item' in self.__data__) and (new_album_id != self.__last_album_id__):
            # look in the cache first
            if new_album_id in self.__album_art_cache__:
                self.__album_art__ = self.__album_art_cache__[new_album_id]
            else:
                # clear previous art
                self.__album_art__ = ALBUM_PLACEHOLDER
                a_url = next(image['url'] for image in self.__data__[
                    'item']['album']['images'] if image['width'] == 64)
                logger.debug(a_url)
                a_response = get(a_url, stream=True)
                cover = Image.open(a_response.raw).resize((16, 16))
                self.__album_art__ = cover
                self.__album_art_cache__[new_album_id] = cover
            self.__last_album_id__ = new_album_id
            # dom_color = ColorThiefFromImage(cover).get_color(quality=1)
            dom_color = 'white'
            # self.__accent_color__ = scale_lightness(tuple(val / 255 for val in dom_color), 2)
            self.__accent_color__ = dom_color

    def __render_update__(self):

        # clear canvas
        self.__canvas__.paste(
            (0, 0, 0), (0, 0, self.__canvas__.size[0], self.__canvas__.size[1]))

        if self.__data__ is None:
            self.__draw_text__(
                self.__canvas__, (1, self.__top_padding__), "loading")
            self.__draw_text__(
                self.__canvas__, (1, self.__top_padding__ + 7), "spotify...")
        elif 'item' in self.__data__:
            highlight_color = self.__accent_color__
            play_or_pause = self.__pause_icon__
            if not self.__data__['is_playing']:
                highlight_color = self.__GRAY__
                play_or_pause = self.__play_icon__

            self.__canvas__.paste(self.__album_art__,
                                  (1, self.__top_padding__))

            if self.__data__['item']['id'] != self.__last_song_id__:
                self.__title_scroller__.update_text(
                    self.__data__['item']['name'])
                artists = self.__data__['item']['artists']
                self.__artist_scroller__.update_text(
                    ", ".join(list(map(lambda i: i['name'], artists))[:2]))
                self.__last_song_id__ = self.__data__['item']['id']

            self.__title_scroller__.update_color(highlight_color)
            self.__artist_scroller__.update_color(self.__GRAY__)
            self.__title_scroller__.incr()
            self.__artist_scroller__.incr()

            draw = ImageDraw.Draw(self.__canvas__)
            progress_as_pixel = int(
                self.__data__['progress_ms'] / self.__data__['item']['duration_ms'] * 57)
            progress_bar_y = self.__top_padding__ + 21
            draw.rectangle((6, progress_bar_y, 62,
                           progress_bar_y), fill=self.__DARK_GRAY__)
            draw.rectangle((6, progress_bar_y, 6 + progress_as_pixel, progress_bar_y),
                           fill=highlight_color)
            draw.rectangle((6 + progress_as_pixel, self.__top_padding__ + 20, 6 +
                           progress_as_pixel, self.__top_padding__ + 22), fill=highlight_color)
            self.__canvas__.paste(
                play_or_pause, (1, self.__top_padding__ + 19))
        elif "err_code" in self.__data__:
            self.__draw_text__(
                self.__canvas__, (1, self.__top_padding__ + 7), "not playing")
        else:
            self.__draw_text__(
                self.__canvas__, (1, self.__top_padding__ + 7), "API error")

        self.__image_setter__(self.__canvas__)
