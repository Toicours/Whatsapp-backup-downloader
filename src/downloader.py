import os
from tqdm import tqdm

class Downloader:
    def __init__(self, drive_service, config):
        self.drive_service = drive_service
        self.config = config
    
    def download_backups(self, backups):
        """Download WhatsApp backups."""
        total_files = len(backups['database']) + len(backups['media']) + len(backups.get('other', []))
        
        if total_files == 0:
            print("No WhatsApp backups found.")
            return False
        
        print(f"Found a total of {total_files} WhatsApp backup files.")
        print(f"- {len(backups['database'])} database backups")
        print(f"- {len(backups['media'])} media backups")
        print(f"- {len(backups.get('other', []))} autres types de sauvegardes")
        
        # Download database backups
        self._download_backup_set(backups['database'], 'database')
        
        # Download media backups
        self._download_backup_set(backups['media'], 'media')
        
        # Download other backups (special formats, etc.)
        if 'other' in backups and backups['other']:
            self._download_backup_set(backups['other'], 'other')
        
        return True
    
    def _download_backup_set(self, backup_set, backup_type):
        """Download a set of backups (database or media)."""
        if not backup_set:
            print(f"No {backup_type} backups to download.")
            return
        
        # Create type-specific directory
        type_dir = os.path.join(self.config.backup_dir, backup_type)
        os.makedirs(type_dir, exist_ok=True)
        
        print(f"\nDownloading {len(backup_set)} {backup_type} backup(s)...")
        
        for backup in backup_set:
            file_id = backup['id']
            file_name = backup['name']
            file_size = backup.get('size', 'unknown size')
            
            print(f"Downloading {file_name} ({file_size} bytes)...")
            
            file_path = os.path.join(type_dir, file_name)
            self.drive_service.download_file(file_id, file_path)
            
            print(f"Successfully downloaded to {file_path}")