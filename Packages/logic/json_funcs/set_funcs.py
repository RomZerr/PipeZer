import os
import json
from Packages.logic.json_funcs.convert_funcs import json_to_dict, dict_to_json
from Packages.utils.constants.preferences import RECENT_FILES_JSON_PATH, CLICKED_ITEMS_JSON_PATH
from Packages.utils.constants.project_pipezer_data import pipezer_data_FILE_DATA, CURRENT_PROJECT_NAME
from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
from Packages.utils.constants.user import USERNAME


def ensure_pipezer_data_directory_exists(base_path):
    """Ensure that the .pipezer_data directory and necessary files exist."""
    data_directory = os.path.join(base_path, '.pipezer_data')
    os.makedirs(data_directory, exist_ok=True)

    # Define the path for file_data.json
    file_data_path = os.path.join(data_directory, 'file_data.json')

    # Create file_data.json with default structure if it does not exist
    if not os.path.exists(file_data_path):
        with open(file_data_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)  # Create an empty JSON structure

    # Additional files or directories can be added here if needed
    return file_data_path


def set_recent_file(file_path: str):
    '''
    '''
    # récupérer la liste des fichiers récents dans le .json
    recent_files_dict = json_to_dict(RECENT_FILES_JSON_PATH)
    recent_files_list = recent_files_dict['recent_files']

    # si le fichier est déjà dans la liste, le placer au début de la liste
    if file_path in recent_files_list:
        recent_files_list.remove(file_path)
    recent_files_list.insert(0, file_path)

    # mettre à jour la liste et l'envoyer dans le .json
    recent_files_dict['recent_files'] = recent_files_list
    dict_to_json(recent_files_dict, RECENT_FILES_JSON_PATH)


def set_current_project(project_path: str) -> str:
    """Met à jour le projet actuel dans un fichier JSON avec le chemin du nouveau projet.

    Args:
        project_path (str): Le chemin absolu du nouveau projet.

    Returns:
        str: Le nom du projet mis à jour.
    """

    project_name = os.path.basename(project_path)

    with open(CURRENT_PROJECT_JSON_PATH, 'r') as file:
        project_dict = json.load(file)

    project_dict['current_project'] = {project_name: project_path}
    project_dict['projects'][project_name] = project_path

    with open(CURRENT_PROJECT_JSON_PATH, 'w') as file:
        json.dump(project_dict, file, indent=4)

    return project_name


def set_clicked_radio_button(radio_button):
    # vérifier si l'argument passé est bien une string
    if not isinstance(radio_button, str) and radio_button:
        radio_button = radio_button.text()

    # récupérer le dictionnaire des items cliqués depuis le fichier JSON
    clicked_items_dict = json_to_dict(CLICKED_ITEMS_JSON_PATH)

    # Vérifiez si le projet actuel existe dans le dictionnaire
    if CURRENT_PROJECT_NAME not in clicked_items_dict:
        clicked_items_dict[CURRENT_PROJECT_NAME] = {}  # Initialisez avec un dictionnaire vide

    # passez le bouton radio dans la clé "radio_button" du projet actuel
    clicked_items_dict[CURRENT_PROJECT_NAME]["radio_button"] = radio_button

    # mettre à jour le fichier JSON
    dict_to_json(clicked_items_dict, CLICKED_ITEMS_JSON_PATH)


def set_clicked_item(radio_button, item_index, item, shot=False, item_parent=None):
    # vérifier si l'argument passé est bien une string
    if not isinstance(radio_button, str) and radio_button:
        radio_button = radio_button.text()

    if not isinstance(item, str) and item:
        item = item.text()

    # récupérer le dictionnaire des items cliqués depuis le fichier JSON
    clicked_items_dict = json_to_dict(CLICKED_ITEMS_JSON_PATH)

    # Vérifiez si le projet actuel existe dans le dictionnaire
    if CURRENT_PROJECT_NAME not in clicked_items_dict:
        clicked_items_dict[CURRENT_PROJECT_NAME] = {}  # Initialisez avec un dictionnaire vide

    # Vérifiez si la sous-clé du bouton radio existe
    if radio_button not in clicked_items_dict[CURRENT_PROJECT_NAME]:
        clicked_items_dict[CURRENT_PROJECT_NAME][radio_button] = {}  # Initialisez avec un dictionnaire vide

    # condition shot -> à patcher
    if shot:
        clicked_items_dict[CURRENT_PROJECT_NAME][radio_button][item_index] = [item, item_parent]
        dict_to_json(clicked_items_dict, CLICKED_ITEMS_JSON_PATH)
        return

    # envoyer les informations dans le .json
    clicked_items_dict[CURRENT_PROJECT_NAME][radio_button][item_index] = item
    dict_to_json(clicked_items_dict, CLICKED_ITEMS_JSON_PATH)


def get_clicked_item(radio_button, item_index):
    # Charger le dictionnaire des éléments cliqués à partir du fichier JSON
    clicked_items_dict = json_to_dict(CLICKED_ITEMS_JSON_PATH)

    # Vérifiez si le projet actuel existe dans le dictionnaire
    if CURRENT_PROJECT_NAME not in clicked_items_dict:
        clicked_items_dict[CURRENT_PROJECT_NAME] = {}  # Initialisez avec un dictionnaire vide

    # Vérifiez si le bouton radio existe dans le projet actuel
    if radio_button not in clicked_items_dict[CURRENT_PROJECT_NAME]:
        clicked_items_dict[CURRENT_PROJECT_NAME][radio_button] = {}  # Initialisez avec un dictionnaire vide

    # Vérifiez si l'index de l'élément existe dans le bouton radio
    if item_index not in clicked_items_dict[CURRENT_PROJECT_NAME][radio_button]:
        raise KeyError(
            f"L'index de l'élément '{item_index}' n'existe pas dans le bouton radio '{radio_button}' du projet '{CURRENT_PROJECT_NAME}'.")

    # Retourner l'élément cliqué
    return clicked_items_dict[CURRENT_PROJECT_NAME][radio_button][item_index]


def get_file_data(filepath):
    # Utiliser os.path.join pour créer un chemin correct
    filepath = ensure_pipezer_data_directory_exists('//Storage01/3D4/nordicPhone')

    # Vérifiez si le fichier existe
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Le fichier {filepath} n'existe pas.")

    with open(filepath, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


def update_file_data(file_path: str, comment_string: str = '') -> None:
    '''
    '''

    file_path = file_path.replace('\\', '/')
    file_infos_dict = json_to_dict(pipezer_data_FILE_DATA)

    if not file_path in file_infos_dict.keys():
        file_infos_dict[file_path] = {'comment': None, 'user': None}

    file_infos_dict[file_path]['user'] = USERNAME

    # vérifier s'il y a du texte dans la "comment_string"
    if bool(comment_string.strip()):
        file_infos_dict[file_path]['comment'] = comment_string

    dict_to_json(file_infos_dict, pipezer_data_FILE_DATA)
