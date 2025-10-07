import os
import re
import datetime
import operator
from typing import Literal
from Packages.logic.filefunc.file_class import AssetFileInfos, SequenceFileInfos, ShotFileInfos


def get_items(directory_path: str, type: Literal['dir', 'file'], exclude_type: list = []) -> list:
    """
    Retourne une liste triée des noms d'éléments (fichiers ou répertoires) dans le chemin spécifié.

    Args:
    - directory_path (str): Chemin du répertoire où chercher les éléments.
    - type (str): Type d'éléments à rechercher ('dir' pour répertoires, 'file' pour fichiers).
    - exclude_type (list, optional): Liste des extensions à exclure pour les fichiers. Par défaut, vide.

    Returns:
    - list: Liste triée des noms des éléments correspondants aux critères spécifiés.
    """

    os_dict = {
        'dir': os.path.isdir,
        'file': os.path.isfile
    }

    if type not in ['dir', 'file']:
        raise ValueError("Le paramètre 'type' doit être soit 'dir' soit 'file'.")

    item_names = []
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)

        if item.endswith(tuple(exclude_type)):
            continue

        if os_dict[type](item_path):
            item_names.append(item)

    return sorted(item_names)


def get_dirs(directory_path: str) -> list[str]:
    print(f'Search directories in directory : {directory_path}')
    return get_items(directory_path=directory_path, type='dir')


def get_files(directory_path: str) -> list[str]:
    print(f'Search files in directory : {directory_path}')
    return get_items(directory_path=directory_path, type='file', exclude_type=[".txt", '.mel', '.db'])


def get_version_file(version: str, parent_directory: str) -> str:
    """
    Renvoie le nom du fichier contenant la version spécifiée dans le répertoire parent.
    """
    for file in get_files(parent_directory):
        if version in file:
            return file


def get_file_base_folder(filename: str):
    """
    Détermine le dossier de base du fichier.
    """
    if '_seq' in filename:
        if '_sh' in filename:
            return 'shot'
        return 'sequence'
    else:
        return 'asset'


def get_version_num(filename: str, is_usd: bool = False):
    """
    Récupère un numéro de version à trois chiffres à partir du nom de fichier spécifié.
    """
    if is_usd:
        return ''  # Pas de version pour les fichiers USD

    if '_E_' in filename:
        match = re.search(r'\d{3}', filename[::-1])
        if match:
            return match.group(0)[::-1]
        return ""

    elif '_P_' in filename:
        match = re.search(r'\d{3}', filename)
        if not match:
            return ''

        increment = match.group()
        base_folder = get_file_base_folder(filename)

        if base_folder == 'asset':
            infos = AssetFileInfos(filename)
            name = infos.asset_name()
        elif base_folder == 'sequence':
            infos = SequenceFileInfos(filename)
            name = infos.sequence()
        else:
            infos = ShotFileInfos(filename)
            name = infos.shot()

        return f'{name}\n{increment}'

    elif '_P.' in filename:
        base_folder = get_file_base_folder(filename)

        if base_folder == 'asset':
            infos = AssetFileInfos(filename)
            name = infos.asset_name()
        elif base_folder == 'sequence':
            infos = SequenceFileInfos(filename)
            name = infos.sequence()
        else:
            infos = ShotFileInfos(filename)
            name = infos.shot()

        return name

    else:
        return ''


def get_file_modification_date_time(file_path: str):
    """
    Récupère la date et l'heure de modification d'un fichier spécifié au format "jj/mm/aaaa hh:mm".
    """
    if not os.path.exists(file_path):
        return

    # Obtenir les informations de modification du fichier
    file_stat = os.stat(file_path)
    modification_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
    formatted_date = modification_time.strftime("%d/%m/%Y")
    formatted_time = modification_time.strftime("%H:%M")
    formatted_date_time = f'{formatted_date}\n{formatted_time}'

    return formatted_date_time


def return_publish_name(file_name: str, usd: bool = False, variant: str = ''):
    """
    Renomme un fichier en fonction du format d'export :
    - Si USD, supprime le suffixe '_E_XXX' et remplace '_geo' par '_geoT'.
    - Si non USD, supprime '_E_XXX' par '_P' sans toucher à '_geo'.
    """
    # Motif pour "_E_" suivi de chiffres
    edit_string = r'_E_\d+'
    match = re.findall(edit_string, file_name)

    # Étape 1: Gestion du motif '_E_XXX'
    if match:
        if usd:
            # Si USD, on supprime simplement le motif
            publish_file_name = file_name.replace(match[0], '')
        else:
            # Si non USD, on remplace par '_P'
            publish_file_name = file_name.replace(match[0], '_P')
    else:
        publish_file_name = file_name

    # Étape 2: Gestion du suffixe '_geo'
    if usd and "_geo" in publish_file_name:
        # Si USD, remplacer '_geo' par '_geoT'
        publish_file_name = publish_file_name.replace("_geo", "_geoT")
    elif not usd and "_geo" in publish_file_name:
        # Si non USD, laisser '_geo' intact
        publish_file_name = publish_file_name

    # Étape 3: Changer l'extension en fonction du format
    if usd:
        base_name = os.path.splitext(publish_file_name)[0]
        publish_file_name = f'{base_name}.usd'

    print(f'Return Publish Name : {publish_file_name}')
    return publish_file_name

def extract_increment(file_name: str, mode='v'):
    """
    Extrait l'incrément numérique d'un nom de fichier contenant un suffixe '_XXX.'.

    Args:
    - file_name (str): Le nom de fichier à partir duquel l'incrément doit être extrait.

    Returns:
    - int: L'incrément numérique extrait du nom de fichier, ou None si aucun incrément n'est trouvé.
    """

    match = re.search(r'_(\d{3})\.', file_name)
    if match:
        return int(match.group(1))
    print(f"Aucun motif '_XXX.' trouvé dans le fichier : {file_name}")
    return None


def return_increment_edit(file_path: str, is_usd: bool = False):
    """
    Modifie le nom de fichier en ajoutant un suffixe numérique incrémenté '_XXX.'.

    Args:
    - file_path (str): Le chemin du fichier dont le nom doit être modifié.
    - is_usd (bool): Indique si le fichier est en USD (dans ce cas, ne pas incrémenter).

    Returns:
    - str: Le chemin du fichier avec le nouveau nom incrémenté.
    """
    if is_usd:
        return file_path  # Ne pas incrémenter pour les fichiers USD

    parent_dir = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    other_files = get_files(parent_dir)

    # Filtrer les fichiers qui ont le même préfixe que le fichier actuel
    matching_files = [f for f in other_files if base_name.split('_')[0] in f]
    if not matching_files:
        print(f"Aucun fichier correspondant trouvé dans le répertoire : {parent_dir}")
        return None

    # Trouver le fichier avec le numéro d'incrément le plus élevé
    last_file = sorted(matching_files)[-1]
    last_increment = extract_increment(last_file)

    if last_increment is None:
        print(f"Aucun incrément trouvé pour le fichier : {last_file}")
        return None

    # Incrémenter le numéro de version
    new_increment = f'_{last_increment + 1:03}.'

    # Remplacer l'ancien numéro de version par le nouveau
    new_file_path = re.sub(r'_(\d{3})\.', new_increment, file_path)

    print(f"Nouveau chemin de fichier : {new_file_path}")
    return new_file_path


def return_increment_publish_name(file_name: str, publish_list: list, is_usd: bool = False):
    if is_usd:
        return file_name  # Ne pas incrémenter pour les fichiers USD
    """
    Incrémente le nom de fichier publié en fonction de la liste des publications existantes.
    """
    if not publish_list:
        return file_name.replace('.', f'_001.')

    publish_list.sort()
    last_publish_file = publish_list[-1]
    new_increment = f'{extract_increment(last_publish_file, mode="P") + 1:03}'

    new_last_publish_file_name = file_name.replace('.', f'_{new_increment}.')
    return new_last_publish_file_name


def clean_directory(path: str, dir: str):
    """
    Nettoie un chemin en supprimant une partie spécifique du chemin.
    """
    if dir not in path:
        return path
    else:
        return path.split(dir)[0]


def _get_files_by_extension(directory: str):
    """
    Retourne un dictionnaire de fichiers avec leurs dates de modification.
    """
    EXTENSIONS = ('.ma', '.mb', '.hip', '.hipnc', '.nk', '.zpr')
    return_dict = {}

    for root_directory, _, files in os.walk(directory):
        for file in files:
            if file.endswith(tuple(EXTENSIONS)):
                file_path = os.path.join(root_directory, file)
                date_time = datetime.datetime.fromtimestamp(os.stat(file_path).st_mtime)
                return_dict[file_path] = date_time

    return return_dict


def get_recent_files(dictionnary: dict, num: int = 10):
    """
    Récupère les fichiers les plus récents d'un dictionnaire.
    """
    sorted_files = sorted(dictionnary.items(), key=operator.itemgetter(1), reverse=True)
    filtered_files = [(path, date) for path, date in sorted_files if
                      "bak" not in path and os.path.basename(os.path.dirname(path)) != 'backup']
    all_recent_files = filtered_files[:num]
    recent_files = [fichier for fichier, _ in all_recent_files]

    return recent_files


def get_recent_files_old(directory: str, num: int = 10):
    """
    Obtenir les fichiers récents d'un répertoire.
    """
    files = _get_files_by_extension(directory)
    recent_files = get_recent_files(files, num=num)
    return recent_files


def get_publish_files(directory: str):
    """
    Récupère les fichiers publiés d'un répertoire.
    """
    if not os.path.exists(directory):
        return []

    filepaths = []

    for root, _, files in os.walk(directory):
        if os.path.basename(root) == 'publish':
            for file in files:
                if '_P.' in file:
                    filepaths.append(os.path.join(root, file))

    return filepaths
