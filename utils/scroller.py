from PIL import Image, ImageFont, ImageDraw


class Scroller():
    def __init__(self, canvas: Image.Image, x: int, y: int, width: int, text: str) -> None:
        self.__canvas__ = canvas
        self.__x__ = x
        self.__y__ = y
        self.__width__ = width
        self.__text__ = text
        self.__current_offset__ = 0
        self.__font__ = ImageFont.truetype('fonts/tiny.otf', size=5)
        self.__text_width__ = self.__font__.getsize(self.__text__)[0]
        self.__text_height__ = self.__font__.getsize(self.__text__)[1]
        self.__sub_canvas__ = Image.new(
            'RGB', (self.__width__, self.__text_height__), (0, 0, 0))
        self.__PADDING__ = 14
        self.__WAIT_THRES__ = 40
        self.__HAS_WAITED__ = 0
        self.__color__ = 'white'

    def update_text(self, text):
        self.__text__ = text
        self.__text_width__ = self.__font__.getsize(self.__text__)[0]
        self.__text_height__ = self.__font__.getsize(self.__text__)[1]
        self.__sub_canvas__ = Image.new(
            'RGB', (self.__width__, self.__text_height__), (0, 0, 0))
        self.__current_offset__ = 0

    def update_color(self, color):
        self.__color__ = color

    def incr(self):
        # clear region on canvas
        self.__sub_canvas__.paste(
            (0, 0, 0), (0, 0, self.__sub_canvas__.size[0], self.__sub_canvas__.size[1]))
        draw = ImageDraw.Draw(self.__sub_canvas__)

        # if the string is narrower than the bounding box, just print again
        if self.__text_width__ <= self.__width__:
            draw.text((self.__current_offset__, 0), self.__text__,
                      fill=self.__color__, font=self.__font__)
            self.__canvas__.paste(self.__sub_canvas__,
                                  (self.__x__, self.__y__))
            return

        # draw text with offset
        draw.text((self.__current_offset__, 0), self.__text__,
                  fill=self.__color__, font=self.__font__)
        draw.text((self.__current_offset__ + self.__text_width__ + self.__PADDING__,
                  0), self.__text__, fill=self.__color__, font=self.__font__)

        # calculate new offset
        if self.__current_offset__ == -1 * (self.__text_width__ + self.__PADDING__):
            # reset padding
            self.__current_offset__ = 0
        elif self.__current_offset__ == 0:
            if self.__HAS_WAITED__ > self.__WAIT_THRES__:
                self.__HAS_WAITED__ = 0
                self.__current_offset__ -= 1
            else:
                self.__HAS_WAITED__ += 1
        else:
            self.__current_offset__ -= 1

        # paste to canvas
        self.__canvas__.paste(self.__sub_canvas__, (self.__x__, self.__y__))
