"""
Duplicate photo finder using hash and perceptual methods.
"""

import builtins
from collections import defaultdict
import contextlib
import hashlib
from pathlib import Path
from typing import Dict, List

import imagehash
from PIL import Image

from photo_manager.utils import logging_utils

logger = logging_utils.get_logger(__name__)


class DuplicateFinder:
    """Find duplicate photos using various methods."""

    def __init__(self):
        """Initialize the duplicate finder."""
        self.supported_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".tiff",
            ".webp",
            ".heic",
            ".heif",
        }

    def find_duplicates(
        self, directory: Path, method: str = "hash"
    ) -> List[List[Path]]:
        """
        Find duplicate images in a directory.

        Args:
            directory: Directory to search
            method: Detection method ('hash' or 'perceptual')

        Returns:
            List of duplicate groups (each group is a list of file paths)
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Find all image files
        image_files = self._find_image_files(directory)

        if not image_files:
            logger.info(f"No image files found in {directory}")
            return []

        logger.info(
            f"Analyzing {len(image_files)} images for duplicates using {method} method"
        )

        if method == "hash":
            return self._find_duplicates_by_hash(image_files)
        elif method == "perceptual":
            return self._find_duplicates_by_perceptual_hash(image_files)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _find_image_files(self, directory: Path) -> List[Path]:
        """Find all image files in directory recursively."""
        image_files = []

        for file_path in directory.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.supported_extensions
            ):
                image_files.append(file_path)

        return image_files

    def _find_duplicates_by_hash(self, image_files: List[Path]) -> List[List[Path]]:
        """Find duplicates using file hash (exact matches)."""
        hash_groups = defaultdict(list)

        for file_path in image_files:
            try:
                file_hash = self._calculate_file_hash(file_path)
                hash_groups[file_hash].append(file_path)
            except Exception as e:
                logger.warning(f"Could not hash {file_path}: {e}")

        # Return groups with more than one file
        duplicate_groups = [group for group in hash_groups.values() if len(group) > 1]

        logger.info(f"Found {len(duplicate_groups)} groups of exact duplicates")
        return duplicate_groups

    def _find_duplicates_by_perceptual_hash(
        self, image_files: List[Path]
    ) -> List[List[Path]]:
        """Find duplicates using perceptual hashing (similar images)."""
        hash_groups = defaultdict(list)

        for file_path in image_files:
            try:
                phash = self._calculate_perceptual_hash(file_path)
                if phash is not None:
                    hash_groups[str(phash)].append(file_path)
            except Exception as e:
                logger.warning(
                    f"Could not calculate perceptual hash for {file_path}: {e}"
                )

        # Return groups with more than one file
        duplicate_groups = [group for group in hash_groups.values() if len(group) > 1]

        logger.info(
            f"Found {len(duplicate_groups)} groups of perceptually similar images"
        )
        return duplicate_groups

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content."""
        hasher = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)

        return hasher.hexdigest()

    def _calculate_perceptual_hash(self, file_path: Path) -> str:
        """Calculate perceptual hash of image."""
        try:
            with Image.open(file_path) as i:
                img = i.copy()
                # Convert to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Calculate average hash (fast and reasonably accurate)
                return str(imagehash.average_hash(img))

        except Exception as e:
            logger.warning(f"Could not open image {file_path}: {e}")
            return None

    def find_similar_images(
        self, directory: Path, threshold: int = 5
    ) -> List[List[Path]]:
        """
        Find similar images using perceptual hashing with hamming distance.

        Args:
            directory: Directory to search
            threshold: Maximum hamming distance for similarity

        Returns:
            List of similar image groups
        """
        image_files = self._find_image_files(directory)

        if not image_files:
            return []

        # Calculate hashes for all images
        image_hashes = {}
        for file_path in image_files:
            try:
                phash = self._calculate_perceptual_hash(file_path)
                if phash:
                    image_hashes[file_path] = imagehash.hex_to_hash(phash)
            except Exception as e:
                logger.warning(f"Could not hash {file_path}: {e}")

        # Find similar groups
        similar_groups = []
        processed = set()

        for file1, hash1 in image_hashes.items():
            if file1 in processed:
                continue

            group = [file1]
            processed.add(file1)

            for file2, hash2 in image_hashes.items():
                if file2 in processed:
                    continue

                # Calculate hamming distance
                distance = hash1 - hash2
                if distance <= threshold:
                    group.append(file2)
                    processed.add(file2)

            if len(group) > 1:
                similar_groups.append(group)

        logger.info(f"Found {len(similar_groups)} groups of similar images")
        return similar_groups

    def get_duplicate_stats(self, duplicate_groups: List[List[Path]]) -> Dict[str, int]:
        """Get statistics about found duplicates."""
        total_files = sum(len(group) for group in duplicate_groups)
        total_duplicates = total_files - len(
            duplicate_groups
        )  # Keep one from each group
        total_size = 0

        for group in duplicate_groups:
            for file_path in group[1:]:  # Skip first file in each group
                with contextlib.suppress(builtins.BaseException):
                    total_size += file_path.stat().st_size

        return {
            "total_groups": len(duplicate_groups),
            "total_files": total_files,
            "total_duplicates": total_duplicates,
            "total_size_mb": total_size / (1024 * 1024),
        }
