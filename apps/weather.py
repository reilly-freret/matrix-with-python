from os import getenv
from PIL import Image, ImageFont, ImageDraw
from apps.App import App
from datetime import datetime
import itertools
import math

BIN_LENGTH = 3
NUM_BINS = 18


class WeatherApp(App):
    def __init__(self, image_setter, data_refresh_rate=10) -> None:
        super().__init__(image_setter=image_setter, data_refresh_rate=data_refresh_rate)
        api_key = getenv("WEATHER_API_KEY")
        zip_code = getenv("ZIP_CODE")
        self.__api_url__ = f"http://api.weatherapi.com/v1/forecast.json?q={zip_code}&key={api_key}&aqi=no&alerts=no&days=2"
        self.__top_padding__ = 2
        self.__current_face__ = 0
        self.__faces__ = [self.clock2, self.clock1]
        self.__precip__ = []
        self.__temps__ = []

    def clock1(self, canvas):
        self.__draw_text__(canvas, (1, self.__top_padding__), datetime.now().strftime("%I:%M:%S %p").lstrip(
                '0')[:-1].lower(), font=ImageFont.truetype('fonts/tiny.otf', size=7), fill='yellow')
        self.__draw_text__(
            canvas, (1, self.__top_padding__ + 9), f"{self.__data__['location']['name']}", fill=(180, 180, 180))
        self.__draw_text__(
            canvas, (40, self.__top_padding__ + 9), f"{self.__data__['current']['feelslike_f']}°", fill='lightBlue')
        
        condition = self.__data__['current']['condition']['text'] if len(self.__data__['current']['condition']['text']) < 11 else self.__data__['current']['condition']['text'][0:7] + "..."

        self.__draw_text__(canvas, (1, self.__top_padding__ + 16), condition)
        # print(self.__data__['forecast']['forecastday'][0]['day']['maxtemp_f'])
        self.__draw_text__(canvas, (40, self.__top_padding__ + 16), str(math.ceil(self.__data__['forecast']['forecastday'][0]['day']['mintemp_f'])), fill=(180, 180, 180))
        self.__draw_text__(canvas, (50, self.__top_padding__ + 16), str(math.ceil(self.__data__['forecast']['forecastday'][0]['day']['maxtemp_f'])), fill=(255,165,0))
        
        # graphs
        draw = ImageDraw.Draw(canvas)
        for index in range(0, len(self.__precip__)):
            chance_of_rain = self.__precip__[index]
            temp = self.__temps__[index]

            start_x = 1 + (index * BIN_LENGTH)
            end_x = BIN_LENGTH + (index * BIN_LENGTH)

            y_precip = 29 - (math.ceil(chance_of_rain / 25))
            y_temp_offset = (((temp - min(self.__temps__)) / (max(self.__temps__) - min(self.__temps__))) * 4)
            y_temp = 29 - y_temp_offset

            f = (180, 180, 180) if index % 2 == 0 else (255, 255, 255)
            draw.line([(start_x, y_precip), (end_x, y_precip)], fill=f)
            f1 = (173,216,230) if y_temp_offset < 2 else (255,165,0)
            draw.line([(start_x, y_temp), (end_x, y_temp)], fill=f1)
            

        # for index, chance_of_rain in enumerate(self.__precip__):
        #     start_x = 1 + (index * BIN_LENGTH)
        #     start_y = 29 - (math.ceil(chance_of_rain / 25))
        #     end_x = 0 + BIN_LENGTH + (index * BIN_LENGTH)
        #     f = (180, 180, 180) if index % 2 == 0 else (255, 255, 255)
        #     draw.line([(start_x, start_y), (end_x, start_y)], fill=f)
        self.__draw_text__(canvas, (58, 25), "%")

    
    def __data_update__(self):
        super().__data_update__()
        hourObjects = list(itertools.chain(
            self.__data__['forecast']['forecastday'][0]['hour'],
            self.__data__['forecast']['forecastday'][1]['hour']
        ))
        curr = datetime.now().hour
        self.__precip__ = [x['chance_of_rain'] for x in hourObjects[curr:curr+NUM_BINS]]
        self.__temps__ = [x['temp_f'] for x in hourObjects[curr:curr+NUM_BINS]]

            
        
    def clock2(self, canvas):
        d = datetime.now()
        self.__draw_text_centered__(canvas, d.strftime("%I:%M").lstrip(
                '0'), font=ImageFont.truetype('fonts/tiny.otf', size=13))

    def __render_update__(self):
        canvas = Image.new("RGB", (64, 32), (0, 0, 0))
        if self.__data__ is None:
            self.__draw_text__(canvas, (1, self.__top_padding__), "loading")
            self.__draw_text__(canvas, (1, self.__top_padding__ + 7), "weather...")
        else:
            self.__faces__[self.__current_face__](canvas=canvas)
            
        self.__image_setter__(canvas)

    def inc_page(self):
        self.__current_face__ = (self.__current_face__ + 1) % len(self.__faces__)

    def dec_page(self):
        self.__current_face__ = (self.__current_face__ - 1) % len(self.__faces__)
