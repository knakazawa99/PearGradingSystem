_base_ = '/mmdetection/configs/faster_rcnn/faster_rcnn_r50_caffe_fpn_mstrain_1x_coco.py'
          
runner = dict(type='EpochBasedRunner', max_epochs=24)
# use caffe img_norm
img_norm_cfg = dict(
    mean=[103.530, 116.280, 123.675], std=[1.0, 1.0, 1.0], to_rgb=True)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations', with_bbox=True),
    dict(
        type='Resize',
        img_scale=[(1333, 640), (1333, 672), (1333, 704), (1333, 736),
                   (1333, 768), (1333, 800)],
        multiscale_mode='value',
        keep_ratio=False),
    dict(type='RandomFlip', flip_ratio=0.0),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size_divisor=32),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_bboxes', 'gt_labels']),
] 
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(1333, 800),
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=False),
            # dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='Pad', size_divisor=32),
            # dict(type='ImageToTensor', keys=['img']),
            dict(type='DefaultFormatBundle'),
            dict(type='Collect', keys=['img']),
        ],
    )
]

data_root = '/var/deepstation/datasets/'
img_prefix = 'JPEGImages'
label_path_root = 'Labels'
dataset_type = 'CocoDataset'
# classes = ('deterioration',)
# classes = ('alternaria', 'injury', 'speckle', 'chemical', 'plane', 'unkown')
classes = ('alternaria', 'injury', 'speckle', 'chemical', 'plane')
data = dict(
    train=dict(
        type=dataset_type, 
        data_root=data_root,
        ann_file=f'{label_path_root}/train_annotations_multi.json',
        classes=classes,
        img_prefix=img_prefix,
        pipeline=train_pipeline),
    val=dict(
            type=dataset_type, 
            data_root=data_root,
            ann_file=f'{label_path_root}/validation_annotations_multi.json',
            classes=classes,
            img_prefix=img_prefix,
            pipeline=test_pipeline
        ),
    test=dict(
            type=dataset_type, 
            data_root=data_root,
            ann_file=f'{label_path_root}/validation_annotations_multi.json',
            classes=classes,
            img_prefix=img_prefix,
            pipeline=test_pipeline
        )
)
load_from = '/var/deepstation/checkpoints/faster_rcnn_r50_caffe_fpn_mstrain_3x_coco_20210526_095054-1f77628b.pth'
work_dir = '/var/deepstation/work_dir'
optimizer_config = dict(grad_clip=None)
