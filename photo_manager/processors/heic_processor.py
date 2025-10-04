"""
HEIC file processor for extracting videos and converting images.
"""

from pathlib import Path
import subprocess

from PIL import Image
from pillow_heif import register_heif_opener

from photo_manager.config import config
from photo_manager.utils import logging_utils

# Register HEIF opener for PIL
register_heif_opener()

logger = logging_utils.get_logger(__name__)


class HEICProcessor:
    """Process HEIC files to extract videos and convert images."""

    def __init__(self):
        """Initialize the HEIC processor."""
        self.extract_videos = config.heic_extract_videos
        self.keep_original = config.heic_keep_original
        self.output_format = config.heic_output_format

    def process_file(self, heic_path: Path, output_dir: Path) -> dict:
        """
        Process a single HEIC file.

        Args:
            heic_path: Path to the HEIC file
            output_dir: Directory to save processed files

        Returns:
            Dictionary with processing results
        """
        if not heic_path.exists():
            raise FileNotFoundError(f"HEIC file not found: {heic_path}")

        if heic_path.suffix.lower() not in [".heic", ".heif"]:
            raise ValueError(f"Not a HEIC file: {heic_path}")

        results = {
            "original_file": heic_path,
            "image_file": None,
            "video_file": None,
            "errors": [],
        }

        try:
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)

            # Extract video component if requested
            if self.extract_videos:
                video_file = self._extract_video(heic_path, output_dir)
                if video_file:
                    results["video_file"] = video_file

            # Convert image component
            image_file = self._convert_image(heic_path, output_dir)
            if image_file:
                results["image_file"] = image_file

            # Remove original if not keeping it
            if not self.keep_original and (
                results["image_file"] or results["video_file"]
            ):
                try:
                    heic_path.unlink()
                    logger.info(f"Removed original file: {heic_path}")
                except Exception as e:
                    results["errors"].append(f"Could not remove original: {e}")

        except Exception as e:
            error_msg = f"Error processing {heic_path}: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

        return results

    def _extract_video(self, heic_path: Path, output_dir: Path) -> Path | None:
        """
        Extract video component from HEIC file using FFmpeg.

        Args:
            heic_path: Path to HEIC file
            output_dir: Output directory

        Returns:
            Path to extracted video file or None
        """
        try:
            # Check if file has video component
            if not self._has_video_component(heic_path):
                return None

            # Create output path
            video_filename = heic_path.stem + ".mov"
            video_path = output_dir / video_filename

            # Extract video using FFmpeg
            cmd = [
                "ffmpeg",
                "-i",
                str(heic_path),
                "-map",
                "0:v:1",  # Select second video stream (motion)
                "-c",
                "copy",  # Copy without re-encoding
                "-y",  # Overwrite output file
                str(video_path),
            ]

            result = subprocess.run(  # noqa: S603
                cmd, check=False, capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0 and video_path.exists():
                logger.info(f"Extracted video: {video_path}")
                return video_path
            else:
                logger.warning(f"FFmpeg failed for {heic_path}: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"FFmpeg timeout for {heic_path}")
            return None
        except Exception as e:
            logger.error(f"Error extracting video from {heic_path}: {e}")
            return None

    def _has_video_component(self, heic_path: Path) -> bool:
        """
        Check if HEIC file has a video component (Live Photo).

        Args:
            heic_path: Path to HEIC file

        Returns:
            True if file has video component
        """
        try:
            cmd = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_streams",
                str(heic_path),
            ]

            result = subprocess.run(  # noqa: S603
                cmd, check=False, capture_output=True, text=True, timeout=30
            )

            if result.returncode != 0:
                return False

            import json

            probe_data = json.loads(result.stdout)
            streams = probe_data.get("streams", [])

            # Count video streams
            video_streams = [s for s in streams if s.get("codec_type") == "video"]

            # Live Photos typically have 2 video streams (still + motion)
            return len(video_streams) > 1

        except Exception:
            return False

    def _convert_image(self, heic_path: Path, output_dir: Path) -> Path | None:
        """
        Convert HEIC image to specified format.

        Args:
            heic_path: Path to HEIC file
            output_dir: Output directory

        Returns:
            Path to converted image file or None
        """
        try:
            # Create output path
            image_filename = heic_path.stem + f".{self.output_format}"
            image_path = output_dir / image_filename

            # Open and convert image
            with Image.open(heic_path) as i:
                img = i.copy()
                # Convert to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Save in specified format
                save_kwargs = {}
                if self.output_format.lower() == "jpg":
                    save_kwargs["quality"] = config.optimize_quality
                    save_kwargs["optimize"] = True

                img.save(image_path, format=self.output_format.upper(), **save_kwargs)

            logger.info(f"Converted image: {image_path}")
            return image_path

        except Exception as e:
            logger.error(f"Error converting image {heic_path}: {e}")
            return None

    def process_directory(self, input_dir: Path, output_dir: Path) -> list[dict]:
        """
        Process all HEIC files in a directory.

        Args:
            input_dir: Directory containing HEIC files
            output_dir: Directory to save processed files

        Returns:
            List of processing results
        """
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Find all HEIC files
        heic_files = []
        for pattern in ["*.heic", "*.HEIC", "*.heif", "*.HEIF"]:
            heic_files.extend(input_dir.glob(pattern))

        if not heic_files:
            logger.info(f"No HEIC files found in {input_dir}")
            return []

        logger.info(f"Found {len(heic_files)} HEIC files to process")

        # Process each file
        results = []
        for heic_file in heic_files:
            try:
                result = self.process_file(heic_file, output_dir)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {heic_file}: {e}")
                results.append(
                    {
                        "original_file": heic_file,
                        "image_file": None,
                        "video_file": None,
                        "errors": [str(e)],
                    }
                )

        return results

    def get_file_info(self, heic_path: Path) -> dict:
        """
        Get information about a HEIC file.

        Args:
            heic_path: Path to HEIC file

        Returns:
            Dictionary with file information
        """
        info = {
            "path": heic_path,
            "size": 0,
            "has_video": False,
            "image_size": None,
            "metadata": {},
        }

        try:
            # Basic file info
            if heic_path.exists():
                info["size"] = heic_path.stat().st_size

            # Check for video component
            info["has_video"] = self._has_video_component(heic_path)

            # Get image info
            try:
                with Image.open(heic_path) as img:
                    info["image_size"] = img.size
                    info["metadata"] = dict(img.getexif())
            except Exception:
                logger.debug(
                    f"Could not extract image metadata from {heic_path}",
                )

        except Exception as e:
            logger.error(f"Error getting info for {heic_path}: {e}")

        return info
