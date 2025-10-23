import os
import json
from PySide2.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QLineEdit, QRadioButton, QButtonGroup, QFileDialog,
    QStackedWidget, QFrame, QSpacerItem, QSizePolicy
)
from PySide2.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide2.QtGui import QFont, QPixmap, QPainter, QColor

from Packages.utils.translation import translation_manager


class PreferencesDialog(QDialog):
    """
    Dialog de préférences moderne avec navigation par étapes
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 0
        self.total_steps = 5
        self.selected_language = "fr"
        self.selected_theme = "dark"
        self.username = ""
        self.project_path = ""
        self.pipeline_choice = "create_new"  # "create_new", "use_existing"
        
        self.setup_ui()
        self.setup_style()
        self.load_saved_preferences()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.setWindowTitle(translation_manager.get_text("preferences.title"))
        self.setFixedSize(600, 650)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header avec titre et progression
        self.create_header(main_layout)
        
        # Widget empilé pour les différentes étapes
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stacked_widget")
        
        # Créer les différentes étapes
        self.create_language_step()
        self.create_username_step()
        self.create_theme_step()
        self.create_project_step()
        self.create_pipeline_step()
        
        main_layout.addWidget(self.stacked_widget)
        
        # Footer avec boutons de navigation
        self.create_footer(main_layout)
        
        self.setLayout(main_layout)
        
    def create_header(self, parent_layout):
        """Crée l'en-tête avec titre et barre de progression"""
        header_frame = QFrame()
        header_frame.setObjectName("header_frame")
        header_frame.setFixedHeight(120)
        
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(40, 20, 40, 20)
        header_layout.setSpacing(10)
        
        # Titre principal
        self.title_label = QLabel(translation_manager.get_text("preferences.welcome"))
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # Sous-titre
        self.subtitle_label = QLabel(translation_manager.get_text("preferences.subtitle"))
        self.subtitle_label.setObjectName("subtitle_label")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        
        # Barre de progression
        self.progress_label = QLabel(translation_manager.get_text("preferences.step", current=1, total=self.total_steps))
        self.progress_label.setObjectName("progress_label")
        self.progress_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)
        header_layout.addWidget(self.progress_label)
        
        header_frame.setLayout(header_layout)
        parent_layout.addWidget(header_frame)
        
    def create_footer(self, parent_layout):
        """Crée le pied de page avec boutons de navigation"""
        footer_frame = QFrame()
        footer_frame.setObjectName("footer_frame")
        footer_frame.setFixedHeight(80)
        
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(40, 20, 40, 20)
        footer_layout.setSpacing(15)
        
        # Bouton précédent
        self.previous_button = QPushButton(translation_manager.get_text("preferences.previous"))
        self.previous_button.setObjectName("previous_button")
        self.previous_button.setFixedHeight(40)
        self.previous_button.setEnabled(False)
        self.previous_button.clicked.connect(self.previous_step)
        
        # Espaceur
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # Bouton suivant/terminer
        self.next_button = QPushButton(translation_manager.get_text("preferences.next"))
        self.next_button.setObjectName("next_button")
        self.next_button.setFixedHeight(40)
        self.next_button.clicked.connect(self.next_step)
        
        # Bouton annuler
        self.cancel_button = QPushButton(translation_manager.get_text("preferences.cancel"))
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.clicked.connect(self.reject)
        
        footer_layout.addWidget(self.previous_button)
        footer_layout.addItem(spacer)
        footer_layout.addWidget(self.cancel_button)
        footer_layout.addWidget(self.next_button)
        
        footer_frame.setLayout(footer_layout)
        parent_layout.addWidget(footer_frame)
        
    def create_language_step(self):
        """Crée l'étape de sélection de langue"""
        step_widget = QFrame()
        step_layout = QVBoxLayout()
        step_layout.setContentsMargins(60, 40, 60, 40)
        step_layout.setSpacing(30)
        
        # Titre de l'étape
        title = QLabel(translation_manager.get_text("language.title"))
        title.setObjectName("step_title")
        title.setAlignment(Qt.AlignCenter)
        
        # Description
        description = QLabel(translation_manager.get_text("language.description"))
        description.setObjectName("step_description")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        
        # ComboBox pour la langue
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("language_combo")
        self.language_combo.setFixedHeight(50)
        
        # Ajouter les langues disponibles
        languages = translation_manager.get_available_languages()
        for code, name in languages.items():
            self.language_combo.addItem(name, code)
        
        # Sélectionner la langue actuelle
        current_index = self.language_combo.findData(self.selected_language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
        
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        
        step_layout.addWidget(title)
        step_layout.addWidget(description)
        step_layout.addWidget(self.language_combo)
        step_layout.addStretch()
        
        step_widget.setLayout(step_layout)
        self.stacked_widget.addWidget(step_widget)
        
    def create_username_step(self):
        """Crée l'étape de saisie du nom d'utilisateur"""
        step_widget = QFrame()
        step_layout = QVBoxLayout()
        step_layout.setContentsMargins(60, 40, 60, 40)
        step_layout.setSpacing(30)
        
        # Titre de l'étape
        title = QLabel(translation_manager.get_text("username.title"))
        title.setObjectName("step_title")
        title.setAlignment(Qt.AlignCenter)
        
        # Description
        description = QLabel(translation_manager.get_text("username.description"))
        description.setObjectName("step_description")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        
        # Champ de saisie
        self.username_edit = QLineEdit()
        self.username_edit.setObjectName("username_edit")
        self.username_edit.setFixedHeight(50)
        self.username_edit.setPlaceholderText(translation_manager.get_text("username.placeholder"))
        self.username_edit.textChanged.connect(self.on_username_changed)
        
        step_layout.addWidget(title)
        step_layout.addWidget(description)
        step_layout.addWidget(self.username_edit)
        step_layout.addStretch()
        
        step_widget.setLayout(step_layout)
        self.stacked_widget.addWidget(step_widget)
        
    def create_theme_step(self):
        """Crée l'étape de sélection du thème"""
        step_widget = QFrame()
        step_layout = QVBoxLayout()
        step_layout.setContentsMargins(60, 40, 60, 40)
        step_layout.setSpacing(30)
        
        # Titre de l'étape
        title = QLabel(translation_manager.get_text("theme.title"))
        title.setObjectName("step_title")
        title.setAlignment(Qt.AlignCenter)
        
        # Description
        description = QLabel(translation_manager.get_text("theme.description"))
        description.setObjectName("step_description")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        
        # Groupe de boutons radio pour les thèmes
        self.theme_group = QButtonGroup()
        themes = [
            ("dark", translation_manager.get_text("theme.dark")),
            ("light", translation_manager.get_text("theme.light")),
            ("blue", translation_manager.get_text("theme.blue")),
            ("green", translation_manager.get_text("theme.green")),
            ("purple", translation_manager.get_text("theme.purple"))
        ]
        
        for i, (theme_code, theme_name) in enumerate(themes):
            radio = QRadioButton(theme_name)
            radio.setObjectName("theme_radio")
            radio.setProperty("theme", theme_code)
            if theme_code == self.selected_theme:
                radio.setChecked(True)
            radio.toggled.connect(self.on_theme_changed)
            self.theme_group.addButton(radio, i)
            step_layout.addWidget(radio)
        
        step_layout.addStretch()
        
        step_widget.setLayout(step_layout)
        self.stacked_widget.addWidget(step_widget)
        
    def create_project_step(self):
        """Crée l'étape de sélection du projet"""
        step_widget = QFrame()
        step_layout = QVBoxLayout()
        step_layout.setContentsMargins(60, 40, 60, 40)
        step_layout.setSpacing(30)
        
        # Titre de l'étape
        title = QLabel(translation_manager.get_text("project.title"))
        title.setObjectName("step_title")
        title.setAlignment(Qt.AlignCenter)
        
        # Description
        description = QLabel(translation_manager.get_text("project.description"))
        description.setObjectName("step_description")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        
        # Bouton de sélection
        self.select_project_button = QPushButton("📁 " + translation_manager.get_text("project.select"))
        self.select_project_button.setObjectName("select_project_button")
        self.select_project_button.setFixedHeight(50)
        self.select_project_button.clicked.connect(self.select_project)
        
        # Label affichant le chemin sélectionné
        self.project_label = QLabel(translation_manager.get_text("project.none_selected"))
        self.project_label.setObjectName("project_label")
        self.project_label.setWordWrap(True)
        
        step_layout.addWidget(title)
        step_layout.addWidget(description)
        step_layout.addWidget(self.select_project_button)
        step_layout.addWidget(self.project_label)
        step_layout.addStretch()
        
        step_widget.setLayout(step_layout)
        self.stacked_widget.addWidget(step_widget)
        
    def create_pipeline_step(self):
        """Crée l'étape de configuration du pipeline"""
        step_widget = QFrame()
        step_layout = QVBoxLayout()
        step_layout.setContentsMargins(60, 40, 60, 40)
        step_layout.setSpacing(30)
        
        # Titre de l'étape
        title = QLabel(translation_manager.get_text("pipeline.title"))
        title.setObjectName("step_title")
        title.setAlignment(Qt.AlignCenter)
        
        # Description
        description = QLabel(translation_manager.get_text("pipeline.description"))
        description.setObjectName("step_description")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        
        # Groupe de boutons radio pour les options pipeline
        self.pipeline_group = QButtonGroup()
        
        # Option 1: Créer de nouveaux dossiers
        create_new_radio = QRadioButton(translation_manager.get_text("pipeline.create_new"))
        create_new_radio.setObjectName("pipeline_radio")
        create_new_radio.setProperty("choice", "create_new")
        create_new_radio.toggled.connect(self.on_pipeline_choice_changed)
        self.pipeline_group.addButton(create_new_radio, 0)
        
        create_new_desc = QLabel(translation_manager.get_text("pipeline.new_description"))
        create_new_desc.setObjectName("pipeline_description")
        create_new_desc.setWordWrap(True)
        
        # Option 2: Utiliser les dossiers existants
        use_existing_radio = QRadioButton(translation_manager.get_text("pipeline.use_existing"))
        use_existing_radio.setObjectName("pipeline_radio")
        use_existing_radio.setProperty("choice", "use_existing")
        use_existing_radio.toggled.connect(self.on_pipeline_choice_changed)
        self.pipeline_group.addButton(use_existing_radio, 1)
        
        use_existing_desc = QLabel(translation_manager.get_text("pipeline.existing_description"))
        use_existing_desc.setObjectName("pipeline_description")
        use_existing_desc.setWordWrap(True)
        
        # Option par défaut: Créer de nouveaux dossiers
        create_new_radio.setChecked(True)
        
        # Vérifier si le projet a des dossiers existants
        if self.project_path and self.has_existing_folders():
            use_existing_radio.setEnabled(True)
        else:
            use_existing_radio.setEnabled(False)
            use_existing_radio.setToolTip(translation_manager.get_text("project.none_selected"))
        
        step_layout.addWidget(title)
        step_layout.addWidget(description)
        step_layout.addSpacing(20)
        step_layout.addWidget(create_new_radio)
        step_layout.addWidget(create_new_desc)
        step_layout.addSpacing(10)
        step_layout.addWidget(use_existing_radio)
        step_layout.addWidget(use_existing_desc)
        step_layout.addStretch()
        
        step_widget.setLayout(step_layout)
        self.stacked_widget.addWidget(step_widget)
        
    def has_existing_folders(self):
        """Vérifie si le projet a des dossiers existants"""
        if not self.project_path or not os.path.exists(self.project_path):
            return False
            
        # Vérifier la présence de dossiers typiques
        typical_folders = ['04_asset', '05_shot', '02_ressource', 'assets', 'shots', 'resources']
        for folder in typical_folders:
            folder_path = os.path.join(self.project_path, folder)
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                return True
        return False
        
    def setup_style(self):
        """Configuration du style moderne"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 15px;
            }
            
            QFrame#header_frame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }
            
            QFrame#footer_frame {
                background-color: #34495e;
                border-bottom-left-radius: 15px;
                border-bottom-right-radius: 15px;
            }
            
            QLabel#title_label {
                color: white;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLabel#subtitle_label {
                color: #ecf0f1;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLabel#progress_label {
                color: #bdc3c7;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLabel#step_title {
                color: #ecf0f1;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLabel#step_description {
                color: #bdc3c7;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QComboBox#language_combo {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QComboBox#language_combo:focus {
                border-color: #2980b9;
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
            }
            
            QRadioButton#theme_radio {
                color: #ecf0f1;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                spacing: 10px;
            }
            
            QRadioButton#theme_radio::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid #3498db;
                background-color: #34495e;
            }
            
            QRadioButton#theme_radio::indicator:checked {
                background-color: #3498db;
            }
            
            QRadioButton#pipeline_radio {
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                spacing: 10px;
            }
            
            QRadioButton#pipeline_radio::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid #3498db;
                background-color: #34495e;
            }
            
            QRadioButton#pipeline_radio::indicator:checked {
                background-color: #3498db;
            }
            
            QLabel#pipeline_description {
                color: #bdc3c7;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-left: 30px;
            }
            
            QPushButton#select_project_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton#select_project_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f4e79);
            }
            
            QLabel#project_label {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 15px;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            
            QPushButton#next_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 100px;
            }
            
            QPushButton#next_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #229954, stop:1 #1e8449);
            }
            
            QPushButton#previous_button {
                background-color: #95a5a6;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 100px;
            }
            
            QPushButton#previous_button:hover {
                background-color: #7f8c8d;
            }
            
            QPushButton#cancel_button {
                background-color: #e74c3c;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 100px;
            }
            
            QPushButton#cancel_button:hover {
                background-color: #c0392b;
            }
        """)
        
    def next_step(self):
        """Passe à l'étape suivante"""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self.stacked_widget.setCurrentIndex(self.current_step)
            self.update_navigation_buttons()
            self.update_progress_label()
        else:
            # Dernière étape - terminer
            self.save_preferences()
            self.accept()
            
    def previous_step(self):
        """Retourne à l'étape précédente"""
        if self.current_step > 0:
            self.current_step -= 1
            self.stacked_widget.setCurrentIndex(self.current_step)
            self.update_navigation_buttons()
            self.update_progress_label()
            
    def update_navigation_buttons(self):
        """Met à jour l'état des boutons de navigation"""
        self.previous_button.setEnabled(self.current_step > 0)
        
        if self.current_step == self.total_steps - 1:
            self.next_button.setText(translation_manager.get_text("preferences.finish"))
        else:
            self.next_button.setText(translation_manager.get_text("preferences.next"))
            
    def update_progress_label(self):
        """Met à jour le label de progression"""
        self.progress_label.setText(
            translation_manager.get_text("preferences.step", 
                                       current=self.current_step + 1, 
                                       total=self.total_steps)
        )
        
    def on_language_changed(self):
        """Appelé quand la langue change"""
        try:
            # Bloquer temporairement les signaux pour éviter la récursion
            self.language_combo.blockSignals(True)
            
            self.selected_language = self.language_combo.currentData()
            translation_manager.set_language(self.selected_language)
            
            # Mettre à jour seulement les textes principaux
            self.setWindowTitle(translation_manager.get_text("preferences.title"))
            if hasattr(self, 'title_label'):
                self.title_label.setText(translation_manager.get_text("preferences.welcome"))
            if hasattr(self, 'subtitle_label'):
                self.subtitle_label.setText(translation_manager.get_text("preferences.subtitle"))
            if hasattr(self, 'next_button'):
                self.next_button.setText(translation_manager.get_text("preferences.next"))
            if hasattr(self, 'previous_button'):
                self.previous_button.setText(translation_manager.get_text("preferences.previous"))
            if hasattr(self, 'cancel_button'):
                self.cancel_button.setText(translation_manager.get_text("preferences.cancel"))
            
            self.update_progress_label()
            
            # Débloquer les signaux
            self.language_combo.blockSignals(False)
        except Exception as e:
            print(f"Erreur lors du changement de langue: {e}")
            # En cas d'erreur, garder le français par défaut
            self.selected_language = "fr"
            translation_manager.set_language("fr")
            self.language_combo.blockSignals(False)
        
    def on_username_changed(self):
        """Appelé quand le nom d'utilisateur change"""
        self.username = self.username_edit.text().strip()
        
    def on_theme_changed(self):
        """Appelé quand le thème change"""
        checked_button = self.theme_group.checkedButton()
        if checked_button:
            self.selected_theme = checked_button.property("theme")
            
    def on_pipeline_choice_changed(self):
        """Appelé quand le choix du pipeline change"""
        checked_button = self.pipeline_group.checkedButton()
        if checked_button:
            self.pipeline_choice = checked_button.property("choice")
            
    def select_project(self):
        """Ouvre le dialog de sélection de projet"""
        project_path = QFileDialog.getExistingDirectory(
            self, 
            translation_manager.get_text("project.select")
        )
        
        if project_path:
            self.project_path = project_path.replace('\\', '/')
            self.project_label.setText(self.project_path)
            
            # Mettre à jour l'état de l'option "utiliser dossiers existants"
            self.update_pipeline_options()
            
    def update_pipeline_options(self):
        """Met à jour les options du pipeline selon le projet sélectionné"""
        if hasattr(self, 'pipeline_group'):
            use_existing_button = self.pipeline_group.button(1)  # Index 1 = use_existing
            if use_existing_button:
                if self.project_path and self.has_existing_folders():
                    use_existing_button.setEnabled(True)
                    use_existing_button.setToolTip("")
                else:
                    use_existing_button.setEnabled(False)
                    use_existing_button.setToolTip(translation_manager.get_text("project.none_selected"))
            
    def load_saved_preferences(self):
        """Charge les préférences sauvegardées"""
        try:
            user_home_dir = os.path.expanduser("~")
            pipezer_dir = os.path.join(user_home_dir, '.pipezer')
            prefs_file = os.path.join(pipezer_dir, 'preferences.json')
            
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    
                self.selected_language = prefs.get('language', 'fr')
                self.selected_theme = prefs.get('theme', 'dark')
                self.username = prefs.get('username', '')
                self.project_path = prefs.get('project_path', '')
                self.pipeline_choice = prefs.get('pipeline_choice', 'create_new')
                
                # Mettre à jour l'interface
                self.username_edit.setText(self.username)
                if self.project_path:
                    self.project_label.setText(self.project_path)
                    
        except Exception as e:
            print(f"Erreur lors du chargement des préférences: {e}")
            
    def save_preferences(self):
        """Sauvegarde les préférences"""
        try:
            user_home_dir = os.path.expanduser("~")
            pipezer_dir = os.path.join(user_home_dir, '.pipezer')
            
            if not os.path.exists(pipezer_dir):
                os.makedirs(pipezer_dir)
                
            prefs = {
                'language': self.selected_language,
                'theme': self.selected_theme,
                'username': self.username,
                'project_path': self.project_path,
                'pipeline_choice': self.pipeline_choice
            }
            
            prefs_file = os.path.join(pipezer_dir, 'preferences.json')
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des préférences: {e}")
            
    def update_main_texts(self):
        """Met à jour les textes principaux sans toucher aux options de langue"""
        try:
            # Mettre à jour les textes principaux
            self.setWindowTitle(translation_manager.get_text("preferences.title"))
            if hasattr(self, 'title_label'):
                self.title_label.setText(translation_manager.get_text("preferences.welcome"))
            if hasattr(self, 'subtitle_label'):
                self.subtitle_label.setText(translation_manager.get_text("preferences.subtitle"))
            
            # Mettre à jour les boutons
            if hasattr(self, 'next_button'):
                self.next_button.setText(translation_manager.get_text("preferences.next"))
            if hasattr(self, 'previous_button'):
                self.previous_button.setText(translation_manager.get_text("preferences.previous"))
            if hasattr(self, 'cancel_button'):
                self.cancel_button.setText(translation_manager.get_text("preferences.cancel"))
            
            # Mettre à jour la progression
            self.update_progress_label()
            
            # Mettre à jour les textes des étapes (sans les options de langue)
            self.update_step_texts_no_language()
        except Exception as e:
            print(f"Erreur lors de la mise à jour des textes: {e}")
    
    def update_all_texts(self):
        """Met à jour tous les textes de l'interface"""
        try:
            # Mettre à jour les textes principaux
            self.setWindowTitle(translation_manager.get_text("preferences.title"))
            if hasattr(self, 'title_label'):
                self.title_label.setText(translation_manager.get_text("preferences.welcome"))
            if hasattr(self, 'subtitle_label'):
                self.subtitle_label.setText(translation_manager.get_text("preferences.subtitle"))
            
            # Mettre à jour les boutons
            if hasattr(self, 'next_button'):
                self.next_button.setText(translation_manager.get_text("preferences.next"))
            if hasattr(self, 'previous_button'):
                self.previous_button.setText(translation_manager.get_text("preferences.previous"))
            if hasattr(self, 'cancel_button'):
                self.cancel_button.setText(translation_manager.get_text("preferences.cancel"))
            
            # Mettre à jour la progression
            self.update_progress_label()
            
            # Mettre à jour les textes des étapes
            self.update_step_texts()
        except Exception as e:
            print(f"Erreur lors de la mise à jour des textes: {e}")
        
    def update_step_texts(self):
        """Met à jour les textes de toutes les étapes"""
        try:
            # Étape 1: Langue
            if hasattr(self, 'language_combo'):
                # Mettre à jour les options de langue
                self.language_combo.clear()
                languages = translation_manager.get_available_languages()
                for code, name in languages.items():
                    self.language_combo.addItem(name, code)
                
                # Resélectionner la langue actuelle
                current_index = self.language_combo.findData(self.selected_language)
                if current_index >= 0:
                    self.language_combo.setCurrentIndex(current_index)
            
            # Étape 2: Nom d'utilisateur
            if hasattr(self, 'username_edit'):
                self.username_edit.setPlaceholderText(translation_manager.get_text("username.placeholder"))
            
            # Étape 3: Thème
            if hasattr(self, 'theme_group'):
                themes = [
                    ("dark", translation_manager.get_text("theme.dark")),
                    ("light", translation_manager.get_text("theme.light")),
                    ("blue", translation_manager.get_text("theme.blue")),
                    ("green", translation_manager.get_text("theme.green")),
                    ("purple", translation_manager.get_text("theme.purple"))
                ]
                
                for i, (theme_code, theme_name) in enumerate(themes):
                    button = self.theme_group.button(i)
                    if button:
                        button.setText(theme_name)
            
            # Étape 4: Projet
            if hasattr(self, 'select_project_button'):
                self.select_project_button.setText("📁 " + translation_manager.get_text("project.select"))
                if not self.project_path and hasattr(self, 'project_label'):
                    self.project_label.setText(translation_manager.get_text("project.none_selected"))
            
            # Étape 5: Pipeline
            if hasattr(self, 'pipeline_group'):
                create_new_button = self.pipeline_group.button(0)
                use_existing_button = self.pipeline_group.button(1)
                
                if create_new_button:
                    create_new_button.setText(translation_manager.get_text("pipeline.create_new"))
                if use_existing_button:
                    use_existing_button.setText(translation_manager.get_text("pipeline.use_existing"))
        except Exception as e:
            print(f"Erreur lors de la mise à jour des textes des étapes: {e}")
    
    def update_step_texts_no_language(self):
        """Met à jour les textes des étapes sans toucher aux options de langue"""
        try:
            # Étape 2: Nom d'utilisateur
            if hasattr(self, 'username_edit'):
                self.username_edit.setPlaceholderText(translation_manager.get_text("username.placeholder"))
            
            # Étape 3: Thème
            if hasattr(self, 'theme_group'):
                themes = [
                    ("dark", translation_manager.get_text("theme.dark")),
                    ("light", translation_manager.get_text("theme.light")),
                    ("blue", translation_manager.get_text("theme.blue")),
                    ("green", translation_manager.get_text("theme.green")),
                    ("purple", translation_manager.get_text("theme.purple"))
                ]
                
                for i, (theme_code, theme_name) in enumerate(themes):
                    button = self.theme_group.button(i)
                    if button:
                        button.setText(theme_name)
            
            # Étape 4: Projet
            if hasattr(self, 'select_project_button'):
                self.select_project_button.setText("📁 " + translation_manager.get_text("project.select"))
                if not self.project_path and hasattr(self, 'project_label'):
                    self.project_label.setText(translation_manager.get_text("project.none_selected"))
            
            # Étape 5: Pipeline
            if hasattr(self, 'pipeline_group'):
                create_new_button = self.pipeline_group.button(0)
                use_existing_button = self.pipeline_group.button(1)
                
                if create_new_button:
                    create_new_button.setText(translation_manager.get_text("pipeline.create_new"))
                if use_existing_button:
                    use_existing_button.setText(translation_manager.get_text("pipeline.use_existing"))
        except Exception as e:
            print(f"Erreur lors de la mise à jour des textes des étapes: {e}")
        
    def get_preferences(self):
        """Retourne les préférences sélectionnées"""
        return {
            'language': self.selected_language,
            'theme': self.selected_theme,
            'username': self.username,
            'project_path': self.project_path,
            'pipeline_choice': self.pipeline_choice
        }
