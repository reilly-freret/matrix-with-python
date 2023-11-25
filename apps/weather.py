from os import getenv
from PIL import Image, ImageFont
from apps.App import App
from datetime import datetime


class WeatherApp(App):
    def __init__(self, image_setter, data_refresh_rate=10) -> None:
        super().__init__(image_setter=image_setter, data_refresh_rate=data_refresh_rate)

        api_key = getenv("WEATHER_API_KEY")
        zip_code = getenv("ZIP_CODE")
        self.__api_url__ = f"http://api.weatherapi.com/v1/forecast.json?q={zip_code}&key={api_key}"

    def __render_update__(self):
        canvas = Image.new("RGB", (64, 32), (0, 0, 0))
        if self.__data__ is None:
            self.__draw_text__(canvas, (1, 1), "loading")
            self.__draw_text__(canvas, (1, 8), "weather...")
        else:
            self.__draw_text__(canvas, (1, 1), datetime.now().strftime("%I:%M:%S %p").lstrip(
                '0')[:-1].lower(), font=ImageFont.truetype('fonts/tiny.otf', size=7), fill='yellow')
            self.__draw_text__(
                canvas, (1, 10), f"{self.__data__['location']['name']}", fill=(180, 180, 180))
            self.__draw_text__(
                canvas, (40, 10), f"{self.__data__['current']['feelslike_f']}°", fill='lightBlue')
            self.__draw_text__(canvas, (1, 17), self.__data__[
                               'current']['condition']['text'])
            rain = self.__data__[
                'forecast']['forecastday'][0]['day']['daily_will_it_rain']
            snow = self.__data__[
                'forecast']['forecastday'][0]['day']['daily_will_it_snow']
            forecast_string = ('No rain' if not rain else 'Rain') + \
                ', ' + ('No snow' if not snow else 'Snow')
            self.__draw_text__(
                canvas, (1, 24), forecast_string, fill=(247, 148, 236))
        self.__image_setter__(canvas)
