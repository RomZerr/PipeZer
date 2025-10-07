import os
import json


# FUNCTIONS -------------------------------------------------------------------------------
def _generate_increment_names(tuple):
    project_subdirs = {}
    for index, subdir_name in enumerate(tuple, start=1):
        project_subdir_name = f'{index:02}_{subdir_name}'
        project_subdirs[project_subdir_name] = None
        
    return project_subdirs

def _dict_to_dirs(parent_directory, project_dict):
    
    for key, value in project_dict.items():
        
        directory_name = key
        directory_path = os.path.join(parent_directory, directory_name)
        print(f'os.mkdir({directory_path})')
        #os.mkdir(directory_path)
        
        if value:
            _dict_to_dirs(directory_path, value)

#  CONSTANTS ------------------------------------------------------------------------------
# Chemin vers le répertoire utilisateur actuel (cela fonctionnera sur la plupart des systèmes)
user_home_dir = os.path.expanduser("~")

# Définir le dossier .pipezer dans le répertoire utilisateur
pipezer_dir = os.path.join(user_home_dir, '.pipezer')

# S'assurer que le dossier .pipezer existe
if not os.path.exists(pipezer_dir):
    os.makedirs(pipezer_dir)

# Path to user.json in .pipezer
user_file_path = os.path.join(pipezer_dir, 'user.json')

# Check if user.json exists, if not, fallback to system username
if os.path.exists(user_file_path):
    with open(user_file_path, 'r') as user_file:
        data = json.load(user_file)
        USERNAME = data.get("username", os.getenv("USERNAME"))  # Fallback si vide
else:
    USERNAME = os.getenv("USERNAME")

PROJECT_PATH = r"\\Storage01\3D4\nordicPhone"
PROJECT_NAME = os.path.basename(PROJECT_PATH)

PROJECT_SUBDIR_NAMES = (
    'ressources',
    'preprod',
    'asset',
    'texture',
    'sequence',
    'shot',
    'cache',
    'editing',
    'test',
    'com',
    'jury'
    )

ASSET_SUBDIR_NAMES = (
    'character',
    'prop',
    'item',
    'environnement',
    'module',
    'fx',
    'diorama'
)

PROJECT_SUBDIRS = _generate_increment_names(PROJECT_SUBDIR_NAMES)
ASSET_SUBDIRS = _generate_increment_names(ASSET_SUBDIR_NAMES)

PROJECT_DICT = {
    PROJECT_NAME : PROJECT_SUBDIRS
}


if __name__ == '__main__':
    import json
    print(json.dumps(PROJECT_DICT, indent=4))
    
    dir = '//Storage01/3D4/'
    _dict_to_dirs(dir, PROJECT_DICT)