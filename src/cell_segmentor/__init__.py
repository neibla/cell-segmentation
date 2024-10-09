from .processing.cell_segmentation_processor import CellSegmentationProcessor


def get_segmented_cells(input_images: list[str], output_dirs: list[str]) -> None:
    processor = CellSegmentationProcessor()
    processor.process_images(input_images, output_dirs)
