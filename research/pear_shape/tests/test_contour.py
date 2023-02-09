import cv2
from numpy import ndarray
from pear_shape.contour import extract_contour


def test_extract_contour():
    image = cv2.imread('images/01_1.png')
    contour = extract_contour(image)
    assert isinstance(contour, ndarray)
