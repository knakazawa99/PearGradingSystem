
import cv2
from numpy import ndarray
from pear_shape.contour import extract_contour
from pear_shape.feature import calculate_width_ratio, WidthRatio, calculate_efd


def test_calculate_efd():
    image = cv2.imread('images/01_1.png')
    contour = extract_contour(image)
    efd = calculate_efd(contour, 10)
    assert isinstance(efd, ndarray)


def test_calculate_width_ratio():
    image = cv2.imread('images/01_1.png')
    contour = extract_contour(image)
    wr = calculate_width_ratio(contour)
    assert isinstance(wr, WidthRatio)
    for i in range(1, 10):
        print(wr.__getattribute__(f'r{i}'))
