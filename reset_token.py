#!/usr/bin/env python3
"""
Script pour réinitialiser le token d'authentification Google Drive.
Cela est nécessaire après avoir modifié les scopes (étendues) d'autorisation.
"""

import os
import sys

def main():
    token_file = 'token.json'
    
    if os.path.exists(token_file):
        os.remove(token_file)
        print(f"Le fichier '{token_file}' a été supprimé.")
        print("La prochaine fois que vous exécuterez le programme, une nouvelle authentification sera demandée.")
    else:
        print(f"Le fichier '{token_file}' n'existe pas.")
    
    # Vérifier si credentials.json existe
    if not os.path.exists('credentials.json'):
        print("ATTENTION: Le fichier 'credentials.json' n'a pas été trouvé.")
        print("Assurez-vous que ce fichier est présent avant d'exécuter le programme principal.")

if __name__ == "__main__":
    main()