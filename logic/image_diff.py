import tempfile

from PIL import Image, ImageFilter
from pytesseract import Output


def create_image(input_file: 'FileStorage') -> Image:
    suff = input_file.filename.split('.')[-1]
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suff)
    temp_filename = temp_file.name
    input_file.save(temp_filename)

    image = Image.open(temp_filename)
    return image


def process_diff(base: Image, compared: Image):
    # рассчитать поворот

    # повернуть

    # рассчитать размер

    # сравнить

    pass
