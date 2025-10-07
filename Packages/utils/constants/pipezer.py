import os
from Packages.utils.funcs import find_package_path


ROOT_NAME = 'PipeZer'
PIPEZER_PATH = find_package_path(ROOT_NAME)
PACKAGES_PATH = os.path.join(PIPEZER_PATH, 'Packages')