import os
from Packages.utils.funcs import find_package_path, get_current_value


# Software directories
ROOT_NAME = "PipeZer"
ROOT_PATH = find_package_path(ROOT_NAME)
PREF_DEFAULT_PATH = os.path.join(ROOT_PATH, '.pipezer')
VERSION = get_current_value(os.path.join(PREF_DEFAULT_PATH, 'version.json'), 'version')
UNINSTALL_PATH = os.path.join(ROOT_PATH, "unins000.exe")
SITE_PACKAGES_PATH = os.path.join(ROOT_PATH, "bin", "lib")

PYTHON_W = os.path.join(ROOT_PATH, '.venv', 'Scripts', 'pythonw.exe')

# Project Files
PROJECT_FILES_PATH = os.path.join(ROOT_PATH, "ProjectFiles")

EMPTY_SCENES_PATH = os.path.join(PROJECT_FILES_PATH, "Empty_Scenes")
EMPTY_MAYA_MA_PATH = os.path.join(EMPTY_SCENES_PATH, "empty_scene_maya_2024.ma")
EMPTY_MAYA_MB_PATH = os.path.join(EMPTY_SCENES_PATH, "empty_scene_maya_2024.mb")
EMPTY_HOUDINI_PATH = os.path.join(EMPTY_SCENES_PATH, "empty_scene_houdini_20.5.hip")
EMPTY_HOUDINI_NC_PATH = os.path.join(EMPTY_SCENES_PATH, "empty_scene_houdini_20.5.hipnc")
EMPTY_NUKE_PATH = os.path.join(EMPTY_SCENES_PATH, "empty_scene_nuke_13.2v4.nk")
EMPTY_NUKE_NC_PATH = os.path.join(EMPTY_SCENES_PATH, "empty_scene_nuke_13.2v4.nknc")

FALLBACKS_PATH = os.path.join(PROJECT_FILES_PATH, 'Fallbacks')
NO_PREVIEW_FILEPATH = os.path.join(FALLBACKS_PATH, "nopreview.png")

ICON_PATH = os.path.join(PROJECT_FILES_PATH, "Icons")
PIPEZER_ICON_PATH = os.path.join(ICON_PATH, 'pipezer_icon.ico')

INFOS_PATH = os.path.join(PROJECT_FILES_PATH, 'Infos')

STYLE_PATH = os.path.join(PROJECT_FILES_PATH, "Styles")
DARK_STYLE = os.path.join(STYLE_PATH, 'dark.css')

WORKSPACE_MEL_PATH = os.path.join(PROJECT_FILES_PATH, "Workspaces", "workspace.mel")

PIPEZER_APP_ICON_PATH = os.path.join(ROOT_PATH, 'pipezer_app_icon.py')
QRC_PATH = os.path.join(ROOT_PATH, 'ressources.qrc')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT
import json

# Chemins vers les fichiers de données projet
PIPEZER_DATA_DIR = os.path.join(CURRENT_PROJECT, '.pipezer_data')
PREFIX_JSON_PATH = os.path.join(PIPEZER_DATA_DIR, 'prefix.json')  # standardise en minuscule

# Charger la valeur de PREFIX de manière tolérante (fallback si absent)
PREFIX = "NOR"
try:
    if os.path.exists(PREFIX_JSON_PATH):
        with open(PREFIX_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f) or {}
            PREFIX = data.get("PREFIX", PREFIX)
except Exception:
    # Fallback silencieux; le reste de l'appli ne doit pas planter
    pass


CURRENT_PROJECT_PREVIEW_FOLDER = os.path.join(PIPEZER_DATA_DIR, 'preview')
VARIANTS_JSON_PATH = os.path.join(PIPEZER_DATA_DIR, 'variants.json')

ASSET_DIR = os.path.join(CURRENT_PROJECT, '04_asset')
SHOT_DIR = os.path.join(CURRENT_PROJECT, '05_shot')
TEX_DIR = os.path.join(CURRENT_PROJECT, '11_texture')
CACHE_DIR = os.path.join(CURRENT_PROJECT, '12_cache')
PUBLISH_DIR = os.path.join(CURRENT_PROJECT, '12_cache')
