# Google Photos Manager

A Python application for managing your Google Photos library with automation
features for HEIC processing and batch operations.

## Features

- **Google Photos API Integration**: Connect to your Google Photos library
- **HEIC Video Extraction**: Automatically extract and remove video components
from HEIC files
- **Batch Processing**: Reduce file sizes through batch image optimization
- **Smart Organization**: Organize photos by date, location, or custom criteria
- **Duplicate Detection**: Find and manage duplicate photos
- **Metadata Management**: Preserve and modify photo metadata

## Setup

### Prerequisites

- Python 3.8 or higher
- Google Photos API credentials
- FFmpeg (for video processing)

### Installation

1. Clone or download this project
2. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Install FFmpeg:

   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

### Google Photos API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Photos Library API
4. Create credentials (OAuth 2.0 Client IDs)
5. Download the credentials file and save it as `credentials.json` in the
project root
6. Copy `.env.example` to `.env` and configure your settings

## Usage

### Basic Commands

```bash
# Initialize and authenticate
python -m photo_manager auth

# List all albums
python -m photo_manager albums list

# Download photos from a specific album
python -m photo_manager download --album "Album Name" --output ./downloads

# Process HEIC files (extract videos, optimize images)
python -m photo_manager process-heic --input ./photos --output ./processed

# Batch optimize images
python -m photo_manager optimize --input ./photos \
--quality 85 --max-size 1920x1080

# Find duplicates
python -m photo_manager duplicates --path ./photos
```

### Configuration

Edit `.env` file to customize:

- `GOOGLE_PHOTOS_SCOPES`: API permissions
- `DEFAULT_DOWNLOAD_PATH`: Where to save downloaded photos
- `HEIC_EXTRACT_VIDEOS`: Whether to extract videos from HEIC files
- `OPTIMIZE_QUALITY`: Default JPEG quality for optimization
- `MAX_IMAGE_SIZE`: Maximum dimensions for resized images

## Project Structure

```shell
photo-manager/
├── photo_manager/          # Main package
│   ├── __init__.py
│   ├── __main__.py        # CLI entry point
│   ├── auth/              # Authentication handling
│   ├── api/               # Google Photos API wrapper
│   ├── processors/        # Image/video processing
│   ├── utils/             # Utility functions
│   └── config/            # Configuration management
├── tests/                 # Test files
├── credentials.json       # Google API credentials (not in repo)
├── .env                   # Environment variables (not in repo)
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Features

1. Create feature branch
2. Add tests for new functionality
3. Implement the feature
4. Update documentation
5. Submit pull request

## License

MIT License - see LICENSE file for details.
