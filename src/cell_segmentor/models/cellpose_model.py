from typing import Any
from cellpose import models
import numpy as np

DEFAULT_CONFIG: dict[str, Any] = {"channels": [0, 0], "niter": 200, "batch_size": 32}


def get_cellpose_model(model_type: str = "cyto3") -> models.CellposeModel:
    return models.CellposeModel(model_type=model_type)


def predict_masks(
    model: models.CellposeModel, imgs: np.ndarray, config: dict[str, Any] = None
):
    config = config or {}
    config = {**DEFAULT_CONFIG, **config}
    return model.eval(imgs, **config)
