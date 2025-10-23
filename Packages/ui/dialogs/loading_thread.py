import os
import shutil
import time
from PySide2.QtCore import QThread, Signal
from Packages.utils.translation import translation_manager
from Packages.utils.constants.preferences import USER_PREFS, BLANK_PREFS
from Packages.utils.constants.maya_pref import (
    ICONS, ICONS_PATHS_SOURCE,
    MENU_PIPEZER_NAME, MENU_PIPEZER_SOURCE,
    SHELF_PIPEZER_NAME, SHELF_PIPEZER_SOURCE,
    USER_SETUP_NAME, USER_SETUP_SOURCE,
    MAYA_SHELF_PATH, MAYA_MENU_PATH, MAYA_SCRIPTS_PATH, MAYA_ICON_PATH
)
from Packages.utils.constants.houdini_pref import (
    H_MENU_PIPEZER_NAME, H_MENU_PIPEZER_SOURCE,
    H_SHELF_PIPEZER_NAME, H_SHELF_PIPEZER_SOURCE,
    HOUDINI_SHELF_PATH, HOUDINI_MENU_PATH
)


class LoadingThread(QThread):
    """
    Thread pour gérer l'initialisation de PipeZer en arrière-plan
    """
    
    progress_updated = Signal(int, str)  # value, message
    finished_loading = Signal()
    
    def __init__(self):
        super().__init__()
        self.total_steps = 8
        self.current_step = 0
        
    def run(self):
        """Exécute l'initialisation avec mise à jour de la progression"""
        
        # Étape 1: Vérification des préférences PipeZer
        self.update_progress(10, translation_manager.get_text("app.loading"))
        self.check_pipezer_pref()
        
        # Étape 2: Vérification des préférences Maya
        self.update_progress(25, translation_manager.get_text("app.loading"))
        self.check_maya_pref()
        
        # Étape 3: Vérification des préférences Houdini
        self.update_progress(40, translation_manager.get_text("app.loading"))
        self.check_houdini_pref()
        
        # Étape 4: Recherche des applications
        self.update_progress(55, translation_manager.get_text("app.loading"))
        self.find_apps()
        
        # Étape 5: Vérification du projet
        self.update_progress(70, translation_manager.get_text("app.loading"))
        self.check_project()
        
        # Étape 6: Finalisation
        self.update_progress(85, translation_manager.get_text("app.loading"))
        time.sleep(0.5)  # Petite pause pour l'effet visuel
        
        # Étape 7: Terminé
        self.update_progress(100, translation_manager.get_text("app.ready"))
        time.sleep(0.3)
        
        self.finished_loading.emit()
        
    def update_progress(self, value, message):
        """Met à jour la progression"""
        self.progress_updated.emit(value, message)
        time.sleep(0.1)  # Petite pause pour l'effet visuel
        
    def check_pipezer_pref(self):
        """Vérifie et initialise les préférences PipeZer"""
        if not os.path.exists(USER_PREFS):
            shutil.copytree(BLANK_PREFS, USER_PREFS)
            return

        for json_file in os.listdir(BLANK_PREFS):
            json_file_path = os.path.join(USER_PREFS, json_file)
            if not os.path.exists(json_file_path):
                shutil.copy(os.path.join(BLANK_PREFS, json_file), USER_PREFS)
                
    def check_maya_pref(self):
        """Vérifie et initialise les préférences Maya"""
        if not os.path.exists(os.path.join(MAYA_SHELF_PATH, SHELF_PIPEZER_NAME)):
            shutil.copy(SHELF_PIPEZER_SOURCE, MAYA_SHELF_PATH)

        if not os.path.exists(os.path.join(MAYA_MENU_PATH, MENU_PIPEZER_NAME)):
            shutil.copy(MENU_PIPEZER_SOURCE, MAYA_MENU_PATH)

        if not os.path.exists(os.path.join(MAYA_SCRIPTS_PATH, USER_SETUP_NAME)):
            shutil.copy(USER_SETUP_SOURCE, MAYA_SCRIPTS_PATH)

        for icon, icon_source in zip(ICONS, ICONS_PATHS_SOURCE):
            if not os.path.exists(os.path.join(MAYA_ICON_PATH, icon)):
                shutil.copy(icon_source, MAYA_ICON_PATH)
                
    def check_houdini_pref(self):
        """Vérifie et initialise les préférences Houdini"""
        if not os.path.exists(os.path.join(HOUDINI_SHELF_PATH, H_SHELF_PIPEZER_NAME)):
            shutil.copy(H_SHELF_PIPEZER_SOURCE, HOUDINI_SHELF_PATH)

        if not os.path.exists(os.path.join(HOUDINI_MENU_PATH, H_MENU_PIPEZER_NAME)):
            shutil.copy(H_MENU_PIPEZER_SOURCE, HOUDINI_MENU_PATH)
            
    def find_apps(self):
        """Recherche les applications installées"""
        from Packages.utils.app_finder import AppFinder
        from Packages.utils.constants.preferences import APPS_JSON_PATH
        import json
        
        apps_dict = AppFinder().app_dict
        with open(APPS_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(apps_dict, file, indent=4, ensure_ascii=False)
            
    def check_project(self):
        """Vérifie la configuration du projet"""
        from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
        from Packages.utils.funcs import get_current_value
        
        project_directory = get_current_value(CURRENT_PROJECT_JSON_PATH, 'current_project', '')
        if not project_directory or not os.path.isdir(project_directory):
            # Le projet sera demandé après le chargement
            pass
