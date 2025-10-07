import os
import shutil
import json
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel, QFileDialog
from Packages.logic.json_funcs.convert_funcs import json_to_dict, dict_to_json
from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
from Packages.utils.constants.project_pipezer_data import BLANK_PIPEZER_DATA, pipezer_data_PATH
from Packages.ui.dialogs.user_dialog import UserDialog

class InitProject(QDialog):

    PROJECT = ''
    ACCEPTED = False

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.init_ui()
        self.create_connections()
        self.setup_pipezer()

    def init_ui(self) -> None:
        self.setWindowTitle('Select project')
        self.setMinimumSize(300, 150)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.button = QPushButton('Select your project.')
        self.label = QLabel('<project path>')
        self.ok_button = QPushButton('Apply')
        self.main_layout.addWidget(self.button)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.ok_button)

    def create_connections(self) -> None:
        self.button.clicked.connect(self.select_project)
        self.ok_button.clicked.connect(self.set_project)

    def update_label(self, string: str) -> None:
        self.label.setText(string)

    def apply(self) -> None:
        current_project_dict: dict = json_to_dict(CURRENT_PROJECT_JSON_PATH)
        current_project_dict['current_project'] = self.label.text()
        dict_to_json(current_project_dict, CURRENT_PROJECT_JSON_PATH)
        self.check_pipezer_data()
        self.close()

    def check_pipezer_data(self) -> None:
        if not os.path.exists(pipezer_data_PATH):
            shutil.copytree(BLANK_PIPEZER_DATA, pipezer_data_PATH)

    def select_project(self) -> None:
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        options = QFileDialog.Options()
        project_path: str = file_dialog.getExistingDirectory(self, 'Select directory', options=options)
        self.PROJECT = project_path.replace('\\', '/')
        self.update_label(string=self.PROJECT)

    def set_project(self) -> None:
        project_dict: dict = json_to_dict(CURRENT_PROJECT_JSON_PATH)
        project_dict['current_project'] = self.PROJECT
        dict_to_json(dictionary=project_dict, json_file_path=CURRENT_PROJECT_JSON_PATH)
        self.ACCEPTED = True
        self.accept()

    def setup_pipezer(self) -> None:
        # Chemin vers le répertoire utilisateur actuel (cela fonctionnera sur la plupart des systèmes)
        user_home_dir = os.path.expanduser("~")

        # Définir le dossier .pipezer dans le répertoire utilisateur
        pipezer_dir = os.path.join(user_home_dir, '.pipezer')

        # S'assurer que le dossier .pipezer existe
        if not os.path.exists(pipezer_dir):
            os.makedirs(pipezer_dir)

        # Vérification si user.json existe
        user_file_path = os.path.join(pipezer_dir, 'user.json')
        if not os.path.exists(user_file_path):
            user_dialog = UserDialog()
            if user_dialog.exec_() == QDialog.Accepted:
                username = user_dialog.get_username()

                # Sauvegarder le nom d'utilisateur dans user.json
                with open(user_file_path, 'w') as user_file:
                    json.dump({"username": username}, user_file)

        # Enregistrer le projet sélectionné dans current_project.json
        project_file_path = os.path.join(pipezer_dir, 'current_project.json')
        with open(project_file_path, 'w') as project_file:
            json.dump({"project_path": self.PROJECT}, project_file)
