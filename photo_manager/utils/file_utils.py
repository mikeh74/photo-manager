"""
File utility functions.
"""

import os
from pathlib import Path
import shutil


def ensure_directory(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to create

    Returns:
        Path to the directory
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size_mb(file_path: Path) -> float:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to file

    Returns:
        File size in MB
    """
    if file_path.exists():
        return file_path.stat().st_size / (1024 * 1024)
    return 0.0


def safe_copy(src: Path, dst: Path, overwrite: bool = False) -> bool:
    """
    Safely copy a file.

    Args:
        src: Source file path
        dst: Destination file path
        overwrite: Whether to overwrite existing files

    Returns:
        True if copy was successful
    """
    try:
        if dst.exists() and not overwrite:
            return False

        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src, dst)
        return True

    except Exception:
        return False


def find_files_by_extension(directory: Path, extensions: list[str]) -> list[Path]:
    """
    Find all files with specified extensions in a directory.

    Args:
        directory: Directory to search
        extensions: List of file extensions (e.g., ['.jpg', '.png'])

    Returns:
        List of matching file paths
    """
    if not directory.exists():
        return []

    files = []
    for ext in extensions:
        files.extend(directory.glob(f"*{ext}"))
        files.extend(directory.glob(f"*{ext.upper()}"))

    return files


def cleanup_empty_directories(directory: Path) -> int:
    """
    Remove empty directories recursively.

    Args:
        directory: Root directory to clean

    Returns:
        Number of directories removed
    """
    removed_count = 0

    for root, dirs, _files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    removed_count += 1
            except (OSError, RuntimeError):
                pass

    return removed_count
