from apps.subway import SubwayApp
from apps.weather import WeatherApp
from apps.APP import App
from time import sleep
from PIL import Image
from dotenv import load_dotenv
from os import getenv
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils.timer import setInterval
from signal import pause

load_dotenv()

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

        self.MAIN_IMAGE = Image.new("RGB", (64,32), (255,0,0))

        self.frame_rate = 10

    # this should be passed to each app. used to update the image
    def set_canvas(self, i: Image):
        self.MAIN_IMAGE = i

    # this should not be used by apps directly
    def push_canvas(self):
        self.matrix.SetImage(self.MAIN_IMAGE, unsafe=False)


if __name__ == "__main__":
    # initialize matrix
    m = MAIN_MATRIX()
    # push image to led board frame_rate times per second
    i = setInterval(1 / m.frame_rate, m.push_canvas)

    apps: list[App] = [
        SubwayApp(m.set_canvas),
        WeatherApp(m.set_canvas),
    ]

    try:
        for app in apps:
            app.start()

        shown_app_index = 0

        # just one app; don't cycle through
        if len(apps) == 1:
            apps[0].show()
            pause()
        # multiple apps; cycle through
        else:
            while True:
                apps[shown_app_index % len(apps)].show()
                sleep(6)
                apps[shown_app_index % len(apps)].hide()
                shown_app_index += 1

    except KeyboardInterrupt as e:
        print("\n\nexiting...\n")
        for app in apps:
            app.stop()
        i.cancel()