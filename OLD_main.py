from os import getenv
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw
from signal import pause
from utils.timer import setInterval
import threading

MAIN_IMAGE = Image.new("RGB", (64,32), (255,0,0))
c = 0

print("yooo")
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.hardware_mapping = 'adafruit-hat'
options.gpio_slowdown = int(getenv('GPIO_SLOWDOWN', '3'))
options.brightness = int(getenv('MAX_BRIGHTNESS', '80'))
options.drop_privileges = False
options.pixel_mapper_config = 'Rotate:180'
matrix = RGBMatrix(options=options)

# matrix.SetImage(MAIN_IMAGE, unsafe=False)

def toggle_image():
    global MAIN_IMAGE, c
    if c % 2 == 0:
        MAIN_IMAGE = Image.new("RGB", (64,32), (255,0,0))
        draw = ImageDraw.Draw(MAIN_IMAGE)
        draw.rectangle((4, 4, 8, 8), fill="blue")
        draw.text((16, 16), "hello")
        draw.regular_polygon((20,10,10),n_sides=3, fill="green")
    else:
        MAIN_IMAGE = Image.new("RGB", (64,32), (255,0,0))
    c += 1

if __name__ == "__main__":
    i = setInterval(0.1, lambda : matrix.SetImage(MAIN_IMAGE, unsafe=False))
    j = setInterval(1, toggle_image)

    def cancel():
        i.cancel()
        j.cancel()
    try:
        pause()
    except KeyboardInterrupt:
        print("\nquitting...\n")
        cancel()