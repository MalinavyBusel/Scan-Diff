import pytesseract
import tempfile

from PIL import Image, ImageFilter
from pytesseract import Output

from logic.config import settings


pytesseract.pytesseract.tesseract_cmd = settings['TESSERACT']


def set_dpi_and_filter(image: Image) -> Image:
    """
    Rescaling image to 300dpi and filter it to improve the quality of recognition
    :param image: A PIL or cv2 image
    :return: A rescaled image
    """
    pytess_image = image

    pytess_image = pytess_image.filter(ImageFilter.SHARPEN)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    temp_filename = temp_file.name
    pytess_image.save(temp_filename, dpi=(300, 300))
    return temp_filename


def get_rotation_angle(input_image: Image) -> int:
    """
    Get the image, tries to recognize the text and returns the number of degrees to rotate
    Since the lang is not specified, its better not to use for hieroglyphs
    :param input_image: A PIL or cv2 image
    :return: A number of degrees
    """
    image_ = set_dpi_and_filter(input_image)
    # не cтавил языки в image_to_osd, тк так результаты точнее
    results = pytesseract.image_to_osd(image_,
                                       config='--psm 0 -c min_characters_to_try=5',
                                       output_type=Output.DICT)
    return results["rotate"]
