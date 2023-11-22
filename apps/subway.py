from PIL import Image
from utils.date import mins_in_future
from apps.APP import App


class SubwayApp(App):
    def __init__(self, image_setter, data_refresh_rate=10) -> None:
        super().__init__(image_setter=image_setter, data_refresh_rate=data_refresh_rate)
        self.__api_url__ = "http://platform-pro-api.herokuapp.com/by-id/4564"

    def __show_data__(self):
        if self.__data__ is None:
            canvas = Image.new("RGB", (64, 32), (0, 100, 0))
            self.__draw_text__(canvas, (0,0), "subway...")
            self.__image_setter__(canvas)
        else:
            canvas = Image.new("RGB", (64, 32), (0, 0, 0))
            for index, train in enumerate(self.__data__['data'][0]['N']):
                train_string = f"{train['route']} - {mins_in_future(train['time']):.0f}m"
                self.__draw_text__(canvas, (1, 1 + index * 7), train_string)
            self.__image_setter__(canvas)
