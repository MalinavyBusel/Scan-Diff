import tempfile
import numpy
import imutils
import cv2

from PIL import Image, ImageFilter, ImageDraw

from logic.angle_getter import get_rotation_angle


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

    b_w, b_h = base.size
    h_w, h_h = compared.size
    # выбрал минимальный размер, чтобы качество не сильно портилось,
    # да и сравнивать проще
    im_size = (min(b_w, h_w), min(b_h, h_h))
    base = base.resize(im_size, Image.LANCZOS)
    compared = compared.resize(im_size, Image.LANCZOS)

    return get_diff(base, compared, im_size)


def get_pixel_diff(data1: Image, data2: Image, size: tuple) -> Image:
    data3 = data1.convert("L")
    data4 = data2.convert("L")
    raw1 = data3.getdata()
    raw2 = data4.getdata()

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
            Drawer = ImageDraw.Draw(data2)
            Drawer.rectangle((x1, y1, x1, y1), outline="red", width=1)
        c += 1

    return data2
