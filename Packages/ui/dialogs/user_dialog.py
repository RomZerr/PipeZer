from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont

class UserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration PipeZer")
        self.setFixedSize(400, 250)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        self.setup_ui()
        self.setup_style()

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)

        # Titre
        self.title_label = QLabel("Configuration initiale")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName('title_label')
        
        # Label d'instruction
        self.label = QLabel("Veuillez entrer votre nom d'utilisateur:")
        self.label.setObjectName('instruction_label')
        
        # Line edit pour le nom d'utilisateur
        self.username_edit = QLineEdit(self)
        self.username_edit.setPlaceholderText("Votre nom d'utilisateur")
        self.username_edit.setObjectName('username_edit')
        
        # Layout pour les boutons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.ok_button = QPushButton("Continuer", self)
        self.cancel_button = QPushButton("Annuler", self)
        
        # Définir la hauteur des boutons
        self.ok_button.setFixedHeight(40)
        self.cancel_button.setFixedHeight(40)
        
        self.ok_button.setObjectName('ok_button')
        self.cancel_button.setObjectName('cancel_button')
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        # Ajout des éléments au layout principal
        layout.addWidget(self.title_label)
        layout.addWidget(self.label)
        layout.addWidget(self.username_edit)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        
    def setup_style(self):
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
            
            QLabel#instruction_label {
                color: #bdc3c7;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLineEdit#username_edit {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLineEdit#username_edit:focus {
                border-color: #2980b9;
                background-color: #2c3e50;
            }
            
            QPushButton#ok_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton#ok_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f4e79);
            }
            
            QPushButton#ok_button:pressed {
                background: #1f4e79;
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

    def get_username(self):
        return self.username_edit.text()
