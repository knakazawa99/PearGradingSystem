ARG PYTORCH="1.6.0"
ARG CUDA="10.1"
ARG CUDNN="7"

# nvcr.io/nvidia/tensorrtserver:19.10-py3
# nvcr.io/nvidia/tritonserver:20.03-py3 -> 一旦できている -> ここまで trtserver 1.4
# nvcr.io/nvidia/tritonserver:20.10-py3 -> mmdetection ビルドできない
# nvcr.io/nvidia/tritonserver:20.11-py3 ->　mmdetectionビルドできない
# nvcr.io/nvidia/tritonserver:20.12-py3 -> 
# nvcr.io/nvidia/tritonserver:20.06-py3 -> tritonserver backend:python ができない 1.2

# nvcr.io/nvidia/tritonserver:22.09-py3 -> ImportError: libcudart.so.10.1: cannot open shared object file: No such file or directory 1.3
FROM nvcr.io/nvidia/tritonserver:20.12-py3

# # 1.6.0-cuda10.1-cudnn7-devel
# FROM pytorch/pytorch:${PYTORCH}-cuda${CUDA}-cudnn${CUDNN}-devel
# COPY --from=tis /opt/ /opt/

ENV TORCH_CUDA_ARCH_LIST="8.0+PTX"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
ENV CMAKE_PREFIX_PATH="$(dirname $(which conda))/../"

# RUN echo 'alias python="python3"' >> ~/.bashrc
# apt-get update や apt-get upgrade の前に
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
RUN apt-get update && apt-get install -y build-essential gcc ffmpeg libsm6 libxext6 git ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6 python3-dev python3-pip\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#
ENV CUDA_HOME='/usr/local/cuda-11.7'
ENV SLACK_WEB_HOOK_URL="https://hooks.slack.com/services/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"
# ENV FORCE_CUDA="1"

# installed torch-1.12.1 torchaudio-0.12.1 torchvision-0.13.1
# # Install MMCV
RUN pip3 install --no-cache-dir --upgrade pip wheel setuptools
# RUN pip3 install --no-cache-dir mmcv-full==1.3.17 -f https://download.openmmlab.com/mmcv/dist/cu101/torch1.6.0/index.html
RUN pip3 install --no-cache-dir mmcv-full==1.3.17 -f https://download.openmmlab.com/mmcv/dist/cu111/torch1.10.0/index.html
RUN pip3 install future tensorboard
RUN pip3 install slackweb==1.0.5
RUN pip3 install scikit-learn==1.1.2
RUN pip3 install pyefd==1.6.0

# RUN pip3 install torch==1.12.1 torchvision==1.12.1  --extra-index-url https://download.pytorch.org/whl/cu111
RUN pip3 install torch==1.10.0 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu111

RUN pip3 install "git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI"

# # Install MMDetection
RUN git clone https://github.com/open-mmlab/mmdetection.git /mmdetection
WORKDIR /mmdetection
RUN pip3 install -r requirements/build.txt
RUN pip3 install -v -e .
RUN cp -r mmdet /usr/local/lib/python3.8/dist-packages/mmdet

# # Install MMSegmentation
# RUN pip3 install mmsegmentation
RUN git clone https://github.com/open-mmlab/mmsegmentation.git /mmsegmentation
WORKDIR /mmsegmentation
RUN pip3 install .

RUN export PATH=$PATH:/opt/tritonserver/bin/tritonserver
WORKDIR /opt/tritonserver
# WORKDIR /opt/tensorrtserver

CMD ["tritonserver", "--model-repository=/models", "--backend-config=python,grpc-timeout-milliseconds=5000"]

