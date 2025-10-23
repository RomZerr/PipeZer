"""
Utilitaires pour ouvrir l'explorateur Windows
"""

import os
import subprocess
import platform

def open_in_explorer(file_path):
    """
    Ouvre l'explorateur Windows à l'emplacement du fichier
    
    Args:
        file_path (str): Chemin vers le fichier ou dossier
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le chemin n'existe pas: {file_path}")
        
        # Normaliser le chemin pour Windows
        normalized_path = os.path.normpath(file_path)
        
        # Ouvrir l'explorateur Windows avec le fichier sélectionné
        if platform.system() == "Windows":
            # Utiliser la syntaxe correcte pour Windows
            try:
                # Méthode 1: avec /select, (sans check=True pour éviter l'exception)
                result = subprocess.run(['explorer', '/select,', normalized_path], 
                                      capture_output=True, text=True)
                # Si ça marche, on s'arrête là
                if result.returncode == 0:
                    return
            except Exception:
                pass
            
            # Méthode 2: ouvrir le dossier parent seulement si la première méthode a échoué
            try:
                subprocess.run(['explorer', os.path.dirname(normalized_path)], 
                             capture_output=True, text=True)
            except Exception:
                # Méthode 3: utiliser start en dernier recours
                subprocess.run(['start', '', os.path.dirname(normalized_path)], 
                             shell=True, capture_output=True, text=True)
        else:
            # Pour les autres systèmes (Linux, macOS)
            subprocess.run(['xdg-open', os.path.dirname(normalized_path)], 
                         capture_output=True, text=True)
            
    except Exception as e:
        # Ne pas lever d'exception, juste imprimer l'erreur
        print(f"Erreur lors de l'ouverture de l'explorateur: {e}")

def open_folder_in_explorer(folder_path):
    """
    Ouvre l'explorateur Windows dans le dossier spécifié
    
    Args:
        folder_path (str): Chemin vers le dossier
    """
    try:
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Le dossier n'existe pas: {folder_path}")
        
        if not os.path.isdir(folder_path):
            raise ValueError(f"Le chemin n'est pas un dossier: {folder_path}")
        
        # Normaliser le chemin pour Windows
        normalized_path = os.path.normpath(folder_path)
        
        # Ouvrir l'explorateur Windows dans le dossier
        if platform.system() == "Windows":
            subprocess.run(['explorer', normalized_path], check=True)
        else:
            # Pour les autres systèmes (Linux, macOS)
            subprocess.run(['xdg-open', normalized_path], check=True)
            
    except subprocess.CalledProcessError as e:
        raise Exception(f"Erreur lors de l'ouverture de l'explorateur: {e}")
    except Exception as e:
        raise Exception(f"Erreur inattendue: {e}")
