"""
Widget de sélection de langue
"""

from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PySide2.QtCore import Qt, Signal
from Packages.utils.translations import translation_manager

class LanguageSelector(QWidget):
    """Widget pour sélectionner la langue de l'interface"""
    
    language_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_current_language()
    
    def setup_ui(self):
        """Configure l'interface du sélecteur de langue"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = QLabel("🌐 Language / Langue / Idioma")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Select your preferred language / Sélectionnez votre langue préférée / Seleccione su idioma preferido")
        desc.setObjectName("page_description")
        layout.addWidget(desc)
        
        # Sélecteur de langue
        language_layout = QHBoxLayout()
        
        language_label = QLabel("Language:")
        language_layout.addWidget(language_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("🇫🇷 Français", "fr")
        self.language_combo.addItem("🇺🇸 English", "en")
        self.language_combo.addItem("🇪🇸 Español", "es")
        
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        language_layout.addWidget(self.language_combo)
        
        language_layout.addStretch()
        layout.addLayout(language_layout)
        
        # Bouton d'application
        self.apply_button = QPushButton("Apply / Appliquer / Aplicar")
        self.apply_button.clicked.connect(self.apply_language)
        layout.addWidget(self.apply_button)
        
        layout.addStretch()
    
    def load_current_language(self):
        """Charge la langue actuelle dans le combo box"""
        current_lang = translation_manager.current_language
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_lang:
                self.language_combo.setCurrentIndex(i)
                break
    
    def on_language_changed(self, text):
        """Gère le changement de langue dans le combo box"""
        # Cette méthode est appelée quand l'utilisateur change la sélection
        pass
    
    def apply_language(self):
        """Applique la langue sélectionnée"""
        current_data = self.language_combo.currentData()
        if current_data:
            self.language_changed.emit(current_data)
