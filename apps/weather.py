from os import getenv
from PIL import Image, ImageFont, ImageDraw
from apps.App import App
from datetime import datetime
import itertools
import math
from utils.scroller import Scroller

BIN_LENGTH = 3
NUM_BINS = 18


def create_gradient_color(value, min_value, max_value):
    # Normalize the value between 0 and 1
    normalized = (value - min_value) / (max_value - min_value)

    # Interpolate between blue and red
    red = int(normalized * 255)
    blue = int((1 - normalized) * 255)
    return (red, 0, blue)


class WeatherApp(App):
    def __init__(self, image_setter, data_refresh_rate=10) -> None:
        super().__init__(image_setter=image_setter, data_refresh_rate=data_refresh_rate)
        api_key = getenv("WEATHER_API_KEY")
        zip_code = getenv("ZIP_CODE")
        self.__api_url__ = f"http://api.weatherapi.com/v1/forecast.json?q={zip_code}&key={api_key}&aqi=no&alerts=no&days=2"
        self.__top_padding__ = 2
        self.__current_face__ = 0
        self.__faces__ = [self.clock1, self.clock2, self.clock3]
        self.__precip__ = []
        self.__temps__ = []
        # danger
        self.__canvas__ = Image.new("RGB", (64, 32), (0, 0, 0))
        self.__last_condition__ = ""
        self.__condition_scroller__ = Scroller(
            self.__canvas__, 1, self.__top_padding__ + 16, 42, ""
        )

    def clock1(self):
        self.__draw_text__(
            self.__canvas__,
            (1, self.__top_padding__),
            datetime.now().strftime("%I:%M:%S %p").lstrip("0")[:-1].lower(),
            font=ImageFont.truetype("fonts/tiny.otf", size=7),
            fill="yellow",
        )
        self.__draw_text__(
            self.__canvas__,
            (1, self.__top_padding__ + 9),
            f"{self.__data__['location']['name']}",
            fill=(180, 180, 180),
        )
        self.__draw_text__(
            self.__canvas__,
            (40, self.__top_padding__ + 9),
            f"{self.__data__['current']['feelslike_f']}°",
            fill="lightBlue",
        )

        self.__draw_text__(
            self.__canvas__,
            (44, self.__top_padding__ + 16),
            str(
                math.ceil(
                    self.__data__["forecast"]["forecastday"][0]["day"]["mintemp_f"]
                )
            ),
            fill=(180, 180, 180),
        )
        self.__draw_text__(
            self.__canvas__,
            (52, self.__top_padding__ + 16),
            str(
                math.ceil(
                    self.__data__["forecast"]["forecastday"][0]["day"]["maxtemp_f"]
                )
            ),
            fill=(255, 165, 0),
        )

        if self.__data__["current"]["condition"]["text"] != self.__last_condition__:
            self.__condition_scroller__.update_text(
                self.__data__["current"]["condition"]["text"]
            )
            self.__last_condition__ = self.__data__["current"]["condition"]["text"]
        self.__condition_scroller__.incr()

        # graphs
        draw = ImageDraw.Draw(self.__canvas__)
        for index in range(0, len(self.__precip__)):
            chance_of_rain = self.__precip__[index]
            temp = self.__temps__[index]

            start_x = 1 + (index * BIN_LENGTH)
            end_x = BIN_LENGTH + (index * BIN_LENGTH)

            y_precip = 29 - (math.ceil(chance_of_rain / 25))
            y_temp_offset = (
                (temp - min(self.__temps__))
                / (max(self.__temps__) - min(self.__temps__))
            ) * 4
            y_temp = 29 - y_temp_offset

            f = (180, 180, 180) if index % 2 == 0 else (255, 255, 255)
            draw.line([(start_x, y_precip), (end_x, y_precip)], fill=f)

            f1 = (173, 216, 230) if y_temp_offset < 2 else (255, 165, 0)
            draw.line([(start_x, y_temp), (end_x, y_temp)], fill=f1)

        self.__draw_text__(self.__canvas__, (58, 25), "%")

        # self.__condition_scroller__.update_text("asdf asdf asdf asdf")

    def clock2(self):
        d = datetime.now()
        self.__draw_text_centered__(
            self.__canvas__,
            d.strftime("%I:%M").lstrip("0"),
            font=ImageFont.truetype("fonts/tiny.otf", size=13),
        )

    def clock3(self):

        # Create an image with a resolution of 64x32
        img_width, img_height = 64, 30
        draw = ImageDraw.Draw(self.__canvas__)

        # Determine the scaling factors
        max_value = max(self.__temps__)
        min_value = min(self.__temps__)
        y_scale = (
            (img_height - 1) / (max_value - min_value) if max_value != min_value else 1
        )

        # Draw the graph
        for i in range(NUM_BINS - 1):
            # x1 = int(i * (img_width / (NUM_BINS - 1)))
            # y1 = int(img_height - (self.__temps__[i] - min_value) * y_scale)
            # x2 = int((i + 1) * (img_width / (NUM_BINS - 1)))
            # y2 = int(img_height - (self.__temps__[i + 1] - min_value) * y_scale)
            # draw.line([(x1, y1), (x2, y2)], fill=create_gradient_color(self.__temps__[i], min_value, max_value), width=1)
            x = int(i * (img_width / NUM_BINS))
            y = int(img_height - (self.__temps__[i] - min_value) * y_scale)

            # Get the gradient color for the current value
            color = create_gradient_color(self.__temps__[i], min_value, max_value)

            # Draw the dot
            draw.rectangle([(x, y), (x + 1, y + 1)], fill=color)

    def __render_update__(self):
        # self.__canvas__ = Image.new("RGB", (64, 32), (0, 0, 0))
        self.__canvas__.paste(
            (0, 0, 0), (0, 0, self.__canvas__.size[0], self.__canvas__.size[1])
        )
        if self.__data__ is None:
            self.__draw_text__(self.__canvas__, (1, self.__top_padding__), "loading")
            self.__draw_text__(
                self.__canvas__, (1, self.__top_padding__ + 7), "weather..."
            )
        else:
            # self.__faces__[self.__current_face__](canvas=self.__canvas__)
            self.__faces__[self.__current_face__]()

        self.__image_setter__(self.__canvas__)

    def __data_update__(self):
        super().__data_update__()
        hourObjects = list(
            itertools.chain(
                self.__data__["forecast"]["forecastday"][0]["hour"],
                self.__data__["forecast"]["forecastday"][1]["hour"],
            )
        )
        curr = datetime.now().hour
        self.__precip__ = [
            x["chance_of_rain"] for x in hourObjects[curr : curr + NUM_BINS]
        ]
        self.__temps__ = [x["temp_f"] for x in hourObjects[curr : curr + NUM_BINS]]

    def inc_page(self):
        self.__current_face__ = (self.__current_face__ + 1) % len(self.__faces__)

    def dec_page(self):
        self.__current_face__ = (self.__current_face__ - 1) % len(self.__faces__)
