"""
Google Photos Manager CLI

Command-line interface for the Google Photos Manager application.
"""

import sys

try:
    from .cli import main
except ImportError:
    print(
        "Error: Could not import CLI module. Please ensure all dependencies are installed."  # noqa E501
    )
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
