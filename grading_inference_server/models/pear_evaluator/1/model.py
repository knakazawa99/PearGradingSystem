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

import json
import os.path as osp
# triton_python_backend_utils is available in every Triton Python model. You
# need to use this module to create inference requests and responses. It also
# contains some utility functions for extracting information from model_config
# and converting Triton input/output types to numpy types.
print('## START!!', flush=True)
import mmcv
# from mmseg.apis import inference_segmentor, init_segmentor, show_result_pyplot
# from mmseg.datasets import build_dataset as build_segmentation_dataset
import mmseg
from mmseg.models import build_segmentor
from mmseg.apis import inference_segmentor
from mmseg.datasets.builder import DATASETS
from mmseg.datasets.custom import CustomDataset

from mmdet.apis import inference_detector, init_detector
from mmdet.datasets import build_dataset as build_detecion_dataset
from mmdet.models import build_detector

import triton_python_backend_utils as pb_utils

import numpy as np
import time
print('## END IMPORT!!', flush=True)

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
    model_root = f'/models/pear_evaluator/1/deeplabv3plus'
    checkpoint_file = f'{model_root}/model_weight.pth'

    cfg = mmcv.Config.fromfile(f'{model_root}/config.py')
    cfg.norm_cfg = dict(type='BN', requires_grad=True)
    cfg.model.backbone.norm_cfg = cfg.norm_cfg
    cfg.model.decode_head.norm_cfg = cfg.norm_cfg
    cfg.model.auxiliary_head.norm_cfg = cfg.norm_cfg
    cfg.device='cuda' 
    cfg.model.decode_head.num_classes = 2
    cfg.model.auxiliary_head.num_classes = 2
    cfg.load_from = checkpoint_file
    cfg.work_dir = f'{model_root}/work_dir'
    cfg.gpu_ids = range(1)


    datasets = mmseg.datasets.build_dataset(cfg.data.test)
    cfg.model.pretrained = None
    cfg.model.train_cfg = None
    model = build_segmentor(cfg.model)
    mmcv.runner.load_checkpoint(model, checkpoint_file, map_location='cpu')
 
    model.CLASSES = datasets.CLASSES
    model.PALETTE = datasets.PALETTE
    model.cfg = cfg
    model.to('cuda')
    model.eval()
    return model

# def get_detection_model():
#     model_root = f'/models/pear_evaluator/1/fasterrcnn'
#     cfg = mmcv.Config.fromfile(f'{model_root}/config.py')
#     cfg.device='cuda' 
#     cfg.model.roi_head.bbox_head.num_classes = 6
#     cfg.load_from = f'{model_root}/model_weight.pth'
#     cfg.work_dir = f'{model_root}/work_dir'
#     cfg.gpu_ids = range(1)

#     datasets = build_detecion_dataset(cfg.data.test)

#     model = build_detector(cfg.model)
#     model.CLASSES = datasets.CLASSES
#     model.cfg = cfg
#     # PALETTE = getattr(datasets, 'PALETTE', None)
#     return model

def get_detection_model():
    model_root = f'/models/pear_evaluator/1/fasterrcnn'
    model_weight = f'{model_root}/model_weight.pth'
    cfg = mmcv.Config.fromfile(f'{model_root}/config.py')
    cfg.device='cuda' 
    cfg.model.roi_head.bbox_head.num_classes = 6
    cfg.load_from = model_weight
    cfg.work_dir = f'{model_root}/work_dir'
    cfg.gpu_ids = range(1)

    model = init_detector(cfg, model_weight, device='cuda')
    return model

class TritonPythonModel:
    """Your Python model must use the same class name. Every Python model
    that is created must have "TritonPythonModel" as the class name.
    """

    def initialize(self, args):
        """`initialize` is called only once when the model is being loaded.
        Implementing `initialize` function is optional. This function allows
        the model to intialize any state associated with this model.
        Parameters
        ----------
        args : dict
          Both keys and values are strings. The dictionary keys and values are:
          * model_config: A JSON string containing the model configuration
          * model_instance_kind: A string containing model instance kind
          * model_instance_device_id: A string containing model instance device ID
          * model_repository: Model repository path
          * model_version: Model version
          * model_name: Model name
        """
        print('## MODEL LOAD!!', flush=True)
        self.segmentation_model = get_segmentation_model()
        self.detection_model = get_detection_model()
        print('## MODEL LOADED!!', flush=True)

        # You must parse model_config. JSON string is not parsed here
        self.model_config = model_config = json.loads(args['model_config'])

        # Get OUTPUT0 configuration
        segmentation_result_config = pb_utils.get_output_config_by_name(
            model_config, "SEGMENTATION_RESULT")

        detection_result_config = pb_utils.get_output_config_by_name(
            model_config, "DETECTION_RESULT")

        # Convert Triton types to numpy types
        self.segmentation_result_dtype = pb_utils.triton_string_to_numpy(
            segmentation_result_config['data_type'])
        self.detection_result_dtype = pb_utils.triton_string_to_numpy(
            detection_result_config['data_type'])            

    def execute(self, requests):
        """`execute` MUST be implemented in every Python model. `execute`
        function receives a list of pb_utils.InferenceRequest as the only
        argument. This function is called when an inference request is made
        for this model. Depending on the batching configuration (e.g. Dynamic
        Batching) used, `requests` may contain multiple requests. Every
        Python model, must create one pb_utils.InferenceResponse for every
        pb_utils.InferenceRequest in `requests`. If there is an error, you can
        set the error argument when creating a pb_utils.InferenceResponse
        Parameters
        ----------
        requests : list
          A list of pb_utils.InferenceRequest
        Returns
        -------
        list
          A list of pb_utils.InferenceResponse. The length of this list must
          be the same as `requests`
        """

        responses = []

        # Every Python backend must iterate over everyone of the requests
        # and create a pb_utils.InferenceResponse for each of them.
        for request in requests:
            # Get INPUT0
            image = pb_utils.get_input_tensor_by_name(request, "IMAGE").as_numpy()
            start = time.perf_counter()
            segmentation_result = inference_segmentor(self.segmentation_model, image)
            mask_indexes = np.where(segmentation_result[0])
            y_min = np.min(mask_indexes[0])
            y_max = np.max(mask_indexes[0])
            x_min = np.min(mask_indexes[1])
            x_max = np.max(mask_indexes[1])
            segmented_image = image[y_min:y_max, x_min:x_max]
            
            detection_inference_results = inference_detector(self.detection_model, segmented_image)
            print(f'{time.perf_counter() - start} s', flush=True)
            detection_results = None
            # print(detection_inference_results, flush=True)

            # differ_position = [x_min, y_min, x_min, y_min, 0] 
            # mo dified_position_result = [result + differ_position for result in result_detect]
            for index, detection_inference_result in enumerate(detection_inference_results):
                detection_inference_result[:, 4] = index
                detection_inference_result = detection_inference_result[:, :] + np.array([x_min, y_min, x_min, y_min, 0])
                
                if detection_results is None:
                    detection_results = detection_inference_result
                else:
                    # print(f'{detection_results.shape}', flush=True)
                    detection_results = np.concatenate([detection_results, detection_inference_result])
                    # print(f'{detection_results.shape}', flush=True)
            # print(detection_results, flush=True)
            # print(f'{type(detection_results)}, {detection_results.shape}', flush=True)
            
            # Create output tensors. You need pb_utils.Tensor
            # objects to create pb_utils.InferenceResponse.
            segmentation_result_tensor = pb_utils.Tensor("SEGMENTATION_RESULT", segmentation_result[0].astype(self.segmentation_result_dtype))
            detection_result_tensor = pb_utils.Tensor("DETECTION_RESULT", detection_results.astype(self.detection_result_dtype))

            # Create InferenceResponse. You can set an error here in case
            # there was a problem with handling this inference request.
            # Below is an example of how you can set errors in inference
            # response:
            #
            # pb_utils.InferenceResponse(
            #    output_tensors=..., TritonError("An error occured"))
            inference_response = pb_utils.InferenceResponse(
                output_tensors=[segmentation_result_tensor, detection_result_tensor])
            responses.append(inference_response)

        # You should return a list of pb_utils.InferenceResponse. Length
        # of this list must match the length of `requests` list.
        return responses

    def finalize(self):
        """`finalize` is called only once when the model is being unloaded.
        Implementing `finalize` function is OPTIONAL. This function allows
        the model to perform any necessary clean ups before exit.
        """
        print('Cleaning up...')