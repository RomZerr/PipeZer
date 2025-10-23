import os
from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QApplication
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QFont, QPixmap
from Packages.utils.translation import translation_manager


class LoadingDialog(QDialog):
    """
    Dialog de chargement moderne avec barre de progression
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translation_manager.get_text("app.title"))
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Logo/Titre
        self.title_label = QLabel(translation_manager.get_text("app.title"))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName('title_label')
        
        # Message de chargement
        self.message_label = QLabel(translation_manager.get_text("app.initialization"))
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setObjectName('message_label')
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName('progress_bar')
        
        # Layout principal
        layout.addWidget(self.title_label)
        layout.addWidget(self.message_label)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
    def setup_style(self):
        """Configuration du style moderne"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 15px;
                border: 2px solid #3498db;
            }
            
            QLabel#title_label {
                color: #ecf0f1;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-bottom: 10px;
            }
            
            QLabel#message_label {
                color: #bdc3c7;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 8px;
                text-align: center;
                background-color: #2c3e50;
                height: 20px;
                color: #ecf0f1;
                font-weight: bold;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 6px;
            }
        """)
        
    def update_progress(self, value, message=""):
        """Met à jour la barre de progression et le message"""
        self.progress_bar.setValue(value)
        if message:
            self.message_label.setText(message)
        QApplication.processEvents()
        
    def show_loading(self):
        """Affiche le dialog et centre-le à l'écran"""
        self.show()
        self.center_on_screen()
        
    def center_on_screen(self):
        """Centre le dialog sur l'écran"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)