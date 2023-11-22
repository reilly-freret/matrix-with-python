from os import getenv
from PIL import Image
from apps.APP import App


class WeatherApp(App):
    def __init__(self, image_setter, data_refresh_rate=10) -> None:
        super().__init__(image_setter=image_setter, data_refresh_rate=data_refresh_rate)

        api_key = getenv("WEATHER_API_KEY")
        zip_code = getenv("ZIP_CODE")
        self.__api_url__ = f"http://api.weatherapi.com/v1/current.json?q={zip_code}&key={api_key}"

    def __show_data__(self):
        if self.__data__ is None:
            canvas = Image.new("RGB", (64, 32), (0, 255, 0))
            self.__draw_text__(canvas, (0, 0), "weather...")
            self.__image_setter__(canvas)
        else:
            canvas = Image.new("RGB", (64, 32), (0, 0, 0))
            self.__draw_text__(canvas, (1,1), f"{self.__data__['location']['name']}  {self.__data__['current']['temp_f']}")
            self.__draw_text__(canvas, (1,8), self.__data__['current']['condition']['text'])
            self.__image_setter__(canvas)
