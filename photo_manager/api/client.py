"""
Google Photos API client implementation.
"""

from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from tqdm import tqdm

from photo_manager.auth import GooglePhotosAuth
from photo_manager.config import config


class GooglePhotosAPI:
    """Google Photos API client for managing photo library."""

    def __init__(self, auth_handler: Optional[GooglePhotosAuth] = None):
        """
        Initialize the Google Photos API client.

        Args:
            auth_handler: Authentication handler instance
        """
        self.auth = auth_handler or GooglePhotosAuth()
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the Google Photos API service."""
        try:
            credentials = self.auth.authenticate()
            self.service = build("photoslibrary", "v1", credentials=credentials)
        except Exception as e:
            raise Exception(f"Failed to initialize Google Photos API: {e}") from e

    def list_albums(
        self, page_size: int = 50
    ) -> Generator[
        Dict[str, Any],
        None,
        None,
    ]:
        """
        List all albums in the user's Google Photos library.

        Args:
            page_size: Number of albums per page

        Yields:
            Album information dictionaries
        """
        page_token = None

        while True:
            try:
                request_body = {
                    "pageSize": min(page_size, 50),  # API limit is 50
                }

                if page_token:
                    request_body["pageToken"] = page_token

                response = self.service.albums().list(**request_body).execute()

                albums = response.get("albums", [])
                yield from albums

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            except HttpError as e:
                print(f"Error listing albums: {e}")
                break

    def get_album_by_name(self, album_name: str) -> Optional[Dict[str, Any]]:
        """
        Get album by name.

        Args:
            album_name: Name of the album to find

        Returns:
            Album information or None if not found
        """
        for album in self.list_albums():
            if album.get("title", "").lower() == album_name.lower():
                return album
        return None

    def list_media_items(
        self, album_id: Optional[str] = None, page_size: int = 100
    ) -> Generator[Dict[str, Any], None, None]:
        """
        List media items from library or specific album.

        Args:
            album_id: Optional album ID to filter by
            page_size: Number of items per page

        Yields:
            Media item dictionaries
        """
        page_token = None

        while True:
            try:
                request_body = {
                    "pageSize": min(page_size, 100),  # API limit is 100
                }

                if album_id:
                    request_body["albumId"] = album_id

                if page_token:
                    request_body["pageToken"] = page_token

                if album_id:
                    response = (
                        self.service.mediaItems().search(body=request_body).execute()
                    )
                else:
                    response = self.service.mediaItems().list(**request_body).execute()

                media_items = response.get("mediaItems", [])
                yield from media_items

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            except HttpError as e:
                print(f"Error listing media items: {e}")
                break

    def download_media_item(
        self,
        media_item: Dict[str, Any],
        download_path: Path,
        preserve_structure: bool = True,
    ) -> Optional[Path]:
        """
        Download a single media item.

        Args:
            media_item: Media item dictionary from API
            download_path: Base download directory
            preserve_structure: Whether to preserve date-based folder structure

        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Get the download URL
            base_url = media_item.get("baseUrl", "")
            if not base_url:
                print(f"No download URL for {media_item.get('filename', 'Unknown')}")
                return None

            # Determine file path
            filename = media_item.get("filename", "unknown_file")

            if preserve_structure:
                # Create date-based folder structure
                creation_time = media_item.get("mediaMetadata", {}).get(
                    "creationTime", ""
                )
                if creation_time:
                    try:
                        # Parse date and create folder structure
                        date_obj = datetime.fromisoformat(
                            creation_time.replace("Z", "+00:00")
                        )
                        folder_path = (
                            download_path / str(date_obj.year) / f"{date_obj.month:02d}"
                        )
                    except Exception:
                        folder_path = download_path / "unknown_date"
                else:
                    folder_path = download_path / "unknown_date"
            else:
                folder_path = download_path

            # Create directory if it doesn't exist
            folder_path.mkdir(parents=True, exist_ok=True)

            file_path = folder_path / filename

            # Skip if file already exists
            if file_path.exists():
                return file_path

            # Download the file
            download_url = f"{base_url}=d"  # =d parameter for download

            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()

            # Write file in chunks
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return file_path

        except Exception as e:
            print(f"Error downloading {media_item.get('filename', 'Unknown')}: {e}")
            return None

    def download_album(
        self, album_name: str, download_path: Path, max_workers: Optional[int] = None
    ) -> List[Path]:
        """
        Download all photos from an album.

        Args:
            album_name: Name of the album to download
            download_path: Directory to save photos
            max_workers: Number of concurrent downloads

        Returns:
            List of downloaded file paths
        """
        # Find the album
        album = self.get_album_by_name(album_name)
        if not album:
            raise ValueError(f"Album '{album_name}' not found")

        album_id = album["id"]
        print(f"Downloading album: {album_name}")

        # Get all media items
        media_items = list(self.list_media_items(album_id=album_id))

        if not media_items:
            print("No media items found in album")
            return []

        # Set up download parameters
        max_workers = max_workers or config.max_workers
        downloaded_files = []

        # Create album-specific folder
        album_path = download_path / album_name
        album_path.mkdir(parents=True, exist_ok=True)

        # Download with progress bar
        with tqdm(total=len(media_items), desc="Downloading") as pbar:
            if config.use_threading and len(media_items) > 1:
                # Multi-threaded download
                with ThreadPoolExecutor(max_workers=max_workers) as executor:

                    def download_with_progress(item):
                        result = self.download_media_item(item, album_path)
                        pbar.update(1)
                        return result

                    futures = [
                        executor.submit(download_with_progress, item)
                        for item in media_items
                    ]

                    for future in futures:
                        result = future.result()
                        if result:
                            downloaded_files.append(result)
            else:
                # Single-threaded download
                for item in media_items:
                    result = self.download_media_item(item, album_path)
                    if result:
                        downloaded_files.append(result)
                    pbar.update(1)

        print(f"Downloaded {len(downloaded_files)} files to {album_path}")
        return downloaded_files

    def get_media_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific media item by ID.

        Args:
            item_id: Media item ID

        Returns:
            Media item dictionary or None if not found
        """
        try:
            response = self.service.mediaItems().get(mediaItemId=item_id).execute()
            return response
        except HttpError as e:
            print(f"Error getting media item {item_id}: {e}")
            return None

    def search_media_items(
        self, filters: Dict[str, Any], page_size: int = 100
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Search media items with filters.

        Args:
            filters: Search filters (dates, media types, etc.)
            page_size: Number of items per page

        Yields:
            Media item dictionaries
        """
        page_token = None

        while True:
            try:
                request_body = {"pageSize": min(page_size, 100), "filters": filters}

                if page_token:
                    request_body["pageToken"] = page_token

                response = self.service.mediaItems().search(body=request_body).execute()

                media_items = response.get("mediaItems", [])
                yield from media_items

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            except HttpError as e:
                print(f"Error searching media items: {e}")
                break
