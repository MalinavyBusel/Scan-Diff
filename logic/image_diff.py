import re
import numpy
import cv2
import pytesseract
import diff_match_patch
import imutils

from deskew import determine_skew
from PIL import Image, ImageFilter, ImageDraw
from typing import Tuple, Any

from logic.config import settings

pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT


def create_image(input_file: str) -> Image:
    image = Image.open(input_file)
    return image


def process_diff(base: Image, compared: Image, lang: str) -> Tuple[Image, Image, bool]:
    """Rotates, resizes and finds differences between images"""
    rotate_base = get_rotation_angle(base)
    rotate_compared = get_rotation_angle(compared)

    # base = base.rotate(rotate_base, expand=True)
    # compared = compared.rotate(rotate_compared, expand=True)
    b_w, b_h = base.size
    h_w, h_h = compared.size
    # выбрал минимальный размер, чтобы качество не сильно портилось,
    # да и сравнивать проще
    im_size = (min(b_w, h_w), min(b_h, h_h))
    base = base.resize(im_size, Image.LANCZOS)
    compared = compared.resize(im_size, Image.LANCZOS)

    return get_tesseract_diff(base, compared, im_size, lang, rotate_base, rotate_compared)


def get_rotation_angle(image: Image) -> int:
    """
    Get the image, tries to recognize the text and returns the number of degrees to rotate
    Since the lang is not specified, its better not to use for hieroglyphs
    :param image: A PIL or cv2 image
    :return: A number of degrees
    """
    image = numpy.array(image)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    angle = determine_skew(grayscale)
    return angle


def get_string(img: numpy.ndarray, lang: str) -> str:
    data_str = pytesseract.image_to_string(img, lang=lang)
    return data_str


def get_tesseract_diff(img1: Image, img2: Image, size: Tuple[Any],
                       lang: str, angle1: int, angle2: int) -> Tuple[Image, Image, bool]:
    """
        Scans images with pytesseract and finds differences between two texts with diff-match-patch
        Highlights the different symbols with red rectangles
    """

    img1 = numpy.array(img1)
    img1 = imutils.rotate(img1, angle1)
    img2 = numpy.array(img2)
    img2 = imutils.rotate(img2, angle2)
    i_h = size[1]

    data_str_1 = get_string(img1, lang)
    data_str_1 = re.sub('[ \t\n\r]', '', data_str_1)

    box_str_1 = pytesseract.image_to_boxes(img1, lang=lang).splitlines()

    data_str_2 = get_string(img2, lang)
    data_str_2 = re.sub('[ \t\n\r]', '', data_str_2)

    box_str_2 = pytesseract.image_to_boxes(img2, lang=lang).splitlines()
    diff_obj = diff_match_patch.diff_match_patch()
    diffs = diff_obj.diff_main(text1=data_str_1, text2=data_str_2)

    # -1 - встречается только в изображении 1, 1 - только в изображении 2
    len1, len2 = 0, 0
    same, differ = 0, 0
    for text_part in diffs:
        text = text_part[1]

        if text_part[0] == 1:
            for box2 in box_str_2[len2:(len2 + len(text))]:
                box2 = box2.split(' ')
                x, y, w, h = int(box2[1]), int(box2[2]), int(box2[3]), int(box2[4])
                cv2.rectangle(img2, (x - 1, i_h - y + 1), (w + 1, i_h - h - 2), (255, 0, 0), 1)
            len2 += len(text)
            differ += len(text)

        elif text_part[0] == -1:
            for box1 in box_str_1[len1:(len1 + len(text))]:
                box1 = box1.split(' ')
                x, y, w, h = int(box1[1]), int(box1[2]), int(box1[3]), int(box1[4])
                cv2.rectangle(img1, (x - 1, i_h - y + 1), (w + 1, i_h - h - 2), (255, 0, 0), 1)
            len1 += len(text)
            differ += len(text)

        elif not text_part[0]:
            for box1 in box_str_1[len1:(len1 + len(text))]:
                box1 = box1.split(' ')
                x, y, w, h = int(box1[1]), int(box1[2]), int(box1[3]), int(box1[4])
                cv2.rectangle(img1, (x - 1, i_h - y + 1), (w + 1, i_h - h - 2), (0, 255, 0), 1)
            for box2 in box_str_2[len2:(len2 + len(text))]:
                box2 = box2.split(' ')
                x, y, w, h = int(box2[1]), int(box2[2]), int(box2[3]), int(box2[4])
                cv2.rectangle(img2, (x - 1, i_h - y + 1), (w + 1, i_h - h - 2), (0, 255, 0), 1)
            len1 += len(text)
            len2 += len(text)
            same += len(text)

    if same != 0:
        too_different = True if differ/same > 2 else False
    else:
        too_different = True
    return img1, img2, too_different


def get_pixel_diff(img1: Image, img2: Image, size: tuple) -> tuple:
    """
        OLD VERSION
        Compares two images by pixels. Was done first and is left here just as an alternative.
        Highlights differences by making different pixels red
        Better not to use with low-quality pics
    """
    img1_L = img1.convert("L")
    img2_L = img2.convert("L")
    raw1 = img1_L.getdata()
    raw2 = img2_L.getdata()

    # Subtracting pixels
    diff_pix = numpy.subtract(raw1, raw2)

    # Creating a new image with only the different pixels
    img_diff = Image.new("L", size)
    img_diff.putdata(diff_pix)

    # Calculating box coordinates
    c = 0
    for i in img_diff.getdata():
        if i > 15 or i < -10:
            x10 = c % size[0]
            y10 = c // size[0]

            # Drawing the box
            xsub = 2
            ysub = 2
            x1, y1, x2, y2 = max(0, x10 - xsub), max(0, y10 - ysub), x10, y10
            Drawer = ImageDraw.Draw(img2)
            Drawer.rectangle((x1, y1, x1, y1), outline="red", width=1)
        c += 1

    return numpy.array(img1), numpy.array(img2)
