# Cell Segmentation

## Overview

Apply cell segmentation to images using the CLI tool or AWS Batch.

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

## CLI Usage

```bash
uv run cell-segmentor -d tests/data --output  test_output
uv run cell-segmentor --input-images ./tests/data/L11_s1_w2_slice_0.png --output test_output
```

## Setting up AWS batch 

Install terraform (MacOS)

```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

Setup AWS infrastructure
```bash
./update_infrastructure.sh
```
## Building docker image and pushing to ECR
```bash
./build_docker.sh
```

```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws batch submit-job \
    --job-name "cell-segmentation-job" \
    --job-queue "arn:aws:batch:us-west-2:${AWS_ACCOUNT_ID}:job-queue/cell-segmentation-job-queue" \
    --job-definition "cell-segmentation-job-def" \
    --container-overrides '{
        "command": [
            "uv",
            "run",
            "src/cell_segmentor_cli/main.py",
            "-d",
            "s3://cell-segmentation-data-a05c1c99b4410510/data/test_data",
            "-o",
            "s3://cell-segmentation-data-a05c1c99b4410510/test_outputs"
        ]
    }'
```