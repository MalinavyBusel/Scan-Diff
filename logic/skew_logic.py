""" Import required modules"""
import os
import imghdr
import optparse
import numpy as np
import matplotlib.pyplot as plt

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from skimage import io
from skimage.transform import rotate
from skimage.feature import canny
from skimage.color import rgb2gray, rgba2rgb
from skimage.transform import hough_line, hough_line_peaks


class Deskew:

    def __init__(self, input_file, display_image, output_file, r_angle):

        self.input_file = input_file
        self.display_image = display_image
        self.output_file = output_file
        self.r_angle = r_angle
        self.skew_obj = SkewDetect(self.input_file)

    def deskew(self):

        img = io.imread(self.input_file)
        res = self.skew_obj.process_single_file()
        angle = res['Estimated Angle']

        if angle >= 0 and angle <= 90:
            rot_angle = angle - 90 + self.r_angle
        if angle >= -45 and angle < 0:
            rot_angle = angle - 90 + self.r_angle
        if angle >= -90 and angle < -45:
            rot_angle = 90 + angle + self.r_angle

        rotated = rotate(img, rot_angle, resize=True)

        if self.display_image:
            self.display(rotated)

        if self.output_file:
            self.saveImage(rotated*255)

    def saveImage(self, img):
        path = self.skew_obj.check_path(self.output_file)
        io.imsave(path, img.astype(np.uint8))

    def display(self, img):

        plt.imshow(img)
        plt.show()

    def run(self):

        if self.input_file:
            self.deskew()

class SkewDetect:

    piby4 = np.pi / 4

    def __init__(
        self,
        input_file=None,
        batch_path=None,
        output_file=None,
        sigma=3.0,
        display_output=None,
        num_peaks=20,
        plot_hough=None
    ):

        self.sigma = sigma
        self.input_file = input_file
        self.batch_path = batch_path
        self.output_file = output_file
        self.display_output = display_output
        self.num_peaks = num_peaks
        self.plot_hough = plot_hough

    def write_to_file(self, wfile, data):

        for d in data:
            wfile.write(d + ': ' + str(data[d]) + '\n')
        wfile.write('\n')

    def get_max_freq_elem(self, arr):

        max_arr = []
        freqs = {}
        for i in arr:
            if i in freqs:
                freqs[i] += 1
            else:
                freqs[i] = 1

        sorted_keys = sorted(freqs, key=freqs.get, reverse=True)
        max_freq = freqs[sorted_keys[0]]

        for k in sorted_keys:
            if freqs[k] == max_freq:
                max_arr.append(k)

        return max_arr

    def display_hough(self, h, a, d):

        plt.imshow(
            np.log(1 + h),
            extent=[np.rad2deg(a[-1]), np.rad2deg(a[0]), d[-1], d[0]],
            cmap=plt.cm.gray,
            aspect=1.0 / 90)
        plt.show()

    def compare_sum(self, value):
        if value >= 44 and value <= 46:
            return True
        else:
            return False

    def display(self, data):

        for i in data:
            print(i + ": " + str(data[i]))

    def calculate_deviation(self, angle):

        angle_in_degrees = np.abs(angle)
        deviation = np.abs(SkewDetect.piby4 - angle_in_degrees)

        return deviation

    def run(self):

        if self.display_output:
            if self.display_output.lower() == 'yes':
                self.display_output = True
            else:
                self.display_output = False

        if self.plot_hough:
            if self.plot_hough.lower() == 'yes':
                self.plot_hough = True
            else:
                self.plot_hough = False

        if self.input_file is None:
            if self.batch_path:
                self.batch_process()
            else:
                print("Invalid input, nothing to process.")
        else:
            self.process_single_file()

    def check_path(self, path):

        if os.path.isabs(path):
            full_path = path
        else:
            full_path = os.getcwd() + '/' + str(path)
        return full_path

    def process_single_file(self):

        file_path = self.check_path(self.input_file)
        res = self.determine_skew(file_path)

        if self.output_file:
            output_path = self.check_path(self.output_file)
            wfile = open(output_path, 'w')
            self.write_to_file(wfile, res)
            wfile.close()

        return res

    def batch_process(self):

        wfile = None

        if self.batch_path == '.':
            self.batch_path = ''

        abs_path = self.check_path(self.batch_path)
        files = os.listdir(abs_path)

        if self.output_file:
            out_path = self.check_path(self.output_file)
            wfile = open(file_path, 'w')

        for f in files:
            file_path = abs_path + '/' + f
            if os.path.isdir(file_path):
                continue
            if imghdr.what(file_path):
                res = self.determine_skew(file_path)
                if wfile:
                    self.write_to_file(wfile, res)
        if wfile:
            wfile.close()

    def determine_skew(self, img_file):

        img = io.imread(img_file, as_grey=True)
        edges = canny(img, sigma=self.sigma)
        h, a, d = hough_line(edges)
        _, ap, _ = hough_line_peaks(h, a, d, num_peaks=self.num_peaks)

        if len(ap) == 0:
            return {"Image File": img_file, "Message": "Bad Quality"}

        absolute_deviations = [self.calculate_deviation(k) for k in ap]
        average_deviation = np.mean(np.rad2deg(absolute_deviations))
        ap_deg = [np.rad2deg(x) for x in ap]

        bin_0_45 = []
        bin_45_90 = []
        bin_0_45n = []
        bin_45_90n = []

        for ang in ap_deg:

            deviation_sum = int(90 - ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_45_90.append(ang)
                continue

            deviation_sum = int(ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_0_45.append(ang)
                continue

            deviation_sum = int(-ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_0_45n.append(ang)
                continue

            deviation_sum = int(90 + ang + average_deviation)
            if self.compare_sum(deviation_sum):
                bin_45_90n.append(ang)

        angles = [bin_0_45, bin_45_90, bin_0_45n, bin_45_90n]
        lmax = 0

        for j in range(len(angles)):
            l = len(angles[j])
            if l > lmax:
                lmax = l
                maxi = j

        if lmax:
            ans_arr = self.get_max_freq_elem(angles[maxi])
            ans_res = np.mean(ans_arr)

        else:
            ans_arr = self.get_max_freq_elem(ap_deg)
            ans_res = np.mean(ans_arr)

        data = {
            "Image File": img_file,
            "Average Deviation from pi/4": average_deviation,
            "Estimated Angle": ans_res,
            "Angle bins": angles}

        if self.display_output:
            self.display(data)

        if self.plot_hough:
            self.display_hough(h, a, d)
        return data


def _get_max_freq_elem(peaks: List[int]) -> List[float]:
    freqs: Dict[float, int] = {}
    for peak in peaks:
        if peak in freqs:
            freqs[peak] += 1
        else:
            freqs[peak] = 1

    sorted_keys = sorted(freqs.keys(), key=freqs.get, reverse=True)  # type: ignore
    max_freq = freqs[sorted_keys[0]]

    max_arr = []
    for sorted_key in sorted_keys:
        if freqs[sorted_key] == max_freq:
            max_arr.append(sorted_key)

    return max_arr


def _compare_sum(value: float) -> bool:
    return 44 <= value <= 46


def _calculate_deviation(angle: float) -> np.float64:

    angle_in_degrees = np.abs(angle)
    deviation: np.float64 = np.abs(np.pi / 4 - angle_in_degrees)

    return deviation


if TYPE_CHECKING:
    ImageType = np.ndarray[np.uint8, Any]
    ImageTypeUint64 = np.ndarray[np.uint8, Any]
    ImageTypeFloat64 = np.ndarray[np.uint8, Any]
else:
    ImageType = np.ndarray
    ImageTypeUint64 = np.ndarray
    ImageTypeFloat64 = np.ndarray


def determine_skew_dev(
    image: ImageType,
    sigma: float = 3.0,
    num_peaks: int = 20,
    num_angles: int = 180,
    angle_pm_90: bool = False,
) -> Tuple[
    Optional[np.float64],
    List[List[np.float64]],
    np.float64,
    Tuple[ImageTypeUint64, List[List[np.float64]], ImageTypeFloat64],
]:
    """Calculate skew angle."""
    imagergb = rgba2rgb(image) if len(image.shape) == 3 and image.shape[2] == 4 else image
    img = rgb2gray(imagergb) if len(imagergb.shape) == 3 else imagergb
    edges = canny(img, sigma=sigma)
    out, angles, distances = hough_line(edges, np.linspace(-np.pi / 2, np.pi / 2, num_angles, endpoint=False))
    hough_line_out = (out, angles, distances)

    _, angles_peaks, _ = hough_line_peaks(
        out, angles, distances, num_peaks=num_peaks, threshold=0.05 * np.max(out)
    )

    absolute_deviations = [_calculate_deviation(k) for k in angles_peaks]
    average_deviation: np.float64 = np.mean(np.rad2deg(absolute_deviations))
    angles_peaks_degree = [np.rad2deg(x) for x in angles_peaks]

    bin_0_45 = []
    bin_45_90 = []
    bin_0_45n = []
    bin_45_90n = []

    for angle in angles_peaks_degree:

        deviation_sum = int(90 - angle + average_deviation)
        if _compare_sum(deviation_sum):
            bin_45_90.append(angle)
            continue

        deviation_sum = int(angle + average_deviation)
        if _compare_sum(deviation_sum):
            bin_0_45.append(angle)
            continue

        deviation_sum = int(-angle + average_deviation)
        if _compare_sum(deviation_sum):
            bin_0_45n.append(angle)
            continue

        deviation_sum = int(90 + angle + average_deviation)
        if _compare_sum(deviation_sum):
            bin_45_90n.append(angle)

    angles = [bin_0_45, bin_45_90, bin_0_45n, bin_45_90n]
    nb_angles_max = 0
    max_angle_index = -1
    for angle_index, angle in enumerate(angles):
        nb_angles = len(angle)
        if nb_angles > nb_angles_max:
            nb_angles_max = nb_angles
            max_angle_index = angle_index

    if nb_angles_max:
        ans_arr = _get_max_freq_elem(angles[max_angle_index])
        angle = np.mean(ans_arr)
    elif angles_peaks_degree:
        ans_arr = _get_max_freq_elem(angles_peaks_degree)
        angle = np.mean(ans_arr)
    else:
        return None, angles, average_deviation, hough_line_out

    if not angle_pm_90:
        rot_angle = (angle + 45) % 90 - 45
    else:
        rot_angle = (angle + 90) % 180 - 90

    return rot_angle, angles, average_deviation, hough_line_out


def determine_skew(
    image: ImageType,
    sigma: float = 3.0,
    num_peaks: int = 20,
    num_angles: int = 180,
    angle_pm_90: bool = False,
) -> Optional[np.float64]:
    """
    Calculate skew angle.

    Return None if no skew will be found
    """
    angle, _, _, _ = determine_skew_dev(
        image, sigma=sigma, num_peaks=num_peaks, num_angles=num_angles, angle_pm_90=angle_pm_90
    )
    return angle

