# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
from tracemalloc import start
from tritonclient.utils import *
# import tritonclient.grpc as grpcclient
import tritonclient.http as httpclient

import numpy as np
import cv2


import time

model_name = "pear_evaluator"



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
with httpclient.InferenceServerClient("133.35.129.10:8000") as client:

    image = cv2.imread('pear_grade_inference_client/images/01_1.png')

    inputs = [
        httpclient.InferInput("IMAGE", image.shape,
                              np_to_triton_dtype(image.dtype)),
    ]

    inputs[0].set_data_from_numpy(image)

    outputs = [
        # httpclient.InferRequestedOutput("SEGMENTATION_RESULT"),
        httpclient.InferRequestedOutput("DETECTION_RESULT"),
        # httpclient.InferRequestedOutput("SHAPE_RESULT"),
    ]
    start_request = time.perf_counter()
    response = client.infer(model_name,
                            inputs,
                            request_id=str(1),
                            outputs=outputs)
    request_time = time.perf_counter() - start_request
    print(f'request time {request_time} s')
    result = response.get_response()
    # print(response.as_numpy("SEGMENTATION_RESULT"))
    # np.save('segmented_pear.npy', response.as_numpy("SEGMENTATION_RESULT"))
    
    print(response.as_numpy("DETECTION_RESULT"))
    # print(response.as_numpy("SHAPE_RESULT"))
    coordinates = response.as_numpy("DETECTION_RESULT")
    np.save('./a', response.as_numpy('DETECTION_RESULT'))
    for coordinate in coordinates:
        image = labeling(image, coordinate)
    cv2.imwrite('./result.jpg', image)

# print(f'{time.perf_counter() - start}s')

