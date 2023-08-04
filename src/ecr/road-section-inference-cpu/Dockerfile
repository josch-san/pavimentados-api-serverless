# https://aws.amazon.com/cn/releasenotes/available-deep-learning-containers-images/
# https://github.com/aws/deep-learning-containers/blob/master/available_images.md

FROM 763104351884.dkr.ecr.us-east-1.amazonaws.com/tensorflow-training:2.6.2-cpu-py38-ubuntu20.04

RUN python3 -m pip install --upgrade pip --no-cache-dir
RUN pip3 install --upgrade --no-cache-dir \
    pavimentados==0.29.1 awswrangler==3.2.1
