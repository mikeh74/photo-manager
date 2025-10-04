"""
Basic tests for the configuration module.
"""

from photo_manager.config import Config


def test_config_initialization():
    """Test that config initializes with default values."""
    config = Config()

    assert config.optimize_quality == 85  # noqa: S101
    assert config.max_image_size == (1920, 1080)  # noqa: S101
    assert config.heic_extract_videos is True  # noqa: S101
    assert config.max_workers == 4  # noqa: S101


def test_config_validation():
    """Test configuration validation."""
    config = Config()

    # Should have errors due to missing credentials file
    errors = config.validate()
    assert len(errors) > 0  # noqa: S101
    assert any(  # noqa: S101
        "Credentials file not found" in error for error in errors
    )


def test_parse_dimensions():
    """Test dimension parsing."""
    config = Config()

    # Valid format
    assert config._parse_dimensions("1920x1080") == (1920, 1080)  # noqa: S101
    assert config._parse_dimensions("800x600") == (800, 600)  # noqa: S101

    # Invalid format should return default
    assert config._parse_dimensions("invalid") == (1920, 1080)  # noqa: S101
    assert config._parse_dimensions("") == (1920, 1080)  # noqa: S101
