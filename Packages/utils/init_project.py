import os
import shutil
import json
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from PySide2.QtGui import QFont
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
        self.setWindowTitle('Configuration du projet')
        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        self.setup_ui()
        self.setup_style()

    def setup_ui(self) -> None:
        """Configuration de l'interface utilisateur"""
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(25)
        self.setLayout(self.main_layout)

        # Titre
        self.title_label = QLabel('Sélection du projet')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName('title_label')
        
        # Description
        self.description_label = QLabel('Veuillez sélectionner le dossier de votre projet PipeZer:')
        self.description_label.setObjectName('description_label')
        self.description_label.setWordWrap(True)

        # Bouton de sélection
        self.button = QPushButton('📁 Sélectionner le dossier du projet')
        self.button.setObjectName('select_button')
        self.button.setFixedHeight(50)

        # Label affichant le chemin sélectionné
        self.label = QLabel('Aucun projet sélectionné')
        self.label.setObjectName('path_label')
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            QLabel#path_label {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 15px;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
        """)

        # Layout pour les boutons d'action
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.ok_button = QPushButton('Continuer')
        self.cancel_button = QPushButton('Annuler')
        
        self.ok_button.setObjectName('ok_button')
        self.cancel_button.setObjectName('cancel_button')
        self.ok_button.setFixedHeight(40)
        self.cancel_button.setFixedHeight(40)
        
        # Désactiver le bouton OK initialement
        self.ok_button.setEnabled(False)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)

        # Ajout des éléments au layout principal
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.description_label)
        self.main_layout.addWidget(self.button)
        self.main_layout.addWidget(self.label)
        self.main_layout.addLayout(button_layout)
        
    def setup_style(self) -> None:
        """Configuration du style moderne"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 10px;
            }
            
            QLabel#title_label {
                color: #ecf0f1;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-bottom: 10px;
            }
            
            QLabel#description_label {
                color: #bdc3c7;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton#select_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton#select_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f4e79);
            }
            
            QPushButton#select_button:pressed {
                background: #1f4e79;
            }
            
            QPushButton#ok_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton#ok_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #229954, stop:1 #1e8449);
            }
            
            QPushButton#ok_button:pressed {
                background: #1e8449;
            }
            
            QPushButton#ok_button:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
            
            QPushButton#cancel_button {
                background-color: #95a5a6;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton#cancel_button:hover {
                background-color: #7f8c8d;
            }
            
            QPushButton#cancel_button:pressed {
                background-color: #6c7b7d;
            }
        """)

    def create_connections(self) -> None:
        self.button.clicked.connect(self.select_project)
        self.ok_button.clicked.connect(self.set_project)
        self.cancel_button.clicked.connect(self.reject)

    def update_label(self, string: str) -> None:
        self.label.setText(string)
        # Activer le bouton OK si un projet est sélectionné
        self.ok_button.setEnabled(bool(string and string != 'Aucun projet sélectionné'))

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
