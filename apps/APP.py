from utils.timer import setInterval
from requests import get
from PIL import ImageFont, ImageDraw

class App:
    def __init__(self, image_setter, data_refresh_rate = 10) -> None:
        self.__data_refresh_rate_s__ = data_refresh_rate
        self.__api_url__ = None
        self.__data__ = None
        self.__main_interval__ = None
        self.__image_setter__ = image_setter
        self.__font__ = ImageFont.truetype('fonts/tiny.otf', size=5)
        self.__is_shown__ = False

    def __show_data__(self):
        if self.__data__ is None:
            # show loading screen here
            pass
        else:
            # main data rendering
            pass

    def __data_update__(self):
        print(f"attempting fetch - {self.__class__.__name__}")
        self.__data__ = get(self.__api_url__).json()
        if self.__is_shown__: self.__show_data__()

    def __draw_text__(self, canvas, *args, **kwargs):
        draw = ImageDraw.Draw(canvas)
        draw.text(*args, font=self.__font__, **kwargs)

    def start(self):
        if self.__api_url__ is None:
            raise ValueError(f"!!! __api_url__ not set on class {self.__class__.__name__}")
        self.__main_interval__ = setInterval(self.__data_refresh_rate_s__, self.__data_update__)

    def stop(self):
        self.__is_shown__ = False
        self.__main_interval__.cancel()

    def show(self):
        self.__is_shown__ = True
        self.__show_data__()
        self.__data_update__()

    def hide(self):
        self.__is_shown__ = False

    