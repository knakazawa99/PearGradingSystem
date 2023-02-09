import copy

import cv2
import numpy as np




image = cv2.imread('pear_grade_inference_client/images/01_1.jpg') 
image_c = copy.deepcopy(image)
ret, encoded = cv2.imencode(".jpg", image_c, (cv2.IMWRITE_JPEG_QUALITY, 10))
# encoded_image = RLE_numpy2(image_c)
# decoded_image = rle_decode(encoded_image, encoded_image.shape)


print(encoded_image)