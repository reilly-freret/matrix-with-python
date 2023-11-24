from PIL import Image
from utils.date import mins_in_future
from apps.App import App


class SubwayApp(App):
    def __init__(self, image_setter, data_refresh_rate=10) -> None:
        super().__init__(image_setter=image_setter, data_refresh_rate=data_refresh_rate)
        self.__api_url__ = "http://platform-pro-api.herokuapp.com/by-id/4564,6e3b"

    def __render_update__(self):
        canvas = Image.new("RGB", (64, 32), (0, 0, 0))
        if self.__data__ is None:
            self.__draw_text__(canvas, (1, 1), "loading")
            self.__draw_text__(canvas, (1, 8), "subway...")
        else:

            # southbound 456
            x_offset = 3
            y_offset = 2
            row_height = 11
            for index, train in enumerate(self.__data__['data'][0]['S'][:3]):
                arrival_time = mins_in_future(train['time'])
                arrival_string = ""
                if arrival_time < 1.5:
                    arrival_string = "now"
                else:
                    arrival_string = f"{arrival_time:.0f}m"

                box = self.__draw_text_bg__(
                    canvas, "green", 2, (x_offset, y_offset + index * row_height), train['route'])
                self.__draw_text__(
                    canvas, (box[2] + 3, y_offset + index * row_height), arrival_string)

            # southbound Q
            x_offset = 28
            for index, train in enumerate(self.__data__['data'][1]['S'][:3]):
                arrival_time = mins_in_future(train['time'])
                arrival_string = ""
                if arrival_time < 1.5:
                    arrival_string = "now"
                else:
                    arrival_string = f"{arrival_time:.0f}m"

                box = self.__draw_text_bg__(
                    canvas, "yellow", 2, (x_offset, y_offset + index * row_height), train['route'], fill="black")
                self.__draw_text__(
                    canvas, (box[2] + 3, y_offset + index * row_height), arrival_string)

        self.__image_setter__(canvas)
