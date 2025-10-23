"""
Widget de paramètres moderne intégré dans la fenêtre principale
"""

import os
import json
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QLineEdit, QRadioButton, QButtonGroup, QFileDialog,
    QGroupBox, QFormLayout, QMessageBox, QTabWidget, QFrame, QStackedWidget
)
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QFont

from Packages.utils.translations import translation_manager
from Packages.ui.widgets.language_selector import LanguageSelector


class ModernSettingsWidget(QWidget):
    """
    Widget de paramètres moderne avec sidebar et contenu
    """
    
    # Signal émis quand les paramètres changent
    settings_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_theme = "dark"  # Thème par défaut
        self.setup_ui()
        self.setup_theme()
        self.load_current_settings()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Créer la sidebar des paramètres
        self.create_settings_sidebar()
        
        # Créer le contenu des paramètres
        self.create_settings_content()
        
        # Ajouter au layout principal
        main_layout.addWidget(self.settings_sidebar)
        main_layout.addWidget(self.settings_content)
        
    def create_settings_sidebar(self):
        """Crée la sidebar des paramètres"""
        self.settings_sidebar = QFrame()
        self.settings_sidebar.setObjectName("settings_sidebar")
        self.settings_sidebar.setFixedWidth(200)
        
        # Layout de la sidebar
        sidebar_layout = QVBoxLayout(self.settings_sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(5)
        
        # Titre
        title_label = QLabel("Settings")
        title_label.setObjectName("settings_title")
        title_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title_label)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("separator")
        sidebar_layout.addWidget(separator)
        
        # Boutons de navigation des paramètres
        self.settings_nav_buttons = {}
        
        # General
        self.settings_nav_buttons['general'] = self.create_settings_nav_button("⚙", "General", "general")
        sidebar_layout.addWidget(self.settings_nav_buttons['general'])
        
        # Appearance
        self.settings_nav_buttons['appearance'] = self.create_settings_nav_button("🎨", "Appearance", "appearance")
        sidebar_layout.addWidget(self.settings_nav_buttons['appearance'])
        
        # Project
        self.settings_nav_buttons['project'] = self.create_settings_nav_button("📁", "Project", "project")
        sidebar_layout.addWidget(self.settings_nav_buttons['project'])
        
        # Pipeline
        self.settings_nav_buttons['pipeline'] = self.create_settings_nav_button("🔧", "Pipeline", "pipeline")
        sidebar_layout.addWidget(self.settings_nav_buttons['pipeline'])
        
        # Software
        self.settings_nav_buttons['software'] = self.create_settings_nav_button("💻", "Software", "software")
        sidebar_layout.addWidget(self.settings_nav_buttons['software'])
        
        
        # About
        self.settings_nav_buttons['about'] = self.create_settings_nav_button("ℹ", "About", "about")
        sidebar_layout.addWidget(self.settings_nav_buttons['about'])
        
        # Espace flexible
        sidebar_layout.addStretch()
        
        # Boutons d'action
        action_layout = QVBoxLayout()
        action_layout.setSpacing(10)
        
        # Bouton Reset
        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.clicked.connect(self.reset_preferences)
        action_layout.addWidget(self.reset_button)
        
        # Bouton Apply
        self.apply_button = QPushButton("✓ Apply")
        self.apply_button.setObjectName("apply_button")
        self.apply_button.clicked.connect(self.apply_settings)
        action_layout.addWidget(self.apply_button)
        
        sidebar_layout.addLayout(action_layout)
        
        # Sélectionner General par défaut
        self.settings_nav_buttons['general'].setChecked(True)
        
    def create_settings_nav_button(self, icon, text, button_id):
        """Crée un bouton de navigation des paramètres"""
        button = QPushButton()
        button.setObjectName(f"settings_nav_{button_id}")
        button.setCheckable(True)
        button.setFixedHeight(45)
        
        # Layout horizontal pour l'icône et le texte
        layout = QHBoxLayout(button)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)
        
        # Icône
        icon_label = QLabel(icon)
        icon_label.setObjectName("settings_nav_icon")
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Texte
        text_label = QLabel(text)
        text_label.setObjectName("settings_nav_text")
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Ajouter au layout
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        
        # Connecter le signal
        button.clicked.connect(lambda: self.on_settings_nav_clicked(button_id))
        
        return button
        
    def create_settings_content(self):
        """Crée la zone de contenu des paramètres"""
        self.settings_content = QFrame()
        self.settings_content.setObjectName("settings_content")
        
        # Layout du contenu
        content_layout = QVBoxLayout(self.settings_content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Stacked widget pour les différents paramètres
        self.settings_stacked = QStackedWidget()
        self.settings_stacked.setObjectName("settings_stacked")
        
        # Créer les pages de paramètres
        self.create_settings_pages()
        
        content_layout.addWidget(self.settings_stacked)
        
    def create_settings_pages(self):
        """Crée les différentes pages de paramètres"""
        # Page General
        self.general_page = self.create_general_page()
        self.settings_stacked.addWidget(self.general_page)
        
        # Page Appearance
        self.appearance_page = self.create_appearance_page()
        self.settings_stacked.addWidget(self.appearance_page)
        
        # Page Project
        self.project_page = self.create_project_page()
        self.settings_stacked.addWidget(self.project_page)
        
        # Page Pipeline
        self.pipeline_page = self.create_pipeline_page()
        self.settings_stacked.addWidget(self.pipeline_page)
        
        # Page Software
        self.software_page = self.create_software_page()
        self.settings_stacked.addWidget(self.software_page)
        
        
        # Page About
        self.about_page = self.create_about_page()
        self.settings_stacked.addWidget(self.about_page)
        
    def create_general_page(self):
        """Crée la page des paramètres généraux"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("General")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Groupe Langue
        language_group = QGroupBox("Language")
        language_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("language_combo")
        
        # Ajouter les langues disponibles
        language_names = {
            'fr': '🇫🇷 Français',
            'en': '🇺🇸 English', 
            'es': '🇪🇸 Español'
        }
        for code, name in language_names.items():
            self.language_combo.addItem(name, code)
        
        # Sélectionner la langue actuelle
        current_index = self.language_combo.findData(translation_manager.current_language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
        
        # Connecter le signal de changement de langue
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        language_layout.addRow("Select language:", self.language_combo)
        language_group.setLayout(language_layout)
        
        # Groupe Nom d'utilisateur
        username_group = QGroupBox("Username")
        username_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setObjectName("username_edit")
        self.username_edit.setPlaceholderText("Your username")
        
        username_layout.addRow("Enter your username:", self.username_edit)
        username_group.setLayout(username_layout)
        
        layout.addWidget(language_group)
        layout.addWidget(username_group)
        layout.addStretch()
        
        return page
        
    def create_appearance_page(self):
        """Crée la page des paramètres d'apparence"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("Appearance")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Groupe Thème
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        
        self.theme_group = QButtonGroup()
        themes = [
            ("dark", "Dark")
        ]
        
        for i, (theme_code, theme_name) in enumerate(themes):
            radio = QRadioButton(theme_name)
            radio.setObjectName("theme_radio")
            radio.setProperty("theme", theme_code)
            radio.setChecked(True)  # Always dark theme
            radio.setEnabled(False)  # Disable since only one option
            self.theme_group.addButton(radio, i)
            theme_layout.addWidget(radio)
        
        theme_group.setLayout(theme_layout)
        
        # Groupe Couleur d'accent
        accent_group = QGroupBox("Accent Color")
        accent_layout = QVBoxLayout()
        
        self.accent_group = QButtonGroup()
        accent_colors = [
            ("purple", "Purple", "#8B5CF6"),
            ("blue", "Blue", "#3B82F6"),
            ("green", "Green", "#22C55E"),
            ("orange", "Orange", "#F97316"),
            ("pink", "Pink", "#EC4899")
        ]
        
        # Layout en grille pour les couleurs
        color_layout = QHBoxLayout()
        for i, (color_code, color_name, color_hex) in enumerate(accent_colors):
            color_button = QPushButton()
            color_button.setObjectName(f"color_button_{color_code}")
            color_button.setFixedSize(40, 40)
            color_button.setProperty("color", color_hex)
            color_button.setProperty("color_code", color_code)
            color_button.setStyleSheet(f"background-color: {color_hex}; border-radius: 20px; border: 2px solid transparent;")
            color_button.clicked.connect(lambda checked, c=color_code: self.on_accent_color_changed(c))
            self.accent_group.addButton(color_button, i)
            color_layout.addWidget(color_button)
        
        accent_layout.addLayout(color_layout)
        accent_group.setLayout(accent_layout)
        
        layout.addWidget(theme_group)
        layout.addWidget(accent_group)
        layout.addStretch()
        
        return page
        
    def create_project_page(self):
        """Crée la page des paramètres de projet"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("Project")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Groupe Projet
        project_group = QGroupBox("Project Selection")
        project_layout = QVBoxLayout()
        
        self.project_label = QLabel("No project selected")
        self.project_label.setObjectName("project_label")
        self.project_label.setWordWrap(True)
        
        self.select_project_button = QPushButton("📁 Select project folder")
        self.select_project_button.setObjectName("select_project_button")
        self.select_project_button.clicked.connect(self.select_project)
        
        project_layout.addWidget(self.select_project_button)
        project_layout.addWidget(self.project_label)
        project_group.setLayout(project_layout)
        
        layout.addWidget(project_group)
        layout.addStretch()
        
        return page
        
    def create_pipeline_page(self):
        """Crée la page des paramètres de pipeline"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("Pipeline")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Groupe Pipeline
        pipeline_group = QGroupBox("Pipeline Configuration")
        pipeline_layout = QVBoxLayout()
        
        self.pipeline_group = QButtonGroup()
        
        create_new_radio = QRadioButton("Create new folders")
        create_new_radio.setObjectName("pipeline_radio")
        create_new_radio.setProperty("choice", "create_new")
        self.pipeline_group.addButton(create_new_radio, 0)
        
        use_existing_radio = QRadioButton("Use existing folders")
        use_existing_radio.setObjectName("pipeline_radio")
        use_existing_radio.setProperty("choice", "use_existing")
        self.pipeline_group.addButton(use_existing_radio, 1)
        
        pipeline_layout.addWidget(create_new_radio)
        pipeline_layout.addWidget(use_existing_radio)
        pipeline_group.setLayout(pipeline_layout)
        
        layout.addWidget(pipeline_group)
        layout.addStretch()
        
        return page
        
    def create_software_page(self):
        """Crée la page de configuration des logiciels"""
        from PySide2.QtWidgets import QScrollArea
        
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setSpacing(20)
        
        # Titre
        title = QLabel("Software")
        title.setObjectName("page_title")
        main_layout.addWidget(title)
        
        # Créer une zone scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("software_scroll")
        
        # Widget contenu du scroll
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(15)
        
        # Dictionnaire des logiciels
        self.software_paths = {}
        
        software_list = [
            ("maya", "Maya", "Autodesk Maya", "C:/Program Files/Autodesk/Maya2024/bin/maya.exe"),
            ("houdini", "Houdini", "SideFX Houdini", ""),
            ("nuke", "Nuke", "The Foundry Nuke", ""),
            ("blender", "Blender", "Blender 3D", ""),
            ("zbrush", "ZBrush", "Pixologic ZBrush", ""),
            ("substance_painter", "Substance Painter", "Adobe Substance 3D Painter", ""),
            ("substance_designer", "Substance Designer", "Adobe Substance 3D Designer", ""),
            ("photoshop", "Photoshop", "Adobe Photoshop", ""),
            ("unreal", "Unreal Engine", "Epic Games Unreal Engine", ""),
            ("krita", "Krita", "Krita Digital Painting", ""),
            ("resolve", "DaVinci Resolve", "Blackmagic DaVinci Resolve", "")
        ]
        
        for software_info in software_list:
            software_id, software_name, software_full_name, default_path = software_info
            group = self.create_software_group(software_id, software_name, software_full_name, default_path)
            layout.addWidget(group)
        
        layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        return page
    
    def create_software_group(self, software_id, software_name, software_full_name, default_path=""):
        """Crée un groupe pour un logiciel"""
        group = QGroupBox(software_name)
        group_layout = QVBoxLayout()
        group_layout.setSpacing(10)
        
        # Description
        desc = QLabel(software_full_name)
        desc.setObjectName("software_description")
        desc.setWordWrap(True)
        group_layout.addWidget(desc)
        
        # Layout horizontal pour le chemin et le bouton
        path_layout = QHBoxLayout()
        
        # Champ de texte pour le chemin
        path_edit = QLineEdit()
        path_edit.setObjectName(f"software_path_{software_id}")
        path_edit.setPlaceholderText(f"Path to {software_name} executable...")
        # Définir le chemin par défaut s'il existe
        if default_path:
            path_edit.setText(default_path)
        self.software_paths[software_id] = path_edit
        
        # Bouton parcourir
        browse_button = QPushButton("📁 Browse")
        browse_button.setObjectName("browse_button")
        browse_button.setFixedWidth(100)
        browse_button.clicked.connect(lambda: self.browse_software(software_id, software_name))
        
        path_layout.addWidget(path_edit)
        path_layout.addWidget(browse_button)
        
        group_layout.addLayout(path_layout)
        group.setLayout(group_layout)
        
        return group
    
    def browse_software(self, software_id, software_name):
        """Ouvre le dialog de sélection de fichier pour un logiciel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {software_name} executable",
            "",
            "Executable Files (*.exe);;All Files (*.*)"
        )
        
        if file_path:
            self.software_paths[software_id].setText(file_path.replace('\\', '/'))
    
    def create_about_page(self):
        """Crée la page À propos"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Titre
        title = QLabel("About")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Informations sur l'application
        info_group = QGroupBox("Application Information")
        info_layout = QVBoxLayout()
        
        app_name = QLabel("PipeZer")
        app_name.setObjectName("app_name")
        info_layout.addWidget(app_name)
        
        version = QLabel("Version 1.0.0")
        version.setObjectName("version")
        info_layout.addWidget(version)
        
        description = QLabel("A modern pipeline management tool for creative professionals.")
        description.setObjectName("description")
        description.setWordWrap(True)
        info_layout.addWidget(description)
        
        info_group.setLayout(info_layout)
        
        layout.addWidget(info_group)
        layout.addStretch()
        
        return page
        
    def on_settings_nav_clicked(self, button_id):
        """Gère le clic sur un bouton de navigation des paramètres"""
        # Décocher tous les autres boutons
        for btn_id, button in self.settings_nav_buttons.items():
            if btn_id != button_id:
                button.setChecked(False)
                
        # Changer la page affichée
        page_map = {
            'general': 0,
            'appearance': 1,
            'project': 2,
            'pipeline': 3,
            'software': 4,
            'about': 5
        }
        
        if button_id in page_map:
            self.settings_stacked.setCurrentIndex(page_map[button_id])
            
    def on_language_changed(self):
        """Appelé quand la langue change"""
        try:
            # Bloquer temporairement les signaux pour éviter la récursion
            self.language_combo.blockSignals(True)
            
            selected_language = self.language_combo.currentData()
            if selected_language:
                translation_manager.set_language(selected_language)
                
                # Notifier le parent du changement
                self.settings_changed.emit({'language': selected_language})
                
                # Émettre le signal de changement de langue pour la fenêtre principale
                if hasattr(self.parent(), 'set_language'):
                    self.parent().set_language(selected_language)
            
            # Débloquer les signaux
            self.language_combo.blockSignals(False)
        except Exception as e:
            print(f"Erreur lors du changement de langue: {e}")
            self.language_combo.blockSignals(False)
            
    def on_accent_color_changed(self, color_code):
        """Appelé quand la couleur d'accent change"""
        # Notifier le parent du changement
        self.settings_changed.emit({'accent_color': color_code})
        
    def select_project(self):
        """Ouvre le dialog de sélection de projet"""
        project_path = QFileDialog.getExistingDirectory(
            self, 
            "Select project folder"
        )
        
        if project_path:
            self.project_path = project_path.replace('\\', '/')
            self.project_label.setText(self.project_path)
            
    def load_current_settings(self):
        """Charge les paramètres actuels"""
        try:
            user_home_dir = os.path.expanduser("~")
            pipezer_dir = os.path.join(user_home_dir, '.pipezer')
            prefs_file = os.path.join(pipezer_dir, 'preferences.json')
            
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    
                # Charger les paramètres
                self.username_edit.setText(prefs.get('username', ''))
                self.project_path = prefs.get('project_path', '')
                if self.project_path:
                    self.project_label.setText(self.project_path)
                
                # Sélectionner le thème
                theme = prefs.get('theme', 'dark')
                for i in range(self.theme_group.buttons().__len__()):
                    button = self.theme_group.button(i)
                    if button and button.property("theme") == theme:
                        button.setChecked(True)
                        break
                
                # Sélectionner le pipeline
                pipeline = prefs.get('pipeline_choice', 'create_new')
                for i in range(self.pipeline_group.buttons().__len__()):
                    button = self.pipeline_group.button(i)
                    if button and button.property("choice") == pipeline:
                        button.setChecked(True)
                        break
            
            # Charger les chemins des logiciels depuis apps.json
            apps_file = os.path.join(pipezer_dir, 'apps.json')
            if os.path.exists(apps_file):
                with open(apps_file, 'r', encoding='utf-8') as f:
                    apps = json.load(f)
                    
                # Remplir les champs avec les chemins actuels (écrase les valeurs par défaut)
                for software_id, path_edit in self.software_paths.items():
                    if software_id in apps and 'path' in apps[software_id]:
                        path_edit.setText(apps[software_id]['path'])
            else:
                # Si apps.json n'existe pas, créer avec le chemin par défaut de Maya
                default_apps = {
                    "maya": {
                        "path": "C:/Program Files/Autodesk/Maya2024/bin/maya.exe"
                    }
                }
                with open(apps_file, 'w', encoding='utf-8') as f:
                    json.dump(default_apps, f, indent=2, ensure_ascii=False)
                        
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres: {e}")
            
    def apply_settings(self):
        """Applique les paramètres"""
        try:
            user_home_dir = os.path.expanduser("~")
            pipezer_dir = os.path.join(user_home_dir, '.pipezer')
            
            if not os.path.exists(pipezer_dir):
                os.makedirs(pipezer_dir)
                
            # Récupérer les valeurs
            language = self.language_combo.currentData()
            username = self.username_edit.text().strip()
            
            # Récupérer le thème sélectionné
            theme = "dark"
            checked_theme_button = self.theme_group.checkedButton()
            if checked_theme_button:
                theme = checked_theme_button.property("theme")
            
            # Récupérer le choix de pipeline
            pipeline_choice = "create_new"
            checked_pipeline_button = self.pipeline_group.checkedButton()
            if checked_pipeline_button:
                pipeline_choice = checked_pipeline_button.property("choice")
            
            prefs = {
                'language': language,
                'theme': theme,
                'username': username,
                'project_path': getattr(self, 'project_path', ''),
                'pipeline_choice': pipeline_choice
            }
            
            prefs_file = os.path.join(pipezer_dir, 'preferences.json')
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
            
            # Sauvegarder le nom d'utilisateur dans user.json
            if username:
                user_file_path = os.path.join(pipezer_dir, 'user.json')
                with open(user_file_path, 'w', encoding='utf-8') as f:
                    json.dump({'username': username}, f, indent=2, ensure_ascii=False)
            
            # Sauvegarder les chemins des logiciels dans apps.json
            apps_file = os.path.join(pipezer_dir, 'apps.json')
            apps_data = {}
            
            # Charger les données existantes
            if os.path.exists(apps_file):
                with open(apps_file, 'r', encoding='utf-8') as f:
                    apps_data = json.load(f)
            
            # Mettre à jour avec les nouveaux chemins
            for software_id, path_edit in self.software_paths.items():
                path = path_edit.text().strip()
                if path:
                    if software_id not in apps_data:
                        apps_data[software_id] = {}
                    apps_data[software_id]['path'] = path
            
            # Sauvegarder
            with open(apps_file, 'w', encoding='utf-8') as f:
                json.dump(apps_data, f, indent=2, ensure_ascii=False)
            
            # Notifier le parent des changements
            self.settings_changed.emit(prefs)
            
            QMessageBox.information(self, "Success", "Settings applied successfully!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving settings: {e}")
            
    def reset_preferences(self):
        """Remet les préférences à zéro"""
        reply = QMessageBox.question(self, 
                                   "Confirmation", 
                                   "Are you sure you want to reset all preferences?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Supprimer le fichier de préférences
                user_home_dir = os.path.expanduser("~")
                pipezer_dir = os.path.join(user_home_dir, '.pipezer')
                prefs_file = os.path.join(pipezer_dir, 'preferences.json')
                
                if os.path.exists(prefs_file):
                    os.remove(prefs_file)
                
                # Recharger les paramètres par défaut
                self.load_current_settings()
                
                QMessageBox.information(self, "Success", "Preferences reset successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error resetting preferences: {e}")
                
    def setup_theme(self):
        """Configuration du thème moderne"""
        if self.current_theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def apply_dark_theme(self):
        """Applique le thème sombre aux paramètres"""
        self.setStyleSheet("""
            QFrame#settings_sidebar {
                background-color: #161B22;
                border-right: 1px solid #30363D;
            }
            
            QFrame#settings_content {
                background-color: #0D1117;
            }
            
            QLabel#settings_title {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            
            QPushButton[objectName^="settings_nav_"] {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                text-align: left;
                color: #FFFFFF;
                font-size: 14px;
                padding: 10px;
            }
            
            QPushButton[objectName^="settings_nav_"]:hover {
                background-color: #30363D;
            }
            
            QPushButton[objectName^="settings_nav_"]:checked {
                background-color: #6366F1;
            }
            
            QLabel#settings_nav_icon {
                color: #FFFFFF;
                font-size: 16px;
            }
            
            QLabel#settings_nav_text {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 500;
            }
            
            QLabel#page_title {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            
            QGroupBox {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #3C3C4F;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QComboBox#language_combo {
                background-color: #3C3C4F;
                border: 2px solid #4A3B66;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                color: #FFFFFF;
            }
            
            QLineEdit#username_edit {
                background-color: #3C3C4F;
                border: 2px solid #4A3B66;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                color: #FFFFFF;
            }
            
            QRadioButton#theme_radio, QRadioButton#pipeline_radio {
                color: #FFFFFF;
                font-size: 14px;
                spacing: 10px;
            }
            
            QRadioButton#theme_radio::indicator, QRadioButton#pipeline_radio::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #4A3B66;
                background-color: #3C3C4F;
            }
            
            QRadioButton#theme_radio::indicator:checked, QRadioButton#pipeline_radio::indicator:checked {
                background-color: #4A3B66;
            }
            
            QPushButton#select_project_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A3B66, stop:1 #3A2B56);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
            
            QPushButton#select_project_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3A2B56, stop:1 #2A1B46);
            }
            
            QLabel#project_label {
                background-color: #3C3C4F;
                border: 2px solid #4A3B66;
                border-radius: 8px;
                padding: 10px;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            
            QPushButton#apply_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #22C55E, stop:1 #16A34A);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            
            QPushButton#apply_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #16A34A, stop:1 #15803D);
            }
            
            QPushButton#reset_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F97316, stop:1 #EA580C);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
            
            QPushButton#reset_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #EA580C, stop:1 #DC2626);
            }
            
            QLabel#app_name {
                color: #FFFFFF;
                font-size: 20px;
                font-weight: bold;
            }
            
            QLabel#version {
                color: #A0A0A0;
                font-size: 14px;
            }
            
            QLabel#description {
                color: #FFFFFF;
                font-size: 14px;
                line-height: 1.4;
            }
            
            QFrame#separator {
                color: #3C3C4F;
                background-color: #3C3C4F;
            }
            
            QScrollArea#software_scroll {
                background-color: transparent;
                border: none;
            }
            
            QLabel#software_description {
                color: #A0A0A0;
                font-size: 12px;
                font-weight: normal;
            }
            
            QPushButton#browse_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A3B66, stop:1 #3A2B56);
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 6px;
            }
            
            QPushButton#browse_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6366F1, stop:1 #4F46E5);
            }
        """)
    
    def apply_light_theme(self):
        """Light theme removed - only dark theme available"""
        # Light theme has been removed, always use dark theme
        self.apply_dark_theme()



    def set_theme(self, theme):
        """Change le thème des paramètres"""
        self.current_theme = theme
        self.setup_theme()
    
