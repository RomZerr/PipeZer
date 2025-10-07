import os
import shutil
from PySide2.QtWidgets import QDialog, QWidget, QVBoxLayout, QRadioButton, QPushButton, QLabel, QLineEdit, QCheckBox, QGridLayout
from Packages.apps.maya_app.ui.maya_main_window import maya_main_window
from Packages.utils.constants.constants_old import ASSET_DIR, PREFIX, WORKSPACE_MEL_PATH
from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT
from maya import cmds
import maya.api.OpenMaya as om
from PySide2.QtGui import QFont
import json

# Chemin vers le fichier de notifications (lié au projet courant)
NOTIF_FILE_PATH = os.path.join(CURRENT_PROJECT, '.pipezer_data', 'notifs.json')

def add_notification(username, action, file_name):
    """
    Ajoute une notification dans le fichier JSON.
    :param username: Nom de l'utilisateur effectuant l'action.
    :param action: Type d'action effectuée (ex: 'create_asset').
    :param file_name: Nom de l'élément lié à l'action (ex: nom de l'asset).
    """
    notification = {
        "username": username,
        "action": action,
        "file": file_name
    }

    try:
        # Charger les notifications existantes
        if os.path.exists(NOTIF_FILE_PATH):
            with open(NOTIF_FILE_PATH, 'r') as notif_file:
                data = json.load(notif_file)
                if not isinstance(data, list):  # Si les données ne sont pas une liste
                    print("Format de données invalides dans notifs.json. Réinitialisation.")
                    data = []
        else:
            data = []

        # Ajouter la nouvelle notification
        data.append(notification)

        # Sauvegarder les notifications mises à jour
        with open(NOTIF_FILE_PATH, 'w') as notif_file:
            json.dump(data, notif_file, indent=4)

        print(f"Notification ajoutée : {notification}")

    except Exception as e:
        print(f"Erreur lors de l'ajout d'une notification : {e}")

def get_username():
    """
    Récupère le nom d'utilisateur depuis user.json ou utilise le nom par défaut.
    """
    user_home_dir = os.path.expanduser("~")
    pipezer_dir = os.path.join(user_home_dir, '.pipezer')
    user_file_path = os.path.join(pipezer_dir, 'user.json')

    try:
        if os.path.exists(user_file_path):
            print(f"Chargement de {user_file_path} pour récupérer le nom d'utilisateur.")
            with open(user_file_path, 'r') as user_file:
                data = json.load(user_file)
                username = data.get("username")
                if username:
                    print(f"Nom d'utilisateur trouvé dans user.json : {username}")
                    return username
                else:
                    print("Clé 'username' absente dans user.json.")
        else:
            print(f"Fichier user.json introuvable à : {user_file_path}")
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur : {e}")

    # Retour par défaut si user.json est absent ou invalide
    default_username = os.getenv("USERNAME", "unknown_user")
    print(f"Utilisation du nom par défaut : {default_username}")
    return default_username



class CreateAssetDialog(QDialog):

    def __init__(self, parent = maya_main_window()) -> None:
        super().__init__(parent)

        self.setWindowTitle('Create Asset')
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.show()

        # Définir la police plus grande
        font = QFont()
        font.setPointSize(10)

    def create_widgets(self):
        self.asset_name_label = QLabel('Asset name :')
        self.asset_name_line_edit = QLineEdit('')

        self.asset_type_label = QLabel('Asset type :')
        self.character_radio_btn = QRadioButton('01_character')
        self.prop_radio_btn = QRadioButton('02_prop')
        self.item_radio_btn = QRadioButton('03_item')
        self.enviro_radio_btn = QRadioButton('04_enviro')
        self.module_radio_btn = QRadioButton('05_module')

        self.radio_list = (
            self.character_radio_btn, 
            self.prop_radio_btn,
            self.item_radio_btn,
            self.enviro_radio_btn,
            self.module_radio_btn
        )

        self.subfolders_label = QLabel('Subfolders :')
        self.data_checkbox = QCheckBox('data')
        self.images_checkbox = QCheckBox('images')
        self.scenes_checkbox = QCheckBox('scenes')
        self.out_checkbox = QCheckBox('out')
        self.sourceimages_checkbox = QCheckBox('sourceimages')
        self.scripts_checkbox = QCheckBox('scripts')
        self.sound_checkbox = QCheckBox('sound')
        self.clip_checkbox = QCheckBox('clip')
        self.movie_checkbox = QCheckBox('sourceimages')

        self.data_checkbox.setChecked(True)
        self.scenes_checkbox.setChecked(True)

        self.subfolders_list = (
            self.data_checkbox,
            self.images_checkbox,
            self.scenes_checkbox,
            self.out_checkbox,
            self.sourceimages_checkbox,
            self.scripts_checkbox,
            self.sound_checkbox,
            self.clip_checkbox,
            self.movie_checkbox
        )

        self.department_label = QLabel('Departments :')
        self.geo_cb = QCheckBox('geo')
        self.ldv_cb = QCheckBox('ldv')
        self.rig_cb = QCheckBox('rig')

        self.department_list = (
            self.geo_cb,
            self.ldv_cb,
            self.rig_cb
        )

        self.geo_cb.setChecked(True)
        self.ldv_cb.setChecked(True)

        self.create_groups_button = QCheckBox('Create groups')
        self.run_button = QPushButton('Create Asset')
        self.run_button.setFixedSize(200, 60)

    def create_layout(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)

        SEP = '-------------------------'

        self.grid_layout.addWidget(self.asset_name_label, 0, 0)
        self.grid_layout.addWidget(self.asset_name_line_edit, 0, 1)

        self.grid_layout.addWidget(self.asset_type_label, 1, 0)
        self.grid_layout.addWidget(QLabel(SEP), 1, 1)
        self.grid_layout.addWidget(self.character_radio_btn, 2, 1)
        self.grid_layout.addWidget(self.prop_radio_btn, 3, 1)
        self.grid_layout.addWidget(self.item_radio_btn, 4, 1)
        self.grid_layout.addWidget(self.enviro_radio_btn, 5, 1)
        self.grid_layout.addWidget(self.module_radio_btn, 6, 1)

        self.grid_layout.addWidget(self.department_label, 7, 0)
        self.grid_layout.addWidget(QLabel(SEP), 7, 1)
        self.grid_layout.addWidget(self.geo_cb, 8, 1)
        self.grid_layout.addWidget(self.ldv_cb, 9, 1)
        self.grid_layout.addWidget(self.rig_cb, 10, 1)

        self.grid_layout.addWidget(self.subfolders_label, 11, 0)
        self.grid_layout.addWidget(QLabel(SEP), 11, 1)
        self.grid_layout.addWidget(self.data_checkbox, 12, 1)
        self.grid_layout.addWidget(self.images_checkbox, 13, 1)
        self.grid_layout.addWidget(self.scenes_checkbox, 14, 1)
        self.grid_layout.addWidget(self.out_checkbox, 15, 1)
        self.grid_layout.addWidget(self.sourceimages_checkbox, 16, 1)
        self.grid_layout.addWidget(self.scripts_checkbox, 17, 1)
        self.grid_layout.addWidget(self.sound_checkbox, 18, 1)
        self.grid_layout.addWidget(self.clip_checkbox, 19, 1)
        self.grid_layout.addWidget(self.movie_checkbox, 20, 1)

        self.grid_layout.addWidget(self.create_groups_button, 21, 0)

        self.main_layout.addWidget(self.grid_widget)
        self.main_layout.addWidget(self.run_button)

    def create_connections(self):
        self.run_button.clicked.connect(self.create_asset)
        for radio_btn in self.radio_list:
            radio_btn.clicked.connect(self.toggle_ui)

    def toggle_ui(self):
        radio_btn = self.sender()
        if radio_btn.text() in ['01_character', '02_prop']:
            self.geo_cb.setChecked(True)
            self.ldv_cb.setChecked(True)
            self.rig_cb.setChecked(True)
        else:
            self.geo_cb.setChecked(True)
            self.ldv_cb.setChecked(True)
            self.rig_cb.setChecked(False)

    def get_asset_name(self) -> str:
        return self.asset_name_line_edit.text()
    
    def get_asset_type(self) -> str:
        for radio_btn in self.radio_list:
            if radio_btn.isChecked():
                return radio_btn.text().lower()
            
    def get_departments(self) -> list:
        dep_list = []
        for dep_cb in self.department_list:
            if dep_cb.isChecked():
                dep_list.append(dep_cb.text().lower())
        return dep_list
    
    def get_subfolders(self) -> list:
        subfolder_list = []
        for sub_cb in self.subfolders_list:
            if sub_cb.isChecked():
                subfolder_list.append(sub_cb.text().lower())
        return subfolder_list

    def create_asset(self):
        asset_name = self.get_asset_name()
        asset_type = self.get_asset_type()
        departments = self.get_departments()
        subfolders = self.get_subfolders()

        if asset_name == '':
            om.MGlobal.displayError('Please enter asset name.')
            return

        elif asset_type is None:
            om.MGlobal.displayError('Please select asset type.')
            return

        elif not departments:
            om.MGlobal.displayError('Please select departments.')
            return

        elif not subfolders:
            om.MGlobal.displayError('Please select subfolders.')
            return

        # Répertoire de base pour le type d'asset
        asset_type_directory = os.path.join(ASSET_DIR, asset_type)
        asset_directory = os.path.join(asset_type_directory, asset_name)

        # Créer les répertoires "maya", "houdini", "texture" et "substance" dans le répertoire principal de l'asset
        maya_directory = os.path.join(asset_directory, 'maya')
        houdini_directory = os.path.join(asset_directory, 'houdini')
        texture_directory = os.path.join(asset_directory, 'texture')
        substance_directory = os.path.join(asset_directory, 'substance')

        # Créer les dossiers
        os.makedirs(maya_directory, exist_ok=True)
        os.makedirs(houdini_directory, exist_ok=True)
        os.makedirs(texture_directory, exist_ok=True)
        os.makedirs(substance_directory, exist_ok=True)

        # Création des sous-dossiers dans maya
        for subfolder in subfolders:
            subfolder_path = os.path.join(maya_directory, subfolder)
            os.mkdir(subfolder_path)
            if subfolder == 'scenes':
                for department in departments:
                    if department == 'ldv':  # Exclure la création de ldv ici, car il sera dans houdini
                        continue
                    os.mkdir(os.path.join(subfolder_path, department))

        # Copier le fichier workspace.mel dans le dossier maya
        shutil.copy(WORKSPACE_MEL_PATH, maya_directory)

        # Création du dossier ldv dans houdini si sélectionné
        if 'ldv' in departments:
            ldv_directory = os.path.join(houdini_directory, 'ldv')
            os.makedirs(ldv_directory, exist_ok=True)

        # Nommer et enregistrer le fichier pour le département geo
        asset_type_dict = {
            '01_character': 'chr',
            '02_prop': 'prp',
            '03_item': 'itm',
            '04_enviro': 'env',
            '05_module': 'mod',
        }

        asset_type_abbr = asset_type_dict[asset_type]

        # Ex. de nom de fichier pour le département geo : CDS_chr_petru_geo_E_001.ma
        file_name_geo = '_'.join([PREFIX, asset_type_abbr, asset_name, 'geo', 'E', '001.ma'])
        file_path_geo = os.path.join(maya_directory, 'scenes', 'geo', file_name_geo)
        cmds.file(rename=file_path_geo)
        cmds.file(save=True, type='mayaAscii')

        # Créer des fichiers pour les départements restants (ldv, rig) si sélectionnés
        for dep in ['ldv', 'rig']:
            if dep not in departments:
                continue

            file_name_dep = '_'.join([PREFIX, asset_type_abbr, asset_name, dep, '001.ma'])
            if dep == 'ldv':
                directory_dep = ldv_directory  # Dossier ldv dans houdini
            else:
                directory_dep = os.path.join(maya_directory, 'scenes', dep)

            os.makedirs(directory_dep, exist_ok=True)
            shutil.copy(file_path_geo, directory_dep)
            tmp_dep_file_path = os.path.join(directory_dep, file_name_geo)
            new_dep_file_path = os.path.join(directory_dep, file_name_dep)
            os.rename(tmp_dep_file_path, new_dep_file_path)

        # Créer les groupes de base si sélectionné
        if self.create_groups_button.isChecked():
            geo_grp = cmds.group(name=f'{asset_type_abbr}_{asset_name}_geo', empty=True, world=True)
            cmds.group(geo_grp, name=f'{asset_type_abbr}_{asset_name}', world=True)
            cmds.file(save=True)

            # Ajouter une notification
            username = get_username()
            add_notification(username, "create_asset", asset_name)

        self.close()

