#!/bin/bash

# Get the AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com
docker buildx build \
     --push \
     --platform linux/amd64 \
     -t ${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/cell-segmentation-job:latest \
     -f docker/Dockerfile \
     .