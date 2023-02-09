import json

import pandas as pd

from grading.evaluate.evaluate import Evaluate
from grading.objects.pear import BoundingBox, PearSide, Pear


def main():
    with open('./datasets/annotations/annotation_for_grading.json', 'r') as f:
        annotations = json.load(f)
    # count = 0
    # for annotation_pear in annotations['pears']:
    #     if annotation_pear['shape_type_id'] == 10 or annotation_pear['grading_id'] == 0 or annotation_pear['graiding_id_deterioration'] == 0:
    #         del annotations['pears'][count]
    #     else:
    #         count +=1
    
    pear_grade_information = []
    correct_count = 0
    for annotation_pear in annotations['pears']:
        pear = Pear(
            pear_id=annotation_pear['id'],
            shape_type_id=annotation_pear['shape_type_id'],
            graiding_id_deterioration=annotation_pear['graiding_id_deterioration'],
            pear_sides=[]
        )
        for pear_image in annotation_pear['images']:
            image_id = pear_image['id']
            pear_side = PearSide(file_name=pear_image['file_name'], bboxes=[])
            for annotation in annotations['annotations']:
                if annotation['image_id'] == image_id:
                    bbox  = BoundingBox(
                        left=annotation['bbox'][0],
                        top=annotation['bbox'][1],
                        right=annotation['bbox'][0]+annotation['bbox'][2],
                        bottom=annotation['bbox'][1]+annotation['bbox'][3],
                        category=annotation['category_id']
                    )
                    pear_side.bboxes.append(bbox)
            pear.pear_sides.append(pear_side)
        try:
            pear_grade_point, count, deterioration_in_pear = Evaluate.grading(pear)
            pear_grade_information.append(
                [pear.pear_id, pear.graiding_id_deterioration, pear_grade_point, count['excelent_count'], count['brilliant_count'], count['good_count']]
            )
            correct = False
            if pear_grade_point < 1:
                if pear.graiding_id_deterioration == 1:
                    correct = True
            elif pear_grade_point <= 3:
                if pear.graiding_id_deterioration == 2:
                    correct = True
            elif pear_grade_point <= 5:
                if pear.graiding_id_deterioration == 3:
                    correct = True
            else:
                if pear.graiding_id_deterioration > 3:
                    correct = True
            if correct:
                correct_count += 1
            # pear_grade_information.append([
            #     pear.pear_id, 
            #     pear.graiding_id_deterioration,
            #     deterioration_in_pear.alternaria.bbox_area, 
            #     deterioration_in_pear.alternaria.bbox_count,
            #     deterioration_in_pear.injury.bbox_area, 
            #     deterioration_in_pear.injury.bbox_count,
            #     deterioration_in_pear.speckle.bbox_area, 
            #     deterioration_in_pear.speckle.bbox_count,
            #     deterioration_in_pear.chemical.bbox_area, 
            #     deterioration_in_pear.chemical.bbox_count,
            #     deterioration_in_pear.plane.bbox_area, 
            #     deterioration_in_pear.plane.bbox_count,
            # ])
        except Exception as e:
            print(e)
            continue
    print(f"annotation length: {len(annotations['pears'])}")
    print(correct_count / len(annotations['pears']))
    pear_df = pd.DataFrame(data=pear_grade_information, columns=['pear_id', 'grading_id', 'grade_point', 'excelent_count', 'brilliant_count', 'good_count'])
        # pear_df = pd.DataFrame(
        #     data=pear_grade_information, 
        #     columns=['pear_id', 'grading_id', 'alternaria_area', 'alternaria_count', 'injury_area', 'injury_count', 'speckle_area', 'speckle_count',
        #             'chemical_area', 'chemical_count', 'plane_area', 'plane_count'
        #     ]
        # )
    # pear_df.to_csv('./result.csv')
    # print(pear_grade)
        # break
        
if __name__ == '__main__':
    main()