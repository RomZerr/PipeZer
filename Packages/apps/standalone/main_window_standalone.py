import os
from Packages.ui.base_main_window import BaseMainWindow
from Packages.ui.widgets import OpenFileWidget
from Packages.utils.logger import init_logger
from Packages.logic import json_funcs
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from Packages.ui.dialogs.create_shot_dialog import CreateShotDialog
from Packages.ui.base_main_window import CreateAssetDialogStandalone


logger = init_logger(__file__)

class MainWindowStandalone(BaseMainWindow):
    """
    """
    def __init__(self, parent = None):
        super(MainWindowStandalone, self).__init__(parent, set_style = True)
        self.add_dev_mode()

        # Définir la taille initiale de la fenêtre
        self.setGeometry(100, 100, 1700, 1000)  # Position x, y et taille largeur x hauteur

    def create_widgets(self):
        super().create_widgets()
        self._open_file_widget_browser = OpenFileWidget(self.current_directory)
        self._open_file_widget_browser.setObjectName("_open_file_widget_browser")
        self._open_file_widget_recent = OpenFileWidget(None)
        self._open_file_widget_browser.setObjectName("_open_file_widget_recent")
        self._open_file_widget_search_file = OpenFileWidget(None)
        self._open_file_widget_search_file.setObjectName("_open_file_widget_search_file")

    def create_layout(self):
        super().create_layout()
        self._browser_file_layout.addWidget(self._open_file_widget_browser)
        self._recent_file_layout.addWidget(self._open_file_widget_recent)
        self._search_file_layout.addWidget(self._open_file_widget_search_file)

        # Créer un layout vertical pour les boutons
        button_layout = QHBoxLayout()

        # Créer le bouton "Create Asset" avec une taille spécifique
        self.create_asset_button = QPushButton("Create Asset", self)
        self.create_asset_button.setCheckable(True)
        font = self.create_asset_button.font()
        font.setPointSize(10)
        self.create_asset_button.setFont(font)
        self.create_asset_button.setFixedSize(200, 40)
        self.create_asset_button.clicked.connect(self.open_create_asset_dialog)


        # Ajouter le bouton "Create Asset" au layout vertical
        button_layout.addWidget(self.create_asset_button)

        # Créer le bouton "Create Shot" avec une taille spécifique
        self.create_shot_button = QPushButton("Create Shot", self)
        self.create_shot_button.setCheckable(True)
        font = self.create_shot_button.font()
        font.setPointSize(10)
        self.create_shot_button.setFont(font)
        self.create_shot_button.setFixedSize(200, 40)
        self.create_shot_button.clicked.connect(self.open_create_shot_dialog)


        # Ajouter le bouton "Create Shot" juste en dessous du bouton "Create Asset"
        button_layout.addWidget(self.create_shot_button)

        # Créer le bouton "Construct Pipeline" à côté
        self.construct_pipeline_button = QPushButton("Construct Pipeline", self)
        self.construct_pipeline_button.setCheckable(True)
        font2 = self.construct_pipeline_button.font()
        font2.setPointSize(10)
        self.construct_pipeline_button.setFont(font2)
        self.construct_pipeline_button.setFixedSize(200, 40)
        self.construct_pipeline_button.clicked.connect(self.open_construct_pipeline_dialog)

        button_layout.addWidget(self.construct_pipeline_button)

        # Déplacer/ajouter le bouton Settings à côté, même hauteur
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.setCheckable(True)
        f3 = self.settings_button.font()
        f3.setPointSize(10)
        self.settings_button.setFont(f3)
        self.settings_button.setFixedSize(200, 40)
        from Packages.ui.dialogs.option_dialog import OptionDialog
        def open_settings():
            self.settings_button.setChecked(True)
            dlg = OptionDialog(self)
            dlg.finished.connect(lambda _: self.settings_button.setChecked(False))
            dlg.exec_()
        self.settings_button.clicked.connect(open_settings)
        button_layout.addWidget(self.settings_button)

        # Ajouter des marges pour un meilleur alignement
        button_layout.setContentsMargins(10, 0, 0, 20)  # Gauche, Haut, Droite, Bas

        # Ajouter un espace entre les boutons pour les séparer un peu
        button_layout.addSpacing(10)

        # Aligner les boutons en bas à gauche de la fenêtre
        button_layout.addStretch()

        # Créer le bouton Refresh tout à droite avec icône et texte
        from Packages.utils.constants.project_pipezer_data import ICONS_PATH
        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.setIcon(QIcon(os.path.join(ICONS_PATH, 'refresh_icon.png')))
        self.refresh_button.setIconSize(QSize(24, 24))
        self.refresh_button.setFixedSize(120, 40)
        self.refresh_button.setToolTip("Rafraîchir la vue")
        self.refresh_button.clicked.connect(self.refresh_view)
        button_layout.addWidget(self.refresh_button)
        
        # Ajouter une marge à droite du bouton refresh
        button_layout.addSpacing(20)

        # Ajouter le layout des boutons au layout principal
        self._browser_main_layout.addLayout(button_layout)

    def open_construct_pipeline_dialog(self):
        from Packages.ui.dialogs.construct_pipeline_dialog import ConstructPipelineDialog
        self.construct_pipeline_button.setChecked(True)
        dlg = ConstructPipelineDialog(self)
        dlg.finished.connect(lambda: self.construct_pipeline_button.setChecked(False))
        dlg.exec_()

    def open_create_asset_dialog(self):
        self.create_asset_button.setChecked(True)
        self.create_asset_dialog = CreateAssetDialogStandalone(self)
        self.create_asset_dialog.finished.connect(lambda: self.create_asset_button.setChecked(False))
        self.create_asset_dialog.exec_()

    def open_create_shot_dialog(self):
        print("Ouverture de la fenêtre Create Shot")
        self.create_shot_button.setChecked(True)
        try:
            self.create_shot_dialog = CreateShotDialog(self)
            self.create_shot_dialog.finished.connect(lambda: self.create_shot_button.setChecked(False))
            self.create_shot_dialog.exec_()
        except Exception as e:
            print(f"Erreur lors de l'ouverture de la fenêtre Create Shot : {e}")

    def create_connections(self):
        super().create_connections()
        self._open_file_widget_browser.open_file_button.clicked.connect(self.open_file_in_app)
        self._open_file_widget_recent.open_file_button.clicked.connect(self.open_file_in_app)
        self._open_file_widget_search_file.open_file_button.clicked.connect(self.open_file_in_app)

    def on_browser_tab_active(self):
        super().on_browser_tab_active()
        self.status_bar.update(self.current_directory)
        print(f'current dir : {self.current_directory}')

    def on_recent_tab_active(self):
        super().on_recent_tab_active()
        self._open_file_widget_recent.update_buttons(None)
        recent_files = json_funcs.get_recent_files()
        self.recent_file_table.update_file_items(recent_files)

    def refresh_view(self):
        """
        Rafraîchit la vue actuelle en rechargeant les données.
        """
        print("Rafraîchissement de la vue...")
        # Rafraîchir selon l'onglet actif
        active_tab = self._get_active_tab_text()
        
        if active_tab == 'Browser':
            # Rafraîchir le browser
            self.on_radio_button_clicked()
        elif active_tab == 'Recent':
            # Rafraîchir les fichiers récents
            self.on_recent_tab_active()
        elif active_tab == 'Search File':
            # Rafraîchir la recherche si nécessaire
            pass
        
        print("Vue rafraîchie !")

    def open_file_in_app(self):

        if self._get_active_tab_text() == 'Browser':
            self._open_file_widget_browser.open_file_in_app(self.status_bar.get_text())

        elif self._get_active_tab_text() == 'Recent':
            self._open_file_widget_recent.open_file_in_app(self.status_bar.get_text())

        elif self._get_active_tab_text() == 'Anim Filter':
            self._open_file_widget_filtered.open_file_in_app(self.status_bar.get_text())

    def _on_file_item_clicked(self, item):
        super()._on_file_item_clicked(item)

        file_path = item.data(32)

        if self._get_active_tab_text() == 'Browser':
            self._open_file_widget_browser.update_buttons(file_path)

        elif self._get_active_tab_text() == 'Recent':
            self._open_file_widget_recent.update_buttons(file_path)

        elif self._get_active_tab_text() == 'Anim Filter':
            self._open_file_widget_filtered.update_buttons(file_path)

        else:
            return

    def _add_dir(self, item):
        super()._add_dir(item)
        self._open_file_widget_browser.update_buttons(self.status_bar.get_text())

    def add_dev_mode(self):

        if json_funcs.get_dev_mode_state():
            self._open_file_widget_browser.prefs_button.show()

        else:
            self._open_file_widget_browser.prefs_button.hide()

    def get_selected_file_path(self, item):
        """
        Récupère le chemin du fichier sélectionné à partir de l'élément sélectionné dans la table de fichiers.
        Args:
            item (QTableWidgetItem): L'élément sélectionné dans la table.
        Returns:
            str: Le chemin du fichier sélectionné.
        """
        # Détermine quelle table est active et utilise le bon index pour récupérer le chemin du fichier
        active_tab = self._get_active_tab_text()
        print(f"Active Tab: {active_tab}")  # Ligne de débogage pour voir le nom de l'onglet actif

        if active_tab == 'Browser':
            table = self.browser_file_table
        elif active_tab == 'Recent':
            table = self.recent_file_table
        elif active_tab == 'Search File':
            table = self.search_file_table
        else:
            print("Tab non pris en charge.")
            return None

        # Assurez-vous que l'élément est valide et qu'il y a suffisamment d'éléments sélectionnés
        if item and table:
            row = table.row(item)
            # Assurez-vous que la colonne contenant le chemin du fichier est correcte (ici on suppose que c'est la première colonne)
            file_path_item = table.item(row, 0)  # Remplacez 0 par l'index correct de la colonne du chemin du fichier
            if file_path_item:
                return file_path_item.text()

        print("Aucun fichier sélectionné.")
        return None

