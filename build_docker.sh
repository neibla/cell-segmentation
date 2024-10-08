#!/bin/bash
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 245511142268.dkr.ecr.us-west-2.amazonaws.com
docker buildx build \
     --push \
     --platform linux/amd64 \
     -t 245511142268.dkr.ecr.us-west-2.amazonaws.com/cell-segmentation-job:latest \
     -f docker/Dockerfile \
     .