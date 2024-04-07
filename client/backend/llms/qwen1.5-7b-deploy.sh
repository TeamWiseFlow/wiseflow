#!/bin/sh

docker run -d --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=<secret>" \
    --env "LMDEPLOY_USE_MODELSCOPE=True" \
    --env "TOKENIZERS_PARALLELISM=False" \
    --name qwen1.5-7b-service \
    -p 6003:6003 \
    --restart=always \
    --ipc=host \
    openmmlab/lmdeploy:v0.2.5 \
    pip install modelscope & \
    lmdeploy serve api_server Qwen/Qwen1.5-7B-Chat \
    --server-name 0.0.0.0 --server-port 6003 --tp 1 --rope-scaling-factor 1 --backend pytorch