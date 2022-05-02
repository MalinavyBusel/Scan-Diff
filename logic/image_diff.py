import tempfile
import re
import numpy
import cv2
import pytesseract
import diff_match_patch

from PIL import Image, ImageFilter, ImageDraw

from logic.angle_getter import get_rotation_angle
from logic.config import settings


pytesseract.pytesseract.tesseract_cmd = settings['TESSERACT']


def create_image(input_file: str) -> Image:
    image = Image.open(input_file)
    return image


def create_tempfile(input_file: 'FileStorage') -> str:
    suff = input_file.filename.split('.')[-1]
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suff)
    temp_filename = temp_file.name
    input_file.save(temp_filename)
    return temp_filename


def process_diff(base: Image, compared: Image) -> tuple:
    rotate_base = get_rotation_angle(base)
    rotate_compared = get_rotation_angle(compared)

    base = base.rotate(rotate_base)
    compared = compared.rotate(rotate_compared)

    b_w, b_h = base.size
    h_w, h_h = compared.size
    # выбрал минимальный размер, чтобы качество не сильно портилось,
    # да и сравнивать проще
    im_size = (min(b_w, h_w), min(b_h, h_h))
    base = base.resize(im_size, Image.LANCZOS)
    compared = compared.resize(im_size, Image.LANCZOS)

    return get_tesseract_diff(base, compared, im_size) # TODO добавить создание файлов


def get_pixel_diff(img1: Image, img2: Image, size: tuple) -> tuple:
    img1_L  = img1.convert("L")
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

    return img1, img2


def get_tesseract_diff(img1: Image, img2: Image, size: tuple) -> tuple:
    img1 = numpy.array(img1)
    img2 = numpy.array(img2)
    i_h = size[1]
    i_w = size[0]

    data_str_1 = pytesseract.image_to_string(img1)
    data_str_1 = re.sub('[ \t\n\r]', '', data_str_1)

    box_str_1 = pytesseract.image_to_boxes(img1).splitlines()

    data_str_2 = pytesseract.image_to_string(img2)
    data_str_2 = re.sub('[ \t\n\r]', '', data_str_2)

    box_str_2 = pytesseract.image_to_boxes(img2).splitlines()
    diff_obj = diff_match_patch.diff_match_patch()
    diffs = diff_obj.diff_main(text1=data_str_1, text2=data_str_2)

    # -1 - встречается только в изображении 1, 1 - только в изображении 2
    len1, len2 = 0, 0
    for text_part in diffs:
        text = text_part[1]

        if text_part[0] == 1:
            for box2 in box_str_2[len2:(len2 + len(text))]:
                box2 = box2.split(' ')
                x, y, w, h = int(box2[1]), int(box2[2]), int(box2[3]), int(box2[4])
                cv2.rectangle(img2, (x, i_h - y), (w, i_h - h), (0, 0, 255), 1)
            len2 += len(text)

        elif text_part[0] == -1:
            for box1 in box_str_1[len1:(len1 + len(text))]:
                box1 = box1.split(' ')
                x, y, w, h = int(box1[1]), int(box1[2]), int(box1[3]), int(box1[4])
                cv2.rectangle(img1, (x, i_h - y), (w, i_h - h), (0, 0, 255), 1)
            len1 += len(text)

        elif not text_part[0]:
            len1 += len(text)
            len2 += len(text)

    return img1, img2
