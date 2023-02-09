import cv2
import numpy as np
from numpy import ndarray


def extract_contour(image: ndarray):
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    img_blur = cv2.blur(img_hsv, (10, 10))
    img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
    ret, img_th = cv2.threshold(img_gray, 0, 255, cv2.THRESH_OTSU)
    kernel = np.ones((10, 10), np.uint8)
    closing = cv2.morphologyEx(img_th, cv2.MORPH_CLOSE, kernel)
    print(type(closing))
    print(closing.shape)
    print(closing.dtype)
    print(np.unique(closing))
    contours, _ = cv2.findContours(closing, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    max_cnt = max(contours, key=lambda x: cv2.contourArea(x))

    # 重心に原点を移動
    moment = cv2.moments(max_cnt)
    cx = int(moment['m10'] / moment['m00'])
    cy = int(moment['m01'] / moment['m00'])
    max_cnt[:, :, 0] -= cx
    max_cnt[:, :, 1] -= cy

    return max_cnt
