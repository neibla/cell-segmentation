import numpy as np
import concurrent.futures
import os
import logging
import torch
from cell_segmentor.models.cellpose_model import predict_masks, get_cellpose_model
from cell_segmentor.utils.image_utils import load_image, save_image, save_mask


class CellSegmentationProcessor:
    NUM_WORKERS = os.cpu_count() or 1

    def __init__(
        self,
        model_type: str = "cyto3",
        num_workers: int = NUM_WORKERS,
        device: torch.device | None = None,
    ):
        self.logger = logging.getLogger(__name__)
        if not device:
            device = torch.device(
                "cuda"
                if torch.cuda.is_available()
                else "mps"
                if torch.backends.mps.is_available()
                else "cpu"
            )
        self.device = device
        self.logger.info(f"Using device: {self.device}")

        self.model = get_cellpose_model(model_type)
        self.logger.info(f"Loaded Cellpose model {model_type}")
        self.num_workers = num_workers

    def process_images(self, image_paths: list[str], output_dir: str) -> None:
        for path in image_paths:
            file_name = os.path.splitext(os.path.basename(path))[0]
            output_path = os.path.join(output_dir, file_name)
            self.process_image(path, output_path)

    def process_image(self, image_path: str, output_dir: str) -> None:
        image_np = load_image(image_path)
        self.logger.info(f"Processing image {image_path}")
        masks_pred, _, _ = predict_masks(self.model, [image_np])
        # using the latest mask
        self.save_detected_cells(masks_pred[-1], image_np, output_dir)

    def save_detected_cells(
        self, masks_pred: np.ndarray, image_np: np.ndarray, output_dir: str
    ) -> None:
        # save the mask
        save_mask(masks_pred, f"{output_dir}/mask.npy")
        cells_output_dir = os.path.join(output_dir, "cells")
        unique_cells = np.unique(masks_pred)[1:]

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.NUM_WORKERS
        ) as executor:
            futures = [
                executor.submit(
                    self.process_cell, cell_id, masks_pred, image_np, cells_output_dir
                )
                for cell_id in unique_cells
            ]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Failed to save cell: {e}")
                    raise e
        self.logger.info(f"Saved {len(unique_cells)} detected cells to {output_dir}")

    def process_cell(
        self,
        cell_id: int,
        masks_pred: np.ndarray,
        image_np: np.ndarray,
        output_dir: str,
    ) -> None:
        cell_mask = masks_pred == cell_id
        rows, cols = np.where(cell_mask)
        top, bottom, left, right = rows.min(), rows.max(), cols.min(), cols.max()

        cell_image = image_np[top : bottom + 1, left : right + 1]
        cell_mask_cropped = cell_mask[top : bottom + 1, left : right + 1]

        if len(cell_image.shape) == 3 and len(cell_mask_cropped.shape) == 2:
            cell_mask_cropped = cell_mask_cropped[:, :, np.newaxis]

        masked_cell = cell_image * cell_mask_cropped
        masked_cell = (
            (masked_cell - masked_cell.min())
            / (masked_cell.max() - masked_cell.min())
            * 255
        ).astype(np.uint8)

        cell_filename = (
            f"{output_dir}/cell_{cell_id}_bbox_{top}_{bottom}_{left}_{right}.png"
        )
        try:
            save_image(masked_cell, cell_filename)
        except Exception as e:
            raise Exception(f"Failed to save image {cell_filename}: {str(e)}")
