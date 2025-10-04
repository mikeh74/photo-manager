"""
Image optimization utilities.
"""

from pathlib import Path

from PIL import Image, ImageOps

from photo_manager.config import config
from photo_manager.utils import logging_utils

logger = logging_utils.get_logger(__name__)


class ImageOptimizer:
    """Optimize images to reduce file size while maintaining quality."""

    def __init__(self):
        """Initialize the image optimizer."""
        self.quality = config.optimize_quality
        self.max_size = config.max_image_size
        self.preserve_metadata = config.preserve_metadata

    def optimize_image(self, input_path: Path, output_path: Path | None = None) -> dict:
        """
        Optimize a single image file.

        Args:
            input_path: Path to input image
            output_path: Optional output path (defaults to overwrite)

        Returns:
            Dictionary with optimization results
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Image file not found: {input_path}")

        # Set output path
        if output_path is None:
            output_path = input_path

        result = {
            "input_file": input_path,
            "output_file": output_path,
            "size_before": input_path.stat().st_size,
            "size_after": 0,
            "success": False,
            "error": None,
        }

        try:
            # Open image
            with Image.open(input_path) as i:
                # Convert to RGB if necessary (for JPEG)
                img = i.copy()
                if img.mode in ["RGBA", "P"]:
                    img = img.convert("RGB")

                # Resize if larger than max size
                if self.max_size:
                    img.thumbnail(self.max_size, Image.Resampling.LANCZOS)

                # Apply auto-orientation
                img = ImageOps.exif_transpose(img)

                # Prepare save options
                save_kwargs = {
                    "format": "JPEG",
                    "quality": self.quality,
                    "optimize": True,
                }

                # Preserve metadata if requested
                if self.preserve_metadata and hasattr(img, "getexif"):
                    exif = img.getexif()
                    if exif:
                        save_kwargs["exif"] = exif

                # Save optimized image
                img.save(output_path, **save_kwargs)

            # Update result
            result["size_after"] = output_path.stat().st_size
            result["success"] = True

            reduction = (
                (result["size_before"] - result["size_after"]) / result["size_before"]
            ) * 100
            logger.info(f"Optimized {input_path.name}: {reduction:.1f}% reduction")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error optimizing {input_path}: {e}")

        return result

    def optimize_directory(
        self, input_dir: Path, output_dir: Path | None = None
    ) -> list[dict]:
        """
        Optimize all images in a directory.

        Args:
            input_dir: Directory containing images
            output_dir: Optional output directory

        Returns:
            List of optimization results
        """
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Supported image extensions
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

        # Find all image files
        image_files = []
        for ext in image_extensions:
            image_files.extend(input_dir.glob(f"*{ext}"))
            image_files.extend(input_dir.glob(f"*{ext.upper()}"))

        if not image_files:
            logger.info(f"No image files found in {input_dir}")
            return []

        logger.info(f"Found {len(image_files)} images to optimize")

        # Process each image
        results = []
        for image_file in image_files:
            try:
                # Determine output path
                if output_dir:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_path = output_dir / image_file.name
                else:
                    output_path = None

                result = self.optimize_image(image_file, output_path)
                results.append(result)

            except Exception as e:
                logger.error(f"Failed to optimize {image_file}: {e}")
                results.append(
                    {
                        "input_file": image_file,
                        "output_file": None,
                        "size_before": 0,
                        "size_after": 0,
                        "success": False,
                        "error": str(e),
                    }
                )

        return results
