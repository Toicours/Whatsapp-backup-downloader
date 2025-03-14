from tqdm import tqdm

class BackupFinder:
    # WhatsApp backup MIME types and identifiers
    WHATSAPP_DB_MIME = 'application/x-sqlite3'
    WHATSAPP_MEDIA_MIME = 'application/x-tar'
    WHATSAPP_PACKAGE = 'com.whatsapp'
    
    def __init__(self, drive_service):
        self.drive_service = drive_service
    
    def find_backups(self):
        """Find WhatsApp backups in Google Drive."""
        print("Searching for WhatsApp backups...")
        
        # Méthode 1: Chercher les fichiers spécifiques à WhatsApp en utilisant les types MIME
        db_query = f"mimeType='{self.WHATSAPP_DB_MIME}' and name contains '{self.WHATSAPP_PACKAGE}'"
        db_backups = self.drive_service.list_files(query=db_query)
        
        media_query = f"mimeType='{self.WHATSAPP_MEDIA_MIME}' and name contains '{self.WHATSAPP_PACKAGE}'"
        media_backups = self.drive_service.list_files(query=media_query)
        
        # Méthode 2: Chercher explicitement les sauvegardes WhatsApp par nom
        whatsapp_name_query = "name contains 'WhatsApp' and name contains 'sauvegarde'"
        whatsapp_backups = self.drive_service.list_files(query=whatsapp_name_query)
        
        # Méthode 3: Chercher dans la section "Sauvegardes" de Google Drive
        # Cette requête cherche les fichiers dans le dossier "Sauvegardes" qui contiennent "WhatsApp"
        backups_query = "name contains 'WhatsApp' and mimeType!='application/vnd.google-apps.folder'"
        all_backups = self.drive_service.list_files(query=backups_query)
        
        # Méthode 4: Chercher explicitement par le numéro de téléphone dans le nom (si visible)
        # Si vous connaissez votre numéro de téléphone associé, vous pouvez le spécifier ici
        phone_number = "3376340848"  # Extrait de votre capture d'écran
        phone_query = f"name contains '{phone_number}'"
        phone_backups = self.drive_service.list_files(query=phone_query)
        
        # Consolider tous les résultats
        all_potential_backups = db_backups + media_backups + whatsapp_backups + all_backups + phone_backups
        
        # Déduplication basée sur l'ID de fichier
        unique_backups = {}
        for backup in all_potential_backups:
            if self._is_whatsapp_backup(backup):
                unique_backups[backup['id']] = backup
        
        # Organiser par type (si possible)
        database_backups = []
        media_backups = []
        other_backups = []
        
        for backup in unique_backups.values():
            name = backup.get('name', '').lower()
            mime = backup.get('mimeType', '')
            
            if 'database' in name or mime == self.WHATSAPP_DB_MIME:
                database_backups.append(backup)
            elif 'media' in name or mime == self.WHATSAPP_MEDIA_MIME:
                media_backups.append(backup)
            else:
                other_backups.append(backup)
        
        # Afficher les résultats pour le débogage
        print(f"Trouvé {len(database_backups)} sauvegardes de base de données potentielles")
        print(f"Trouvé {len(media_backups)} sauvegardes de médias potentielles")
        print(f"Trouvé {len(other_backups)} autres sauvegardes potentielles")
        
        for backup in other_backups:
            print(f"Autre sauvegarde trouvée: {backup.get('name')} (Type: {backup.get('mimeType')})")
        
        return {
            'database': database_backups,
            'media': media_backups,
            'other': other_backups
        }
    
    def _is_whatsapp_backup(self, file_info):
        """Check if a file is likely a WhatsApp backup."""
        name = file_info.get('name', '').lower()
        mime = file_info.get('mimeType', '').lower()
        
        # Vérifier si c'est probablement une sauvegarde WhatsApp
        whatsapp_indicators = [
            'whatsapp' in name,
            self.WHATSAPP_PACKAGE in name,
            'sauvegarde' in name and 'whatsapp' in name,
            mime in [self.WHATSAPP_DB_MIME, self.WHATSAPP_MEDIA_MIME],
            'compte whatsapp' in name
        ]
        
        return any(whatsapp_indicators)