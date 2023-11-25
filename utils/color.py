from colorthief import ColorThief
from PIL import Image

class ColorThiefFromImage(ColorThief):
    def __init__(self, image: Image.Image):
        self.image = image