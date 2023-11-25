from apps import WeatherApp, SubwayApp, SpotifyApp
from apps.App import App
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from os import getenv
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils.timer import setInterval
from signal import pause
import sys
from utils.logger import Logger as l

load_dotenv()
PAGE_TIME_S = 5


class MAIN_MATRIX:
    def __init__(self) -> None:
        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.cols = 64
        self.options.hardware_mapping = 'adafruit-hat'
        self.options.gpio_slowdown = int(getenv('GPIO_SLOWDOWN', '4'))
        self.options.brightness = int(getenv('MAX_BRIGHTNESS', '80'))
        self.options.drop_privileges = False
        self.options.pixel_mapper_config = 'Rotate:180'
        self.matrix = RGBMatrix(options=self.options)

        self.MAIN_IMAGE = Image.new("RGB", (64, 32), (70, 70, 70))
        self.__loading_frame__ = 0
        self.__interval__ = None

        self.FRAME_RATE = 10

    def __update_loading__(self):
        self.MAIN_IMAGE = Image.new("RGB", (64, 32), (70, 70, 70))
        draw = ImageDraw.Draw(self.MAIN_IMAGE)
        draw.regular_polygon((32, 10, 8), n_sides=6, fill=None,
                             outline='white', rotation=self.__loading_frame__ * 10)
        draw.regular_polygon((32, 10, 8), n_sides=3, fill=None,
                             outline='white', rotation=self.__loading_frame__ * -10)
        draw.text((16, 23), "loading", font=ImageFont.truetype(
            'fonts/tiny.otf', size=5))
        self.__loading_frame__ = (self.__loading_frame__ + 1)

    def start_loading(self):
        self.__interval__ = setInterval(0.1, self.__update_loading__)

    def stop_loading(self):
        self.__interval__.cancel()

    # this should be passed to each app. used to update the image
    def set_canvas(self, i: Image):
        self.MAIN_IMAGE = i

    # this should not be used by apps directly
    def push_canvas(self):
        self.matrix.SetImage(self.MAIN_IMAGE, unsafe=False)


if __name__ == "__main__":
    args = sys.argv[1:]

    # initialize matrix
    m = MAIN_MATRIX()
    # push image to led board frame_rate times per second
    i = setInterval(1 / m.FRAME_RATE, m.push_canvas)

    l.INFO(f"initializing display with args {args}")
    l.FULL(f"This shouldn't display")

    m.start_loading()

    app_list: list[App] = []

    if "weather" in args:
        app_list.append(WeatherApp(m.set_canvas, data_refresh_rate=60))
    if "spotify" in args:
        app_list.append(SpotifyApp(m.set_canvas, data_refresh_rate=2))
    if "subway" in args:
        app_list.append(SubwayApp(m.set_canvas))

    # if we didn't get any valid app names in args, just use all of them
    if len(app_list) == 0:
        app_list = [
            WeatherApp(m.set_canvas, data_refresh_rate=60),
            SpotifyApp(m.set_canvas, data_refresh_rate=2),
            SubwayApp(m.set_canvas),
        ]

    m.stop_loading()

    l.INFO("===== initialized; starting display with: =====")
    l.INFO(", ".join(map(lambda app: app.__class__.__name__, app_list)))

    try:
        for app in app_list:
            app.start()

        shown_app_index = 0

        # just one app; don't cycle through
        if len(app_list) == 1:
            app_list[0].show()
            pause()
        # multiple apps; cycle through
        else:
            while True:
                app_list[shown_app_index % len(app_list)].show()
                sleep(PAGE_TIME_S)
                app_list[shown_app_index % len(app_list)].hide()
                shown_app_index += 1

    except KeyboardInterrupt as e:
        l.INFO("\n\n")
        l.INFO("exiting...")
        l.INFO("\n")
        for app in app_list:
            app.stop()
        i.cancel()
