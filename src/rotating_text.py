import pytesseract
import tempfile

from PIL import Image
from pytesseract import Output


def set_image_dpi(image: Image) -> Image:
    """
    Rescaling image to 300dpi without resizing
    :param image: A PIL or cv2 image
    :return: A rescaled image
    """
    image_resize = image
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    temp_filename = temp_file.name
    image_resize.save(temp_filename, dpi=(300, 300))
    return temp_filename


def get_rotation_angle(input_image: Image) -> int:
    image_ = set_image_dpi(input_image)
    results = pytesseract.image_to_osd(image_,
                                       config='--psm 0 -c min_characters_to_try=5',
                                       output_type=Output.DICT)
    return results["rotate"]


pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'  # TODO location в env
