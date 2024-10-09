import logging
import argparse
import sys
from cell_segmentor import get_segmented_cells

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Cell Segmentation CLI")
    parser.add_argument(
        "-i",
        "--input-images",
        nargs="+",
        required=True,
        help="Input image files",
    )
    parser.add_argument(
        "-o",
        "--output-dirs",
        nargs="+",
        required=True,
        help="Output directories",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    print(args.input_images)
    print(args.output_dirs)
    if len(args.input_images) != len(args.output_dirs):
        logger.error(
            "The number of input images must match the number of output directories."
        )
        sys.exit(1)

    logger.info(f"Processing {len(args.input_images)} image(s)")
    get_segmented_cells(args.input_images, args.output_dirs)
    logger.info("Processing complete")


if __name__ == "__main__":
    main()
