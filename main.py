from apps import WeatherApp, SubwayApp, SpotifyApp, DrawingApp, GifApp, MessageApp
from apps.App import App
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from os import getenv
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils.httpServer import HTTP_SERVER
from utils.timer import setInterval
from utils.logging import get_logger
from signal import pause

logger = get_logger(__name__)

load_dotenv()
PAGE_TIME_S = 5


class MAIN_MATRIX:
    def __init__(self) -> None:
        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.cols = 64
        self.options.hardware_mapping = "adafruit-hat"
        self.options.gpio_slowdown = int(getenv("GPIO_SLOWDOWN", "4"))
        self.options.brightness = int(getenv("MAX_BRIGHTNESS", "80"))
        self.options.drop_privileges = False
        self.options.pixel_mapper_config = f'Rotate:{getenv("ROTATION")}'
        self.matrix = RGBMatrix(options=self.options)

        self.MAIN_IMAGE = Image.new("RGB", (64, 32), (0, 0, 0))
        self.__loading_frame__ = 0
        self.__interval__ = None

        self.FRAME_RATE = 20

        self.buffer = self.matrix.CreateFrameCanvas()

    def __update_loading__(self):
        self.MAIN_IMAGE = Image.new("RGB", (64, 32), (0, 0, 0))
        draw = ImageDraw.Draw(self.MAIN_IMAGE)
        draw.regular_polygon(
            (32, 10, 8),
            n_sides=6,
            fill=None,
            outline="white",
            rotation=self.__loading_frame__ * 10,
        )
        draw.regular_polygon(
            (32, 10, 8),
            n_sides=3,
            fill=None,
            outline="white",
            rotation=self.__loading_frame__ * -10,
        )
        draw.text(
            (16, 23), "loading", font=ImageFont.truetype("fonts/tiny.otf", size=5)
        )
        self.__loading_frame__ = self.__loading_frame__ + 1

    def start_loading(self):
        self.__interval__ = setInterval(0.1, self.__update_loading__)

    def stop_loading(self):
        self.__interval__.cancel()

    # this should be passed to each app. used to update the image
    def set_canvas(self, i: Image):
        self.MAIN_IMAGE = i

    # this should not be used by apps directly
    def push_canvas(self):
        self.buffer.SetImage(self.MAIN_IMAGE, unsafe=False)
        self.matrix.SwapOnVSync(self.buffer)


shown_app_index = 0
app_list: list[App] = []


def cycle(app_to_hide: App, app_to_show: App):
    app_to_hide.hide()
    app_to_show.show()


def next_app():
    global app_list
    global shown_app_index
    next_app_index = (shown_app_index + 1) % len(app_list)

    logger.debug(
        f"page transition: {app_list[shown_app_index].__class__.__name__} -> {app_list[next_app_index].__class__.__name__}"
    )

    app_list[shown_app_index].hide()
    app_list[next_app_index].show()

    shown_app_index = next_app_index


def prev_app():
    global app_list
    global shown_app_index
    next_app_index = (shown_app_index - 1) % len(app_list)

    logger.debug(
        f"page transition: {app_list[shown_app_index].__class__.__name__} -> {app_list[next_app_index].__class__.__name__}"
    )

    app_list[shown_app_index].hide()
    app_list[next_app_index].show()

    shown_app_index = next_app_index


def page_up():
    global app_list
    global shown_app_index
    app_list[shown_app_index].dec_page()


def page_down():
    global app_list
    global shown_app_index
    app_list[shown_app_index].inc_page()


if __name__ == "__main__":
    # initialize matrix
    m = MAIN_MATRIX()

    server = HTTP_SERVER(next_app, prev_app, page_up, page_down, m)
    server.start()

    # push image to led board frame_rate times per second
    i = setInterval(1 / m.FRAME_RATE, m.push_canvas)

    m.start_loading()
    enabled_apps = ["weather", "spotify", "subway", "gif"]

    if "weather" in enabled_apps:
        app_list.append(WeatherApp(m.set_canvas, data_refresh_rate=60))
    if "spotify" in enabled_apps:
        app_list.append(SpotifyApp(m.set_canvas, data_refresh_rate=2))
    if "subway" in enabled_apps:
        app_list.append(SubwayApp(m.set_canvas))
    if "drawing" in enabled_apps:
        app_list.append(DrawingApp(m.set_canvas))
    if "gif" in enabled_apps:
        app_list.append(GifApp(m.set_canvas))
    if "message" in enabled_apps:
        app_list.append(MessageApp(m.set_canvas))

    if len(app_list) == 0:
        i.cancel()
        m.stop_loading()
        raise Exception(f"no apps matched {app_list}")

    m.stop_loading()

    logger.info("initialized; starting display with:")
    logger.info(", ".join(map(lambda app: app.__class__.__name__, app_list)))

    try:
        for app in app_list:
            app.start()

        shown_app_index = 0
        app_list[0].show()
        pause()

    except KeyboardInterrupt as e:
        logger.info("")
        logger.info("exiting...")
        logger.info("\n")
        for app in app_list:
            app.stop()
        i.cancel()
