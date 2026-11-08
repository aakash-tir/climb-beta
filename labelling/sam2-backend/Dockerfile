# SAM 2.1 ML backend for Label Studio, rebuilt for Blackwell GPUs (RTX 50-series, sm_120).
#
# Upstream (HumanSignal/label-studio-ml-backend, examples/segment_anything_2_image) builds
# on CUDA 12.6 with TORCH_CUDA_ARCH_LIST up to 9.0, which can't run on sm_120. This keeps
# upstream's code (pinned commit) and swaps the base to CUDA 12.8 and adds 12.0 to the
# arch list. Everything else follows upstream's Dockerfile.
FROM pytorch/pytorch:2.11.0-cuda12.8-cudnn9-devel

ARG ML_BACKEND_REPO=https://github.com/HumanSignal/label-studio-ml-backend.git
ARG ML_BACKEND_SHA=a13c5fb6e7766c6ce9007c0c77d44d17239ffd42
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update \
    && apt-get install -y --no-install-recommends git wget g++ build-essential \
       ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=9090 \
    CUDA_HOME=/usr/local/cuda \
    TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0+PTX"

RUN git clone "$ML_BACKEND_REPO" /src \
    && cd /src && git checkout "$ML_BACKEND_SHA" \
    && cp -r label_studio_ml/examples/segment_anything_2_image /app \
    && rm -rf /src

WORKDIR /app
RUN pip install --no-cache-dir -r requirements-base.txt \
    && pip install --no-cache-dir -r requirements.txt

# SAM 2 itself + its checkpoints (~2.5 GB for all sizes).
RUN git clone --depth 1 https://github.com/facebookresearch/sam2.git /sam2 \
    && cd /sam2 && pip install --no-cache-dir --no-build-isolation -e . \
    && cd checkpoints && ./download_ckpts.sh

WORKDIR /sam2
EXPOSE 9090
CMD ["/app/start.sh"]
