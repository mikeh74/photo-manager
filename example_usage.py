"""
Example script showing how to use the Google Photos Manager programmatically.
"""

from pathlib import Path

from photo_manager import GooglePhotosAPI, GooglePhotosAuth
from photo_manager.processors import DuplicateFinder, HEICProcessor, ImageOptimizer


def main():
    """Example usage of the photo manager."""

    # Initialize components
    auth = GooglePhotosAuth()
    api = GooglePhotosAPI(auth)
    heic_processor = HEICProcessor()
    optimizer = ImageOptimizer()
    duplicate_finder = DuplicateFinder()

    print("Google Photos Manager - Example Usage")
    print("=" * 40)

    # 1. List albums
    print("\n1. Listing first 5 albums:")
    album_count = 0
    for album in api.list_albums():
        print(
            f"  • {album.get('title', 'Untitled')} ({album.get('mediaItemsCount', '?')} items)"  # noqa E501
        )
        album_count += 1
        if album_count >= 5:
            break

    # 2. Download a specific album (uncomment to use)
    # print("\n2. Downloading album:")
    # downloaded_files = api.download_album(
    #     album_name="Your Album Name",
    #     download_path=Path("./downloads")
    # )
    # print(f"Downloaded {len(downloaded_files)} files")

    # 3. Process HEIC files in a directory
    print("\n3. Processing HEIC files:")
    heic_dir = Path("./sample_photos")  # Change to your HEIC directory
    if heic_dir.exists():
        results = heic_processor.process_directory(heic_dir, Path("./processed"))
        successful = sum(1 for r in results if r["image_file"] or r["video_file"])
        print(f"Processed {successful}/{len(results)} HEIC files successfully")
    else:
        print(f"Directory {heic_dir} not found - skipping HEIC processing")

    # 4. Optimize images
    print("\n4. Optimizing images:")
    images_dir = Path("./photos")  # Change to your photos directory
    if images_dir.exists():
        results = optimizer.optimize_directory(images_dir)
        successful = sum(1 for r in results if r["success"])
        if successful > 0:
            total_before = sum(r["size_before"] for r in results if r["success"])
            total_after = sum(r["size_after"] for r in results if r["success"])
            reduction = ((total_before - total_after) / total_before) * 100
            print(f"Optimized {successful} images with {reduction:.1f}% size reduction")
    else:
        print(f"Directory {images_dir} not found - skipping optimization")

    # 5. Find duplicates
    print("\n5. Finding duplicates:")
    search_dir = Path("./photos")  # Change to your photos directory
    if search_dir.exists():
        duplicates = duplicate_finder.find_duplicates(search_dir, method="hash")
        if duplicates:
            stats = duplicate_finder.get_duplicate_stats(duplicates)
            print(
                f"Found {stats['total_groups']} groups with {stats['total_duplicates']} duplicates"  # noqa E501
            )
            print(f"Potential space savings: {stats['total_size_mb']:.1f} MB")
        else:
            print("No duplicates found")
    else:
        print(f"Directory {search_dir} not found - skipping duplicate detection")

    print("\nExample completed!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have authenticated with: python -m photo_manager auth")
