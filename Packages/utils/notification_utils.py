"""
Utilities for managing notifications
"""

import os
import json
from datetime import datetime


def get_username():
    """Récupère le nom d'utilisateur depuis le fichier JSON."""
    try:
        from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT
        usernames_file = os.path.join(CURRENT_PROJECT, 'ProjectFiles', 'Infos', 'usernames.json')
        if os.path.exists(usernames_file):
            with open(usernames_file, 'r') as f:
                data = json.load(f)
                return data.get('current_user', 'Unknown')
    except Exception as e:
        print(f"Erreur lors de la récupération du nom d'utilisateur : {e}")
    return 'Unknown'


def add_notification(username, action, file_name):
    """Ajoute une notification dans le fichier JSON."""
    try:
        from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT
        notif_file_path = os.path.join(CURRENT_PROJECT, '.pipezer_data', 'notifs.json')
        
        notification = {
            "username": username,
            "action": action,
            "file": file_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if os.path.exists(notif_file_path):
            with open(notif_file_path, 'r') as notif_file:
                data = json.load(notif_file)
                if not isinstance(data, list):
                    data = []
        else:
            data = []
            # Créer le dossier .pipezer_data s'il n'existe pas
            os.makedirs(os.path.dirname(notif_file_path), exist_ok=True)

        data.append(notification)

        with open(notif_file_path, 'w') as notif_file:
            json.dump(data, notif_file, indent=4)

        print(f"Notification ajoutée : {notification}")

    except Exception as e:
        print(f"Erreur lors de l'ajout d'une notification : {e}")

