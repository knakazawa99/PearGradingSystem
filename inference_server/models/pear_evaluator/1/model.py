from itertools import chain
import json

import cv2
import numpy as np
import mmcv
from mmdet.apis import inference_detector, init_detector
import mmseg
import triton_python_backend_utils as pb_utils

from shape import calculate_efd, calculate_width_ratio


import time

palette = [[128, 0, 0]]
classes = ('pear',)

def get_detection_model():
    model_root = f'/models/pear_evaluator/1/fasterrcnn'
    model_weight = f'{model_root}/model_weight.pth'
    cfg = mmcv.Config.fromfile(f'{model_root}/config.py')
    cfg.device='cuda' 
    cfg.model.roi_head.bbox_head.num_classes = 5
    cfg.load_from = model_weight
    cfg.work_dir = f'{model_root}/work_dir'
    cfg.gpu_ids = range(1)

    model = init_detector(cfg, model_weight, device='cuda')
    return model

def remove_backgroud(image):
    image_blur = cv2.GaussianBlur(image, (19, 19), 0)
    image_saturation = cv2.cvtColor(image_blur, cv2.COLOR_BGR2HLS)[:, :, 2].astype(np.uint8)
    _, binary_image = cv2.threshold(image_saturation, 0, 255, cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(
        image=binary_image,
        mode=cv2.RETR_EXTERNAL,
        method=cv2.CHAIN_APPROX_SIMPLE
    )
        # 一番大きい輪郭を抽出
    max_contours = max(contours, key=lambda x: cv2.contourArea(x))
    x_min, y_min, width, height = cv2.boundingRect(max_contours)

    y_max = y_min + height
    x_max = x_min + width
    return (x_min, y_min, x_max, y_max)


SHAPE_TYPES = {
    0: 'short',
    1: 'fat',
    2: 'other'
}

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
        self.detection_model = get_detection_model()
        print('## MODEL LOADED!!', flush=True)

        # You must parse model_config. JSON string is not parsed here
        self.model_config = model_config = json.loads(args['model_config'])

        # Get OUTPUT0 configuration
        # segmentation_result_config = pb_utils.get_output_config_by_name(
        #     model_config, "SEGMENTATION_RESULT")

        detection_result_config = pb_utils.get_output_config_by_name(
            model_config, "DETECTION_RESULT")

        # shape_result_config = pb_utils.get_output_config_by_name(
        #     model_config, "SHAPE_RESULT")

        # Convert Triton types to numpy types
        # self.segmentation_result_dtype = pb_utils.triton_string_to_numpy(
        #     segmentation_result_config['data_type'])
        self.detection_result_dtype = pb_utils.triton_string_to_numpy(
            detection_result_config['data_type'])   
        # self.shape_result_config = pb_utils.triton_string_to_numpy(
        #     shape_result_config['data_type'])                     

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
            x_min, y_min, x_max, y_max = remove_backgroud(image)
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
            
            detection_result_tensor = pb_utils.Tensor("DETECTION_RESULT", detection_results.astype(self.detection_result_dtype))

            # Create InferenceResponse. You can set an error here in case
            # there was a problem with handling this inference request.
            # Below is an example of how you can set errors in inference
            inference_response = pb_utils.InferenceResponse(
                output_tensors=[detection_result_tensor])
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