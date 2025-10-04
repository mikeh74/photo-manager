"""
Configuration settings for Google Photos Manager.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for Google Photos Manager."""

    def __init__(self):
        """Initialize configuration with environment variables."""
        self.project_root = Path(__file__).parent.parent.parent

        # Google Photos API settings
        self.google_photos_scopes = self._get_list_env(
            "GOOGLE_PHOTOS_SCOPES",
            [
                "https://www.googleapis.com/auth/photoslibrary.readonly",
                "https://www.googleapis.com/auth/photoslibrary.sharing",
            ],
        )
        self.credentials_file = self._get_path_env(
            "CREDENTIALS_FILE", "credentials.json"
        )
        self.token_file = self._get_path_env("TOKEN_FILE", "token.json")

        # Download settings
        self.default_download_path = self._get_path_env(
            "DEFAULT_DOWNLOAD_PATH", "./downloads"
        )
        self.max_concurrent_downloads = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "5"))

        # HEIC processing settings
        self.heic_extract_videos = (
            os.getenv("HEIC_EXTRACT_VIDEOS", "true").lower() == "true"
        )
        self.heic_keep_original = (
            os.getenv("HEIC_KEEP_ORIGINAL", "true").lower() == "true"
        )
        self.heic_output_format = os.getenv("HEIC_OUTPUT_FORMAT", "jpg")

        # Image optimization settings
        self.optimize_quality = int(os.getenv("OPTIMIZE_QUALITY", "85"))
        self.max_image_size = self._parse_dimensions(
            os.getenv("MAX_IMAGE_SIZE", "1920x1080")
        )
        self.preserve_metadata = (
            os.getenv("PRESERVE_METADATA", "true").lower() == "true"
        )

        # Logging settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = self._get_path_env("LOG_FILE", "photo_manager.log")

        # Processing settings
        self.batch_size = int(os.getenv("BATCH_SIZE", "100"))
        self.use_threading = os.getenv("USE_THREADING", "true").lower() == "true"
        self.max_workers = int(os.getenv("MAX_WORKERS", "4"))

    def _get_list_env(self, key: str, default: list[str]) -> list[str]:
        """Get a list from environment variable."""
        value = os.getenv(key)
        if value:
            return [item.strip() for item in value.split(",")]
        return default

    def _get_path_env(self, key: str, default: str) -> Path:
        """Get a path from environment variable."""
        value = os.getenv(key, default)
        path = Path(value)
        if not path.is_absolute():
            path = self.project_root / path
        return path

    def _parse_dimensions(self, dimensions_str: str) -> tuple[int, int]:
        """Parse dimensions string like '1920x1080' into tuple."""
        try:
            width, height = dimensions_str.split("x")
            return (int(width), int(height))
        except (ValueError, AttributeError):
            return (1920, 1080)

    def create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.default_download_path,
            self.log_file.parent,
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []

        # Check required files
        if not self.credentials_file.exists():
            errors.append(f"Credentials file not found: {self.credentials_file}")

        # Validate quality setting
        if not 1 <= self.optimize_quality <= 100:
            errors.append("OPTIMIZE_QUALITY must be between 1 and 100")

        # Validate dimensions
        if self.max_image_size[0] <= 0 or self.max_image_size[1] <= 0:
            errors.append("MAX_IMAGE_SIZE must contain positive integers")

        # Validate worker count
        if self.max_workers < 1:
            errors.append("MAX_WORKERS must be at least 1")

        return errors


# Global configuration instance
config = Config()
