"""Image and video processing modules."""

from .duplicate_finder import DuplicateFinder
from .heic_processor import HEICProcessor
from .image_optimizer import ImageOptimizer

__all__ = ["DuplicateFinder", "HEICProcessor", "ImageOptimizer"]
