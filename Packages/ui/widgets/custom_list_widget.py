import os
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QListWidget, QMenu, QAbstractItemView, QAction
from Packages.logic.filefunc.interactions import open_explorer

import logging  # Importer le module de logging

# Initialiser le logger
logger = logging.getLogger(__name__)

class CustomListWidget(QListWidget):
    def __init__(self, parent = None, max_height = None):
        super(CustomListWidget, self).__init__()
        self.init_widget(parent, max_height)

        # on crée l'attribut "data" qui va stocker le répertoire auquel correspond le CustomLitWidget
        self.data = ''
        self.itemSelectionChanged.connect(self.update_data)

    def update_data(self):
        """
        Méthode mise à jour des données du widget de liste personnalisé.
        """
        selected_items = self.selectedItems()
        if not selected_items or selected_items[0] is None or selected_items[0].data(32) is None:
            print("Selected item or its data is None. Cannot update data.")
            return  # Ne rien faire si l'élément sélectionné ou ses données sont None

        try:
            self.data = os.path.dirname(selected_items[0].data(32))
        except TypeError as e:
            print(f"Error updating data: {e}")
            self.data = None  # Remettre à None pour éviter des erreurs futures

    def set_data(self, data_arg: str):
        self.data = data_arg
        
    def init_widget(self, parent, max_height):
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setFocusPolicy(Qt.NoFocus)
        if max_height:
            self.setMaximumHeight(max_height)

    def create_context_menu(self, project_action: bool = False):
        self._create_context_menu(project_action=project_action)
        self._connect_context_menu()
            
    def _create_context_menu(self, project_action: bool = False):
        """
        """
        self.context_menu = QMenu(self)

        self.open_explorer_action = QAction("Open in explorer", self)
        self.context_menu.addAction(self.open_explorer_action)
        self.open_explorer_action.triggered.connect(self._open_in_explorer)
        
        if project_action:
            self.create_project_action = QAction("Create project", self)
            self.context_menu.addAction(self.create_project_action)
        
        self.create_folder_action = QAction("Create folder", self)
        self.context_menu.addAction(self.create_folder_action)
        
    def _connect_context_menu(self):
        """
        """
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def _show_context_menu(self, pos):
        """
        """
        global_pos = self.mapToGlobal(pos)
        self.context_menu.exec_(global_pos)
    
    def _open_in_explorer(self):
        
        open_explorer(self.data)