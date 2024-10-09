import boto3
from botocore.exceptions import ClientError
from urllib.parse import urlparse
from io import BytesIO
from typing import Optional, Tuple
import logging

s3 = boto3.client("s3")


def parse_s3_path(s3_path: str) -> Tuple[str, str]:
    parsed = urlparse(s3_path)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    return bucket, key


def handle_s3_error(operation: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ClientError as e:
                logging.error(f"Error {operation} S3: {e}")
                raise

        return wrapper

    return decorator


@handle_s3_error("listing")
def list_s3_files(s3_directory: str) -> list[str]:
    bucket, prefix = parse_s3_path(s3_directory)

    if not prefix.endswith("/"):
        prefix += "/"

    paginator = s3.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

    file_list = []
    for page in page_iterator:
        if "Contents" in page:
            for obj in page["Contents"]:
                file_key = obj["Key"]
                if not file_key.endswith("/"):  # Skip directories
                    file_list.append(f"s3://{bucket}/{file_key}")

    return file_list


@handle_s3_error("downloading from")
def download_from_s3(s3_path: str) -> Optional[BytesIO]:
    bucket, key = parse_s3_path(s3_path)
    response = s3.get_object(Bucket=bucket, Key=key)
    return BytesIO(response["Body"].read())


@handle_s3_error("uploading to")
def upload_to_s3(data, s3_path: str):
    bucket, key = parse_s3_path(s3_path)
    s3.put_object(Body=data, Bucket=bucket, Key=key)


def is_s3_path(path: str) -> bool:
    return path.startswith("s3://")
