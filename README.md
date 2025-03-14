# WhatsApp Backup Downloader

A Python tool to download WhatsApp backups from Google Drive.

## Project Structure

```
whatsapp_backup_downloader/
├── .env                    # Environment variables (credentials)
├── .gitignore              # Git ignore file
├── README.md               # Project documentation
├── requirements.txt        # Dependencies
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration loader
│   ├── drive_service.py    # Google Drive API service
│   ├── backup_finder.py    # WhatsApp backup finder
│   └── downloader.py       # Backup downloader
└── main.py                 # Main entry point
```

## Setup

1. Create a Google Cloud Project and enable the Google Drive API:

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials JSON file and save it as `credentials.json` in the project root

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file based on the provided template or use the default settings

## Usage

Run the application:

```
python main.py
```

The first time you run the application, it will:

1. Open a browser window for Google authentication
2. Ask you to log in to the Google account where WhatsApp backups are stored
3. Request permission to access your Google Drive
4. Save the authentication token for future use

Backups will be downloaded to the directory specified in the `.env` file.

## Features

- Identifies and downloads WhatsApp database backups
- Identifies and downloads WhatsApp media backups
- Organizes backups into separate folders by type
- Reuses authentication to avoid repeated logins

## Notes

- WhatsApp backups are stored in a special format on Google Drive
- This tool identifies the backup files based on their MIME type and metadata
- Both database and media backups will be downloaded if available
