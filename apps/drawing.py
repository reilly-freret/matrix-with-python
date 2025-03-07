from apps.App import App
from PIL import Image
from io import BytesIO
import base64
from utils.logging import get_logger

logger = get_logger(__name__)


class DrawingApp(App):
    def __init__(self, image_setter, data_refresh_rate=0.5) -> None:
        super().__init__(image_setter=image_setter, data_refresh_rate=data_refresh_rate)
        self.__base64_img__ = None
        self.__top_padding__ = 2

    def __data_update__(self):
        # get image from file
        try:
            with open("/home/freret/Documents/drawing-frontend/files/test.txt") as f:
                image = f.read()
                self.__base64_img__ = image.replace("data:image/png;base64,", "")
                # self.__base64_img__ = image
        except:
            logger.error("failed to get image from filesystem")
        pass

    def __render_update__(self):
        canvas = Image.new("RGB", (64, 32), (0, 0, 0))
        if self.__base64_img__ is None:
            self.__draw_text__(canvas, (1, self.__top_padding__), "no image")
        else:
            i = Image.open(BytesIO(base64.b64decode(self.__base64_img__))).resize(
                (64, 32)
            )
            canvas.paste(i, (0, 0))

        self.__image_setter__(canvas)
