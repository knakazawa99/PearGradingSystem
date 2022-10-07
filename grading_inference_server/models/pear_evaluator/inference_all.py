import os.path as osp
import time
import pickle
import mmcv
from mmseg.apis import inference_segmentor, init_segmentor, show_result_pyplot
from mmseg.datasets import build_dataset as build_segmentation_dataset
from mmseg.models import build_segmentor
from mmseg.datasets.builder import DATASETS
from mmseg.datasets.custom import CustomDataset
from mmdet.apis import inference_detector, single_gpu_test
from mmdet.datasets import build_dataset as build_detecion_dataset
from mmdet.models import build_detector
import numpy as np
from mmcv.runner import load_checkpoint
import cv2
PROJECT_ROOT = '/var/deepstation'
EXTENTION = 'jpg'
from notify.slack import notify_to_slack

palette = [[128, 0, 0]]
classes = ('pear',)

@DATASETS.register_module()
class StanfordBackgroundDataset(CustomDataset):
  CLASSES = classes
  PALETTE = palette
  def __init__(self, split, **kwargs):
    super().__init__(img_suffix='.jpg', seg_map_suffix='.png', 
                     split=split, **kwargs)
    assert osp.exists(self.img_dir) and self.split is not None


def get_segmentation_model():
    model_root = f'{PROJECT_ROOT}/models/deeplabv3plus'
    checkpoint_file = f'{model_root}/latest.pth'

    cfg = mmcv.Config.fromfile(f'{model_root}/config.py')
    cfg.norm_cfg = dict(type='BN', requires_grad=True)
    cfg.model.backbone.norm_cfg = cfg.norm_cfg
    cfg.model.decode_head.norm_cfg = cfg.norm_cfg
    cfg.model.auxiliary_head.norm_cfg = cfg.norm_cfg
    cfg.device='cuda' 
    cfg.model.decode_head.num_classes = 2
    cfg.model.auxiliary_head.num_classes = 2
    cfg.load_from = checkpoint_file
    cfg.work_dir = f'{PROJECT_ROOT}/work_dir'
    cfg.gpu_ids = range(1)


    datasets = build_segmentation_dataset(cfg.data.test)
    cfg.model.pretrained = None
    cfg.model.train_cfg = None
    model = build_segmentor(cfg.model)
    load_checkpoint(model, checkpoint_file, map_location='cpu')

    model.CLASSES = datasets.CLASSES
    model.PALETTE = datasets.PALETTE
    model.cfg = cfg
    model.to('cuda')
    model.eval()
    return model

def get_detection_model():
    model_root = f'{PROJECT_ROOT}/models/faster_r_cnn/v2'
    cfg = mmcv.Config.fromfile(f'{model_root}/config.py')
    cfg.device='cuda' 
    cfg.model.roi_head.bbox_head.num_classes = 6
    cfg.load_from = f'{model_root}/latest.pth'
    cfg.work_dir = f'{PROJECT_ROOT}/work_dir'
    cfg.gpu_ids = range(1)

    datasets = build_detecion_dataset(cfg.data.test)

    model = build_detector(cfg.model)
    model.CLASSES = datasets.CLASSES
    model.cfg = cfg
    PALETTE = getattr(datasets, 'PALETTE', None)
    return model, PALETTE


def main():
    segmentation_model = get_segmentation_model()
    detection_model, palette = get_detection_model()

    lines = mmcv.list_from_file(f'{PROJECT_ROOT}/datasets/val.txt')

    predicted = []
    times = []
    count = 0
    # results = []
    for line in lines:
        file_name = line.strip()
        if file_name in predicted:
            continue
        predicted.append(file_name)
        img = mmcv.imread(f'{PROJECT_ROOT}/datasets/JPEGImages/{file_name}.{EXTENTION}')
        start = time.perf_counter()
        result = inference_segmentor(segmentation_model, img)
        mask_indexes = np.where(result[0])
        y_min = np.min(mask_indexes[0])
        y_max = np.max(mask_indexes[0])
        x_min = np.min(mask_indexes[1])
        x_max = np.max(mask_indexes[1])
        segmented_image = img[y_min:y_max, x_min:x_max]
        # cv2.imwrite(f'{PROJECT_ROOT}/segmented/{file_name}.{EXTENTION}', img[y_min:y_max, x_min:x_max])
        # inference_detectorを噛ませるとうまくいかない
        result_detect = inference_detector(detection_model, segmented_image)
        # 時間計測終了
        elappsed_time = time.perf_counter() - start
        detection_model.show_result(
            img,
            result_detect,
            show=True,
            bbox_color=palette,
            text_color=(200, 200, 200),
            out_file=f'{PROJECT_ROOT}/detected/{file_name}.{EXTENTION}')
        print(f'elappsed time: {elappsed_time}')
        times.append(elappsed_time)
        # results.append(result)
        count += 1
    # with open("results.pkl", mode="wb") as f:
    #     pickle.dump(results, f)

    print(f'average time: {sum(times) / len(times)}')


if __name__ == '__main__':
    try:
        main()
        notify_to_slack("<@U01RU7TNSFM> 推論が終了しました。inference all")
    except Exception as e:
        print(e)
        notify_to_slack("<@U01RU7TNSFM> 異常終了しました。inference all")
