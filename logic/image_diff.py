import tempfile

from PIL import Image, ImageFilter
from pytesseract import Output

from angle_getter import get_rotation_angle


def create_image(input_file: 'FileStorage') -> Image:
    suff = input_file.filename.split('.')[-1]
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suff)
    temp_filename = temp_file.name
    input_file.save(temp_filename)

    image = Image.open(temp_filename)
    return image


def process_diff(base: Image, compared: Image):
    rotate_base = get_rotation_angle(base)
    rotate_compared = get_rotation_angle(compared)

    base = base.rotate(rotate_base)
    compared = compared.rotate(rotate_compared)

    # рассчитать размер

    # сравнить

    pass
