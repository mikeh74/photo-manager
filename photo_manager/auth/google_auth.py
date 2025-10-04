"""
Google Photos API authentication handler.
"""

import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from photo_manager.config import config


class GooglePhotosAuth:
    """Handle Google Photos API authentication."""

    def __init__(self):
        """Initialize the authentication handler."""
        self.credentials: Credentials | None = None
        self.scopes = config.google_photos_scopes
        self.credentials_file = config.credentials_file
        self.token_file = config.token_file

    def authenticate(self, force_refresh: bool = False) -> Credentials:
        """
        Authenticate with Google Photos API.

        Args:
            force_refresh: Force re-authentication even if token exists

        Returns:
            Google OAuth2 credentials

        Raises:
            FileNotFoundError: If credentials file is missing
            Exception: If authentication fails
        """
        if not force_refresh and self.credentials and self.credentials.valid:
            return self.credentials

        # Load existing token if available
        if not force_refresh and self.token_file.exists():
            try:
                with open(self.token_file, "rb") as token_file:
                    self.credentials = pickle.load(token_file)  # noqa: S301
            except Exception as e:
                print(f"Error loading saved token: {e}")
                self.credentials = None

        # Refresh token if it's expired
        if (
            self.credentials
            and not self.credentials.valid
            and self.credentials.expired
            and self.credentials.refresh_token
        ):
            try:
                self.credentials.refresh(Request())
                self._save_token()
                return self.credentials
            except Exception as e:
                print(f"Error refreshing token: {e}")
                self.credentials = None

        # If we have valid credentials, return them
        if self.credentials and self.credentials.valid:
            return self.credentials

        # Perform new authentication flow
        return self._perform_auth_flow()

    def _perform_auth_flow(self) -> Credentials:
        """Perform OAuth2 authentication flow."""
        if not self.credentials_file.exists():
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_file}\n"
                "Please download it from Google Cloud Console and place it "
                "in the project root directory."
            )

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_file), self.scopes
            )

            # Run local server for authentication
            self.credentials = flow.run_local_server(
                port=0,
                prompt="select_account",
            )

            # Save the credentials for the next run
            self._save_token()

            print("Authentication successful!")
            return self.credentials

        except Exception as e:
            raise Exception(f"Authentication failed: {e}") from e

    def _save_token(self):
        """Save credentials to token file."""
        try:
            # Ensure token directory exists
            self.token_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.token_file, "wb") as token_file:
                pickle.dump(self.credentials, token_file)

            print(f"Token saved to {self.token_file}")

        except Exception as e:
            print(f"Warning: Could not save token: {e}")

    def revoke_token(self):
        """Revoke the current authentication token."""
        if self.credentials:
            try:
                self.credentials.revoke(Request())
                print("Token revoked successfully")
            except Exception as e:
                print(f"Error revoking token: {e}")

        # Remove saved token file
        if self.token_file.exists():
            try:
                self.token_file.unlink()
                print("Saved token file removed")
            except Exception as e:
                print(f"Error removing token file: {e}")

        self.credentials = None

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self.credentials is not None and self.credentials.valid

    def get_user_info(self) -> dict | None:
        """Get basic user information if available."""
        if not self.is_authenticated():
            return None

        # For Google Photos API, user info would come from
        # the People API or OAuth token info
        return {
            "authenticated": True,
            "scopes": self.scopes,
            "token_file": str(self.token_file),
        }
