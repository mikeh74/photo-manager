# Google Photos API Setup Guide

This guide will help you set up Google Photos API credentials for the Phot
Manager application.

## Prerequisites

1. A Google account with Google Photos
2. Access to Google Cloud Console

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "New Project"
4. Enter project name: "Photo Manager" (or your preferred name)
5. Click "Create"

### 2. Enable the Photos Library API

1. In the Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Photos Library API"
3. Click on "Photos Library API"
4. Click "Enable"

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted to configure OAuth consent screen:

   - Choose "External" (unless you have a G Suite account)
   - Fill in required fields:
     - App name: "Photo Manager"
     - User support email: your email
     - Developer contact information: your email
   - Click "Save and Continue"
   - Add scopes (optional for testing)
   - Add test users (your email address)
   - Click "Save and Continue"

4. Back to creating OAuth client ID:

   - Application type: "Desktop application"
   - Name: "Photo Manager Desktop"
   - Click "Create"

5. Download the JSON file and save it as `credentials.json` in your project
root directory

### 4. Configure Environment

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file if needed (defaults should work)

### 5. First-Time Authentication

Run the authentication command:

```bash
python -m photo_manager auth
```

This will:

1. Open your web browser
2. Ask you to sign in to Google
3. Ask for permission to access your Photos
4. Save an authentication token for future use

## Security Notes

- Keep `credentials.json` and `token.json` files secure
- Never commit these files to version control
- The application only requests read access to your photos
- You can revoke access anytime in your Google Account settings

## Troubleshooting

### "API has not been used" Error

- Make sure you enabled the Photos Library API in step 2
- Wait a few minutes after enabling the API

### "Access blocked" Error

- Make sure you added your email as a test user in the OAuth consent screen
- If your app is in "Testing" mode, only test users can access it

### "Invalid client" Error

- Check that `credentials.json` is in the correct location
- Verify the file wasn't corrupted during download

## API Quotas

Google Photos API has the following quotas:

- 10,000 requests per day (free tier)
- 100 requests per 100 seconds per user

The application respects these limits and will handle rate limiting automatically.

## Next Steps

Once authentication is set up, you can:

- List your albums: `python -m photo_manager albums list`
- Download photos: `python -m photo_manager download --album "Album Name"`
- Process HEIC files: `python -m photo_manager process-heic --input ./photos
--output ./processed`
