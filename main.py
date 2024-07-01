from apps import WeatherApp, SubwayApp, SpotifyApp, DrawingApp, GifApp, MessageApp
from apps.App import App
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from os import getenv
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils.timer import setInterval
from utils.logging import get_logger
import sshkeyboard
import argparse
from signal import pause

logger = get_logger(__name__)

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
        self.options.pixel_mapper_config = f'Rotate:{getenv("ROTATION")}'
        self.matrix = RGBMatrix(options=self.options)

        self.MAIN_IMAGE = Image.new("RGB", (64, 32), (0,0,0))
        self.__loading_frame__ = 0
        self.__interval__ = None

        self.FRAME_RATE = 20

        self.buffer = self.matrix.CreateFrameCanvas()

    def __update_loading__(self):
        self.MAIN_IMAGE = Image.new("RGB", (64, 32), (0,0,0))
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

    logger.debug(f"page transition: {app_list[shown_app_index].__class__.__name__} -> {app_list[next_app_index].__class__.__name__}")
    
    app_list[shown_app_index].hide()
    app_list[next_app_index].show()

    shown_app_index = next_app_index


def prev_app():
    global app_list
    global shown_app_index
    next_app_index = (shown_app_index - 1) % len(app_list)

    logger.debug(f"page transition: {app_list[shown_app_index].__class__.__name__} -> {app_list[next_app_index].__class__.__name__}")
    
    app_list[shown_app_index].hide()
    app_list[next_app_index].show()

    shown_app_index = next_app_index


if __name__ == "__main__":
    # args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description='Display some info on an RGB matrix.')
    parser.add_argument('-a', '--apps', nargs='+', default=[
                        'weather', 'spotify', 'subway', 'drawing', 'gif'], help='List of app names to run (weather|spotify|subway|drawing)')
    parser.add_argument('-i', '--interactive',
                        action='store_true', help='Enable keyboard interaction')
    parser.add_argument('-d', '--delay', default=PAGE_TIME_S,
                        help='When interactive mode is disabled, wait for this number of seconds between apps', type=int)
    parser.add_argument('-l', '--log_level', default=getenv('LOG_LEVEL'), help='Log level (SILENT|ERROR|WARN|INFO|DEBUG|FULL)', type=str)
    args = parser.parse_args()

    # l.update_level(args.log_level.upper())

    # initialize matrix
    m = MAIN_MATRIX()
    # push image to led board frame_rate times per second
    i = setInterval(1 / m.FRAME_RATE, m.push_canvas)

    logger.info(f"initializing display with args {args}")

    m.start_loading()

    if "weather" in args.apps:
        app_list.append(WeatherApp(m.set_canvas, data_refresh_rate=60))
    if "spotify" in args.apps:
        app_list.append(SpotifyApp(m.set_canvas, data_refresh_rate=2))
    if "subway" in args.apps:
        app_list.append(SubwayApp(m.set_canvas))
    if "drawing" in args.apps:
        app_list.append(DrawingApp(m.set_canvas))
    if "gif" in args.apps:
        app_list.append(GifApp(m.set_canvas))
    if "message" in args.apps:
        app_list.append(MessageApp(m.set_canvas))
    

    if len(app_list) == 0:
        i.cancel()
        m.stop_loading()
        raise Exception(f"no apps matched {app_list}")

    def press(key):
        logger.debug(f"'{key}' pressed")
        if key == 'right':
            next_app()
        elif key == 'left':
            prev_app()
        elif key == 'up':
            app_list[shown_app_index].dec_page()
        elif key == 'down':
            app_list[shown_app_index].inc_page()


    def release(key):
        logger.debug(f"'{key}' released")

    m.stop_loading()

    logger.info("initialized; starting display with:")
    logger.info(", ".join(map(lambda app: app.__class__.__name__, app_list)))

    try:
        for app in app_list:
            app.start()

        shown_app_index = 0

        # just one app; don't cycle through
        # if len(app_list) == 1:
        #     app_list[0].show()
        #     pause()
        # multiple apps; cycle through
        # else:
            # show the first app
        app_list[0].show()
        if args.interactive:
            logger.info("starting interactive mode...")
            sshkeyboard.listen_keyboard(
                on_press=press,
                on_release=release
            )
        else:
            if len(app_list) == 1:
                logger.info("starting non-interactive single-app...")
                pause()
            else:
                logger.info("starting non-interactive multiple-app...")
                while True:
                    sleep(args.delay)
                    next_app()

    except KeyboardInterrupt as e:
        logger.info("")
        logger.info("exiting...")
        logger.info("\n")
        for app in app_list:
            app.stop()
        i.cancel()
