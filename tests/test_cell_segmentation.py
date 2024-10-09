import pytest
from cell_segmentor import segment_cells, segment_cells_from_directory
import os
import tempfile


def test_segment_cells():
    with tempfile.TemporaryDirectory() as tmp_dir:
        segment_cells(["./tests/data/L11_s1_w2_slice_0.png"], tmp_dir)

        cell_images = [
            f
            for f in os.listdir(tmp_dir + "/L11_s1_w2_slice_0/cells")
            if f.startswith("cell_") and f.endswith(".png")
        ]
        assert len(cell_images) == 219


def test_invalid_input():
    with pytest.raises(FileNotFoundError):
        segment_cells(["nonexistent.png"], "/tmp")

    with tempfile.TemporaryDirectory() as tmp_dir:
        segment_cells_from_directory("./tests/data2", tmp_dir)
        print(tmp_dir)
        cell_images = [
            f
            for f in os.listdir(tmp_dir + "/L11_s1_w2_slice_0/cells")
            if f.startswith("cell_") and f.endswith(".png")
        ]
        assert len(cell_images) == 219


def test_invalid_input_directory():
    with pytest.raises(FileNotFoundError):
        segment_cells_from_directory("nonexistent_directory", "/tmp")
