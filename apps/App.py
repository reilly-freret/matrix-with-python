from utils.timer import setInterval
from requests import get
from PIL import ImageFont, ImageDraw
from simplejson import JSONDecodeError


class App:
    def __init__(self, image_setter, data_refresh_rate=10, render_refresh_rate=0.1) -> None:
        self.__data_refresh_rate_s__ = data_refresh_rate
        self.__render_refresh_rate_s__ = render_refresh_rate
        self.__api_url__ = None
        self.__api_headers__ = None
        self.__data__ = None
        self.__data_interval__ = None
        self.__render_interval__ = None
        self.__image_setter__ = image_setter
        self.__font__ = ImageFont.truetype('fonts/tiny.otf', size=5)
        self.__is_shown__ = False

    def __data_update__(self):
        res = get(self.__api_url__, headers=self.__api_headers__)
        try:
            # will except if there's nothing currently playing
            self.__data__ = res.json()
        except JSONDecodeError:
            # append to existing data; don't overwrite it
            if self.__data__ is None:
                self.__data__ = {
                    'err_msg': 'nothing playing',
                    'err_code': 6
                }
            else:
                self.__data__['err_msg'] = 'nothing playing'
                self.__data__['err_msg'] = 6

    def __render_update__(self):
        pass

    def __draw_text__(self, canvas, *args, **kwargs):
        draw = ImageDraw.Draw(canvas)
        if 'font' in kwargs:
            draw.text(*args, **kwargs)
        else:
            draw.text(*args, font=self.__font__, **kwargs)

    def __draw_text_bg__(self, canvas, bgcolor, padding=1, *args, **kwargs) -> tuple[int, int, int, int]:
        draw = ImageDraw.Draw(canvas)
        l, t, r, b = draw.textbbox(*args, font=self.__font__)
        adjusted_bounds = (
            l - padding,
            t - padding,
            r - 2 + padding,
            b - 1 + padding
        )
        draw.rectangle(adjusted_bounds, fill=bgcolor)
        draw.text(*args, font=self.__font__, **kwargs)
        return adjusted_bounds

    def __conditional_render__(self):
        if self.__is_shown__:
            self.__render_update__()

    def start(self):
        if self.__api_url__ is None:
            raise ValueError(
                f"!!! __api_url__ not set on class {self.__class__.__name__}")
        self.__data_interval__ = setInterval(
            self.__data_refresh_rate_s__, self.__data_update__)
        self.__render_interval__ = setInterval(
            self.__render_refresh_rate_s__, self.__conditional_render__)

    def stop(self):
        self.__is_shown__ = False
        self.__data_interval__.cancel()
        self.__render_interval__.cancel()

    def show(self):
        self.__is_shown__ = True
        self.__data_update__()

    def hide(self):
        self.__is_shown__ = False
