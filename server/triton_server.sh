#!/bin/bash

wget https://storage.googleapis.com/tf_model_garden/vision/waste_identification_ml/Jan2025_ver2_merged_1024_1024.zip && unzip Jan2025_ver2_merged_1024_1024.zip



mkdir -p model_repository/Jan2025_ver2_merged_1024_1024/1/model.savedmodel



echo 'name: "Jan2025_ver2_merged_1024_1024"\nplatform: "tensorflow_savedmodel"\nmax_batch_size : 0' > model_repository/Jan2025_ver2_merged_1024_1024/config.pbtxt


mv Jan2025_ver2_merged_1024_1024/* model_repository/Jan2025_ver2_merged_1024_1024/1/model.savedmodel/ && rm -r Jan2025_ver2_merged_1024_1024

#sudo apt install screen
sudo screen -dmS triton_server_session bash -c 'docker run --runtime=nvidia --rm -p 8000:8000 -p 8001:8001 -p 8002:8002 -v ${PWD}/model_repository:/models nvcr.io/nvidia/deepstream-l4t:7.0-triton-multiarch tritonserver --model-repository=/models --backend-config=tensorflow,version=2'

