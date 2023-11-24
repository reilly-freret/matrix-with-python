from apps import WeatherApp, SubwayApp, SpotifyApp
from apps.App import App
from time import sleep
from PIL import Image
from dotenv import load_dotenv
from os import getenv
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils.timer import setInterval
from signal import pause
import sys

load_dotenv()
PAGE_TIME_S = 5


class MAIN_MATRIX:
    def __init__(self) -> None:
        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.cols = 64
        self.options.hardware_mapping = 'adafruit-hat'
        self.options.gpio_slowdown = int(getenv('GPIO_SLOWDOWN', '3'))
        self.options.brightness = int(getenv('MAX_BRIGHTNESS', '80'))
        self.options.drop_privileges = False
        self.options.pixel_mapper_config = 'Rotate:180'
        self.matrix = RGBMatrix(options=self.options)

        self.MAIN_IMAGE = Image.new("RGB", (64, 32), (150, 150, 150))

        self.FRAME_RATE = 10

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

    print("\n===== starting display with: =====")
    for app in app_list:
        print(app.__class__.__name__)

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
        print("\n\nexiting...\n")
        for app in app_list:
            app.stop()
        i.cancel()
