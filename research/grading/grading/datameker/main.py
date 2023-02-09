"""
JAによる形状判定と等級判定の結果から作成した annotation_ja.jsonと
物体検出に利用しているtrain_annotations_multi.json, validation_annotations_multi.jsonを統合した
annotation.jsonを作成するためのプログラム
"""
import json


ANNOTATION_DIR = './datasets/annotations'

def main():
    with open(f"{ANNOTATION_DIR}/annotation_ja.json", 'r') as f:
        annotation = json.load(f)
    with open(f'{ANNOTATION_DIR}/train_annotations_multi.json', 'r') as f:
        train_annotations = json.load(f)
    with open(f'{ANNOTATION_DIR}/validation_annotations_multi.json', 'r') as f:
        valid_annotations = json.load(f)
    
    annotation['categories'] = train_annotations['categories']
    annotation_ids = []
    for pear in annotation['pears']:
        pear_id = int(str(pear['id'])[6:])
        annotation_ids.append(pear_id)
        keys = []
        if pear_id < 10:
            pear_id = f'0{str(pear_id)}'
        for image in train_annotations['images']:
            if image['file_name'].startswith(f'{pear_id}_'):
                keys.append(image)
        for image in valid_annotations['images']:
            if image['file_name'].startswith(f'{pear_id}_'):
                keys.append(image)
        pear['images'] = keys

    # images = dict()
    # for train_annotation in train_annotations['images']:
    #     pear_id = train_annotation['file_name'].split('_')[0]
    #     if pear_id in annotation_ids:
    #         continue
    #     if pear_id in images.keys():
    #         images[f'{pear_id}'].append(train_annotation)
    #     else:
    #         images[f'{pear_id}'] = [train_annotation]

    # for valid_annotation in valid_annotations['images']:
    #     pear_id = valid_annotation['file_name'].split('_')[0]
    #     if pear_id in annotation_ids:
    #         continue
    #     if pear_id in images.keys():
    #         images[f'{pear_id}'].append(valid_annotation)
    #     else:
    #         images[f'{pear_id}'] = [valid_annotation]
    
    # for key, value in images.items():
    #     pear_id = key.rjust(3, '0')
    #     data = {
    #         "id": int(f'202000{pear_id}'),
    #         "year": "2020",
    #         "shape_type_id": 10,
    #         "graiding_id_deterioration": 0,
    #         "grading_id": 0,
    #         "images": value,
    #         "comment": "等級判定の実施なし"
    #     }
    #     annotation['pears'].append(data)

    annotation['annotations'] = train_annotations['annotations']
    for valid_annotation in valid_annotations['annotations']:
        annotation['annotations'].append(valid_annotation)
    with open(f'{ANNOTATION_DIR}/annotation_for_grading.json', 'w') as f:
        json.dump(annotation, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()