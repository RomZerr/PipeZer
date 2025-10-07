import os
import shutil
from Packages.logic.filefunc import get_funcs

def increment_file_external(file_path: str) -> str:
    """
    Copie un fichier spécifié vers le même répertoire en incrémentant le suffixe numérique
    au nom du fichier pour le différencier de la version précédente.

    Args:
        file_path (str): Le chemin absolu du fichier à copier.

    Returns:
        str: Le chemin absolu du nouveau fichier créé avec un nom incrémenté.
    """
    # Vérifier si le fichier existe
    if not os.path.isfile(file_path):
        print(f"Erreur : Le fichier spécifié n'existe pas : {file_path}")
        return None

    parent_directory: str = os.path.dirname(file_path)

    # Obtenir le nouveau nom de fichier incrémenté
    new_file_name: str = get_funcs.return_increment_edit(file_path)

    if new_file_name is None:
        print("Erreur : Impossible d'incrémenter le fichier car aucune correspondance n'a été trouvée.")
        return None

    new_file_path: str = os.path.join(parent_directory, new_file_name)

    # Vérifier que le chemin de destination n'existe pas déjà
    if os.path.exists(new_file_path):
        print(f"Erreur : Le fichier de destination existe déjà : {new_file_path}")
        return None

    # Copier le fichier vers le nouveau chemin
    try:
        shutil.copy(file_path, new_file_path)
        print(f"Fichier incrémenté créé avec succès : {new_file_path}")
        return new_file_path
    except Exception as e:
        print(f"Erreur lors de la copie du fichier : {e}")
        return None
