import os
from typing import Any
import torch
from .processing.cell_segmentation_processor import CellSegmentationProcessor
from .utils.s3_utils import is_s3_path, list_s3_files
from .utils.image_utils import is_image_file


def segment_cells(input_images: list[str], output_dir: str, device: torch.device | None = None, batch_size: int = 64, config: dict[str, Any] | None = None) -> None:
    processor = CellSegmentationProcessor(device=device)
    processor.process_images(input_images, output_dir, batch_size=batch_size, config=config)


def segment_cells_from_directory(input_directory: str, output_dir: str, device: torch.device | None = None, batch_size: int = 64, config: dict[str, Any] | None = None) -> None:
    if is_s3_path(input_directory):
        files = list_s3_files(input_directory)
    else:
        files = [os.path.join(input_directory, file) for file in os.listdir(input_directory)]
    image_files = [file for file in files if is_image_file(file)]
    segment_cells(image_files, output_dir, device, batch_size, config)
