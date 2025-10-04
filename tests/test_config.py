"""
Basic tests for the configuration module.
"""

from photo_manager.config import Config


def test_config_initialization():
    """Test that config initializes with default values."""
    config = Config()

    assert config.optimize_quality == 85  # noqa PLR2004
    assert config.max_image_size == (1920, 1080)
    assert config.heic_extract_videos is True
    assert config.max_workers == 4  # noqa PLR2004


def test_config_validation():
    """Test configuration validation."""
    config = Config()

    # Should have errors due to missing credentials file
    errors = config.validate()
    assert len(errors) > 0
    assert any("Credentials file not found" in error for error in errors)


def test_parse_dimensions():
    """Test dimension parsing."""
    config = Config()

    # Valid format
    assert config._parse_dimensions("1920x1080") == (1920, 1080)
    assert config._parse_dimensions("800x600") == (800, 600)

    # Invalid format should return default
    assert config._parse_dimensions("invalid") == (1920, 1080)
    assert config._parse_dimensions("") == (1920, 1080)
