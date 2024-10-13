from typing import Any
from cellpose import models
import numpy as np
import torch

DEFAULT_CONFIG: dict[str, Any] = {"channels": [0, 0], "niter": 200, "batch_size": 64}


def get_cellpose_model(model_type: str = "cyto3", device: torch.device | None = None) -> models.CellposeModel:
    gpu = True if device and device.type == "cuda" else False
    return models.CellposeModel(model_type=model_type, device=device, gpu=gpu)


def predict_masks(
    model: models.CellposeModel, imgs: list[np.ndarray], config: dict[str, Any] | None = None
):
    config = config or {}
    config = {**DEFAULT_CONFIG, **config}
    return model.eval(imgs, **config)
