from typing import List

import numpy as np
from dataclasses import dataclass

from numpy import ndarray
import pyefd as efd


@dataclass
class WidthRatio:
    r1: float = 0.0
    r2: float = 0.0
    r3: float = 0.0
    r4: float = 0.0
    r5: float = 0.0
    r6: float = 0.0
    r7: float = 0.0
    r8: float = 0.0
    r9: float = 0.0

    def get_list(self) -> List[float]:
        result = []
        for i in range(1, 10):
            result.append(self.__getattribute__(f'r{i}'))
        return result


@dataclass
class WidthInfo:
    w0: List[int] = None
    w1: List[int] = None
    w2: List[int] = None
    w3: List[int] = None
    w4: List[int] = None
    w5: List[int] = None
    w6: List[int] = None
    w7: List[int] = None
    w8: List[int] = None
    w9: List[int] = None
    w10: List[int] = None


def calculate_efd(contour: ndarray, order: int) -> List[float]:
    coefficients = efd.elliptic_fourier_descriptors(np.squeeze(contour), order=order, normalize=True)
    return coefficients.flatten()[3:]


def calculate_width_ratio(contour: ndarray) -> WidthRatio:
    x_points = contour[:, 0, 0]
    y_points = contour[:, 0, 1]
    widths = []
    widths_append = widths.append
    for index in range(min(y_points), max(y_points)):
        x_indexes_same_on_y = np.where(contour[:, 0, 1] == index)[0]
        if x_indexes_same_on_y.size == 0 or x_indexes_same_on_y.size > 2:
            # 対象のy座標と同じy座標を持つx座標が必ず2個である前提
            continue
        width = abs(x_points[x_indexes_same_on_y[0]] - x_points[x_indexes_same_on_y[1]])
        if width >= 200 or index > 0:
            widths_append([width, index])
    widths = np.array(widths)
    width_info = WidthInfo()
    width_ratio = WidthRatio()

    width_info.w0 = widths[np.argmax(widths[:, 0], axis=0)]
    width_info.w10 = widths[0]

    min_max_distance = width_info.w0[1] - width_info.w10[1]
    for index in range(1, 10):
        value = widths[np.where(widths[:, 1] == width_info.w0[1] - int(min_max_distance * (index / 10)))[0][0]]
        width_info.__setattr__(f'w{index}', value)

    for index in range(1, 10):
        width_ratio.__setattr__(f'r{index}', (width_info.__getattribute__(f'w{index}')[0] / width_info.w0[0]))
    return width_ratio