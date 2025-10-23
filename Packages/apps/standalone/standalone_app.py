import os
import shutil
import sys
import json
from PySide2.QtWidgets import QApplication, QDialog
from PySide2.QtCore import QTimer
from Packages.apps.standalone.main_window_standalone import MainWindowStandalone
from Packages.ui.dialogs.loading_dialog import LoadingDialog
from Packages.ui.dialogs.loading_thread import LoadingThread
from Packages.logic.json_funcs.convert_funcs import dict_to_json
from Packages.utils.constants.version import VERSION, USER_VERSION
from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT
from Packages.utils.constants.preferences import (
    USER_PREFS, BLANK_PREFS,
    VERSION_JSON_PATH, BLANK_VERSION_JSON_PATH,
    APPS_JSON_PATH, CURRENT_PROJECT_JSON_PATH
)
from Packages.utils.funcs import get_current_value
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
from Packages.utils.app_finder import AppFinder
from Packages.utils.init_project import InitProject
from Packages.ui.dialogs.preferences_dialog import PreferencesDialog
from Packages.utils.translation import translation_manager


class PipeZerApp(QApplication):

    def __init__(self, argv=sys.argv):
        super(PipeZerApp, self).__init__(argv)
        
        # Afficher le dialog de chargement
        self.loading_dialog = LoadingDialog()
        self.loading_dialog.show_loading()
        
        # Créer et démarrer le thread de chargement
        self.loading_thread = LoadingThread()
        self.loading_thread.progress_updated.connect(self.loading_dialog.update_progress)
        self.loading_thread.finished_loading.connect(self.on_loading_finished)
        self.loading_thread.start()

    def on_loading_finished(self):
        """Appelé quand le chargement est terminé"""
        # Fermer le dialog de chargement
        self.loading_dialog.close()
        
        # Charger les préférences de langue
        translation_manager.load_language_preference()
        
        # Effectuer les vérifications restantes
        self.check_pref()
        self.find_apps()

        # Vérifier si c'est le premier lancement ou si les préférences sont manquantes
        if self.is_first_launch() or not self.has_valid_preferences():
            # Afficher le dialog de préférences
            prefs_dialog = PreferencesDialog()
            if prefs_dialog.exec_() == QDialog.Accepted:
                prefs = prefs_dialog.get_preferences()
                self.apply_preferences(prefs)
            else:
                self.quit()
                sys.exit(0)
        else:
            # Charger les préférences existantes
            self.load_existing_preferences()

        # Récupération dynamique du projet courant
        project_directory = get_current_value(CURRENT_PROJECT_JSON_PATH, 'current_project', '')

        # Définir le répertoire du projet ici (sélectionné ou chargé dynamiquement)
        self.check_pipezer_data_folder(project_directory)
        self.create_main_window()
        
    def is_first_launch(self):
        """Vérifie si c'est le premier lancement"""
        user_home_dir = os.path.expanduser("~")
        pipezer_dir = os.path.join(user_home_dir, '.pipezer')
        prefs_file = os.path.join(pipezer_dir, 'preferences.json')
        return not os.path.exists(prefs_file)
        
    def has_valid_preferences(self):
        """Vérifie si les préférences sont valides"""
        try:
            user_home_dir = os.path.expanduser("~")
            pipezer_dir = os.path.join(user_home_dir, '.pipezer')
            prefs_file = os.path.join(pipezer_dir, 'preferences.json')
            
            if not os.path.exists(prefs_file):
                return False
                
            with open(prefs_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
                
            # Vérifier que tous les champs requis sont présents
            required_fields = ['language', 'theme', 'username', 'project_path', 'pipeline_choice']
            return all(field in prefs and prefs[field] for field in required_fields)
            
        except Exception:
            return False
            
    def apply_preferences(self, prefs):
        """Applique les préférences sélectionnées"""
        # Sauvegarder le nom d'utilisateur
        if prefs.get('username'):
            self.save_username(prefs['username'])
            
        # Sauvegarder le projet
        if prefs.get('project_path'):
            self.save_project_path(prefs['project_path'])
            
        # Configurer le pipeline si demandé
        if prefs.get('pipeline_choice') and prefs.get('project_path'):
            self.configure_pipeline(prefs['pipeline_choice'], prefs['project_path'])
            
    def load_existing_preferences(self):
        """Charge les préférences existantes"""
        try:
            user_home_dir = os.path.expanduser("~")
            pipezer_dir = os.path.join(user_home_dir, '.pipezer')
            prefs_file = os.path.join(pipezer_dir, 'preferences.json')
            
            with open(prefs_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
                
            # Appliquer la langue
            if 'language' in prefs:
                translation_manager.set_language(prefs['language'])
                
        except Exception as e:
            print(f"Erreur lors du chargement des préférences: {e}")
            
    def save_username(self, username):
        """Sauvegarde le nom d'utilisateur"""
        try:
            user_home_dir = os.path.expanduser("~")
            pipezer_dir = os.path.join(user_home_dir, '.pipezer')
            user_file_path = os.path.join(pipezer_dir, 'user.json')
            
            with open(user_file_path, 'w', encoding='utf-8') as f:
                json.dump({"username": username}, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du nom d'utilisateur: {e}")
            
    def save_project_path(self, project_path):
        """Sauvegarde le chemin du projet"""
        try:
            from Packages.logic.json_funcs.convert_funcs import json_to_dict, dict_to_json
            
            current_project_dict = json_to_dict(CURRENT_PROJECT_JSON_PATH)
            current_project_dict['current_project'] = project_path
            dict_to_json(current_project_dict, CURRENT_PROJECT_JSON_PATH)
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du projet: {e}")
            
    def configure_pipeline(self, choice, project_path):
        """Configure le pipeline selon le choix de l'utilisateur"""
        try:
            if choice == "create_new":
                # Créer les dossiers par défaut
                for folder in ['04_asset', '05_shot', '02_ressource']:
                    folder_path = os.path.join(project_path, folder)
                    os.makedirs(folder_path, exist_ok=True)
                print("Dossiers de pipeline créés avec succès")
                
            elif choice == "use_existing":
                # Ici on pourrait implémenter la logique de mapping
                # Pour l'instant, on affiche juste un message
                print("Configuration du mapping des dossiers existants")
            
        except Exception as e:
            print(f"Erreur lors de la configuration du pipeline: {e}")

    def check_pipezer_data_folder(self, project_directory):
        data_folder_path = os.path.join(project_directory, '.pipezer_data')

        # Crée le dossier s'il n'existe pas
        if not os.path.exists(data_folder_path):
            os.makedirs(data_folder_path)
            print(f"Création du dossier : {data_folder_path}")

            # Contenu des fichiers à créer
            files_content = {
                'file_data.json': '{}',
                'prefix.json': '{"prefix": ""}',
                'variants.json': '{"variants": []}',
                'notifs.json': '{}'
            }

            # Création des fichiers avec le contenu spécifié
            for filename, content in files_content.items():
                file_path = os.path.join(data_folder_path, filename)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                    print(f"Création du fichier : {file_path}")

    def find_apps(self):
        apps_dict = AppFinder().app_dict
        with open(APPS_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(apps_dict, file, indent=4, ensure_ascii=False)

    def check_pref(self):
        self.check_pipezer_pref()
        self.check_maya_pref()
        self.check_houdini_pref()

    def check_pipezer_pref(self):
        if not os.path.exists(USER_PREFS):
            shutil.copytree(BLANK_PREFS, USER_PREFS)
            return

        for json_file in os.listdir(BLANK_PREFS):
            json_file_path = os.path.join(USER_PREFS, json_file)
            if not os.path.exists(json_file_path):
                shutil.copy(os.path.join(BLANK_PREFS, json_file), USER_PREFS)

    def check_maya_pref(self):
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
        if not os.path.exists(os.path.join(HOUDINI_SHELF_PATH, H_SHELF_PIPEZER_NAME)):
            shutil.copy(H_SHELF_PIPEZER_SOURCE, HOUDINI_SHELF_PATH)

        if not os.path.exists(os.path.join(HOUDINI_MENU_PATH, H_MENU_PIPEZER_NAME)):
            shutil.copy(H_MENU_PIPEZER_SOURCE, HOUDINI_MENU_PATH)

    def update_pipezer_pref(self):
        if self.VERSION == self.USER_VERSION:
            return

        os.remove(VERSION_JSON_PATH)
        shutil.copy(BLANK_VERSION_JSON_PATH, USER_PREFS)

        self.update_maya_prefs()
        self.update_houdini_prefs()

    def update_maya_prefs(self):
        maya_shelf_path = os.path.join(MAYA_SHELF_PATH, SHELF_PIPEZER_NAME)
        if os.path.exists(maya_shelf_path):
            os.remove(maya_shelf_path)
        shutil.copy(SHELF_PIPEZER_SOURCE, MAYA_SHELF_PATH)

        maya_menu_path = os.path.join(MAYA_MENU_PATH, MENU_PIPEZER_NAME)
        if os.path.exists(maya_menu_path):
            os.remove(maya_menu_path)
        shutil.copy(MENU_PIPEZER_SOURCE, MAYA_MENU_PATH)

        maya_scripts_path = os.path.join(MAYA_SCRIPTS_PATH, USER_SETUP_NAME)
        if os.path.exists(maya_scripts_path):
            os.remove(maya_scripts_path)
        shutil.copy(USER_SETUP_SOURCE, MAYA_SCRIPTS_PATH)

        for icon, icon_source in zip(ICONS, ICONS_PATHS_SOURCE):
            if os.path.exists(os.path.join(MAYA_ICON_PATH, icon)):
                os.remove(os.path.join(MAYA_ICON_PATH, icon))
            shutil.copy(icon_source, MAYA_ICON_PATH)

    def update_houdini_prefs(self):
        houdini_shelf_path = os.path.join(HOUDINI_SHELF_PATH, H_SHELF_PIPEZER_NAME)
        if os.path.exists(houdini_shelf_path):
            os.remove(houdini_shelf_path)
        shutil.copy(H_SHELF_PIPEZER_SOURCE, HOUDINI_SHELF_PATH)

        houdini_menu_path = os.path.join(HOUDINI_MENU_PATH, H_MENU_PIPEZER_NAME)
        if os.path.exists(houdini_menu_path):
            os.remove(houdini_menu_path)
        if not os.path.exists(HOUDINI_MENU_PATH):
            os.mkdir(HOUDINI_MENU_PATH)
        shutil.copy(H_MENU_PIPEZER_SOURCE, HOUDINI_MENU_PATH)

    def create_main_window(self):
        self.window = MainWindowStandalone()
        self.window.show()
