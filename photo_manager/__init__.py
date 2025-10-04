"""
Google Photos Manager

A Python application for managing your Google Photos library with automation
features for HEIC processing and batch operations.
"""

__version__ = "1.0.0"
__author__ = "Photo Manager"
__email__ = "contact@example.com"

try:
    from .api import GooglePhotosAPI
    from .auth import GooglePhotosAuth
    from .config import Config

    __all__ = ["Config", "GooglePhotosAPI", "GooglePhotosAuth"]
except ImportError:
    # Handle import errors during development
    __all__ = []
