"""
Fenêtre principale standalone moderne
"""

import os
from Packages.ui.base_main_window import BaseMainWindow
from Packages.ui.modern_main_window import ModernMainWindow
from Packages.ui.modern_settings_widget import ModernSettingsWidget
from Packages.ui.content_migrator import ContentMigrator
from Packages.ui.widgets import OpenFileWidget
from Packages.utils.logger import init_logger
from Packages.logic import json_funcs
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QVBoxLayout, QLabel
from PySide2.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from Packages.ui.dialogs.create_shot_dialog import CreateShotDialog
from Packages.ui.base_main_window import CreateAssetDialogStandalone


logger = init_logger(__file__)

class MainWindowStandalone(ModernMainWindow):
    """
    Fenêtre principale standalone avec interface moderne
    """
    def __init__(self, parent = None):
        super(MainWindowStandalone, self).__init__(parent)
        self.setup_standalone_content()
        self.add_dev_mode()

        # Définir la taille initiale de la fenêtre
        self.setGeometry(100, 100, 1700, 1000)  # Position x, y et taille largeur x hauteur

    def setup_standalone_content(self):
        """Configure le contenu spécifique à la version standalone"""
        # Initialiser le répertoire courant
        self.current_directory = os.getcwd()
        
        # Charger le nom d'utilisateur
        from Packages.ui.base_main_window import get_username
        username = get_username()
        self.set_username(username)
        
        # Intégrer le contenu existant dans les pages
        self.setup_browser_content()
        self.setup_recent_content()
        self.setup_search_content()
        self.setup_asset_content()
        self.setup_shot_content()
        self.setup_settings_content()
        self.setup_crash_content()
        self.setup_notifications_content()
        
        # Connecter les signaux
        self.connect_signals()
        
        # Configurer le mode développeur après que tout le contenu soit créé
        self.configure_dev_mode()
        
    def setup_browser_content(self):
        """Configure le contenu de la page Browser"""
        # Utiliser le ContentMigrator pour créer le contenu du browser
        self.browser_content = ContentMigrator.create_browser_content(self, self.current_directory)
        
        # Ajouter au layout de la page
        layout = QVBoxLayout(self.browser_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser_content)
        
    def setup_recent_content(self):
        """Configure le contenu de la page Recent"""
        # Utiliser le ContentMigrator pour créer le contenu des fichiers récents
        self.recent_content = ContentMigrator.create_recent_content(self)
        
        # Ajouter au layout de la page
        layout = QVBoxLayout(self.recent_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.recent_content)
        
    def setup_search_content(self):
        """Configure le contenu de la page Search"""
        # Utiliser le ContentMigrator pour créer le contenu de recherche
        self.search_content = ContentMigrator.create_search_content(self)
        
        # Ajouter au layout de la page
        layout = QVBoxLayout(self.search_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.search_content)
        
    def setup_asset_content(self):
        """Configure le contenu de la page Create Asset"""
        # Utiliser le ContentMigrator pour créer le contenu Create Asset
        self.asset_content = ContentMigrator.create_asset_content(self)
        
        # Ajouter au layout de la page
        layout = QVBoxLayout(self.asset_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.asset_content)
        
    def setup_shot_content(self):
        """Configure le contenu de la page Create Shot"""
        # Utiliser le ContentMigrator pour créer le contenu Create Shot
        self.shot_content = ContentMigrator.create_shot_content(self)
        
        # Ajouter au layout de la page
        layout = QVBoxLayout(self.shot_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.shot_content)
        
    def setup_settings_content(self):
        """Configure le contenu de la page Settings"""
        # Intégrer le widget de paramètres moderne
        layout = QVBoxLayout(self.settings_page)
        layout.setContentsMargins(0, 0, 0, 0)
        self.settings_widget = ModernSettingsWidget(self)
        layout.addWidget(self.settings_widget)
        
        # Synchroniser le thème
        self.settings_widget.set_theme(self.current_theme)
        
    def setup_crash_content(self):
        """Configure le contenu de la page Crash"""
        # Utiliser le ContentMigrator pour créer le contenu Crash
        self.crash_content = ContentMigrator.create_crash_content(self)
        
        # Ajouter au layout de la page
        layout = QVBoxLayout(self.crash_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.crash_content)
        
    def setup_notifications_content(self):
        """Configure le contenu de la page Notifications"""
        from Packages.ui.notifications_widget import NotificationsWidget
        
        # Créer le widget de notifications
        self.notifications_widget = NotificationsWidget(self)
        
        # Ajouter au layout de la page
        layout = QVBoxLayout(self.notifications_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.notifications_widget)
        
    def connect_signals(self):
        """Connecte les signaux"""
        # Connecter le signal de changement de paramètres
        if hasattr(self, 'settings_widget'):
            self.settings_widget.settings_changed.connect(self.on_settings_changed)
            
        # Connecter les boutons du header
        if hasattr(self, 'refresh_button'):
            self.refresh_button.clicked.connect(self.refresh_current_content)
            
        # Connecter le signal de navigation du browser
        self.browser_navigation_requested.connect(self.on_browser_navigation_requested)
            
    def on_browser_navigation_requested(self, target_path):
        """Appelé quand un bouton de raccourci demande une navigation"""
        if hasattr(self, 'browser_content') and hasattr(self.browser_content, 'update_navigation'):
            self.browser_content.update_navigation(target_path)
        else:
            print(f"Fonction update_navigation non trouvée dans browser_content")
            
    def on_settings_changed(self, settings):
        """Appelé quand les paramètres changent"""
        # Mettre à jour le thème si nécessaire
        if 'theme' in settings:
            self.set_theme(settings['theme'])
            
        # Mettre à jour le nom d'utilisateur si nécessaire
        if 'username' in settings and settings['username']:
            self.set_username(settings['username'])
            
    def refresh_current_content(self):
        """Rafraîchit le contenu de la page actuelle"""
        current_index = self.stacked_widget.currentIndex()
        
        if current_index == 0:  # Browser
            if hasattr(self, 'browser_content') and hasattr(self.browser_content, 'current_directory'):
                # Rafraîchir l'affichage des fichiers (le filtrage est géré dans le ContentMigrator)
                if hasattr(self.browser_content, 'browser_file_table'):
                    self.browser_content.browser_file_table.setRowCount(0)
                    # Le filtrage sera géré par la fonction update_filtered_file_table
        elif current_index == 1:  # Recent
            if hasattr(self, 'recent_content') and hasattr(self.recent_content, 'open_file_widget_recent'):
                self.recent_content.open_file_widget_recent.refresh()
        elif current_index == 2:  # Search
            if hasattr(self, 'search_content') and hasattr(self.search_content, 'open_file_widget_search_file'):
                self.search_content.open_file_widget_search_file.refresh()
        elif current_index == 3:  # Asset
            if hasattr(self, 'asset_content') and hasattr(self.asset_content, 'create_asset_dialog'):
                # Rafraîchir le dialog Create Asset si nécessaire
                pass
        elif current_index == 4:  # Shot
            if hasattr(self, 'shot_content') and hasattr(self.shot_content, 'create_shot_dialog'):
                # Rafraîchir le dialog Create Shot si nécessaire
                pass
        elif current_index == 5:  # Settings
            if hasattr(self, 'settings_widget'):
                # Rafraîchir les paramètres si nécessaire
                pass
        elif current_index == 6:  # Crash
            # Pas de rafraîchissement nécessaire pour la page Crash
            pass
        elif current_index == 7:  # Notifications
            if hasattr(self, 'notifications_widget'):
                # Rafraîchir les notifications
                self.notifications_widget.load_notifications()

    def add_dev_mode(self):
        """Ajoute le mode développeur"""
        # Cette méthode est appelée avant que le contenu soit créé
        # On va la déplacer après la création du contenu
        pass

    def configure_dev_mode(self):
        """Configure le mode développeur après création du contenu"""
        if json_funcs.get_dev_mode_state():
            # Afficher les boutons de préférences dans les widgets OpenFileWidget
            if hasattr(self, 'browser_content') and hasattr(self.browser_content, 'open_file_widget_browser'):
                self.browser_content.open_file_widget_browser.prefs_button.show()
            if hasattr(self, 'recent_content') and hasattr(self.recent_content, 'open_file_widget_recent'):
                self.recent_content.open_file_widget_recent.prefs_button.show()
            if hasattr(self, 'search_content') and hasattr(self.search_content, 'open_file_widget_search_file'):
                self.search_content.open_file_widget_search_file.prefs_button.show()
        else:
            # Masquer les boutons de préférences
            if hasattr(self, 'browser_content') and hasattr(self.browser_content, 'open_file_widget_browser'):
                self.browser_content.open_file_widget_browser.prefs_button.hide()
            if hasattr(self, 'recent_content') and hasattr(self.recent_content, 'open_file_widget_recent'):
                self.recent_content.open_file_widget_recent.prefs_button.hide()
            if hasattr(self, 'search_content') and hasattr(self.search_content, 'open_file_widget_search_file'):
                self.search_content.open_file_widget_search_file.prefs_button.hide()

    def refresh_interface_texts(self):
        """Rafraîchit tous les textes de l'interface selon la langue actuelle"""
        try:
            # Cette méthode peut être étendue pour traduire tous les textes de l'interface
            # Pour l'instant, les textes principaux sont en dur (Create Asset, Create Shot, etc.)
            # Vous pouvez ajouter ici la traduction de tous les éléments si nécessaire
            
            # Forcer le rafraîchissement de l'affichage
            self.update()
        except Exception as e:
            print(f"Erreur lors du rafraîchissement de l'interface: {e}")
