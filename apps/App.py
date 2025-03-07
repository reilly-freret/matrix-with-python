from utils.timer import setInterval
from utils.logging import get_logger
from requests import get, exceptions
from PIL import ImageFont, ImageDraw, Image
from simplejson import JSONDecodeError
import traceback

logger = get_logger(__name__)


class App:
    def __init__(
        self, image_setter, data_refresh_rate=10, render_refresh_rate=0.1
    ) -> None:
        self.__data_refresh_rate_s__ = data_refresh_rate
        self.__render_refresh_rate_s__ = render_refresh_rate
        self.__api_url__ = None
        self.__api_headers__ = None
        self.__data__ = None
        self.__data_interval__ = None
        self.__render_interval__ = None
        self.__image_setter__ = image_setter
        self.__font__ = ImageFont.truetype("fonts/tiny.otf", size=5)
        # self.__font__ = ImageFont.truetype('fonts/5x7-pixel-monospace.otf', size=15)
        self.__is_shown__ = False

    def __data_update__(self):
        logger.debug(f"starting __data_update__ on {self.__class__.__name__}")
        try:
            res = get(self.__api_url__, headers=self.__api_headers__)
            res.raise_for_status()
            # will except if there's nothing currently playing (spotify)
            self.__data__ = res.json()
            logger.debug(len(self.__data__))
        except exceptions.HTTPError as e:
            logger.error(f"HTTP error:\n{traceback.format_exc()}")
        except exceptions.RequestException:
            logger.error(f"REQUEST error:\n{traceback.format_exc()}")
        except JSONDecodeError:
            # should be specific to spotify
            # append to existing data; don't overwrite it
            if self.__data__ is None:
                self.__data__ = {"err_msg": "nothing playing", "err_code": 6}
            else:
                self.__data__["err_msg"] = "nothing playing"
                self.__data__["err_msg"] = 6

    def __render_update__(self):
        pass

    def __draw_text__(self, canvas, *args, **kwargs):
        draw = ImageDraw.Draw(canvas)
        draw.fontmode = "1"
        if "font" in kwargs:
            draw.text(*args, **kwargs)
        else:
            draw.text(*args, font=self.__font__, **kwargs)

    def __draw_text_centered__(self, canvas, text, font):
        W, H = (64, 32)
        draw = ImageDraw.Draw(canvas)
        _, _, w, h = draw.textbbox((0, 0), text, font=font)
        # draw.rectangle(((W-w)/2,(H-h)/2,w,h), fill="red")
        draw.text(
            (2 + (W - w) / 2, (H - h) / 2),
            text,
            font=font,
            fill=(210, 210, 210),
            stroke_fill="black",
            stroke_width=1,
        )

    def __draw_text_bg__(
        self, canvas, bgcolor, padding=1, *args, **kwargs
    ) -> tuple[int, int, int, int]:
        draw = ImageDraw.Draw(canvas)
        draw.fontmode = "1"
        l, t, r, b = draw.textbbox(*args, font=self.__font__)
        adjusted_bounds = (l - padding, t - padding, r - 2 + padding, b - 1 + padding)
        draw.rectangle(adjusted_bounds, fill=bgcolor)
        draw.text(*args, font=self.__font__, **kwargs)
        return adjusted_bounds

    def __conditional_render__(self):
        if self.__is_shown__:
            self.__render_update__()

    def start(self):
        # if self.__api_url__ is None:
        #     raise ValueError(
        #         f"!!! __api_url__ not set on class {self.__class__.__name__}")
        self.__data_interval__ = setInterval(
            self.__data_refresh_rate_s__, self.__data_update__
        )
        self.__render_interval__ = setInterval(
            self.__render_refresh_rate_s__, self.__conditional_render__
        )

    def stop(self):
        self.__is_shown__ = False
        self.__data_interval__.cancel()
        self.__render_interval__.cancel()

    def show(self):
        self.__is_shown__ = True
        self.__data_update__()

    def hide(self):
        self.__is_shown__ = False

    def inc_page(self):
        pass

    def dec_page(self):
        pass
