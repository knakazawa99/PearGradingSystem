import pickle
from itertools import chain

import cv2
from sklearn.decomposition import PCA

from pear_shape.contour import extract_contour
from pear_shape.feature import calculate_efd, calculate_width_ratio


PCA_MODEL_PATH = 'models/pcamodel.sav'
SVM_MODEL_PATH = 'models/svm.sav'

SHAPE_TYPES = {
    0: 'short',
    1: 'fat',
    2: 'other'
}


def main():
    image = cv2.imread('images/02_1.png')
    contour = extract_contour(image)
    coefficient = calculate_efd(contour=contour, order=10)
    ratio = calculate_width_ratio(contour)
    features = list(chain.from_iterable([coefficient, ratio.get_list()]))
    with open(PCA_MODEL_PATH, 'rb') as f:
        pca = pickle.load(f)
    with open(SVM_MODEL_PATH, 'rb') as f:
        svm = pickle.load(f)
    features = pca.transform([features])
    result = svm.predict(features)
    print(SHAPE_TYPES[result[0]])


if __name__ == '__main__':
    main()

