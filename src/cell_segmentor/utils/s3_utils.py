import boto3
from botocore.exceptions import ClientError
from urllib.parse import urlparse
from io import BytesIO
from typing import Optional
import logging

s3 = boto3.client("s3")


def download_from_s3(s3_path: str) -> Optional[BytesIO]:
    parsed = urlparse(s3_path)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    response = s3.get_object(Bucket=bucket, Key=key)
    return BytesIO(response["Body"].read())


def upload_to_s3(data, s3_path: str):
    parsed_url = urlparse(s3_path)
    bucket = parsed_url.netloc
    key = parsed_url.path.lstrip("/")

    try:
        s3.put_object(Body=data, Bucket=bucket, Key=key)
    except ClientError as e:
        logging.error(f"Error uploading to S3: {e}")
        raise


def is_s3_path(path: str) -> bool:
    return path.startswith("s3://")
