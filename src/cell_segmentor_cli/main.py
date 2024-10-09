import logging
import argparse
from cell_segmentor import segment_cells, segment_cells_from_directory

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Cell Segmentation CLI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i",
        "--input-images",
        nargs="+",
        help="Input image files to apply cell segmentation to",
    )
    group.add_argument(
        "-d",
        "--input-directory",
        help="Directory containing image files to apply cell segmentation to",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output directory for cell segmentation results",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.input_images:
        logger.info(f"Processing {len(args.input_images)}")
        segment_cells(args.input_images, args.output)
    elif args.input_directory:
        logger.info(f"Processing {args.input_directory}")
        segment_cells_from_directory(args.input_directory, args.output)
    logger.info("Processing complete")


if __name__ == "__main__":
    main()
