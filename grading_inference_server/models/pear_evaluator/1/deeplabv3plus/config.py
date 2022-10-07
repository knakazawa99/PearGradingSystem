_base_ = '/mmsegmentation/configs/deeplabv3plus/deeplabv3plus_r101-d8_480x480_40k_pascal_context.py'

# checkpoint_file = '/var/deepstation/checkpoints/deeplabv3plus_2.pth'
data_root = '/models/pear_evaluator/1/deeplabv3plus'
img_dir = 'JPEGImages'
ann_dir = 'SegmentationClassPNG-mask'
dataset_type = 'StanfordBackgroundDataset'

img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
crop_size = (256, 256)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations'),
    dict(type='Resize', img_scale=(320, 240), ratio_range=(0.5, 2.0)),
    dict(type='RandomCrop', crop_size=crop_size, cat_max_ratio=0.75),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='PhotoMetricDistortion'),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size=crop_size, pad_val=0, seg_pad_val=255),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg']),
]

test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(320, 240),
        # img_ratios=[0.5, 0.75, 1.0, 1.25, 1.5, 1.75],
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
]

data = dict(
    train=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir=img_dir,
        ann_dir=ann_dir,
        pipeline=train_pipeline,
        split='train.txt'
    ),
    val=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir=img_dir,
        ann_dir=ann_dir,
        pipeline=test_pipeline,
        split='val.txt'
    ),
    test=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir=img_dir,
        ann_dir=ann_dir,
        pipeline=test_pipeline,
        split='val.txt'
    ),
)

# We can still use the pre-trained Mask RCNN model though we do not need to
# use the mask branch
# load_from = checkpoint_file

# Set up working dir to save files and logs.
work_dir = './work_dirs'

iteration_num = 5000
runner=dict(
    max_iters = iteration_num
)
log_config=dict(
    interval = 10
)
evaluation=dict(interval = iteration_num)
checkpoint_config=dict(interval = iteration_num)