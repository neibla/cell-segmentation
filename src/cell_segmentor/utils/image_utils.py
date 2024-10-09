import numpy as np
from PIL import Image
from skimage import io as skio
from typing import Optional
from io import BytesIO
import os
from .s3_utils import is_s3_path, download_from_s3, upload_to_s3


def is_image_file(file_path: str) -> bool:
    # Check file extension
    valid_extensions = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"}
    if os.path.splitext(file_path)[1].lower() not in valid_extensions:
        return False
    return True


def load_image(image_path: str) -> Optional[np.ndarray]:
    if is_s3_path(image_path):
        image_data = download_from_s3(image_path)
        if image_data is None:
            return None
        image = Image.open(BytesIO(image_data.getvalue()))
    else:
        image = Image.open(image_path)
    return np.array(image)


def save_mask(mask: np.ndarray, output_path: str) -> None:
    if is_s3_path(output_path):
        with BytesIO() as buffer:
            np.save(buffer, mask)
            buffer.seek(0)
            upload_to_s3(buffer.getvalue(), output_path)
    else:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        np.save(output_path, mask)


def save_image(image: np.ndarray, output_path: str) -> None:
    if is_s3_path(output_path):
        with BytesIO() as buffer:
            skio.imsave(buffer, image, format="png")
            buffer.seek(0)
            upload_to_s3(buffer.getvalue(), output_path)
    else:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        skio.imsave(output_path, image)
