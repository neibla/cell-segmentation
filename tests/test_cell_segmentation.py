import pytest
from src.main import process_images
import os
import tempfile


def test_process_image():
    with tempfile.TemporaryDirectory() as tmp_dir:
        process_images(["./tests/data/L11_s1_w2_slice_0.png"], [tmp_dir])

        cell_images = [
            f
            for f in os.listdir(tmp_dir)
            if f.startswith("cell_") and f.endswith(".png")
        ]
        assert len(cell_images) == 219


def test_invalid_input():
    with pytest.raises(FileNotFoundError):
        process_images(["nonexistent.png"], ["/tmp"])
