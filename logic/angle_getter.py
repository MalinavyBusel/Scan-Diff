import pytesseract
import tempfile
import cv2

from PIL import Image, ImageFilter
from pytesseract import Output
from numpy import array
from deskew import determine_skew

from logic.config import settings

pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT


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
    pytess_image.save(temp_filename)#, dpi=(300, 300))
    return temp_filename


def get_rotation_angle(image: Image) -> int:
    """
    Get the image, tries to recognize the text and returns the number of degrees to rotate
    Since the lang is not specified, its better not to use for hieroglyphs
    :param input_image: A PIL or cv2 image
    :return: A number of degrees
    """
    image = array(image)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    angle = determine_skew(grayscale)
    return angle



    # OLD VERSION OF get_rotation_angle
    # image_ = set_dpi_and_filter(input_image)
    # # не cтавил языки в image_to_osd, тк так результаты точнее
    # results = pytesseract.image_to_osd(image_,
    #                                    config='--psm 0 -c min_characters_to_try=5 tessedit_char_whitelist=0123456789.',
    #                                    output_type=Output.DICT,
    #                                    lang='rus')
    # return results["rotate"]
