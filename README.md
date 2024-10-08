# Cell Segmentation Pipeline

## Overview

A cell segmentation pipeline built on AWS batch. It accepts a list of image files to extract cells from, and writes the segmented cells to the designated output directories.

## Local Setup 

Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Python 3.12 Setup

```bash
uv python install python==3.12
```

## Setup environment/depdencies

```bash
uv sync
```


## Setting up AWS batch 

Install terraform (MacOS)

```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

Setup AWS infrastructure
```bash
./update_infrastructure
```

## Building docker image and pushing to ECR
TODO: remove hardcoded ECR
```bash
./build_docker.sh
```

Example job submission (replace as job queue arn as appropriate)
```bash
aws batch submit-job \
    --job-name "cell-segmentation-job" \
    --job-queue "arn:aws:batch:us-west-2:245511142268:job-queue/cell-segmentation-job-queue" \
    --job-definition "cell-segmentation-job-def" \
    --container-overrides '{
        "command": ["uv", "run", "src/main.py", 
            "--input_images", 
"s3://cell-segmentation-data-70ee19ba6141f3c9/data/L11_s1_w2_slice_0.png",
"s3://cell-segmentation-data-70ee19ba6141f3c9/data/L11_s1_w2_slice_1.png",
"s3://cell-segmentation-data-70ee19ba6141f3c9/data/L11_s1_w2_slice_2.png",
"s3://cell-segmentation-data-70ee19ba6141f3c9/data/L11_s1_w2_slice_3.png",
"s3://cell-segmentation-data-70ee19ba6141f3c9/data/L11_s1_w2_slice_4.png",
"s3://cell-segmentation-data-70ee19ba6141f3c9/data/L11_s1_w2_slice_5.png",
"s3://cell-segmentation-data-70ee19ba6141f3c9/data/L11_s1_w2_slice_6.png",
"s3://cell-segmentation-data-70ee19ba6141f3c9/data/L11_s1_w2_slice_7.png",
"--output_dirs",
"s3://cell-segmentation-data-70ee19ba6141f3c9/ouputs/L11_s1_w2_slice_0/",
"s3://cell-segmentation-data-70ee19ba6141f3c9/ouputs/L11_s1_w2_slice_1/",
"s3://cell-segmentation-data-70ee19ba6141f3c9/ouputs/L11_s1_w2_slice_2/",
"s3://cell-segmentation-data-70ee19ba6141f3c9/ouputs/L11_s1_w2_slice_3/",
"s3://cell-segmentation-data-70ee19ba6141f3c9/ouputs/L11_s1_w2_slice_4/",
"s3://cell-segmentation-data-70ee19ba6141f3c9/ouputs/L11_s1_w2_slice_5/",
"s3://cell-segmentation-data-70ee19ba6141f3c9/ouputs/L11_s1_w2_slice_6/",
"s3://cell-segmentation-data-70ee19ba6141f3c9/ouputs/L11_s1_w2_slice_7/"
        ]
    }'
```