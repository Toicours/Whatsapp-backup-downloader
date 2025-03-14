from tqdm import tqdm

class BackupFinder:
    # WhatsApp backup MIME types and identifiers
    WHATSAPP_DB_MIME = 'application/x-sqlite3'
    WHATSAPP_MEDIA_MIME = 'application/x-tar'
    WHATSAPP_PACKAGE = 'com.whatsapp'
    WHATSAPP_MIME_TYPES = [
        'application/x-sqlite3',
        'application/x-tar',
        'application/octet-stream',
        'application/vnd.android.package-archive',
        'application/zip',
        'application/x-zip',
        'application/x-gzip',
        'application/x-compressed',
        'application/x-7z-compressed'
    ]
    
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
        
        # Méthode 5: Recherche spécifique dans les dossiers "hidden" ou spéciaux de Google Drive
        # Cette méthode explore tous les fichiers qui pourraient être des sauvegardes WhatsApp
        # basés sur leur type MIME, même s'ils n'ont pas "WhatsApp" dans leur nom
        special_mime_files = []
        
        for mime_type in self.WHATSAPP_MIME_TYPES:
            query = f"mimeType='{mime_type}'"
            results = self.drive_service.list_files(query=query)
            print(f"Cherche des fichiers avec le type MIME '{mime_type}': {len(results)} trouvés")
            
            for file in results:
                print(f"- {file.get('name', 'Sans nom')} ({file.get('mimeType', 'Type inconnu')})")
            
            special_mime_files.extend(results)
        
        # Méthode 6: Rechercher les fichiers cachés ou ".db"
        hidden_query = "name contains '.db' or name contains '.crypt'"
        hidden_files = self.drive_service.list_files(query=hidden_query)
        print(f"Fichiers .db ou .crypt trouvés: {len(hidden_files)}")
        for file in hidden_files:
            print(f"- {file.get('name', 'Sans nom')} ({file.get('mimeType', 'Type inconnu')})")
        
        # Méthode 7: Rechercher explicitement dans l'espace de stockage "appDataFolder"
        try:
            app_data_files = self.drive_service.service.files().list(
                spaces='appDataFolder',
                fields='files(id, name, mimeType, size)'
            ).execute().get('files', [])
            
            print(f"Fichiers trouvés dans l'espace appDataFolder: {len(app_data_files)}")
            for file in app_data_files:
                print(f"- {file.get('name', 'Sans nom')} ({file.get('mimeType', 'Type inconnu')})")
                
            special_mime_files.extend(app_data_files)
        except Exception as e:
            print(f"Impossible d'accéder à l'espace appDataFolder: {str(e)}")
        
        # Méthode 8: Rechercher tous les fichiers modifiés récemment
        # Cette méthode utilise la date de modification comme indice pour trouver les sauvegardes récentes
        try:
            recent_query = "modifiedTime > '2023-01-01T00:00:00'"
            recent_files = self.drive_service.list_files(query=recent_query, fields='files(id, name, mimeType, size, modifiedTime)')
            print(f"Fichiers modifiés récemment: {len(recent_files)} (seulement les 10 premiers affichés)")
            
            for i, file in enumerate(recent_files[:10]):
                print(f"- {file.get('name', 'Sans nom')} (Modifié: {file.get('modifiedTime', 'Date inconnue')})")
                
            # Ajouter seulement ceux qui ont un type MIME intéressant
            special_mime_files.extend([f for f in recent_files if f.get('mimeType') in self.WHATSAPP_MIME_TYPES])
        except Exception as e:
            print(f"Erreur lors de la recherche de fichiers récents: {str(e)}")
        
        # Consolider tous les résultats
        all_potential_backups = db_backups + media_backups + whatsapp_backups + all_backups + phone_backups + special_mime_files + hidden_files
        
        # Déduplication basée sur l'ID de fichier
        unique_backups = {}
        for backup in all_potential_backups:
            file_id = backup.get('id')
            if file_id:
                unique_backups[file_id] = backup
        
        # Organiser par type (si possible)
        database_backups = []
        media_backups = []
        other_backups = []
        
        for backup in unique_backups.values():
            name = backup.get('name', '').lower()
            mime = backup.get('mimeType', '')
            
            if 'database' in name or 'msgstore' in name or '.db' in name or mime == self.WHATSAPP_DB_MIME:
                database_backups.append(backup)
            elif 'media' in name or mime == self.WHATSAPP_MEDIA_MIME:
                media_backups.append(backup)
            else:
                # Filtrer les fichiers qui ne sont probablement pas des sauvegardes WhatsApp
                if self._is_whatsapp_backup(backup) or self._is_potentially_whatsapp_data(backup):
                    other_backups.append(backup)
        
        # Afficher les résultats pour le débogage
        print(f"Trouvé {len(database_backups)} sauvegardes de base de données potentielles")
        print(f"Trouvé {len(media_backups)} sauvegardes de médias potentielles")
        print(f"Trouvé {len(other_backups)} autres sauvegardes potentielles")
        
        for backup in database_backups:
            print(f"Sauvegarde de base de données trouvée: {backup.get('name')} (Type: {backup.get('mimeType')})")
            
        for backup in media_backups:
            print(f"Sauvegarde de médias trouvée: {backup.get('name')} (Type: {backup.get('mimeType')})")
            
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
            'compte whatsapp' in name,
            'backup' in name and ('whatsapp' in name or 'wa' in name),
            'msgstore' in name
        ]
        
        return any(whatsapp_indicators)
    
    def _is_potentially_whatsapp_data(self, file_info):
        """Check if a file could potentially be WhatsApp related data."""
        name = file_info.get('name', '').lower()
        mime = file_info.get('mimeType', '').lower()
        
        # Types de fichiers qui pourraient être liés à WhatsApp
        potential_indicators = [
            # Extensions de fichiers
            '.db' in name,
            '.crypt' in name,
            '.bak' in name,
            
            # Types MIME
            mime in self.WHATSAPP_MIME_TYPES,
            
            # Noms de fichiers de base de données WhatsApp
            'msgstore' in name,
            'wa.db' in name,
            'chatstore' in name,
            'chatsettings' in name,
            
            # Autres indices
            '3376340848' in name,  # Le numéro de téléphone repéré précédemment
        ]
        
        return any(potential_indicators) and 'image' not in mime and 'jpeg' not in mime