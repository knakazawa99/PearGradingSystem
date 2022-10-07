



import numpy as np
import cv2
import requests


import time

model_name = "pear_evaluator"
shape = [4]



def labeling(image, coordinates):
    """
    ラベルをつける対象の画像に対して，バウンディングボックスの作成及びラベルの文字付与を行う
    Args:
        image(ndarray): 対象の画像
        coordinates(Coordinate): バウンディングボックスのオブジェクト
        class_index(int): 対象領域の汚損要因のクラスインデックス
    Returns:
        labeled_image(ndarray): 対象画像にバウンディングﾎボックス及びラベルをつけた後の画像
    """
    # ラベル付けの対象位置を定義
    upper_left = (int(coordinates[0]), int(coordinates[1]))
    under_right = (int(coordinates[2]), int(coordinates[3]))

    # ラベル付け対象の位置にバウンディングボックスを生成
    labeled_image = cv2.rectangle(image, upper_left, under_right, (255, 255, 255))
    # バウンディングボックスに対してラベルの文字を付与
    labeled_image = cv2.putText(
        labeled_image,
        str(coordinates[4]),
        (int(coordinates[0]), int(coordinates[1] - 5)),
        cv2.FONT_HERSHEY_COMPLEX,
        0.7,
        (0, 0, 0),
        1
    )
    return labeled_image

start = time.perf_counter()
api_url = 'http://133.35.129.10:8000/image'
image = cv2.imread('pear_grade_inference_client/images/01_1.jpg')
data = {
  'image': image.tolist()
}
response = requests.post(api_url, json=data)
print(response)
# cv2.imwrite('./result.jpg', image)

print(f'{time.perf_counter() - start}s')

