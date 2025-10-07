import os
from Packages.utils.constants.pipezer import PIPEZER_PATH
from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
from Packages.utils.funcs import get_current_value


BLANK_PIPEZER_DATA = os.path.join(PIPEZER_PATH, '.pipezer_data')
BLANK_pipezer_data_ICONS = os.path.join(BLANK_PIPEZER_DATA, 'icons')
BLANK_pipezer_data_PREVIEW = os.path.join(BLANK_PIPEZER_DATA, 'preview')
BLANK_pipezer_data_FILE_DATA = os.path.join(BLANK_PIPEZER_DATA, 'file_data.json')
BLANK_pipezer_data_PREFIX = os.path.join(BLANK_PIPEZER_DATA, 'prefix.json')
BLANK_pipezer_data_VARIANTS = os.path.join(BLANK_PIPEZER_DATA, 'variants.json')

#
CURRENT_PROJECT = get_current_value(CURRENT_PROJECT_JSON_PATH, 'current_project', fail_return='str')
CURRENT_PROJECT_NAME = os.path.basename(CURRENT_PROJECT)

pipezer_data_PATH = os.path.join(CURRENT_PROJECT, '.pipezer_data')
pipezer_data_ICONS = os.path.join(pipezer_data_PATH, 'icons')
pipezer_data_PREVIEW = os.path.join(pipezer_data_PATH, 'preview')
pipezer_data_FILE_DATA = os.path.join(pipezer_data_PATH, 'file_data.json')
pipezer_data_PREFIX = os.path.join(pipezer_data_PATH, 'prefix.json')
pipezer_data_VARIANTS = os.path.join(pipezer_data_PATH, 'variants.json')
ICONS_PATH = os.path.join(PIPEZER_PATH, 'ProjectFiles', 'Icons')
