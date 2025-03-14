from src.config import Config
from src.drive_service import DriveService
from src.backup_finder import BackupFinder
from src.downloader import Downloader
import os

def main():
    print("WhatsApp Backup Downloader")
    print("=========================")
    
    # Initialize configuration
    config = Config()
    
    try:
        # Initialize Google Drive service
        print("Connecting to Google Drive...")
        drive_service = DriveService(config)
        
        # Recherche spécifique du dossier "Sauvegardes"
        print("Recherche du dossier Sauvegardes...")
        backups_folder_query = "name = 'Sauvegardes' and mimeType = 'application/vnd.google-apps.folder'"
        backups_folders = drive_service.list_files(query=backups_folder_query)
        
        if backups_folders:
            print(f"Dossier 'Sauvegardes' trouvé! ID: {backups_folders[0]['id']}")
            # Lister le contenu du dossier Sauvegardes
            folder_content_query = f"'{backups_folders[0]['id']}' in parents"
            folder_contents = drive_service.list_files(query=folder_content_query)
            print(f"Contenu du dossier 'Sauvegardes': {len(folder_contents)} fichiers/dossiers")
            
            for item in folder_contents:
                print(f"- {item.get('name')} (Type: {item.get('mimeType')})")
        
        # Find WhatsApp backups
        print("\nRecherche des sauvegardes WhatsApp...")
        backup_finder = BackupFinder(drive_service)
        backups = backup_finder.find_backups()
        
        # Download backups
        downloader = Downloader(drive_service, config)
        success = downloader.download_backups(backups)
        
        if success:
            print("\nTéléchargement des sauvegardes terminé!")
            print(f"Fichiers sauvegardés dans: {os.path.abspath(config.backup_dir)}")
        else:
            print("\nAucune sauvegarde n'a été téléchargée.")
            print("\nVérification supplémentaire - Recherche manuelle de tous les fichiers contenant 'WhatsApp'...")
            
            # Recherche élargie en dernier recours
            whatsapp_query = "name contains 'WhatsApp'"
            whatsapp_files = drive_service.list_files(query=whatsapp_query)
            
            if whatsapp_files:
                print(f"Trouvé {len(whatsapp_files)} fichiers contenant 'WhatsApp' dans le nom:")
                for file in whatsapp_files:
                    print(f"- {file.get('name')} (ID: {file.get('id')}, Type: {file.get('mimeType')})")
                
                # Option pour télécharger ces fichiers
                print("\nVoulez-vous télécharger ces fichiers? (y/n)")
                response = input().strip().lower()
                
                if response == 'y':
                    manual_download_dir = os.path.join(config.backup_dir, 'manual')
                    os.makedirs(manual_download_dir, exist_ok=True)
                    
                    for file in whatsapp_files:
                        file_path = os.path.join(manual_download_dir, file.get('name', f"whatsapp_file_{file.get('id')}"))
                        print(f"Téléchargement de {file.get('name')}...")
                        try:
                            drive_service.download_file(file.get('id'), file_path)
                            print(f"Téléchargé avec succès vers {file_path}")
                        except Exception as e:
                            print(f"Erreur lors du téléchargement: {str(e)}")
            else:
                print("Aucun fichier contenant 'WhatsApp' n'a été trouvé dans votre Google Drive.")
                print("Assurez-vous que les sauvegardes WhatsApp existent dans votre Google Drive.")
            
    except Exception as e:
        print(f"Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()