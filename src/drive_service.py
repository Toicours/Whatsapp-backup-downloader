import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class DriveService:
    def __init__(self, config):
        self.config = config
        self.service = self._build_service()
    
    def _build_service(self):
        """Build and return a Google Drive service."""
        creds = None
        
        # Check if token file exists
        if os.path.exists(self.config.token_file):
            try:
                with open(self.config.token_file, 'r') as token:
                    creds_data = json.load(token)
                    creds = Credentials.from_authorized_user_info(creds_data, self.config.scopes)
            except Exception as e:
                print(f"Erreur lors de la lecture du token: {e}")
                # Si le fichier est corrompu ou dans un format incorrect, on le supprime
                os.remove(self.config.token_file)
                creds = None
            
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.client_secret_file, 
                    self.config.scopes
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for future runs
            with open(self.config.token_file, 'w') as token:
                token.write(creds.to_json())
        
        return build('drive', 'v3', credentials=creds)

    def list_files(self, query=None, fields='files(id, name, mimeType, size)'):
        """List files in Google Drive based on query."""
        results = []
        page_token = None
        
        try:
            while True:
                response = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields=f'nextPageToken, {fields}',
                    pageToken=page_token
                ).execute()
                
                results.extend(response.get('files', []))
                page_token = response.get('nextPageToken')
                
                if not page_token:
                    break
        except Exception as e:
            print(f"Erreur lors de la recherche avec la requête '{query}': {str(e)}")
            
        # Pour le débogage
        if query and 'WhatsApp' in query:
            print(f"Requête '{query}' a retourné {len(results)} résultats")
            
        return results
    
    def download_file(self, file_id, filepath):
        """Download a file from Google Drive."""
        from googleapiclient.http import MediaIoBaseDownload
        import io
        
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(filepath, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            
        return filepath