from copy import deepcopy
import math
from typing import NewType, List, Tuple

import cv2
import numpy as np

from grading.objects.pear import Pear, PearSide, BoundingBox
from grading.objects.deterioration import DeteriorationCategory, Deterioration, DeteriorationInPear, DeteriorationAreaRate

GradingScore = NewType('GradingScore', int)
AreaInBorder = NewType('AreaInBorder', int)

EXCELENT_POINT = 1
BRILLIANT_POINT = 3
GOOD_POINT = 5
MUZI_POINT = 7

class Evaluate:
    @classmethod
    def grading(cls, pear: Pear):
        deterioration_in_pear, area_in_border = cls.grading_count(pear)

        grade_point = 0
        excelent_count = 0
        brilliant_count = 0
        good_count = 0

        alternaria_area, alternaria_count = (deterioration_in_pear.alternaria.bbox_area * DeteriorationAreaRate.ALTERNALIA.value) / area_in_border , deterioration_in_pear.alternaria.bbox_count
        if alternaria_count > 0 and alternaria_count <= 1:
            grade_point += EXCELENT_POINT
            excelent_count += 1
        elif (alternaria_count > 1 and alternaria_count <= 3) and alternaria_area <= 0.3:
            grade_point += BRILLIANT_POINT
            brilliant_count += 1
        elif (alternaria_area > 0.3 and alternaria_area < 0.5) or alternaria_count > 3:
            grade_point += GOOD_POINT
            good_count += 1
        elif alternaria_area >= 0.5 or alternaria_count > 3:
            grade_point += MUZI_POINT
        
        chemical_area = (deterioration_in_pear.chemical.bbox_area * DeteriorationAreaRate.CHEMICAL.value) / area_in_border
        # if chemical_area > 0 and chemical_area <= 0.1:
        #     grade_point += EXCELENT_POINT
        #     excelent_count += 1
        # elif chemical_area > 0.1 and chemical_area <= 0.3:
        #     grade_point += BRILLIANT_POINT
        #     brilliant_count += 1
        # elif chemical_area > 0.3 and chemical_area <= 0.5:
        #     grade_point += GOOD_POINT
        #     good_count += 1

        plane_area = (deterioration_in_pear.plane.bbox_area * DeteriorationAreaRate.PLANE.value) / area_in_border
        # if plane_area > 0 and plane_area <= 0.1:
        #     grade_point += EXCELENT_POINT
        #     excelent_count += 1
        # elif plane_area > 0.1 and plane_area <= 0.3:
        #     grade_point += BRILLIANT_POINT
        #     brilliant_count += 1
        # elif plane_area > 0.3 and plane_area <= 0.5:
        #     grade_point += GOOD_POINT
        #     good_count += 1
        plane_area += chemical_area
        if plane_area > 0 and plane_area <= 0.1:
            grade_point += EXCELENT_POINT
            excelent_count += 1
        elif plane_area > 0.1 and plane_area <= 0.3:
            grade_point += BRILLIANT_POINT
            brilliant_count += 1
        elif plane_area > 0.3 and plane_area <= 0.5:
            grade_point += GOOD_POINT
            good_count += 1
        elif plane_area > 0.5:
            grade_point += MUZI_POINT

        injury_area = (deterioration_in_pear.injury.bbox_area * DeteriorationAreaRate.INJURY.value) / area_in_border
        # if injury_area > 0 and injury_area <= 0.1:
        #     grade_point += EXCELENT_POINT
        #     excelent_count += 1
        # elif injury_area > 0.1 and injury_area <= 0.3:
        #     grade_point += BRILLIANT_POINT
        #     brilliant_count += 1
        # elif injury_area > 0.3 and injury_area <= 0.5:
        #     grade_point += GOOD_POINT
        #     good_count += 1

        speckle_area = (deterioration_in_pear.speckle.bbox_area * DeteriorationAreaRate.SPECKLE.value) / area_in_border
        speckle_area += injury_area
        if speckle_area > 0 and speckle_area <= 0.1:
            grade_point += EXCELENT_POINT
            excelent_count += 1
        elif speckle_area > 0.1 and speckle_area <= 0.3:
            grade_point += BRILLIANT_POINT
            brilliant_count += 1
        elif speckle_area > 0.3 and speckle_area <= 0.5:
            grade_point += GOOD_POINT
            good_count += 1
        elif speckle_area > 0.5:
            grade_point += MUZI_POINT
        deterioration_in_pear.alternaria.bbox_area = alternaria_area
        deterioration_in_pear.chemical.bbox_area = chemical_area
        deterioration_in_pear.injury.bbox_area = injury_area
        deterioration_in_pear.plane.bbox_area = plane_area
        deterioration_in_pear.speckle.bbox_area = speckle_area
        print(f'pear id: {pear.pear_id}')
        print(f'grade point: {grade_point}')
        return grade_point, {'excelent_count': excelent_count, 'brilliant_count': brilliant_count, 'good_count': good_count}, deterioration_in_pear
    
    @classmethod
    def grading_count(cls, pear: Pear) -> Tuple[DeteriorationInPear, AreaInBorder]:
        deterioration_in_pear = DeteriorationInPear(
            alternaria=Deterioration(bbox_area=0, bbox_count=0, category=DeteriorationCategory.ALTERNALIA),
            injury=Deterioration(bbox_area=0, bbox_count=0, category=DeteriorationCategory.INJURY),
            chemical=Deterioration(bbox_area=0, bbox_count=0, category=DeteriorationCategory.CHEMICAL),
            plane=Deterioration(bbox_area=0, bbox_count=0, category=DeteriorationCategory.PLANE),
            speckle=Deterioration(bbox_area=0, bbox_count=0, category=DeteriorationCategory.SPECKLE),
        )
        area_in_border = AreaInBorder(0)
        for pear_side in pear.pear_sides:
            # border_top, border_bottom = cls.get_target_coordinates(pear_side)
            contours = cls.get_contour(pear_side)
            border_bbox = cls.get_border_bbox(contours)
            # for contour in contours:
            #     if contour[0][0] < border_bbox.left:
            #         contour[0][0] = border_bbox.left
            #     if contour[0][0] > border_bbox.right:
            #         contour[0][0] = border_bbox.right
            #     if contour[0][1] < border_bbox.top:
            #         contour[0][1] = border_bbox.top
            #     if contour[0][1] > border_bbox.bottom:
            #         contour[0][1] - border_bbox.bottom
                
            area_in_border += cv2.contourArea(contours)
            for bbox in pear_side.bboxes:
                if bbox.bottom < border_bbox.top or bbox.top > border_bbox.bottom:
                    continue
                elif bbox.top > border_bbox.top and (bbox.bottom > border_bbox.top and bbox.bottom < border_bbox.bottom):
                    bbox.top = border_bbox.top
                elif (bbox.top > border_bbox.top and bbox.top < border_bbox.bottom) and bbox.bottom > border_bbox.bottom:
                    bbox.bottom = border_bbox.bottom
                
                if bbox.category == 1:
                    deterioration_in_pear.alternaria.bbox_area += bbox.area
                    deterioration_in_pear.alternaria.bbox_count += 1
                elif bbox.category == 2:
                    deterioration_in_pear.injury.bbox_area += bbox.area
                    deterioration_in_pear.injury.bbox_count += 1
                elif bbox.category == 3:
                    deterioration_in_pear.speckle.bbox_area += bbox.area
                    deterioration_in_pear.speckle.bbox_count += 1
                elif bbox.category == 4:
                    deterioration_in_pear.chemical.bbox_area += bbox.area
                    deterioration_in_pear.chemical.bbox_count += 1
                elif bbox.category == 5:
                    deterioration_in_pear.plane.bbox_area += bbox.area
                    deterioration_in_pear.plane.bbox_count += 1
        return deterioration_in_pear, area_in_border
    
    @staticmethod
    def get_border_bbox(contours) -> BoundingBox:
        x_min, y_min, width, height = cv2.boundingRect(contours)
        x_max, y_max = x_min + width, y_min + height
        x_length, y_length = x_max - x_min, y_max  - y_min

        _, y_center = x_min + math.floor(x_length / 2), y_min + math.floor(y_length / 2)
        radius = math.floor(y_length / 2)
        mask_target_length = int(radius * math.floor(np.sqrt(2)) / 2)
        top, bottom = y_center - mask_target_length, y_center + mask_target_length
        # left, right = x_center - mask_target_length, x_center + mask_target_length
        return BoundingBox(
            left=x_min, top=y_min, right=x_max, bottom=y_max, category=10
        )

    @staticmethod
    def get_contour(pear_side: PearSide):
        image = cv2.imread(f"./datasets/images/{pear_side.file_name.split('.')[0]}.bmp")
        image_blur = cv2.GaussianBlur(image, (19, 19), 0)
        image_saturation = cv2.cvtColor(image_blur, cv2.COLOR_BGR2HLS)[:, :, 2].astype(np.uint8)
        _, binary_image = cv2.threshold(image_saturation, 0, 255, cv2.THRESH_OTSU)
        contours, hierarchy = cv2.findContours(
            image=binary_image, 
            mode=cv2.RETR_EXTERNAL, 
            method=cv2.CHAIN_APPROX_SIMPLE
        )
        return max(contours, key=lambda x: cv2.contourArea(x))

