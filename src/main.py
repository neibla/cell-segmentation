import argparse
import logging
from processing.cell_segmentation_processor import CellSegmentationProcessor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def process_images(input_images: list[str], output_dirs: list[str]) -> None:
    processor = CellSegmentationProcessor()
    processor.process_images(input_images, output_dirs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Process images and detect cells.")
    parser.add_argument(
        "--input_images",
        nargs="+",
        type=str,
        required=True,
        help="List of input image paths or S3 URIs",
    )
    parser.add_argument(
        "--output_dirs",
        nargs="+",
        type=str,
        required=True,
        help="List of output directories or S3 URIs for detected cells",
    )
    args = parser.parse_args()

    if len(args.input_images) != len(args.output_dirs):
        logger.error(
            "Error: The number of input images must match the number of output directories."
        )
        return

    process_images(args.input_images, args.output_dirs)


if __name__ == "__main__":
    main()
