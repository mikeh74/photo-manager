"""
Command-line interface for Google Photos Manager.
"""

from pathlib import Path

import click

from .api import GooglePhotosAPI
from .auth import GooglePhotosAuth
from .config import config
from .processors import DuplicateFinder, HEICProcessor, ImageOptimizer
from .utils import logging_utils

# Set up logging
logger = logging_utils.setup_logging()


@click.group()
@click.version_option()
def cli():
    """Google Photos Manager - Manage your Google Photos library."""
    # Create necessary directories
    config.create_directories()


@cli.command()
@click.option("--force", is_flag=True, help="Force re-authentication")
def auth(force):
    """Authenticate with Google Photos API."""
    try:
        auth_handler = GooglePhotosAuth()
        credentials = auth_handler.authenticate(force_refresh=force)

        if credentials:
            click.echo("✓ Authentication successful!")
            user_info = auth_handler.get_user_info()
            if user_info:
                click.echo(f"Token saved to: {user_info['token_file']}")
        else:
            click.echo("✗ Authentication failed")

    except Exception as e:
        click.echo(f"✗ Authentication error: {e}")


@cli.group()
def albums():
    """Manage Google Photos albums."""


@albums.command("list")
@click.option("--limit", type=int, help="Maximum number of albums to show")
def list_albums(limit):
    """List all albums in your Google Photos library."""
    try:
        api = GooglePhotosAPI()
        albums_list = []

        for album in api.list_albums():
            albums_list.append(album)
            if limit and len(albums_list) >= limit:
                break

        if not albums_list:
            click.echo("No albums found.")
            return

        click.echo(f"Found {len(albums_list)} albums:")
        for album in albums_list:
            title = album.get("title", "Untitled")
            item_count = album.get("mediaItemsCount", "Unknown")
            click.echo(f"  • {title} ({item_count} items)")

    except Exception as e:
        click.echo(f"✗ Error listing albums: {e}")


@cli.command()
@click.option("--album", required=True, help="Album name to download")
@click.option("--output", type=click.Path(), help="Output directory")
@click.option("--workers", type=int, help="Number of concurrent downloads")
def download(album, output, workers):
    """Download photos from a specific album."""
    try:
        api = GooglePhotosAPI()

        # Set output directory
        output_path = Path(output) if output else config.default_download_path

        # Download album
        downloaded_files = api.download_album(
            album_name=album, download_path=output_path, max_workers=workers
        )

        click.echo(f"✓ Downloaded {len(downloaded_files)} files to {output_path}")

    except Exception as e:
        click.echo(f"✗ Download error: {e}")


@cli.command("process-heic")
@click.option(
    "--input",
    type=click.Path(exists=True),
    required=True,
    help="Input directory containing HEIC files",
)
@click.option(
    "--output",
    type=click.Path(),
    required=True,
    help="Output directory for processed files",
)
@click.option(
    "--extract-videos/--no-extract-videos",
    default=None,
    help="Extract video components from Live Photos",
)
@click.option(
    "--keep-original/--remove-original",
    default=None,
    help="Keep original HEIC files after processing",
)
def process_heic(input, output, extract_videos, keep_original):
    """Process HEIC files to extract videos and convert images."""
    try:
        processor = HEICProcessor()

        # Override config if options provided
        if extract_videos is not None:
            processor.extract_videos = extract_videos
        if keep_original is not None:
            processor.keep_original = keep_original

        input_path = Path(input)
        output_path = Path(output)

        # Process directory
        results = processor.process_directory(input_path, output_path)

        # Summary
        total_files = len(results)
        successful_images = sum(1 for r in results if r["image_file"])
        successful_videos = sum(1 for r in results if r["video_file"])
        errors = sum(1 for r in results if r["errors"])

        click.echo(f"✓ Processed {total_files} HEIC files:")
        click.echo(f"  • {successful_images} images converted")
        click.echo(f"  • {successful_videos} videos extracted")
        if errors:
            click.echo(f"  • {errors} files had errors")

    except Exception as e:
        click.echo(f"✗ Processing error: {e}")


@cli.command()
@click.option(
    "--input",
    type=click.Path(exists=True),
    required=True,
    help="Input directory containing images",
)
@click.option("--quality", type=int, help="JPEG quality (1-100)")
@click.option("--max-size", help="Maximum image size (e.g., 1920x1080)")
@click.option(
    "--output",
    type=click.Path(),
    help="Output directory (default: overwrites originals)",
)
def optimize(input, quality, max_size, output):
    """Optimize images to reduce file size."""
    try:
        optimizer = ImageOptimizer()

        # Override config if options provided
        if quality:
            optimizer.quality = quality
        if max_size:
            try:
                width, height = max_size.split("x")
                optimizer.max_size = (int(width), int(height))
            except ValueError:
                click.echo(
                    f"✗ Invalid max-size format: {max_size}. Use format like '1920x1080'"  # noqa E501
                )
                return

        input_path = Path(input)
        output_path = Path(output) if output else None

        # Process directory
        results = optimizer.optimize_directory(input_path, output_path)

        # Summary
        total_files = len(results)
        successful = sum(1 for r in results if r["success"])
        total_size_before = sum(r["size_before"] for r in results if r["success"])
        total_size_after = sum(r["size_after"] for r in results if r["success"])

        if total_size_before > 0:
            reduction_percent = (
                (total_size_before - total_size_after) / total_size_before
            ) * 100

            click.echo(f"✓ Optimized {successful}/{total_files} images:")
            click.echo(f"  • Size reduction: {reduction_percent:.1f}%")
            click.echo(f"  • Before: {total_size_before / 1024 / 1024:.1f} MB")
            click.echo(f"  • After: {total_size_after / 1024 / 1024:.1f} MB")

    except Exception as e:
        click.echo(f"✗ Optimization error: {e}")


@cli.command()
@click.option(
    "--path",
    type=click.Path(exists=True),
    required=True,
    help="Directory to search for duplicates",
)
@click.option(
    "--method",
    type=click.Choice(["hash", "perceptual"]),
    default="hash",
    help="Duplicate detection method",
)
@click.option(
    "--delete", is_flag=True, help="Delete duplicate files (use with caution!)"
)
def duplicates(path, method, delete):
    """Find and optionally remove duplicate photos."""
    try:
        finder = DuplicateFinder()

        search_path = Path(path)

        # Find duplicates
        duplicate_groups = finder.find_duplicates(search_path, method=method)

        if not duplicate_groups:
            click.echo("No duplicates found.")
            return

        total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
        click.echo(
            f"Found {len(duplicate_groups)} groups with {total_duplicates} duplicate files:"  # noqa E501
        )

        for i, group in enumerate(duplicate_groups, 1):
            click.echo(f"\nGroup {i} ({len(group)} files):")
            for file_path in group:
                size = file_path.stat().st_size / 1024 / 1024
                click.echo(f"  • {file_path} ({size:.1f} MB)")

            if delete:
                # Keep the first file, delete the rest
                files_to_delete = group[1:]
                for file_path in files_to_delete:
                    try:
                        file_path.unlink()
                        click.echo(f"    Deleted: {file_path}")
                    except Exception as e:
                        click.echo(f"    Error deleting {file_path}: {e}")

        if delete:
            click.echo(f"\n✓ Deleted {total_duplicates} duplicate files")

    except Exception as e:
        click.echo(f"✗ Duplicate detection error: {e}")


@cli.command()
def config_info():
    """Show current configuration."""
    click.echo("Current Configuration:")
    click.echo(f"  • Credentials file: {config.credentials_file}")
    click.echo(f"  • Token file: {config.token_file}")
    click.echo(f"  • Download path: {config.default_download_path}")
    click.echo(f"  • HEIC extract videos: {config.heic_extract_videos}")
    click.echo(f"  • HEIC keep original: {config.heic_keep_original}")
    click.echo(f"  • Optimize quality: {config.optimize_quality}")
    click.echo(f"  • Max image size: {config.max_image_size}")
    click.echo(f"  • Max workers: {config.max_workers}")

    # Validate configuration
    errors = config.validate()
    if errors:
        click.echo("\nConfiguration Errors:")
        for error in errors:
            click.echo(f"  ✗ {error}")
    else:
        click.echo("\n✓ Configuration is valid")


def main():
    """Main entry point for the CLI."""
    return cli()


if __name__ == "__main__":
    main()
