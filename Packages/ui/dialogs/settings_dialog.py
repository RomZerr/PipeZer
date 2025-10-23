import os
import json
from PySide2.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QLineEdit, QRadioButton, QButtonGroup, QFileDialog,
    QGroupBox, QFormLayout, QMessageBox, QTabWidget, QWidget
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont

from Packages.utils.translation import translation_manager


class SettingsDialog(QDialog):
    """
    Dialog de paramètres accessible depuis le bouton Settings
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_style()
        self.load_current_settings()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.setWindowTitle("Settings")
        self.setFixedSize(750, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Titre
        title_label = QLabel("Settings")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Widget d'onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("tab_widget")
        
        # Créer les onglets
        self.create_general_tab()
        self.create_project_tab()
        self.create_pipeline_tab()
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.clicked.connect(self.reset_preferences)
        
        self.save_button = QPushButton("Apply")
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        # Ajout des éléments au layout principal
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def create_general_tab(self):
        """Crée l'onglet Général"""
        general_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Groupe Langue
        language_group = QGroupBox("Language")
        language_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("language_combo")
        
        # Ajouter les langues disponibles
        languages = translation_manager.get_available_languages()
        for code, name in languages.items():
            self.language_combo.addItem(name, code)
        
        # Sélectionner la langue actuelle
        current_index = self.language_combo.findData(translation_manager.current_language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
        
        language_layout.addRow("Select language:", self.language_combo)
        language_group.setLayout(language_layout)
        
        # Connecter le signal de changement de langue
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        # Groupe Thème
        theme_group = QGroupBox("Interface Theme")
        theme_layout = QVBoxLayout()
        
        self.theme_group = QButtonGroup()
        themes = [
            ("dark", "Dark"),
            ("light", "Light"),
            ("blue", "Blue"),
            ("green", "Green"),
            ("purple", "Purple")
        ]
        
        for i, (theme_code, theme_name) in enumerate(themes):
            radio = QRadioButton(theme_name)
            radio.setObjectName("theme_radio")
            radio.setProperty("theme", theme_code)
            self.theme_group.addButton(radio, i)
            theme_layout.addWidget(radio)
        
        theme_group.setLayout(theme_layout)
        
        # Groupe Nom d'utilisateur
        username_group = QGroupBox("Username")
        username_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setObjectName("username_edit")
        self.username_edit.setPlaceholderText("Your username")
        
        username_layout.addRow("Enter your username:", self.username_edit)
        username_group.setLayout(username_layout)
        
        layout.addWidget(language_group)
        layout.addWidget(theme_group)
        layout.addWidget(username_group)
        layout.addStretch()
        
        general_tab.setLayout(layout)
        self.tab_widget.addTab(general_tab, "General")
        
    def create_project_tab(self):
        """Crée l'onglet Projet"""
        project_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
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
        
        project_tab.setLayout(layout)
        self.tab_widget.addTab(project_tab, "Project")
        
    def create_pipeline_tab(self):
        """Crée l'onglet Pipeline"""
        pipeline_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
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
        
        pipeline_tab.setLayout(layout)
        self.tab_widget.addTab(pipeline_tab, "Pipeline")
        
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
            
            QTabWidget#tab_widget {
                background-color: transparent;
            }
            
            QTabWidget#tab_widget::pane {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: #34495e;
            }
            
            QTabWidget#tab_widget::tab-bar {
                alignment: center;
            }
            
            QTabBar::tab {
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
            }
            
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #2980b9;
            }
            
            QGroupBox {
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 2px solid #3498db;
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
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLineEdit#username_edit {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QRadioButton#theme_radio, QRadioButton#pipeline_radio {
                color: #ecf0f1;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                spacing: 10px;
            }
            
            QRadioButton#theme_radio::indicator, QRadioButton#pipeline_radio::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #3498db;
                background-color: #34495e;
            }
            
            QRadioButton#theme_radio::indicator:checked, QRadioButton#pipeline_radio::indicator:checked {
                background-color: #3498db;
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
                padding: 8px;
            }
            
            QPushButton#select_project_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f4e79);
            }
            
            QLabel#project_label {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 10px;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            
            QPushButton#save_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #229954);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 100px;
                padding: 10px;
            }
            
            QPushButton#save_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #229954, stop:1 #1e8449);
            }
            
            QPushButton#reset_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f39c12, stop:1 #e67e22);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 100px;
                padding: 10px;
            }
            
            QPushButton#reset_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e67e22, stop:1 #d35400);
            }
            
            QPushButton#cancel_button {
                background-color: #95a5a6;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 100px;
                padding: 10px;
            }
            
            QPushButton#cancel_button:hover {
                background-color: #7f8c8d;
            }
        """)
        
    def on_language_changed(self):
        """Appelé quand la langue change dans les paramètres"""
        try:
            # Bloquer temporairement les signaux pour éviter la récursion
            self.language_combo.blockSignals(True)
            
            selected_language = self.language_combo.currentData()
            if selected_language:
                translation_manager.set_language(selected_language)
                
                # Mettre à jour les textes de l'interface des paramètres
                self.update_interface_texts()
                
                # Mettre à jour la fenêtre principale si elle existe
                if self.parent():
                    if hasattr(self.parent(), 'refresh_interface_texts'):
                        self.parent().refresh_interface_texts()
            
            # Débloquer les signaux
            self.language_combo.blockSignals(False)
        except Exception as e:
            print(f"Erreur lors du changement de langue: {e}")
            self.language_combo.blockSignals(False)
    
    def update_interface_texts(self):
        """Met à jour tous les textes de l'interface selon la langue"""
        try:
            # Les labels de groupes et boutons sont en anglais pour l'instant
            # Vous pouvez les traduire si nécessaire
            pass
        except Exception as e:
            print(f"Erreur lors de la mise à jour des textes: {e}")
    
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
                        
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres: {e}")
            
    def select_project(self):
        """Ouvre le dialog de sélection de projet"""
        project_path = QFileDialog.getExistingDirectory(
            self, 
            translation_manager.get_text("project.select")
        )
        
        if project_path:
            self.project_path = project_path.replace('\\', '/')
            self.project_label.setText(self.project_path)
            
    def save_settings(self):
        """Sauvegarde les paramètres"""
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
                'project_path': self.project_path,
                'pipeline_choice': pipeline_choice
            }
            
            prefs_file = os.path.join(pipezer_dir, 'preferences.json')
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
            
            # Appliquer la langue immédiatement
            translation_manager.set_language(language)
            
            # Sauvegarder aussi le nom d'utilisateur dans .pipezer/user.json
            if username:
                try:
                    # Créer le dossier .pipezer s'il n'existe pas
                    user_home_dir = os.path.expanduser("~")
                    pipezer_dir = os.path.join(user_home_dir, '.pipezer')
                    if not os.path.exists(pipezer_dir):
                        os.makedirs(pipezer_dir)
                    
                    # Sauvegarder le nom d'utilisateur dans user.json
                    user_file_path = os.path.join(pipezer_dir, 'user.json')
                    with open(user_file_path, 'w', encoding='utf-8') as f:
                        json.dump({'username': username}, f, indent=2, ensure_ascii=False)
                    
                    # Mettre à jour le bouton username de la fenêtre principale immédiatement
                    if self.parent():
                        if hasattr(self.parent(), 'user_button'):
                            self.parent().user_button.setText(f"👤 {username}")
                            self.parent().user_button.setToolTip(f"Utilisateur: {username}")
                            # Forcer le rafraîchissement de l'interface
                            self.parent().user_button.update()
                except Exception as e:
                    print(f"Erreur lors de la sauvegarde du nom d'utilisateur: {e}")
            
            # Fermer le dialog sans message de confirmation
            self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {e}")
            
    def reset_preferences(self):
        """Remet les préférences à zéro et ouvre le dialog de configuration"""
        reply = QMessageBox.question(self, 
                                   "Confirmation", 
                                   "Êtes-vous sûr de vouloir réinitialiser toutes les préférences ?\nCela ouvrira la fenêtre de configuration initiale.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Supprimer le fichier de préférences
                user_home_dir = os.path.expanduser("~")
                pipezer_dir = os.path.join(user_home_dir, '.pipezer')
                prefs_file = os.path.join(pipezer_dir, 'preferences.json')
                
                if os.path.exists(prefs_file):
                    os.remove(prefs_file)
                
                self.accept()
                
                # Ouvrir le dialog de préférences
                from Packages.ui.dialogs.preferences_dialog import PreferencesDialog
                prefs_dialog = PreferencesDialog(self.parent())
                prefs_dialog.exec_()
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la réinitialisation: {e}")
