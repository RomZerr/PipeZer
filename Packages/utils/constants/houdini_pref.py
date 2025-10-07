import os
from Packages.utils.constants.pipezer import PACKAGES_PATH
from Packages.utils.funcs import find_directory

HOUDINI_INTEG_PATH = os.path.join(PACKAGES_PATH, 'apps', 'houdini', 'integration')

H_MENU_PIPEZER_NAME = 'pipezer.radialmenu'
H_SHELF_PIPEZER_NAME = 'pipezer.shelf'

H_MENU_PIPEZER_SOURCE = os.path.join(HOUDINI_INTEG_PATH, H_MENU_PIPEZER_NAME)
H_SHELF_PIPEZER_SOURCE = os.path.join(HOUDINI_INTEG_PATH, H_SHELF_PIPEZER_NAME)

#
documents_path = os.path.join(os.path.expanduser("~"), 'Documents')
HOUDINI_PREF_PATH = os.path.join(documents_path, find_directory(documents_path, 'houdini'))

HOUDINI_SHELF_PATH = os.path.join(HOUDINI_PREF_PATH, 'toolbar')
HOUDINI_MENU_PATH = os.path.join(HOUDINI_PREF_PATH, 'radialmenu')
