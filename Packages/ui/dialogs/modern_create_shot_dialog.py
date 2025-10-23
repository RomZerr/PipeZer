"""
Modern dialog for creating shots
"""

import os
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QWidget
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QFont

from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT


class ModernCreateShotDialog(QDialog):
    """Modern dialog for creating shots with sequence folders"""
    
    shot_created = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = "dark"
        self.setup_ui()
        self.setup_theme()
        self.center_on_screen()
        
    def setup_ui(self):
        self.setWindowTitle("Create Shot")
        self.setFixedSize(600, 450)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        title = QLabel("Create Shot")
        title.setObjectName("dialog_title")
        main_layout.addWidget(title)
        
        desc = QLabel("Create a new shot with its sequence and number")
        desc.setObjectName("dialog_description")
        main_layout.addWidget(desc)
        
        form_widget = QWidget()
        form_widget.setObjectName("form_widget")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        sequence_layout = QHBoxLayout()
        self.sequence_label = QLabel('SEQUENCE:')
        self.sequence_label.setObjectName("section_label")
        self.sequence_input = QLineEdit()
        self.sequence_input.setObjectName("input_field")
        self.sequence_input.setPlaceholderText('XXXX (ex: 0020)')
        sequence_layout.addWidget(self.sequence_label)
        sequence_layout.addWidget(self.sequence_input)
        form_layout.addLayout(sequence_layout)
        
        # Ligne pour entrer le numéro de shot
        shot_layout = QHBoxLayout()
        self.shot_label = QLabel('SHOT:')
        self.shot_label.setObjectName("section_label")
        self.shot_input = QLineEdit()
        self.shot_input.setObjectName("input_field")
        self.shot_input.setPlaceholderText('XXXX (ex: 0010)')
        shot_layout.addWidget(self.shot_label)
        shot_layout.addWidget(self.shot_input)
        form_layout.addLayout(shot_layout)
        
        main_layout.addWidget(form_widget)
        
        # Boutons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setFixedSize(120, 45)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.create_button = QPushButton("Create")
        self.create_button.setObjectName("create_button")
        self.create_button.setFixedSize(120, 45)
        self.create_button.clicked.connect(self.create_shot)
        button_layout.addWidget(self.create_button)
        
        main_layout.addLayout(button_layout)
        
    def setup_theme(self):
        """Configure le thème du dialogue"""
        if self.current_theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def apply_dark_theme(self):
        """Applique le thème sombre"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #0D1117, stop:1 #161B22);
                color: #E6EDF3;
            }
            
            QLabel#title_icon {
                font-size: 32px;
                margin-right: 10px;
            }
            
            QLabel#dialog_title {
                color: #E6EDF3;
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 10px;
            }
            
            QLabel#dialog_description {
                color: #8B949E;
                font-size: 14px;
                margin-bottom: 20px;
                line-height: 1.4;
            }
            
            QWidget#form_widget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #161B22, stop:1 #21262D);
                border: 1px solid #30363D;
                border-radius: 16px;
                padding: 25px;
            }
            
            QLabel#section_label {
                color: #E6EDF3;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            
            QLineEdit#input_field {
                background-color: #0D1117;
                border: 2px solid #30363D;
                border-radius: 10px;
                color: #E6EDF3;
                font-size: 14px;
                padding: 14px 18px;
                selection-background-color: #6366F1;
            }
            
            QLineEdit#input_field:focus {
                border-color: #6366F1;
                background-color: #161B22;
            }
            
            QPushButton#create_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6366F1, stop:1 #5B5BD6);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: 600;
                padding: 14px 28px;
            }
            
            QPushButton#create_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #5B5BD6, stop:1 #4F46E5);
            }
            
            QPushButton#create_button:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4F46E5, stop:1 #3730A3);
            }
            
            QPushButton#cancel_button {
                background-color: transparent;
                border: 2px solid #30363D;
                border-radius: 10px;
                color: #E6EDF3;
                font-size: 16px;
                font-weight: 500;
                padding: 14px 28px;
            }
            
            QPushButton#cancel_button:hover {
                background-color: #30363D;
                border-color: #6366F1;
                color: #6366F1;
            }
            
            /* Styles pour QMessageBox */
            QMessageBox {
                background-color: #161B22;
                color: #E6EDF3;
            }
            
            QMessageBox QLabel {
                color: #E6EDF3;
                font-size: 14px;
                min-width: 300px;
            }
            
            QMessageBox QPushButton {
                background-color: #6366F1;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 20px;
                min-width: 80px;
            }
            
            QMessageBox QPushButton:hover {
                background-color: #5B5BD6;
            }
        """)
    
    def apply_light_theme(self):
        """Applique le thème clair"""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                color: #1E1E2E;
            }
            
            QLabel#label {
                color: #1E1E2E;
                font-size: 14px;
                font-weight: 600;
            }
            
            QLineEdit#line_edit {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                color: #1E1E2E;
                font-size: 14px;
                padding: 8px 12px;
            }
            
            QLineEdit#line_edit:focus {
                border-color: #6366F1;
            }
            
            QPushButton#create_button {
                background-color: #6366F1;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 12px 24px;
            }
            
            QPushButton#create_button:hover {
                background-color: #5B5BD6;
            }
            
            QPushButton#create_button:pressed {
                background-color: #4F46E5;
            }
        """)
    
    def set_theme(self, theme):
        """Change le thème du dialogue"""
        self.current_theme = theme
        self.setup_theme()
    
    def create_shot(self):
        """Crée le shot"""
        sequence_number = self.sequence_input.text().strip()
        shot_number = self.shot_input.text().strip()

        if not self.validate_input(sequence_number, shot_number):
            return

        sequence = f"sq{sequence_number}"
        shot = f"sh{shot_number}"

        try:
            # Chercher le dossier qui contient "shot" à la racine du projet
            shot_folder_base = None
            if os.path.exists(CURRENT_PROJECT):
                for folder in os.listdir(CURRENT_PROJECT):
                    folder_path = os.path.join(CURRENT_PROJECT, folder)
                    if os.path.isdir(folder_path) and "shot" in folder.lower():
                        shot_folder_base = folder_path
                        break
            
            # Si le dossier "shot" n'existe pas, créer "05_shot" par défaut
            if not shot_folder_base:
                shot_folder_base = os.path.join(CURRENT_PROJECT, "05_shot")
                os.makedirs(shot_folder_base, exist_ok=True)
            
            # Créer les chemins pour la séquence et le shot
            sequence_folder = os.path.join(shot_folder_base, sequence)
            shot_folder = os.path.join(sequence_folder, f"{sequence}_{shot}")
            
            # Vérifier si le shot existe déjà
            if os.path.exists(shot_folder):
                QMessageBox.warning(
                    self, 
                    "Already Exists", 
                    f"Shot '{sequence}_{shot}' already exists!\n\nPath: {shot_folder}"
                )
                return
            
            # Vérifier si la séquence existe déjà (pour information)
            sequence_already_exists = os.path.exists(sequence_folder)
            
            # Créer les dossiers nécessaires
            if not sequence_already_exists:
                # Créer la séquence avec ses dossiers master et multiShot
                self.create_sequence_folders(sequence_folder)
            
            # Créer le dossier du shot (sq[XXXX]_sh[XXXX])
            os.makedirs(shot_folder, exist_ok=True)
            self.create_shot_subfolders(shot_folder)

            # Ajouter une notification (commenté temporairement)
            # username = get_username()
            # add_notification(username, "create_shot", f"{shot} in {sequence}")

            # Message de succès avec information sur la séquence
            success_message = f"Shot '{sequence}_{shot}' created successfully!"
            if sequence_already_exists:
                success_message += f"\n\nAdded to existing sequence '{sequence}'."
            else:
                success_message += f"\n\nNew sequence '{sequence}' created."
            
            QMessageBox.information(self, "Success", success_message)
            
            # Émettre le signal
            self.shot_created.emit(f"{sequence}_{shot}")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating shot: {str(e)}")

    def validate_input(self, sequence_number, shot_number):
        if not sequence_number.isdigit() or len(sequence_number) != 4:
            QMessageBox.warning(self, "Error", "Sequence number must be a 4-digit number (e.g., 0020).")
            return False
        if not shot_number.isdigit() or len(shot_number) != 4:
            QMessageBox.warning(self, "Error", "Shot number must be a 4-digit number (e.g., 0010).")
            return False
        return True

    def create_sequence_folders(self, sequence_folder):
        master_folder = os.path.join(sequence_folder, f"{os.path.basename(sequence_folder)}_master")
        multi_shot_folder = os.path.join(sequence_folder, f"{os.path.basename(sequence_folder)}_multiShot")

        if not os.path.exists(master_folder):
            os.makedirs(master_folder)
            self.create_master_subfolders(master_folder)

        if not os.path.exists(multi_shot_folder):
            os.makedirs(multi_shot_folder)
            self.create_multi_shot_subfolders(multi_shot_folder)

    def create_master_subfolders(self, master_folder):
        subfolders = [
            "01_animation", "02_lighting", "03_compositing", "04_fx", "05_render"
        ]
        for subfolder in subfolders:
            os.makedirs(os.path.join(master_folder, subfolder), exist_ok=True)

    def create_multi_shot_subfolders(self, multi_shot_folder):
        subfolders = [
            "01_animation", "02_lighting", "03_compositing", "04_fx", "05_render"
        ]
        for subfolder in subfolders:
            os.makedirs(os.path.join(multi_shot_folder, subfolder), exist_ok=True)

    def create_shot_subfolders(self, shot_folder):
        subfolders = [
            "01_animation", "02_lighting", "03_compositing", "04_fx", "05_render"
        ]
        for subfolder in subfolders:
            os.makedirs(os.path.join(shot_folder, subfolder), exist_ok=True)
    
    def center_on_screen(self):
        """Centre la fenêtre sur l'écran"""
        from PySide2.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )