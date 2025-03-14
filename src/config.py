import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Google Drive API credentials
        self.client_secret_file = os.getenv('CLIENT_SECRET_FILE', 'credentials.json')
        self.token_file = os.getenv('TOKEN_FILE', 'token.json')
        
        # WhatsApp backup settings
        self.backup_dir = os.getenv('BACKUP_DIR', 'whatsapp_backups')
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # API scopes required
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']