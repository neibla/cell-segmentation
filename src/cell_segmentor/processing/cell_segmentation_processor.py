from typing import Any
import numpy as np
import concurrent.futures
import os
import logging
import torch
from numba import njit
import multiprocessing
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

        self.model = get_cellpose_model(model_type, device=self.device)
        self.logger.info(f"Loaded Cellpose model {model_type}")
        self.num_workers = num_workers

    def process_images(self, image_paths: list[str], output_dir: str, batch_size: int = 64, config: dict[str, Any] | None = None) -> None:
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i+batch_size]
            self.process_batch(batch_paths, output_dir, config)

    def process_batch(self, batch_paths: list[str], output_dir: str, config: dict[str, Any] | None = None) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            batch_images = list(executor.map(load_image, batch_paths))

        self.logger.info(f"Processing batch of {len(batch_images)} images")
        masks_pred, _, _ = predict_masks(self.model, batch_images, config)
        self.logger.info("Predicted masks for batch")

        with multiprocessing.Pool() as pool:
            jobs = [(masks_pred[j], batch_images[j], self.get_output_path(batch_paths[j], output_dir)) for j in range(len(batch_images))]
            pool.starmap(self.save_detected_cells, jobs)

    @staticmethod
    def get_output_path(path: str, output_dir: str) -> str:
        file_name = os.path.splitext(os.path.basename(path))[0]
        output_path = os.path.join(output_dir, file_name)
        return output_path
    def process_image(self, image_path: str, output_dir: str) -> None:
        self.process_images([image_path], output_dir)

    def save_detected_cells(
        self, masks_pred: np.ndarray, image_np: np.ndarray, output_dir: str
    ) -> None:
        # save the mask
        self.logger.info(f"Saving mask for {output_dir}")
        save_mask(masks_pred, f"{output_dir}/mask.npz")
        cells_output_dir = os.path.join(output_dir, "cells")
        unique_cells = np.unique(masks_pred)[1:]
        cell_masks = {cell_id: masks_pred == cell_id for cell_id in unique_cells}
        for cell_id in unique_cells:
            self.process_cell(cell_id, cell_masks[cell_id], image_np, cells_output_dir)
        self.logger.info(f"Saved {len(unique_cells)} detected cells to {output_dir}")

    def process_cell(
        self,
        cell_id: int,
        cell_mask: np.ndarray,
        image_np: np.ndarray,
        output_dir: str,
    ) -> None:
        rows, cols = find_true_indices(cell_mask)
        top, bottom, left, right = rows.min(), rows.max(), cols.min(), cols.max()

        cell_image = image_np[top:bottom+1, left:right+1]
        cell_mask_cropped = cell_mask[top:bottom+1, left:right+1]

        if len(cell_image.shape) == 3 and len(cell_mask_cropped.shape) == 2:
            cell_mask_cropped = cell_mask_cropped[:, :, np.newaxis]

        masked_cell = cell_image * cell_mask_cropped
        
        # Optimize normalization using vectorized operations
        min_val = np.min(masked_cell)
        max_val = np.max(masked_cell)
        if max_val > min_val:
            masked_cell = np.clip((masked_cell - min_val) * (255.0 / (max_val - min_val)), 0, 255).astype(np.uint8)
        else:
            masked_cell = np.zeros_like(masked_cell, dtype=np.uint8)
        cell_filename = f"{output_dir}/cell_{cell_id}_bbox_{top}_{bottom}_{left}_{right}.png"
        try:
            save_image(masked_cell, cell_filename)
        except Exception as e:
            raise Exception(f"Failed to save image {cell_filename}: {str(e)}")

# optimized version of np.where
@njit
def find_true_indices(mask):
    rows, cols = [], []
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            if mask[i, j]:
                rows.append(i)
                cols.append(j)
    return np.array(rows), np.array(cols)
