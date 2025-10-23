"""
Modern main window with expandable sidebar and themes
"""

import os
import json
from PySide2.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFrame, QStackedWidget, QSizePolicy
)
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QFont, QIcon, QPalette, QColor

from Packages.utils.translations import translation_manager
from Packages.ui.widgets.draggable_nav_button import DraggableNavButton
from Packages.ui.widgets.draggable_sidebar_container import DraggableSidebarContainer


class ModernMainWindow(QMainWindow):
    """Modern main window with expandable sidebar and themes"""
    
    browser_navigation_requested = Signal(str)
    language_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.sidebar_width = 210
        self.current_theme = "dark"
        
        self.setup_ui()
        self.setup_theme()
        self.load_custom_shortcuts()
        
    def setup_ui(self):
        self.setWindowTitle("PipeZer")
        self.setMinimumSize(1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.create_sidebar()
        self.create_main_content()
        self.create_header()
        main_layout.addWidget(self.sidebar_frame)
        main_layout.addWidget(self.content_frame)
        
        # Layout vertical pour le header et le contenu
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Créer les icônes en bas à gauche
        self.create_bottom_icons()
        
        content_layout.addWidget(self.header_frame)
        content_layout.addWidget(self.stacked_widget)
        
    def create_sidebar(self):
        """Crée la sidebar avec les boutons de navigation"""
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebar")
        self.sidebar_frame.setFixedWidth(self.sidebar_width)
        
        # Layout de la sidebar
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(10, 20, 10, 10)
        sidebar_layout.setSpacing(10)
        
        # Username en haut de la sidebar
        self.username_sidebar_button = QPushButton(f"👤 {translation_manager.get_text('user')}")
        self.username_sidebar_button.setObjectName("username_sidebar_button")
        self.username_sidebar_button.setFixedHeight(60)
        self.username_sidebar_button.setEnabled(False)  # Non cliquable
        sidebar_layout.addWidget(self.username_sidebar_button)
        
        # Espace
        sidebar_layout.addSpacing(20)
        
        # Boutons de navigation
        self.nav_buttons = {}
        
        # Container pour TOUS les raccourcis avec drag & drop
        self.shortcuts_container = DraggableSidebarContainer()
        self.shortcuts_container.order_changed.connect(self.on_shortcuts_reordered)
        sidebar_layout.addWidget(self.shortcuts_container)
        
        # Créer les boutons de raccourcis fixes (Template, Asset, Shot)
        template_btn = DraggableNavButton("", translation_manager.get_text('template'), "template")
        template_btn.clicked.connect(lambda: self.on_nav_button_clicked("template"))
        template_btn.renamed.connect(lambda new_name: self.on_shortcut_renamed("template", new_name))
        self.shortcuts_container.add_button_widget(template_btn)
        self.nav_buttons['template'] = template_btn
        
        asset_btn = DraggableNavButton("", translation_manager.get_text('asset'), "asset")
        asset_btn.clicked.connect(lambda: self.on_nav_button_clicked("asset"))
        asset_btn.renamed.connect(lambda new_name: self.on_shortcut_renamed("asset", new_name))
        self.shortcuts_container.add_button_widget(asset_btn)
        self.nav_buttons['asset'] = asset_btn
        
        shot_btn = DraggableNavButton("", translation_manager.get_text('shot'), "shot")
        shot_btn.clicked.connect(lambda: self.on_nav_button_clicked("shot"))
        shot_btn.renamed.connect(lambda new_name: self.on_shortcut_renamed("shot", new_name))
        self.shortcuts_container.add_button_widget(shot_btn)
        self.nav_buttons['shot'] = shot_btn
        
        # Bouton pour ajouter un raccourci personnalisé
        self.add_shortcut_button = QPushButton("+")
        self.add_shortcut_button.setObjectName("add_shortcut_button")
        self.add_shortcut_button.setMinimumHeight(60)
        self.add_shortcut_button.setMaximumHeight(60)
        self.add_shortcut_button.setToolTip("Ajouter un raccourci personnalisé")
        self.add_shortcut_button.clicked.connect(self.create_custom_shortcut)
        sidebar_layout.addWidget(self.add_shortcut_button)
        
        # Espace flexible
        sidebar_layout.addStretch()
        
        # Sélectionner Template par défaut
        self.nav_buttons['template'].button.setChecked(True)
        if self.nav_buttons['template'].icon_label:
            self.nav_buttons['template'].icon_label.setStyleSheet("color: #3B82F6;")
        if self.nav_buttons['template'].text_label:
            self.nav_buttons['template'].text_label.setStyleSheet("color: #3B82F6;")
        
        # Afficher le point de notification sur le bouton notifications (maintenant dans le header)
        # self.nav_buttons['notifications'].notification_dot.show()  # Supprimé car notifications n'est plus dans la sidebar
        
    def create_nav_button(self, icon, text, button_id):
        """Crée un bouton de navigation avec design moderne"""
        # Container principal
        container = QFrame()
        container.setObjectName(f"nav_container_{button_id}")
        # Ne pas fixer la hauteur du container pour éviter le découpage
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # Layout principal
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Bouton principal
        button = QPushButton()
        button.setObjectName(f"nav_button_{button_id}")
        button.setCheckable(True)
        # Augmenter légèrement la hauteur minimale pour éviter le découpage
        button.setMinimumHeight(36)
        
        # Layout du bouton
        button_layout = QHBoxLayout(button)
        button_layout.setContentsMargins(15, 0, 15, 0)
        button_layout.setSpacing(0)
        
        # Texte centré (sans icône)
        text_label = QLabel(text)
        text_label.setObjectName("nav_text")
        text_label.setAlignment(Qt.AlignCenter)
        
        # Ajouter au layout du bouton
        button_layout.addWidget(text_label)
        
        # Variables pour compatibilité (même si icône vide)
        icon_label = QLabel(icon) if icon else QLabel("")
        icon_label.setObjectName("nav_icon")
        icon_label.hide()  # Cacher l'icône par défaut
        
        notification_dot = QLabel("●")
        notification_dot.setObjectName(f"notification_dot_{button_id}")
        notification_dot.setFixedSize(8, 8)
        notification_dot.setAlignment(Qt.AlignCenter)
        notification_dot.setStyleSheet("color: #EF4444; font-size: 8px;")
        notification_dot.hide()
        
        # Ajouter au layout principal
        main_layout.addWidget(button)
        
        # Connecter le signal
        button.clicked.connect(lambda: self.on_nav_button_clicked(button_id))
        
        # Stocker les références pour accès ultérieur
        container.button = button
        container.icon_label = icon_label
        container.text_label = text_label
        container.notification_dot = notification_dot
        
        return container
        
    def create_main_content(self):
        """Crée la zone de contenu principal"""
        self.content_frame = QFrame()
        self.content_frame.setObjectName("content_frame")
        
        # Stacked widget pour les différents contenus
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stacked_widget")
        
        # Créer les pages de contenu
        self.create_content_pages()
        
    def create_content_pages(self):
        """Crée les différentes pages de contenu"""
        # Page Browser (contenu actuel des onglets)
        self.browser_page = QWidget()
        self.browser_page.setObjectName("browser_page")
        self.stacked_widget.addWidget(self.browser_page)
        
        # Page Recent
        self.recent_page = QWidget()
        self.recent_page.setObjectName("recent_page")
        self.stacked_widget.addWidget(self.recent_page)
        
        # Page Search
        self.search_page = QWidget()
        self.search_page.setObjectName("search_page")
        self.stacked_widget.addWidget(self.search_page)
        
        # Page Create Asset
        self.asset_page = QWidget()
        self.asset_page.setObjectName("asset_page")
        self.stacked_widget.addWidget(self.asset_page)
        
        # Page Create Shot
        self.shot_page = QWidget()
        self.shot_page.setObjectName("shot_page")
        self.stacked_widget.addWidget(self.shot_page)
        
        # Page Settings
        self.settings_page = QWidget()
        self.settings_page.setObjectName("settings_page")
        self.stacked_widget.addWidget(self.settings_page)
        
        # Page Notifications
        self.notifications_page = QWidget()
        self.notifications_page.setObjectName("notifications_page")
        self.stacked_widget.addWidget(self.notifications_page)
        
        # Page Crash
        self.crash_page = QWidget()
        self.crash_page.setObjectName("crash_page")
        self.stacked_widget.addWidget(self.crash_page)
        
    def create_header(self):
        """Crée le header avec username, notifications et refresh"""
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header_frame")
        self.header_frame.setFixedHeight(60)
        
        # Layout du header
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(15)
        
        # Boutons de navigation dans le header
        self.header_buttons = {}
        
        # Recent à gauche
        self.header_buttons['recent'] = self.create_header_button("", translation_manager.get_text('recent'), "recent")
        header_layout.addWidget(self.header_buttons['recent'])
        
        # Barre de recherche style Windows
        from PySide2.QtWidgets import QLineEdit
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("search_bar")
        self.search_bar.setPlaceholderText(f"🔍 {translation_manager.get_text('search')}")
        self.search_bar.setFixedWidth(300)
        self.search_bar.setFixedHeight(40)
        self.search_bar.textChanged.connect(self.on_search_text_changed)
        header_layout.addWidget(self.search_bar)
        
        # Espace flexible au milieu
        header_layout.addStretch()
        
        # Create Asset à droite
        self.header_buttons['create_asset'] = self.create_header_button("", translation_manager.get_text('create_asset'), "create_asset")
        self.header_buttons['create_asset'].clicked.connect(self.open_create_asset_dialog)
        header_layout.addWidget(self.header_buttons['create_asset'])
        
        # Create Shot à droite (même niveau horizontal que Create Asset)
        self.header_buttons['create_shot'] = self.create_header_button("", translation_manager.get_text('create_shot'), "create_shot")
        self.header_buttons['create_shot'].clicked.connect(self.open_create_shot_dialog)
        header_layout.addWidget(self.header_buttons['create_shot'])
        
    def create_bottom_icons(self):
        """Crée les icônes en bas à gauche de la sidebar"""
        # Créer un widget pour les icônes en bas
        self.bottom_icons_frame = QFrame()
        self.bottom_icons_frame.setObjectName("bottom_icons_frame")
        self.bottom_icons_frame.setFixedHeight(60)
        
        # Layout pour les icônes
        icons_layout = QHBoxLayout(self.bottom_icons_frame)
        icons_layout.setContentsMargins(10, 10, 10, 10)
        icons_layout.setSpacing(10)
        
        # Notifications
        self.notification_button = QPushButton("🔔")
        self.notification_button.setObjectName("notification_button")
        self.notification_button.setFixedSize(40, 40)
        self.notification_button.clicked.connect(lambda: self.on_nav_button_clicked('notifications'))
        icons_layout.addWidget(self.notification_button)
        
        # Refresh
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setObjectName("refresh_button")
        self.refresh_button.setFixedSize(40, 40)
        icons_layout.addWidget(self.refresh_button)
        
        # Settings
        self.settings_header_button = QPushButton("⚙")
        self.settings_header_button.setObjectName("settings_header_button")
        self.settings_header_button.setFixedSize(40, 40)
        self.settings_header_button.clicked.connect(lambda: self.on_nav_button_clicked('settings'))
        icons_layout.addWidget(self.settings_header_button)
        
        # Ajouter le bouton Crash et les icônes en bas de la sidebar
        sidebar_layout = self.sidebar_frame.layout()
        sidebar_layout.addStretch()  # Pousser les icônes vers le bas
        
        # Bouton Crash au-dessus des icônes
        sidebar_layout.addSpacing(15)
        self.nav_buttons['crash'] = self.create_nav_button("", translation_manager.get_text('crash'), "crash")
        sidebar_layout.addWidget(self.nav_buttons['crash'])
        sidebar_layout.addSpacing(15)
        
        sidebar_layout.addWidget(self.bottom_icons_frame)
        
    def create_header_button(self, icon, text, button_id):
        """Crée un bouton pour le header"""
        button = QPushButton(f"{icon} {text}")
        button.setObjectName(f"header_button_{button_id}")
        button.setCheckable(True)
        button.setFixedHeight(40)
        button.clicked.connect(lambda: self.on_nav_button_clicked(button_id))
        return button
        
                
    def on_nav_button_clicked(self, button_id):
        """Gère le clic sur un bouton de navigation"""
        # Décocher tous les autres boutons de la sidebar
        for btn_id, container in self.nav_buttons.items():
            if btn_id != button_id:
                container.button.setChecked(False)
                # Remettre les couleurs par défaut
                if hasattr(container, 'icon_label') and container.icon_label:
                    container.icon_label.setStyleSheet("color: #FFFFFF;")
                if hasattr(container, 'text_label') and container.text_label:
                    container.text_label.setStyleSheet("color: #FFFFFF;")
        
        # Décocher tous les autres boutons du header
        for btn_id, button in self.header_buttons.items():
            if btn_id != button_id:
                button.setChecked(False)
                
        # Activer le bouton sélectionné (sidebar)
        if button_id in self.nav_buttons:
            selected_container = self.nav_buttons[button_id]
            selected_container.button.setChecked(True)
            # Changer les couleurs pour l'élément actif
            if hasattr(selected_container, 'icon_label') and selected_container.icon_label:
                selected_container.icon_label.setStyleSheet("color: #FFFFFF;")
            if hasattr(selected_container, 'text_label') and selected_container.text_label:
                selected_container.text_label.setStyleSheet("color: #FFFFFF;")
        
        # Activer le bouton sélectionné (header)
        if button_id in self.header_buttons:
            self.header_buttons[button_id].setChecked(True)
        
        # Gérer les boutons de raccourcis (naviguent vers des dossiers spécifiques)
        if button_id in ['template', 'asset', 'shot'] or button_id.startswith('custom_'):
            # D'abord, s'assurer qu'on est sur la page browser
            self.stacked_widget.setCurrentIndex(0)
            # Puis naviguer vers le dossier spécifique
            if button_id.startswith('custom_'):
                # Raccourci personnalisé
                container = self.nav_buttons.get(button_id)
                if container:
                    custom_path = container.button.property('shortcut_path')
                    if custom_path:
                        self.browser_navigation_requested.emit(custom_path)
            else:
                self.navigate_to_shortcut(button_id)
        else:
            # Changer la page affichée pour les autres boutons
            # SAUF pour create_asset et create_shot qui ouvrent des dialogues séparés
            if button_id in ['create_asset', 'create_shot']:
                # Ne rien faire, les dialogues sont ouverts par les connexions directes
                return
            
            page_map = {
                'browser': 0,
                'recent': 1,
                'search': 2,
                'settings': 5,
                'notifications': 6,
                'crash': 7
            }
            
            if button_id in page_map:
                self.stacked_widget.setCurrentIndex(page_map[button_id])
    
    def navigate_to_shortcut(self, button_id):
        """Navigue vers un dossier spécifique selon le bouton de raccourci"""
        import os
        from Packages.utils.funcs import get_current_value
        from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
        
        # Obtenir le chemin du projet courant
        project_path = get_current_value(json_file=CURRENT_PROJECT_JSON_PATH, key='current_project')
        if not project_path:
            project_path = os.getcwd()
        
        # Définir les chemins pour chaque bouton de raccourci
        import tempfile
        shortcut_paths = {
            'template': os.path.join(project_path, '02_ressource', 'template_scenes'),
            'asset': os.path.join(project_path, '04_asset'),
            'shot': os.path.join(project_path, '05_shot'),
            'crash': tempfile.gettempdir()
        }
        
        target_path = shortcut_paths.get(button_id)
        if target_path:
            # Émettre un signal pour que le browser navigue vers ce dossier
            self.browser_navigation_requested.emit(target_path)
        else:
            print(f"Chemin non défini pour: {button_id}")
            
    def setup_theme(self):
        """Configure le thème de l'interface"""
        if self.current_theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
        
        # Synchroniser le thème avec les paramètres si ils existent
        if hasattr(self, 'settings_widget'):
            self.settings_widget.set_theme(self.current_theme)
    
    def set_theme(self, theme):
        """Change le thème de l'interface"""
        self.current_theme = theme
        self.setup_theme()
            
    def apply_dark_theme(self):
        """Applique le thème sombre moderne et sobre"""
        self.setStyleSheet("""
            /* === PALETTE MODERNE SOMBRE === */
            QMainWindow {
                background-color: #0D1117;
                color: #E6EDF3;
            }
            
            QFrame#sidebar {
                background-color: #161B22;
                border-right: 1px solid #30363D;
            }
            
            QFrame#content_frame {
                background-color: #0D1117;
            }
            
            QWidget#files_widget {
                background-color: #161B22;
                border: 1px solid #30363D;
                border-radius: 12px;
            }
            
            QFrame#bottom_icons_frame {
                background-color: transparent;
                border: none;
            }
            
            QPushButton#notification_button,
            QPushButton#refresh_button,
            QPushButton#settings_header_button {
                background-color: #21262D;
                border: 1px solid #30363D;
                border-radius: 8px;
                color: #E6EDF3;
                font-size: 16px;
                padding: 8px 12px;
            }
            
            QPushButton#notification_button:hover,
            QPushButton#refresh_button:hover,
            QPushButton#settings_header_button:hover {
                background-color: #30363D;
                border-color: #6366F1;
            }
            
            QPushButton#notification_button:pressed,
            QPushButton#refresh_button:pressed,
            QPushButton#settings_header_button:pressed {
                background-color: #6366F1;
                border-color: #6366F1;
                color: white;
            }
            
            /* Styles pour les boutons du header */
            QPushButton[objectName^="header_button_"] {
                background-color: transparent !important;
                border: 1px solid #30363D;
                border-radius: 8px;
                color: #E6EDF3;
                font-size: 14px;
                padding: 10px 18px;
                font-weight: 500;
            }
            
            QPushButton[objectName^="header_button_"]:hover {
                background-color: transparent !important;
                border-color: #6366F1;
                color: #6366F1;
            }
            
            QPushButton[objectName^="header_button_"]:checked {
                background-color: rgba(99, 102, 241, 0.15) !important;
                border-color: #6366F1;
                color: #6366F1;
            }
            
            QPushButton[objectName^="header_button_"]:pressed {
                background-color: rgba(99, 102, 241, 0.1) !important;
                border-color: #6366F1;
            }
            
            /* Styles pour la barre de recherche */
            QLineEdit#search_bar {
                background-color: #21262D;
                border: 1px solid #30363D;
                border-radius: 8px;
                color: #E6EDF3;
                font-size: 14px;
                padding: 8px 12px;
            }
            
            QLineEdit#search_bar:focus {
                border-color: #6366F1;
                background-color: #161B22;
            }
            
            /* Styles pour le tableau des fichiers */
            QTableWidget {
                background-color: #161B22;
                border: 1px solid #30363D;
                border-radius: 10px;
                color: #E6EDF3;
                gridline-color: transparent;
                selection-background-color: rgba(99, 102, 241, 0.15);
                show-decoration-selected: 1;
            }
            
            QTableWidget::item {
                background-color: transparent;
                padding: 10px 12px;
                border-bottom: 1px solid #21262D;
                border-right: none;
                border-left: none;
            }
            
            QTableWidget::item:selected {
                background-color: rgba(99, 102, 241, 0.15);
                color: #6366F1;
                border: none;
                border-radius: 0px;
            }
            
            QTableWidget::item:hover {
                background-color: #3C3C4F;
                border-bottom: 1px solid #6366F1;
            }
            
            QTableWidget::item:first {
                border-top: 1px solid #21262D;
            }
            
            QTableWidget::item:last {
                border-bottom: 1px solid #21262D;
            }
            
            /* Style pour la ligne sélectionnée entière */
            QTableWidget::item:selected:first {
                border-top-left-radius: 4px;
                border-bottom-left-radius: 4px;
                border-left: 2px solid #6366F1;
            }
            QTableWidget::item:selected:last {
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                border-right: 2px solid #6366F1;
            }
            QTableWidget::item:selected {
                border-top: 2px solid #6366F1;
                border-bottom: 2px solid #6366F1;
            }
            
            QHeaderView::section {
                background-color: #3C3C4F;
                color: #FFFFFF;
                padding: 4px 8px;
                border: 1px solid #4A3B66;
                font-weight: bold;
            }
            
            QFrame#header_frame {
                background-color: #2D2D44;
                border-bottom: 1px solid #3C3C4F;
            }
            
            
            QPushButton[objectName^="nav_button_"] {
                background-color: transparent !important;
                border: 2px dashed #30363D !important;
                border-radius: 8px;
                text-align: center;
                color: #E6EDF3;
                font-size: 12px;
                font-weight: 500;
                padding: 8px 10px;
                margin: 6px 0px;
                min-height: 32px;
                max-height: 32px;
            }
            
            QPushButton[objectName^="nav_button_"]:hover {
                border-color: #6366F1;
                background-color: transparent !important;
                color: #6366F1;
            }
            
            QPushButton[objectName^="nav_button_"]:checked {
                border-color: #6366F1;
                border-style: solid !important;
                background-color: rgba(99, 102, 241, 0.1) !important;
                color: #6366F1;
            }
            
            QPushButton[objectName^="nav_button_"]:pressed {
                border-color: #6366F1;
                background-color: rgba(99, 102, 241, 0.05) !important;
            }
            
            QPushButton[objectName^="nav_button_"]:focus {
                outline: none;
            }
            
            QPushButton#username_sidebar_button {
                background: #21262D !important;
                border: 1px solid #30363D !important;
                border-radius: 10px;
                text-align: center;
                color: #E6EDF3;
                font-size: 15px;
                font-weight: 600;
                padding: 16px 20px;
                margin: 4px 0px;
            }
            
            QPushButton#add_shortcut_button {
                background: transparent !important;
                border: none !important;
                border-radius: 8px;
                text-align: center;
                color: #6366F1;
                font-size: 32px;
                font-weight: 500;
                padding: 10px 16px;
                margin: 4px 0px;
            }
            
            QPushButton#add_shortcut_button:hover {
                background-color: rgba(99, 102, 241, 0.1) !important;
            }
            
            QPushButton#add_shortcut_button:pressed {
                background-color: rgba(99, 102, 241, 0.2) !important;
            }
            
            QLabel#nav_icon {
                color: #FFFFFF;
                font-size: 18px;
                background-color: transparent;
                border: none;
            }
            
            QLabel#nav_text {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 500;
                background-color: transparent;
                border: none;
            }
            
            QPushButton#username_button {
                background-color: #3C3C4F;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: 500;
            }
            
            QPushButton#notification_button,
            QPushButton#refresh_button,
            QPushButton#settings_header_button {
                background-color: #3C3C4F;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
            }
            
            QPushButton#notification_button:hover,
            QPushButton#refresh_button:hover,
            QPushButton#settings_header_button:hover {
                background-color: #4A3B66;
            }
            
            QFrame#separator {
                color: #3C3C4F;
                background-color: #3C3C4F;
            }
            
            /* Styles pour les onglets du browser */
            QTabWidget {
                background-color: #1E1E2E;
                border: none;
            }
            
            QTabWidget::pane {
                background-color: #1E1E2E;
                border: 1px solid #3C3C4F;
                border-radius: 4px;
            }
            
            QTabBar::tab {
                background-color: #2D2D44;
                color: #FFFFFF;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #3C3C4F;
                border-bottom: none;
            }
            
            QTabBar::tab:selected {
                background-color: #4A3B66;
                color: #FFFFFF;
            }
            
            QTabBar::tab:hover {
                background-color: #3C3C4F;
            }
            
            /* Styles pour les boutons de raccourcis du browser */
            QPushButton#checkable_button {
                background-color: #2D2D44;
                border: 1px solid #3C3C4F;
                border-radius: 6px;
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 500;
                padding: 8px 12px;
            }
            
            QPushButton#checkable_button:hover {
                background-color: #3C3C4F;
                border-color: #4A3B66;
            }
            
            QPushButton#checkable_button:checked {
                background-color: #4A3B66;
                border-color: #3B82F6;
                color: #FFFFFF;
            }
            
            QPushButton#checkable_button:pressed {
                background-color: #3A2B56;
            }
            
            /* Styles pour les listes de navigation */
            QListWidget {
                background-color: #2D2D44;
                border: 1px solid #3C3C4F;
                border-radius: 4px;
                color: #FFFFFF;
                font-size: 12px;
            }
            
            QListWidget::item {
                background-color: transparent;
                padding: 4px 8px;
                border: none;
            }
            
            QListWidget::item:selected {
                background-color: #4A3B66;
                color: #FFFFFF;
            }
            
            QListWidget::item:hover {
                background-color: #3C3C4F;
            }
            
            /* Styles pour l'arbre de navigation */
            QTreeWidget {
                background-color: #2D2D44;
                border: 1px solid #3C3C4F;
                border-radius: 4px;
                color: #FFFFFF;
                font-size: 12px;
            }
            
            QTreeWidget::item {
                background-color: transparent;
                padding: 2px;
                border: none;
            }
            
            QTreeWidget::item:selected {
                background-color: #4A3B66;
                color: #FFFFFF;
            }
            
            QTreeWidget::item:hover {
                background-color: #3C3C4F;
            }
            
            QLabel#info_message {
                color: #8B949E;
                font-size: 16px;
                font-weight: 500;
                padding: 40px;
                background-color: #161B22;
                border: 1px solid #30363D;
                border-radius: 12px;
            }
            
            /* Scrollbars modernes pour le thème sombre */
            QScrollBar:vertical {
                background-color: #1C1C1C;
                width: 14px;
                border: 1px solid #2A2A2A;
                border-radius: 7px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #6366F1;
                border: 1px solid #5558E3;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #7C3AED;
                border: 1px solid #6D28D9;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QScrollBar:horizontal {
                background-color: #1C1C1C;
                height: 14px;
                border: 1px solid #2A2A2A;
                border-radius: 7px;
                margin: 2px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #6366F1;
                border: 1px solid #5558E3;
                border-radius: 6px;
                min-width: 30px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #7C3AED;
                border: 1px solid #6D28D9;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        
    def apply_light_theme(self):
        """Light theme removed - only dark theme available"""
        # Light theme has been removed, always use dark theme
        self.apply_dark_theme()


    def set_theme(self, theme):
        """Apply dark theme (light theme removed)"""
        self.current_theme = "dark"  # Force dark theme
        self.apply_dark_theme()
            
    def set_username(self, username):
        """Met à jour le nom d'utilisateur affiché"""
        self.username_sidebar_button.setText(f"👤 {username}")
        self.username_sidebar_button.setToolTip(f"Utilisateur: {username}")
        
    def on_search_text_changed(self, text):
        """Gère la recherche de fichiers dans le projet"""
        if not text:
            return
            
        import os
        from Packages.utils.funcs import get_current_value
        from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
        
        # Obtenir le chemin du projet courant
        project_path = get_current_value(json_file=CURRENT_PROJECT_JSON_PATH, key='current_project')
        if not project_path:
            project_path = os.getcwd()
        
        # Extensions autorisées
        ALLOWED_EXTENSIONS = {
            '.ma', '.mb', '.hip', '.hipnc', '.png', '.jpg', '.jpeg',
            '.nk', '.nuke', '.nukex', '.blend', '.sbs', '.sbsar',
            '.spp', '.psd', '.psb', '.zpr', '.ztl', '.c4d',
            '.uasset', '.umap', '.txt'
        }
        
        # Rechercher les fichiers
        search_results = []
        search_text_lower = text.lower()
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_lower = file.lower()
                file_ext = os.path.splitext(file)[1].lower()
                
                if search_text_lower in file_lower and file_ext in ALLOWED_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    search_results.append(full_path)
                    
                    # Limiter à 100 résultats pour la performance
                    if len(search_results) >= 100:
                        break
            
            if len(search_results) >= 100:
                break
        
        # Afficher les résultats dans la page search
        if hasattr(self, 'search_content') and hasattr(self.search_content, 'update_search_results'):
            # Basculer vers la page search (index 2)
            self.stacked_widget.setCurrentIndex(2)
            # Mettre à jour les résultats
            self.search_content.update_search_results(text)
        
        
    def create_custom_shortcut(self):
        """Crée un nouveau raccourci personnalisé"""
        from PySide2.QtWidgets import QFileDialog, QInputDialog
        import os
        from Packages.utils.funcs import get_current_value
        from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
        
        # Obtenir le chemin du projet courant
        project_path = get_current_value(json_file=CURRENT_PROJECT_JSON_PATH, key='current_project')
        if not project_path:
            project_path = os.getcwd()
        
        # Demander à l'utilisateur de choisir un dossier
        folder_path = QFileDialog.getExistingDirectory(
            self, 
            "Sélectionner un dossier pour le raccourci",
            project_path
        )
        
        if not folder_path:
            return
        
        # Demander le nom du raccourci
        shortcut_name, ok = QInputDialog.getText(
            self,
            "Nom du raccourci",
            "Entrez le nom du raccourci :",
            text=os.path.basename(folder_path)
        )
        
        if not ok or not shortcut_name:
            return
        
        # Créer le bouton de raccourci personnalisé
        self.add_custom_shortcut_button(shortcut_name, folder_path)
        
        # Sauvegarder dans le fichier JSON
        self.save_custom_shortcuts()
        
    def add_custom_shortcut_button(self, name, path):
        """Ajoute un bouton de raccourci personnalisé à la sidebar"""
        # Créer le bouton de navigation drag & drop
        shortcut_id = f"custom_{len(self.nav_buttons)}"
        button_widget = DraggableNavButton("", name, shortcut_id)
        
        # Stocker le chemin dans le bouton
        button_widget.button.setProperty('shortcut_path', path)
        button_widget.button.setProperty('shortcut_name', name)
        
        # Connecter les signaux
        button_widget.clicked.connect(lambda: self.on_nav_button_clicked(shortcut_id))
        button_widget.renamed.connect(lambda new_name: self.on_shortcut_renamed(shortcut_id, new_name))
        button_widget.deleted.connect(lambda: self.on_shortcut_deleted(shortcut_id))
        
        # Ajouter au container unifié
        self.shortcuts_container.add_button_widget(button_widget)
        
        # Ajouter aux boutons de navigation
        self.nav_buttons[shortcut_id] = button_widget
        
    def on_shortcut_renamed(self, shortcut_id, new_name):
        """Gère le renommage d'un raccourci"""
        if shortcut_id in self.nav_buttons:
            button_widget = self.nav_buttons[shortcut_id]
            button_widget.button.setProperty('shortcut_name', new_name)
            # Sauvegarder les modifications
            self.save_custom_shortcuts()
    
    def on_shortcut_deleted(self, shortcut_id):
        """Gère la suppression d'un raccourci"""
        if shortcut_id in self.nav_buttons:
            button_widget = self.nav_buttons[shortcut_id]
            # Retirer du container unifié
            self.shortcuts_container.remove_button_widget(button_widget)
            # Retirer du dictionnaire
            del self.nav_buttons[shortcut_id]
            # Sauvegarder les modifications
            self.save_custom_shortcuts()
    
    def on_shortcuts_reordered(self):
        """Gère le réordonnancement des raccourcis"""
        # Sauvegarder le nouvel ordre
        self.save_custom_shortcuts()
    
    def save_custom_shortcuts(self):
        """Sauvegarde les raccourcis personnalisés dans un fichier JSON"""
        import json
        import os
        from Packages.utils.funcs import get_current_value
        from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
        
        # Obtenir le chemin du projet courant
        project_path = get_current_value(json_file=CURRENT_PROJECT_JSON_PATH, key='current_project')
        if not project_path:
            return
        
        # Utiliser le dossier .pipezer de l'utilisateur
        user_home_dir = os.path.expanduser("~")
        pipezer_dir = os.path.join(user_home_dir, '.pipezer')
        
        # S'assurer que le dossier .pipezer existe
        if not os.path.exists(pipezer_dir):
            os.makedirs(pipezer_dir)
        
        # Créer le fichier de configuration des raccourcis
        shortcuts_file = os.path.join(pipezer_dir, '.pipezer_shortcuts.json')
        
        # Collecter tous les raccourcis dans l'ordre actuel
        shortcuts = []
        button_order = self.shortcuts_container.get_button_order()
        for btn_id in button_order:
            if btn_id in self.nav_buttons:
                button_widget = self.nav_buttons[btn_id]
                
                # Pour les boutons fixes (template, asset, shot), sauvegarder l'id et le nom personnalisé
                if btn_id in ['template', 'asset', 'shot']:
                    shortcuts.append({
                        'id': btn_id,
                        'name': button_widget.text_label.text()  # Nom affiché (peut être personnalisé)
                    })
                # Pour les raccourcis personnalisés, sauvegarder le nom et le chemin
                else:
                    shortcut_name = button_widget.button.property('shortcut_name')
                    shortcut_path = button_widget.button.property('shortcut_path')
                    if shortcut_name and shortcut_path:
                        shortcuts.append({
                            'name': shortcut_name,
                            'path': shortcut_path
                        })
        
        # Sauvegarder dans le fichier
        try:
            with open(shortcuts_file, 'w', encoding='utf-8') as f:
                json.dump({'shortcuts': shortcuts}, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des raccourcis: {e}")
            
    def load_custom_shortcuts(self):
        """Charge les raccourcis et leur ordre depuis le fichier JSON"""
        import json
        import os
        from Packages.utils.funcs import get_current_value
        from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
        
        # Obtenir le chemin du projet courant
        project_path = get_current_value(json_file=CURRENT_PROJECT_JSON_PATH, key='current_project')
        if not project_path:
            return
        
        # Utiliser le dossier .pipezer de l'utilisateur
        user_home_dir = os.path.expanduser("~")
        pipezer_dir = os.path.join(user_home_dir, '.pipezer')
        
        # Fichier de configuration des raccourcis
        shortcuts_file = os.path.join(pipezer_dir, '.pipezer_shortcuts.json')
        
        if not os.path.exists(shortcuts_file):
            return
        
        # Charger les raccourcis
        try:
            with open(shortcuts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                shortcuts = data.get('shortcuts', [])
                
                # Réorganiser les boutons existants et créer les nouveaux
                for i, shortcut in enumerate(shortcuts):
                    # Si c'est un bouton fixe (template, asset, shot)
                    if 'id' in shortcut:
                        btn_id = shortcut['id']
                        if btn_id in self.nav_buttons:
                            button_widget = self.nav_buttons[btn_id]
                            # Appliquer le nom personnalisé
                            custom_name = shortcut.get('name')
                            if custom_name:
                                button_widget.text_label.setText(custom_name)
                                button_widget.label_text = custom_name
                            
                            # Réorganiser dans le container
                            self.shortcuts_container.button_widgets.remove(button_widget)
                            self.shortcuts_container.button_widgets.insert(i, button_widget)
                            self.shortcuts_container.layout.removeWidget(button_widget)
                            self.shortcuts_container.layout.insertWidget(i, button_widget)
                    
                    # Si c'est un raccourci personnalisé
                    elif 'path' in shortcut:
                        self.add_custom_shortcut_button(shortcut['name'], shortcut['path'])
        except Exception as e:
            print(f"Erreur lors du chargement des raccourcis: {e}")
    
    def set_language(self, language):
        """Change la langue de l'interface"""
        if translation_manager.set_language(language):
            self.language_changed.emit(language)
            self.update_ui_texts()
    
    def on_language_changed(self, language):
        """Gère le changement de langue"""
        self.update_ui_texts()
    
    def update_ui_texts(self):
        """Met à jour tous les textes de l'interface"""
        # Mettre à jour les boutons de navigation
        if hasattr(self, 'nav_buttons'):
            for button_id, container in self.nav_buttons.items():
                if button_id in ['template', 'asset', 'shot', 'crash']:
                    container.text_label.setText(translation_manager.get_text(button_id))
        
        # Mettre à jour les boutons du header
        if hasattr(self, 'header_buttons'):
            for button_id, button in self.header_buttons.items():
                if button_id in ['recent', 'search', 'create_asset', 'create_shot']:
                    button.setText(translation_manager.get_text(button_id))
        
        # Mettre à jour le bouton utilisateur
        if hasattr(self, 'username_sidebar_button'):
            self.username_sidebar_button.setText(f"👤 {translation_manager.get_text('user')}")
        
        # Mettre à jour le bouton d'ajout de raccourci
        if hasattr(self, 'add_shortcut_button'):
            self.add_shortcut_button.setToolTip(translation_manager.get_text('add_shortcut'))
    
    def open_create_asset_dialog(self):
        """Ouvre le dialogue de création d'asset"""
        from Packages.ui.dialogs.modern_create_asset_dialog import ModernCreateAssetDialog
        
        dialog = ModernCreateAssetDialog(self)
        dialog.set_theme(self.current_theme)
        dialog.asset_created.connect(self.on_asset_created)
        dialog.show()  # Fenêtre séparée, ne change pas la fenêtre principale
        # Garder l'affichage actuel (Template, Asset, Shot, etc.)
    
    def open_create_shot_dialog(self):
        """Ouvre le dialogue de création de shot"""
        from Packages.ui.dialogs.modern_create_shot_dialog import ModernCreateShotDialog
        
        dialog = ModernCreateShotDialog(self)
        dialog.set_theme(self.current_theme)
        dialog.shot_created.connect(self.on_shot_created)
        dialog.show()  # Fenêtre séparée, ne change pas la fenêtre principale
        # Garder l'affichage actuel (Template, Asset, Shot, etc.)
    
    def on_asset_created(self, asset_name):
        """Gère la création d'un asset"""
        print(f"Asset créé: {asset_name}")
        # Ici on pourrait rafraîchir la liste des assets ou naviguer vers le nouvel asset
    
    def on_shot_created(self, shot_name):
        """Gère la création d'un shot"""
        print(f"Shot créé: {shot_name}")
        # Ici on pourrait rafraîchir la liste des shots ou naviguer vers le nouveau shot
