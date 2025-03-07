from datetime import datetime
from apps.App import App
from PIL import Image, ImageSequence, ImageFont
import os


class GifApp(App):
    def __init__(
        self, image_setter, data_refresh_rate=10, render_refresh_rate=0.1
    ) -> None:
        super().__init__(image_setter, data_refresh_rate, render_refresh_rate)
        self.__gifs__ = []
        folder = "imgs/gif"
        for filename in sorted(os.listdir(folder)):
            self.__gifs__.append(Image.open(folder + "/" + filename))
        self.__cur_gif_idx__ = 0
        self.__cur_frame__ = 0

    def press(self, key):
        if key == "up":
            self.__cur_gif_idx__ = (self.__cur_gif_idx__ + 1) % len(self.__gifs__)
        elif key == "down":
            self.__cur_gif_idx__ = (self.__cur_gif_idx__ - 1) % len(self.__gifs__)
        self.__cur_frame__ = 0

    def inc_page(self):
        self.__cur_gif_idx__ = (self.__cur_gif_idx__ + 1) % len(self.__gifs__)

    def dec_page(self):
        self.__cur_gif_idx__ = (self.__cur_gif_idx__ - 1) % len(self.__gifs__)

    def __data_update__(self):
        pass

    def __render_update__(self):
        gif = self.__gifs__[self.__cur_gif_idx__ % len(self.__gifs__)]
        curr_gif = ImageSequence.Iterator(gif)
        frame = curr_gif[self.__cur_frame__ % gif.n_frames].convert("RGB")
        ##
        d = datetime.now()
        self.__draw_text_centered__(
            frame,
            d.strftime("%I:%M").lstrip("0"),
            font=ImageFont.truetype("fonts/tiny.otf", size=13),
        )
        ##
        self.__cur_frame__ += 1

        self.__image_setter__(frame)
