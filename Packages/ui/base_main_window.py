import os
import shutil
import re
import json
import logging

from PySide2.QtCore import Qt, QSize, QTimer
from PySide2.QtGui import QPixmap, QCursor, QIcon
from PySide2.QtWidgets import (
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QSizePolicy,
    QLineEdit,
    QHBoxLayout,
    QMenu,
    QSplitter,
    QDialog,
    QTreeWidgetItem,
    QListWidgetItem,
    QPushButton,
    QButtonGroup,
    QTableWidgetItem,
    QListWidget,
    QAction,
    QMessageBox
)

from Packages.ui.widgets.open_file_widget import OpenFileWidget
from Packages.ui.widgets.filtered_list_widget import FilteredListWidget
from Packages.ui.widgets.custom_table_widget import CustomTableWidget
from Packages.ui.widgets import StatusBar, CustomListWidget, CustomListWidgetItem, CustomMainWindow, CustomTreeWidget
from Packages.ui.dialogs import TextEntryDialog, CreateSoftProjectDialog

from Packages.utils.constants.constants_old import ASSET_DIR, PREFIX
from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT, ICONS_PATH
from Packages.utils.constants.project_files import ICON_PATH
from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
from Packages.utils.logger import init_logger
from Packages.utils.funcs import get_current_value

from Packages.logic.json_funcs import (
    get_file_data,
    update_file_data,
    set_clicked_item,
    set_clicked_radio_button,
    get_clicked_item,
    get_clicked_radio_button
)
from Packages.logic.filefunc import clean_directory, open_explorer, increment_file_external
from Packages.logic.file_opener import FileOpener

logger = init_logger(__file__)

class BaseMainWindow(CustomMainWindow):
    """
    """
    def __init__(self, parent = None, set_style: bool = False):
        super(BaseMainWindow, self).__init__(parent, set_style)

        self.PROJECT_PATH = get_current_value(json_file=CURRENT_PROJECT_JSON_PATH, key='current_project')
        self.PROJECT_NAME = os.path.basename(self.PROJECT_PATH)

        self.current_directory = None

        self.init_ui(project = self.PROJECT_NAME)
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_context_menu()
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.filter_files)

        self.status_bar = StatusBar(parent = self._central_layout, text = self.PROJECT_PATH)


    def _create_user_notification_buttons(self):

        # Bouton utilisateur
        self.user_button = QPushButton()
        self.user_button.setObjectName("user_button")
        self.user_button.setMinimumSize(100, 35)
        self.user_button.setMaximumSize(150, 35)
        username = get_username()
        self.user_button.setText(f"👤 {username}")
        self.user_button.setToolTip(f"Utilisateur: {username}")
        
        # Bouton notification
        self.notification_button = QPushButton()
        self.notification_button.setObjectName("notification_button")
        self.notification_button.setMinimumSize(35, 35)
        self.notification_button.setMaximumSize(35, 35)
        self.notification_button.setText("🔔")
        self.notification_button.setToolTip("Notifications")
        
        # Ajouter les boutons au layout
        self._radio_layout.addWidget(self.user_button)
        self._radio_layout.addWidget(self.notification_button)
        
        self.user_button.clicked.connect(self._edit_username)

    def _edit_username(self):
        """
        Ouvre un dialog pour modifier le nom d'utilisateur.
        """
        from PySide2.QtWidgets import QInputDialog
        
        current_username = get_username()
        new_username, ok = QInputDialog.getText(
            self, 
            'Modifier le nom d\'utilisateur', 
            'Nouveau nom d\'utilisateur:', 
            text=current_username
        )
        
        if ok and new_username.strip():
            # Sauvegarder le nouveau nom d'utilisateur
            self._save_username(new_username.strip())
            # Mettre à jour le bouton
            self.user_button.setText(f"👤 {new_username.strip()}")
            self.user_button.setToolTip(f"Utilisateur: {new_username.strip()}")

    def _save_username(self, username):
        """
        Sauvegarde le nom d'utilisateur dans le fichier user.json.
        """
        import os
        import json
        
        user_home_dir = os.path.expanduser("~")
        pipezer_dir = os.path.join(user_home_dir, '.pipezer')
        
        # Créer le dossier .pipezer s'il n'existe pas
        if not os.path.exists(pipezer_dir):
            os.makedirs(pipezer_dir)
        
        user_file_path = os.path.join(pipezer_dir, 'user.json')
        
        try:
            # Charger les données existantes ou créer un nouveau dict
            if os.path.exists(user_file_path):
                with open(user_file_path, 'r') as user_file:
                    data = json.load(user_file)
            else:
                data = {}
            
            # Mettre à jour le nom d'utilisateur
            data["username"] = username
            
            # Sauvegarder
            with open(user_file_path, 'w') as user_file:
                json.dump(data, user_file, indent=2)
                
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du nom d'utilisateur : {e}")

    def create_widgets(self):

        # Initialisation du QTabWidget pour gérer les onglets
        self._tab_widget = QTabWidget(self)
        self._tab_widget.setObjectName("main_tab_widget")
        # Supprimer le background gris du QTabWidget
        self._tab_widget.setStyleSheet("QTabWidget#main_tab_widget { background-color: transparent; }")

        # BROWSER TAB --------------------------------------------------------------------------------------
        self.button_group = QButtonGroup()

        def create_checkable_button(button_text):
            checkable_button = QPushButton(button_text)
            checkable_button.setCheckable(True)
            checkable_button.setMinimumSize(120, 35)
            checkable_button.setObjectName(f"checkable_button")
            self.button_group.addButton(checkable_button)
            return checkable_button

        self._templates_radio_button: QPushButton = create_checkable_button('Template')
        self._asset_radio_button: QPushButton = create_checkable_button("Asset")
        self._shot_radio_button: QPushButton = create_checkable_button('Shot')
        self._localLDV_radio_button: QPushButton = create_checkable_button('Local LDV')
        self._localCOMPO_radio_button: QPushButton = create_checkable_button('Local COMP')
        self._crash_radio_button: QPushButton = create_checkable_button('Crash')

        # Associer les répertoires aux boutons
        self._asset_radio_button.setProperty('directory', '04_asset')
        self._shot_radio_button.setProperty('directory', '05_shot')
        self._templates_radio_button.setProperty('directory', '02_ressource/template_scenes')
        self._localLDV_radio_button.setProperty('directory', 'D:/_PROD/LOOKDEV/04_asset')
        self._localCOMPO_radio_button.setProperty('directory', 'D:/_PROD/COMPO')
        self._crash_radio_button.setProperty('directory', 'C:/Users/3D4/AppData/Local/Temp/')

        # Liste de tous les boutons checkables
        self.checkable_buttons = (
            self._asset_radio_button,
            self._shot_radio_button,
            self._templates_radio_button,
            self._localLDV_radio_button,
            self._localCOMPO_radio_button,
            self._crash_radio_button,
        )

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("")
        self.search_bar.returnPressed.connect(self.filter_items)
        self.tree_browser = CustomTreeWidget()

        self.list_01 = CustomListWidget(max_height=100)
        self.list_02 = CustomListWidget(max_height=100)
        self.list_03 = CustomListWidget(max_height=100)
        self.list_04 = CustomListWidget(max_height=100)

        self.list_01.create_context_menu(project_action=True)
        self.list_02.create_context_menu()
        self.list_03.create_context_menu()

        # Configuration du tableau pour "Browser"
        self.browser_file_table = CustomTableWidget()
        self.browser_file_table.set_table(['File Name', 'Image', 'Version', 'Comment', 'Infos'],
                                          [180, 100, 100, 150, 100])

        # Configuration de la mise en page du tableau
        self._browser_file_layout = QVBoxLayout()
        self._browser_file_layout.addWidget(self.browser_file_table)

        # Configuration du tableau pour "Recent"
        self.recent_file_table = CustomTableWidget()
        self.recent_file_table.set_table(['File Name', 'Image', 'Version', 'Comment', 'Infos'],
                                         [180, 100, 100, 150, 100])

        # Configuration du tableau pour "Search File"
        self.search_file_table = CustomTableWidget()
        self.search_file_table.set_table(['File Name', 'Image', 'Version', 'Comment', 'Infos'], True)


        # SEARCH  TAB --------------------------------------------------------------------------------------
        self.search_file_tab = QWidget()
        self.search_file_tab.setObjectName("search_file_tab")

    def create_layout(self):
        """
        """

        # Créer un QTabWidget
        self._tab_widget = QTabWidget()

        # Créer les 2 onglets
        self.browser_tab = QWidget()
        self.browser_tab.setObjectName("browser_tab")
        self.recent_tab = QWidget()
        self.recent_tab.setObjectName("recent_tab")


        # BROWSER TAB --------------------------------------------------------------------------------------
        # we create all the browser layout
        self._central_widget = QWidget()
        self.setCentralWidget(self._central_widget)
        self._central_layout = QVBoxLayout()
        self._central_widget.setLayout(self._central_layout)

        self._browser_main_layout = QVBoxLayout()
        self._browser_main_layout.setContentsMargins(0, 0, 0, 0)

        self._browser_secondary_layout_widget=QWidget()
        self._browser_secondary_layout_widget.setObjectName("_browser_secondary_layout_widget")
        self._browser_secondary_layout = QHBoxLayout(self._browser_secondary_layout_widget)

        self._radio_layout_widget=QWidget()

        self._radio_layout_widget.setObjectName("_radio_layout_widget")
        self._radio_layout_widget.setStyleSheet("QWidget#_radio_layout_widget { background-color: transparent; }")
        self._radio_layout = QHBoxLayout(self._radio_layout_widget)
        self._radio_layout.setContentsMargins(10, 10, 10, 0)
        self._radio_layout.setAlignment(Qt.AlignCenter)

        self._left_splitter = QSplitter(Qt.Vertical)
        self._left_splitter.setObjectName("_left_splitter")

        self._right_layout_widget=QWidget()
        self._right_layout_widget.setObjectName("_right_layout_widget")
        self._right_layout = QVBoxLayout(self._right_layout_widget)
        self._right_layout.setContentsMargins(0, 0, 0, 0)

        self._filter_layout_widget=QWidget()
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self._filter_layout_widget.setSizePolicy(size_policy)
        self._filter_layout = QHBoxLayout(self._filter_layout_widget)
        self._filter_layout.setContentsMargins(0, 0, 0, 0)

        self._browser_file_layout_widget = QWidget()
        self._browser_file_layout_widget.setObjectName("_file_layout_widget")
        self._browser_file_layout = QVBoxLayout(self._browser_file_layout_widget)
        self._browser_file_layout.setContentsMargins(0, 0, 0, 0)

        self.tool_layout_widget = QWidget()
        self.tool_layout = QVBoxLayout(self.tool_layout_widget)

        for radio_btn in self.checkable_buttons:
            self._radio_layout.addWidget(radio_btn)
        self._radio_layout.addStretch(1)
        
        # Ajouter les boutons utilisateur et notification à droite
        self._create_user_notification_buttons()
        self._left_splitter.addWidget(self.tree_browser)
        self._left_splitter.addWidget(self.tool_layout_widget)

        self._browser_file_layout.addWidget(self.browser_file_table)

        self._filter_layout.addWidget(self.list_01)
        self._filter_layout.addWidget(self.list_02)
        self._filter_layout.addWidget(self.list_03)

        # we fill the window

        self._central_layout.addWidget(self._tab_widget)

        self._tab_widget.addTab(self.browser_tab, 'Browser')
        self._tab_widget.addTab(self.recent_tab, 'Recent')
        self._tab_widget.addTab(self.search_file_tab, "Search File")

        self.browser_tab.setLayout(self._browser_main_layout)
        self._browser_main_layout.addWidget(self._radio_layout_widget)
        self._browser_main_layout.addWidget(self._browser_secondary_layout_widget)

        self._right_layout.addWidget(self._filter_layout_widget)
        self._right_layout.addWidget(self._browser_file_layout_widget)
        self._browser_secondary_layout.addWidget(self._left_splitter)
        self._browser_secondary_layout.addWidget(self._right_layout_widget)

        # RECENT TAB --------------------------------------------------------------------------------------
        self._recent_main_layout = QVBoxLayout()
        self._recent_file_layout = QVBoxLayout()
        self.recent_tab.setLayout(self._recent_main_layout)

        self._recent_file_layout_widget = QWidget()
        self._recent_file_layout_widget.setObjectName("_recent_file_layout_widget")
        self._recent_file_layout = QVBoxLayout(self._recent_file_layout_widget)
        self._recent_file_layout.setContentsMargins(0, 0, 0, 0)

        self._recent_file_layout.addWidget(self.recent_file_table)

        self._recent_main_layout.addWidget(self._recent_file_layout_widget)

        # Barre de recherche
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher un fichier...")
        self.search_bar.setFixedHeight(40)

        # Bouton de recherche
        self.search_button = QPushButton("Recherche", self)
        self.search_button.setFixedSize(150, self.search_bar.sizeHint().height())
        self.search_button.setFixedHeight(40)

        self.search_button.clicked.connect(self.filter_files)

        # Connecter l'événement de la barre de recherche à la méthode de recherche
        self.search_bar.returnPressed.connect(self.filter_files)
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_button)

        # Configuration de la mise en page avec la barre de recherche au-dessus du tableau
        self._search_file_layout = QVBoxLayout(self.search_file_tab)
        self._search_file_layout.addLayout(
            search_layout)  # Ajoute le layout de recherche horizontal au-dessus du tableau
        self._search_file_layout.addWidget(self.search_file_table)  # Ajoute le tableau en dessous

    def filter_files(self):
        print("Début de la méthode filter_files")

        search_text = self.search_bar.text().lower()
        project_folder = CURRENT_PROJECT

        # Effacer les anciennes données du tableau
        print("Effacement du tableau")
        self.search_file_table.setRowCount(0)

        matching_files = []  # Stocker les fichiers correspondants
        max_displayed_results = 100  # Limite le nombre de résultats affichés

        # Parcourir les fichiers dans le dossier du projet
        for root, dirs, files in os.walk(project_folder):
            # Ignorer le dossier "02_ressource"
            if '02_ressource' in root:
                print(f"Dossier ignoré : {root}")
                continue  # Passer à l'itération suivante pour ignorer ce dossier

            print(f"Exploration du dossier : {root}")
            for file in files:
                if search_text in file.lower():
                    file_path = os.path.join(root, file)
                    matching_files.append(file_path)

                    # Vérifie si la limite de résultats a été atteinte
                    if len(matching_files) >= max_displayed_results:
                        print(f"Limite de {max_displayed_results} résultats atteinte")
                        break
            if len(matching_files) >= max_displayed_results:
                break

        # Désactiver les mises à jour du tableau pour éviter les ralentissements
        self.search_file_table.setUpdatesEnabled(False)

        # Ajout des résultats au tableau
        for file_path in matching_files:
            print(f"Ajout du fichier au tableau : {file_path}")
            self.search_file_table.add_item(file_path)

        # Réactiver les mises à jour du tableau
        self.search_file_table.setUpdatesEnabled(True)

        print("Fin de la méthode filter_files")

    def create_connections(self):

        for radio_button in self.checkable_buttons:
            radio_button.clicked.connect(self.on_radio_button_clicked)

        self._tab_widget.currentChanged.connect(self._on_tab_changed)
        self.search_bar.returnPressed.connect(self.start_search_timer)

        self.browser_file_table.itemClicked.connect(self._on_file_item_clicked)
        self.recent_file_table.itemClicked.connect(self._on_file_item_clicked)
        self.search_file_table.itemClicked.connect(self._on_file_item_clicked)
        
        self.browser_file_table.itemDoubleClicked.connect(self._open_file)
        self.recent_file_table.itemDoubleClicked.connect(self._open_file)
        self.search_file_table.itemDoubleClicked.connect(self._open_file)

        self.tree_browser.itemClicked.connect(self.on_tree_item_clicked)

        self.list_01.create_project_action.triggered.connect(self._open_create_soft_project_dialog)
        self.list_01.create_folder_action.triggered.connect(self._open_create_folder_dialog_01)
        self.list_01.itemClicked.connect(self.on_list_item_clicked)
        self.list_02.create_folder_action.triggered.connect(self._open_create_folder_dialog_02)
        self.list_02.itemClicked.connect(self.on_list_item_clicked)
        self._select_item_from_text(self.list_02, 'scenes')
        self.list_03.create_folder_action.triggered.connect(self._open_create_folder_dialog_03)
        self.list_03.itemClicked.connect(self.on_list_item_clicked)
        self.list_04.itemClicked.connect(self.on_list_item_clicked)

    def create_context_menu(self):
        # Définir menu contextuel pour Comment
        self.context_menu = QMenu(self)
        
        self.edit_comment_action = QAction("Edit comment", self)
        self.file_dialog_action = QAction("Open in explorer", self)
        self.increment_file_action = QAction('Increment file', self)
        
        self.edit_comment_action.triggered.connect(self.open_comment_dialog)
        self.file_dialog_action.triggered.connect(self.open_file_dialog)
        self.increment_file_action.triggered.connect(self.increment_file)
        
        self.context_menu.addAction(self.edit_comment_action)
        self.context_menu.addAction(self.file_dialog_action)
        self.context_menu.addAction(self.increment_file_action)
        
        if self._get_active_radio_text() == 'Browser':
            self.context_menu.addAction(self.increment_file_action)
        
        self.browser_file_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.browser_file_table.customContextMenuRequested.connect(self.show_context_menu)

        self.recent_file_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.recent_file_table.customContextMenuRequested.connect(self.show_context_menu_recent)

        self.search_file_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.search_file_table.customContextMenuRequested.connect(self.show_context_menu_recent)

    def filter_items(self):
        # Filtrer les items du QTreeWidget en fonction du texte entré dans la barre de recherche
        filter_text = self.search_bar.text().lower()
        self.tree_browser.clearSelection()
        self.filter_items_recursive(self.tree_browser.invisibleRootItem(), filter_text)

    def filter_items_recursive(self, parent_item, filter_text):
        for index in range(parent_item.childCount()):
            item = parent_item.child(index)
            item_text = item.text(0).lower()
            if filter_text in item_text:
                item.setHidden(False)
                # Expand the parent items of the matching item
                self.expand_parent_items(item)
            else:
                item.setHidden(True)
            # Recursively filter child items
            self.filter_items_recursive(item, filter_text)

    def expand_parent_items(self, item):
        parent_item = item.parent()
        while parent_item:
            parent_item.setExpanded(True)
            parent_item = parent_item.parent()

    def start_search_timer(self):
        self.search_timer.start(300)  # Délai de 300 ms avant de lancer la recherche

    # AUTO-CLIC
    def auto_clic(self):

        text = get_clicked_radio_button()
        if not text:
            return
        
        for radio_btn in self.checkable_buttons:
            if text == radio_btn.text():
                radio_btn.setChecked(True)
                try:
                    self.on_radio_button_clicked()
                except TypeError:
                    continue
        
    # SLOTS
    def _get_active_tab_text(self):

        active_tab_index = self._tab_widget.currentIndex()
        tab_text = self._tab_widget.tabText(active_tab_index)

        return tab_text

    def _on_tab_changed(self, index: int):
        
        tab_text = self.sender().tabText(index)
        
        if tab_text == 'Recent':
            self.on_recent_tab_active()
            
        elif tab_text == 'Browser':
            self.on_browser_tab_active()
            
        else:
            pass
            
    def _get_last_clicked_list_item(self):
        lists = [self.list_01, self.list_02, self.list_03, self.list_04]

        for list_widget in lists:
            if list_widget.currentItem():
                return list_widget.currentItem()

        return None
    
    def on_browser_tab_active(self):
        self.status_bar.update(self.current_directory)
            
    def on_recent_tab_active(self):
        self.status_bar.update('')
    
    def _get_active_radio_text(self):
        return next((value.text() for value in self.checkable_buttons if value.isChecked()), None)
    
    def _click_tree_item_by_text(self, tree_widget: CustomTreeWidget, text_to_find: str, parent_item: QTreeWidgetItem = None):
        if parent_item is None:
            # Si parent_item n'est pas spécifié, commencez la recherche depuis les éléments de niveau supérieur
            root_items = [tree_widget.topLevelItem(i) for i in range(tree_widget.topLevelItemCount())]
        else:
            # Sinon, commencez la recherche depuis les enfants de parent_item
            root_items = [parent_item]
        
        # Parcourez les éléments
        for item in root_items:
            if item.text(0) == text_to_find:  # Supposons que la colonne 0 contient le texte
                # Cliquez sur l'élément trouvé
                tree_widget.setCurrentItem(item)
                return True
            
            # Parcourez les enfants récursivement
            for column in range(item.columnCount()):
                for child_index in range(item.childCount()):
                    child_item = item.child(child_index)
                    if self._click_tree_item_by_text(tree_widget, text_to_find, child_item):
                        return child_item, column
        
        # Si l'élément n'a pas été trouvé, renvoie False
        return False
    
    def on_radio_button_clicked(self):
        
        def find_top_level_item_by_text(tree_widget: CustomTreeWidget, texte: str) -> QTreeWidgetItem:
            """ Trouve et retourne l'élément QTreeWidgetItem top level ayant le texte donné. """
            items = tree_widget.findItems(texte, Qt.MatchExactly, 0)  # Recherche par texte exact dans la colonne 0
            
            for item in items:
                if not item.parent():  # Vérifie si l'élément n'a pas de parent (top level)
                    return item
            
            return None  # Retourne None si aucun élément correspondant n'est trouvé

        self._add_base_folder_to_dir()
        self._fill_tree_items()
        radio_btn = self._get_active_radio_text()
        set_clicked_radio_button(self._get_active_radio_text())
        
        tree_item_text = get_clicked_item(radio_btn, 'tree_item')
        if not tree_item_text:
            return
        
        if isinstance(tree_item_text, list):
            tree_item_text, parent_item_text = tree_item_text
            
            parent_item = find_top_level_item_by_text(self.tree_browser, parent_item_text)
            item, column = self._click_tree_item_by_text(self.tree_browser, tree_item_text, parent_item=parent_item)
            
        else:
            item, column = self._click_tree_item_by_text(self.tree_browser, tree_item_text)
        
        self.on_tree_item_clicked(item, column)
        
    def on_tree_item_clicked(self, item, column):
        
        self._add_tree_item_to_current_dir(item, column)
        self.populate_list_01(item, column)
        self.list_01.set_data(self.current_directory)
        
        if item.parent():
            set_clicked_item(self._get_active_radio_text(), 'tree_item', f'{item.text(column)}')
            
            if '05_shot' in self.current_directory:
                item_parent = item.parent()
                set_clicked_item(self._get_active_radio_text(), 'tree_item', f'{item.text(column)}', shot=True, item_parent=f'{item_parent.text(column)}')
        
    def on_list_item_clicked(self, item):

        # Gérer le clic sur un élément de la liste et éviter les erreurs NoneType
        if item is None:
            logger.warning("No item selected. Cannot update data.")
            return

        dico = {
            self.list_01: self.populate_list_02,
            self.list_02: self.populate_list_03,
            self.list_03: self.populate_list_04
        }
        
        self._add_dir(item)
        self.show_files()
        dico[item.listWidget()](None) # example : self.populate_list_02(None)

        logger.info(f'Item data : {item.data(32)}')
        logger.info(f'List data : {item.listWidget().data}')
        
        dico = {
            self.list_01: self.list_02,
            self.list_02: self.list_03
        }
        
        #
        if item.listWidget() == self.list_01:
            self.list_02.data = item.data(32)
            
        elif item.listWidget() == self.list_02:
            self.list_03.data = item.data(32)
            
        else:
            pass
    
    # CONNECTIONS
    def _open_file(self, item):

        if item:
            file_path = item.data(32)  # Récupérer le chemin du fichier stocké dans l'item
            if file_path:
                # Ouvre le fichier avec le bouton Maya par exemple
                self.open_file_widget.open_maya_file()  # Appeler la méthode de l'OpenFileWidget
            else:
                print("No file path available for the selected item.")
        else:
            print("No item selected.")

    def _fill_tree_items(self):
        self.tree_browser.clear()
        self.list_01.clear()
        self.list_02.clear()
        self.list_03.clear()
        self.list_04.clear()
        self.browser_file_table.setRowCount(0)

        # check if the path exist
        if not os.path.exists(self.current_directory):
            logger.error(f"The path '{self.current_directory}' does not exist.")
            return

        print(os.listdir(self.current_directory))
        for directory in os.listdir(self.current_directory):

            directory_path = os.path.join(self.current_directory, directory)
            if not os.path.isdir(os.path.join(self.current_directory, directory)): 
                #print(os.path.join(self.current_directory, directory)+" is not a dir")#ATTENTION iici j'ai remplacé directory par os.path.join(self.current_directory, directory)
                logger.warning(f'{os.path.join(self.current_directory, directory)} is not a directory.')
                continue

            root = QTreeWidgetItem(self.tree_browser)
            self.set_qtree_item_icon(root, directory)
            root.setText(0, directory)
            root.setFlags(root.flags() & ~Qt.ItemIsSelectable)
            
            for sub_directory in os.listdir(directory_path):
                #print("sub  "+sub_directory)
                sub_directory_path = os.path.join(directory_path, sub_directory)
                #if not os.path.isdir(sub_directory_path): return #ATTENTION ici j'ai du caché une ligne, car sinon le if return car il trouve des fichier dans le .data
                item = QTreeWidgetItem(root)
                item.setText(0, sub_directory)
                item.setSizeHint(0, QSize(40, 40))
                self.set_qtree_item_icon(item, sub_directory)

    def populate_list_01(self, tree_item, column):
        if self.tree_browser.indexOfTopLevelItem(tree_item) != -1:
            self.list_01.clear()
            return

        self.list_01.clear()
        self.list_02.clear()
        self.list_03.clear()
        self.list_04.clear()

        for directory in os.listdir(self.current_directory):
            if not os.path.isdir(os.path.join(self.current_directory, directory)): continue

            #item = QListWidgetItem(directory)
            item = CustomListWidgetItem(directory, self.list_01)
            self._add_icon(item, directory)
            item.setData(32, os.path.join(self.current_directory, directory))
            #self.list_01.addItem(item)

    def populate_list_02(self, parent_directory: str):
        
        self.list_02.clear()
        self.list_03.clear()
        self.list_04.clear()
        
        for directory in os.listdir(self.current_directory):
            if not os.path.isdir(os.path.join(self.current_directory, directory)): continue
            
            item = QListWidgetItem(directory)
            self._add_icon(item, directory)
            item.setData(32, os.path.join(self.current_directory, directory))
            self.list_02.addItem(item)
        
        self._select_item_from_text(self.list_02, 'scenes') #
        
    def populate_list_03(self, parent_directory: str):
        
        self.list_03.clear()
        self.list_04.clear()
        
        for directory in os.listdir(self.current_directory):
            if not os.path.isdir(os.path.join(self.current_directory, directory)): continue
            
            item = QListWidgetItem(directory)
            self._add_icon(item, directory)
            item.setData(32, os.path.join(self.current_directory, directory))
            self.list_03.addItem(item)
        
    
    def populate_list_04(self, parent_directory: str):
        
        self.list_04.clear()
        self.populate_list_04_executed = False
        
        for directory in os.listdir(self.current_directory):
            if not os.path.isdir(os.path.join(self.current_directory, directory)): return
            
            item = QListWidgetItem(directory)
            self._add_icon(item, directory)
            item.setData(32, os.path.join(self.current_directory, directory))
            self.list_04.addItem(item)
        
        #self.list_04.itemClicked.connect(self._add_dir)
                
    # UPDATE CURRENT DIRECTORY
    def _add_base_folder_to_dir(self):
        self.current_directory = self.PROJECT_PATH # je remets le DIR à la racine 
        self.current_directory = os.path.join(self.PROJECT_PATH, self._get_active_radio())
        self.status_bar.update(self.current_directory) # j'ajoute le dir 
                 
    def _add_tree_item_to_current_dir(self, item, column):
        
        text_to_add = f'{item.text(column)}'.lower()
        
        self.current_directory = os.path.join(self.PROJECT_PATH, self._get_active_radio())
        
        if not item.parent():
            self.current_directory = os.path.join(self.current_directory, text_to_add)
            
        else:
            self.current_directory = os.path.join(self.current_directory, item.parent().text(0), text_to_add)
             
        self.status_bar.update(self.current_directory)
        
        self.browser_file_table.setRowCount(0)
        self.show_files()
    
    def _add_dir(self, item):
        
        DIR = item.text().lower()
        LIST = item.listWidget()
        
        for i in range(LIST.count()):
            ITEM = LIST.item(i).text().lower()
            if '\\cageot' in self.current_directory:
                if f'\\{ITEM}' in self.current_directory:
                    self.current_directory = clean_directory(self.current_directory, ITEM)
                    break
                
            else:
                if ITEM in self.current_directory:
                    self.current_directory = clean_directory(self.current_directory, ITEM)
                    break
        
        self.current_directory = os.path.join(self.current_directory, DIR)
        self.status_bar.update(self.current_directory)

    # DIALOGS

    def open_comment_dialog(self):
        file_path = self.status_bar.get_text()
        file_comment = get_file_data(file_path)['comment']
        logger.info(f'Get file infos : {file_path}')

        self.context_menu.close()
        dialog = TextEntryDialog(self, text=file_comment, title='Edit comment')

        if dialog.exec() == QDialog.Accepted:
            entered_text = dialog.get_entered_text()
            logger.info(f'Texte saisi : {entered_text}')

            update_file_data(file_path, entered_text)

            # Vérifier quel onglet est actif et mettre à jour le commentaire
            active_tab = self._get_active_tab_text()
            if active_tab == 'Browser':
                selected_items = self.browser_file_table.selectedItems()
                table = self.browser_file_table
            elif active_tab == 'Sequence Filter':
                selected_items = self.filtered_file_table.selectedItems()
                table = self.filtered_file_table
            elif active_tab == 'Search File':
                selected_items = self.search_file_table.selectedItems()
                table = self.search_file_table
            else:  # Assume 'Recent'
                selected_items = self.recent_file_table.selectedItems()
                table = self.recent_file_table

            # Mise à jour du commentaire dans la bonne colonne
            if len(selected_items) > 3:  # S'assurer qu'il y a suffisamment d'éléments sélectionnés
                comment_item = selected_items[2]  # Utiliser l'indice correct pour la colonne "Comment"
                comment_item.setText(get_file_data(file_path)['comment'])
                logger.info(f"Comment updated for file: {file_path}")
            else:
                logger.warning("No item selected or not enough items selected to update the comment.")

    def _open_create_soft_project_dialog(self):
        
        directory = self.list_01.data
        logger.info(f'directory arg : {directory}')
        logger.info('Open option dialog.')
        project_dialog = CreateSoftProjectDialog(self, directory = directory)
        project_dialog.exec()
        
        self.on_radio_button_clicked()
        
    def _open_create_folder_dialog(self, list_widget):
        
        dialog = TextEntryDialog(self, text = '', title = 'Enter folder name')
        
        if dialog.exec() == QDialog.Accepted:
            directory = list_widget.data
            logger.info(f'DIRECTORY : {directory}')
            folder_name = dialog.get_entered_text()
            logger.info(f'Texte saisi : {folder_name}')
            
            os.mkdir(os.path.join(directory, folder_name))
            self.on_radio_button_clicked()
        
    def _open_create_folder_dialog_01(self):
        self._open_create_folder_dialog(self.list_01)
            
    def _open_create_folder_dialog_02(self):
        self._open_create_folder_dialog(self.list_02)
        
    def _open_create_folder_dialog_03(self):
        self._open_create_folder_dialog(self.list_03)
            
    def open_file_dialog(self):
        """
        """
        
        if self._get_active_tab_text() == 'Browser':
            dir = self.current_directory
        else:
            dir = self.status_bar.get_text()
            
        open_explorer(os.path.dirname(dir))

    # UTILS
    def _get_active_radio(self):

        for radio_button in self.checkable_buttons:
            if radio_button.isChecked():
                return radio_button.property('directory')

    def increment_file(self):
        increment_file_external(self.current_directory)
        self.current_directory = os.path.dirname(self.current_directory)
        self.show_files()
            
    def delete_file(self): # OBSOLETE
        os.remove(self.current_directory)
        
        selected_rows = self.browser_file_table.selectionModel().selectedRows()
        for row in selected_rows:
            self.browser_file_table.removeRow(row.row())
            
        self._on_file_item_clicked()
            
        # ATTENTION LA STATUS BAR N'est pas update

    def _add_icon(self, widget, text="", bw: bool = True):
        '''
        '''
        
        bw_dict = {True: '_bw', False: ''}
        
        icon_file_path = os.path.join(ICON_PATH, f'{text.lower()}{bw_dict[bw]}_icon.ico')
        if not os.path.exists(icon_file_path):
            return
        
        icon = QIcon(icon_file_path)
        widget.setIcon(icon)
         
    def set_qtree_item_icon(self, item: QTreeWidgetItem, item_name: str):
        '''ajoute un icon au Qtree item si il  a une image au bon nom dans le .pipezer_data
        '''
        
        item_name_file=f"{item_name}.png"
        icons = os.listdir(ICONS_PATH)
        
        if item_name_file in icons:
            icon_file_path: str = os.path.join(ICONS_PATH, item_name_file)
            if not os.path.exists(icon_file_path):
                icon_file_path = os.path.join(ICONS_PATH, item_name_file.capitalize())
            
            icon=QIcon(icon_file_path)
            item.setIcon(0,icon)

    def show_files(self):
        logger.info('Show files - - - - - - - - - - - - - - - - - - - - - - - -')
        self.browser_file_table.update_file_items(self.current_directory)
        logger.info('End show files - - - - - - - - - - - - - - - - - - - - - - - -')

    def _add_file_to_table(self, filename: str):
        
        filepath = os.path.join(self.current_directory, filename)
        
        self.browser_file_table.add_item(filepath)
        
    def show_context_menu(self, pos):
        """
        """
        
        self._on_file_item_clicked(self.browser_file_table.itemAt(pos))
        
        global_pos = self.browser_file_table.mapToGlobal(pos)
        self.context_menu.exec_(global_pos)
        
    def show_context_menu_recent(self, pos):
        """
        """
        
        self._on_file_item_clicked(self.recent_file_table.itemAt(pos))
        
        global_pos = self.recent_file_table.mapToGlobal(pos)
        self.context_menu.exec_(global_pos)

    def show_context_menu_filtered(self, pos):
        """Affiche le menu contextuel pour la table de filtres de séquence."""
        self._on_file_item_clicked(self.filtered_file_table.itemAt(pos))

        global_pos = self.filtered_file_table.mapToGlobal(pos)
        self.context_menu.exec(global_pos)

    def _on_file_image_cliked(self, event):
        '''
        '''
        print('file image clicked')
    
    def _on_file_item_clicked(self, item: QTableWidgetItem):
        
        logger.info('file item clicked')
        
        file_path = item.data(32)

        if  self._get_active_tab_text() == 'Browser':
            self.current_directory = file_path
            self.status_bar.update(self.current_directory)
        else:
            self.status_bar.update(file_path)


        
    def _select_item_from_text(self, parent_widget: QListWidget, text = ""):
        
        dico = {
            self.list_01: self.populate_list_02,
            self.list_02: self.populate_list_03,
            self.list_03: self.populate_list_04,
        }
        
        for i in range(parent_widget.count()):
            
            item = parent_widget.item(i)
            
            if item.text() == text:
                
                parent_widget.setItemSelected(item, True)
                self._add_dir(item)
                dico[parent_widget](item)
                self.on_list_item_clicked(item) ########### attention à vérifier !!
                break

    def update_sequences(self):
        """
        Met à jour la liste des séquences pour le personnage sélectionné.
        """
        # Réinitialiser la liste des séquences
        self.sequence_list_widget.clear()

        # Vérifie que le personnage est bien sélectionné
        if self.character_list_widget.currentItem() is None:
            print("No character selected. Cannot filter sequences.")
            return

        character_name = self.character_list_widget.currentItem().text()

        # Récupérer toutes les séquences disponibles pour ce personnage
        sequences = self.get_sequences_for_character(character_name)
        if sequences:
            self.sequence_list_widget.addItems(sequences)
        else:
            print("No sequences found for the selected character.")

    def update_shots(self):
        """
        Met à jour la liste des shots pour la séquence sélectionnée.
        """
        # Réinitialiser la liste des shots
        self.shot_list_widget.clear()

        # Vérifie que la séquence est bien sélectionnée
        if self.sequence_list_widget.currentItem() is None:
            print("No sequence selected. Cannot filter shots.")
            return

        sequence_name = self.sequence_list_widget.currentItem().text()

        # Vérifie que le personnage est bien sélectionné
        if self.character_list_widget.currentItem() is None:
            print("No character selected. Cannot filter shots.")
            return

        character_name = self.character_list_widget.currentItem().text()

        # Récupérer tous les shots disponibles pour ce personnage et cette séquence
        shots = self.get_shots_for_sequence(sequence_name, character_name)
        if shots:
            self.shot_list_widget.addItems(shots)
        else:
            print("No shots found for the selected character and sequence.")

    def update_files(self, item=None):
        """
        Met à jour la liste des fichiers pour le personnage, la séquence ou le shot sélectionné dans l'onglet "Sequence Filter".
        """
        # Réinitialiser le tableau des fichiers
        self.filtered_file_table.setRowCount(0)

        # Vérifie que le personnage est bien sélectionné
        if self.character_list_widget.currentItem() is None:
            print("No character selected. Cannot filter files.")
            return

        character_name = self.character_list_widget.currentItem().text()  # Récupère le nom du personnage sélectionné

        # Si seulement un personnage est sélectionné (pas de séquence ni de shot)
        if self.sequence_list_widget.currentItem() is None and self.shot_list_widget.currentItem() is None:
            files = self.get_files_for_character(character_name)

        # Si une séquence est sélectionnée mais aucun shot n'est sélectionné
        elif self.sequence_list_widget.currentItem() is not None and self.shot_list_widget.currentItem() is None:
            sequence_name = self.sequence_list_widget.currentItem().text()  # Nom de la séquence
            files = self.get_files_for_sequence(sequence_name, character_name)

        # Si un shot est sélectionné
        elif self.shot_list_widget.currentItem() is not None:
            shot_name = self.shot_list_widget.currentItem().text()
            files = self.get_files_for_shot(shot_name, character_name)

        # Si aucun personnage n'est sélectionné, mais une séquence l'est
        elif self.character_list_widget.currentItem() is None and self.sequence_list_widget.currentItem() is not None:
            sequence_name = self.sequence_list_widget.currentItem().text()
            files = self.get_files_for_all_characters_in_sequence(sequence_name)

        # Aucun fichier trouvé ou pas de sélection valide
        else:
            print("Invalid selection or no files found.")
            return

        # Vérifie s'il y a des fichiers correspondants
        if not files:
            print("No files found for the selected character and filters.")
            return  # Ne rien faire s'il n'y a pas de fichiers correspondants

        # Ajouter les fichiers trouvés au tableau
        for file in files:
            self.filtered_file_table.add_item(file)

    def get_files_for_all_characters_in_sequence(self, sequence_name):
        """
        Retourne la liste de tous les fichiers pour tous les personnages dans une séquence donnée.
        """
        files = []
        sequence_directory = os.path.join(self.PROJECT_PATH, '05_shot', sequence_name)

        for root, dirs, files_list in os.walk(sequence_directory):
            for file in files_list:
                file_path = os.path.join(root, file)
                files.append(file_path)

        return files

    def get_files_for_character(self, character_name):
        """
        Retourne la liste de tous les fichiers associés à un personnage donné.
        """
        files = []
        shot_directory = os.path.join(self.PROJECT_PATH, '05_shot')

        for root, dirs, files_list in os.walk(shot_directory):
            for file in files_list:
                # Vérifie que le fichier correspond au personnage
                if character_name in file:
                    file_path = os.path.join(root, file)
                    files.append(file_path)

        return files

    def get_files_for_sequence(self, sequence_name, character_name):
        """
        Retourne la liste des fichiers associés à une séquence spécifique et un personnage donné.
        """
        files = []
        sequence_directory = os.path.join(self.PROJECT_PATH, '05_shot',
                                          sequence_name)  # Chemin du répertoire de la séquence

        for root, dirs, files_list in os.walk(sequence_directory):
            for file in files_list:
                # Vérifie que le fichier correspond au personnage
                if character_name in file:
                    file_path = os.path.join(root, file)
                    files.append(file_path)

        return files

    def get_sequences_for_character(self, character_name):
        """
        Retourne une liste de séquences associées à un personnage spécifique.
        """
        sequences = set()
        shot_directory = os.path.join(self.PROJECT_PATH, '05_shot')

        for root, dirs, files_list in os.walk(shot_directory):
            for file in files_list:
                # Vérifie que le fichier correspond au personnage
                if character_name in file:
                    # Extraire le nom de la séquence à partir du chemin
                    match = re.search(r'(seq\d+)', root)
                    if match:
                        sequences.add(match.group(1))

        return sorted(sequences)

    def get_shots_for_sequence(self, sequence_name, character_name):
        """
        Retourne une liste de shots associés à une séquence et un personnage spécifiques.
        """
        shots = set()
        sequence_directory = os.path.join(self.PROJECT_PATH, '05_shot', sequence_name)

        for root, dirs, files_list in os.walk(sequence_directory):
            for file in files_list:
                # Vérifie que le fichier correspond au personnage
                if character_name in file:
                    # Extraire le nom du shot à partir du chemin
                    match = re.search(r'(sh\d+)', root)
                    if match:
                        shots.add(match.group(1))

        return sorted(shots)

    def get_files_for_shot(self, shot_name, character_name):
        """
        Retourne la liste des fichiers associés à un shot et un personnage spécifique.
        """
        files = []
        shot_directory = os.path.join(self.PROJECT_PATH, '05_shot')

        # Lire les données du fichier file_data.json
        file_data_path = os.path.join(self.PROJECT_PATH, '.pipezer_data', 'file_data.json')

        file_data = {}  # Par défaut, utiliser un dictionnaire vide
        if os.path.exists(file_data_path):
            try:
                with open(file_data_path, 'r') as file:
                    file_data = json.load(file)  # Charge les données JSON
            except json.JSONDecodeError as e:
                print(f"Erreur lors de la lecture du fichier JSON: {e}")
        else:
            print(f"Le fichier '{file_data_path}' n'existe pas.")

        for root, dirs, files_list in os.walk(shot_directory):
            if shot_name not in root:
                continue  # Skip directories that do not match the shot

            for file in files_list:
                # Vérifie que le fichier correspond à la fois au shot et au personnage
                if shot_name in file and character_name in file:
                    file_path = os.path.join(root, file)

                    # Vérifie si des informations supplémentaires sont nécessaires dans file_data.json
                    if file_data.get(file_path):
                        print(f"File data found for {file_path}: {file_data[file_path]}")
                        # Logique supplémentaire si nécessaire...

                    files.append(file_path)

        return files

import os
import shutil
from PySide2.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QPushButton, QLabel, QLineEdit, QCheckBox, QGridLayout
import json
import os

from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT
NOTIF_FILE_PATH = os.path.join(CURRENT_PROJECT, '.pipezer_data', 'notifs.json')
from datetime import datetime

def add_notification(username, action, file_name):
    """
    Ajoute une notification dans le fichier JSON.
    """
    notification = {
        "username": username,
        "action": action,
        "file": file_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formatage de la date et heure

    }

    try:
        if os.path.exists(NOTIF_FILE_PATH):
            with open(NOTIF_FILE_PATH, 'r') as notif_file:
                data = json.load(notif_file)
                if not isinstance(data, list):
                    data = []
        else:
            data = []

        data.append(notification)

        with open(NOTIF_FILE_PATH, 'w') as notif_file:
            json.dump(data, notif_file, indent=4)

        print(f"Notification ajoutée : {notification}")

    except Exception as e:
        print(f"Erreur lors de l'ajout d'une notification : {e}")

def get_username():
    """
    Récupère le nom d'utilisateur depuis user.json ou utilise le nom par défaut.
    """
    user_home_dir = os.path.expanduser("~")
    pipezer_dir = os.path.join(user_home_dir, '.pipezer')
    user_file_path = os.path.join(pipezer_dir, 'user.json')

    try:
        if os.path.exists(user_file_path):
            with open(user_file_path, 'r') as user_file:
                data = json.load(user_file)
                username = data.get("username")
                if username:
                    return username
    except Exception:
        pass

    return os.getenv("USERNAME", "unknown_user")


# Constants and paths used in asset creation
from Packages.utils.constants.constants_old import ASSET_DIR, PREFIX

class CreateAssetDialogStandalone(QDialog):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Create Asset')
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.show()

    def create_widgets(self):
        self.asset_name_label = QLabel('Asset name :')
        self.asset_name_line_edit = QLineEdit('')

        self.asset_type_label = QLabel('Asset type :')
        self.character_radio_btn = QRadioButton('01_character')
        self.prop_radio_btn = QRadioButton('02_prop')
        self.item_radio_btn = QRadioButton('03_item')
        self.enviro_radio_btn = QRadioButton('04_enviro')
        self.module_radio_btn = QRadioButton('05_module')

        self.radio_list = (
            self.character_radio_btn,
            self.prop_radio_btn,
            self.item_radio_btn,
            self.enviro_radio_btn,
            self.module_radio_btn
        )

        self.subfolders_label = QLabel('Subfolders :')
        self.data_checkbox = QCheckBox('data')
        self.images_checkbox = QCheckBox('images')
        self.scenes_checkbox = QCheckBox('scenes')
        self.out_checkbox = QCheckBox('out')
        self.sourceimages_checkbox = QCheckBox('sourceimages')
        self.scripts_checkbox = QCheckBox('scripts')
        self.sound_checkbox = QCheckBox('sound')
        self.clip_checkbox = QCheckBox('clip')
        self.movie_checkbox = QCheckBox('movie')

        self.data_checkbox.setChecked(True)
        self.scenes_checkbox.setChecked(True)

        self.subfolders_list = (
            self.data_checkbox,
            self.images_checkbox,
            self.scenes_checkbox,
            self.out_checkbox,
            self.sourceimages_checkbox,
            self.scripts_checkbox,
            self.sound_checkbox,
            self.clip_checkbox,
            self.movie_checkbox
        )

        self.department_label = QLabel('Departments :')
        self.geo_cb = QCheckBox('geo')
        self.ldv_cb = QCheckBox('ldv')
        self.rig_cb = QCheckBox('rig')

        self.department_list = (
            self.geo_cb,
            self.ldv_cb,
            self.rig_cb
        )

        self.geo_cb.setChecked(True)
        self.ldv_cb.setChecked(True)

        self.create_groups_button = QCheckBox('Create groups')
        self.run_button = QPushButton('Create Asset')
        self.run_button.setFixedSize(200, 60)

    def create_layout(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)

        SEP = '------------------------'

        self.grid_layout.addWidget(self.asset_name_label, 0, 0)
        self.grid_layout.addWidget(self.asset_name_line_edit, 0, 1)

        self.grid_layout.addWidget(self.asset_type_label, 1, 0)
        self.grid_layout.addWidget(QLabel(SEP), 1, 1)
        self.grid_layout.addWidget(self.character_radio_btn, 2, 1)
        self.grid_layout.addWidget(self.prop_radio_btn, 3, 1)
        self.grid_layout.addWidget(self.item_radio_btn, 4, 1)
        self.grid_layout.addWidget(self.enviro_radio_btn, 5, 1)
        self.grid_layout.addWidget(self.module_radio_btn, 6, 1)

        self.grid_layout.addWidget(self.department_label, 7, 0)
        self.grid_layout.addWidget(QLabel(SEP), 7, 1)
        self.grid_layout.addWidget(self.geo_cb, 8, 1)
        self.grid_layout.addWidget(self.ldv_cb, 9, 1)
        self.grid_layout.addWidget(self.rig_cb, 10, 1)

        self.grid_layout.addWidget(self.subfolders_label, 11, 0)
        self.grid_layout.addWidget(QLabel(SEP), 11, 1)
        self.grid_layout.addWidget(self.data_checkbox, 12, 1)
        self.grid_layout.addWidget(self.images_checkbox, 13, 1)
        self.grid_layout.addWidget(self.scenes_checkbox, 14, 1)
        self.grid_layout.addWidget(self.out_checkbox, 15, 1)
        self.grid_layout.addWidget(self.sourceimages_checkbox, 16, 1)
        self.grid_layout.addWidget(self.scripts_checkbox, 17, 1)
        self.grid_layout.addWidget(self.sound_checkbox, 18, 1)
        self.grid_layout.addWidget(self.clip_checkbox, 19, 1)
        self.grid_layout.addWidget(self.movie_checkbox, 20, 1)

        self.grid_layout.addWidget(self.create_groups_button, 21, 0)

        self.main_layout.addWidget(self.grid_widget)
        self.main_layout.addWidget(self.run_button)

    def create_connections(self):
        self.run_button.clicked.connect(self.create_asset)

    def get_asset_name(self) -> str:
        return self.asset_name_line_edit.text()

    def get_asset_type(self) -> str:
        for radio_btn in self.radio_list:
            if radio_btn.isChecked():
                return radio_btn.text().lower()

    def get_departments(self) -> list:
        return [dep_cb.text().lower() for dep_cb in self.department_list if dep_cb.isChecked()]

    def get_subfolders(self) -> list:
        return [sub_cb.text().lower() for sub_cb in self.subfolders_list if sub_cb.isChecked()]

    import shutil  # Import nécessaire pour la copie de fichiers

    import shutil  # Import pour la copie de fichiers

    def create_asset(self):
        # Code existant pour récupérer les informations d'asset
        asset_name = self.get_asset_name()
        asset_type = self.get_asset_type()
        departments = self.get_departments()
        subfolders = self.get_subfolders()

        # Vérifications de validation (inchangées)
        if not asset_name:
            QMessageBox.warning(self, 'Error', 'Please enter asset name.')
            return

        if not asset_type:
            QMessageBox.warning(self, 'Error', 'Please select asset type.')
            return

        if not departments:
            QMessageBox.warning(self, 'Error', 'Please select departments.')
            return

        if not subfolders:
            QMessageBox.warning(self, 'Error', 'Please select subfolders.')
            return

        # Création des dossiers requis
        asset_type_directory = os.path.join(ASSET_DIR, asset_type)
        asset_directory = os.path.join(asset_type_directory, asset_name)

        maya_directory = os.path.join(asset_directory, 'maya')
        houdini_directory = os.path.join(asset_directory, 'houdini')
        texture_directory = os.path.join(asset_directory, 'texture')
        substance_directory = os.path.join(asset_directory, 'substance')

        for directory in [maya_directory, houdini_directory, texture_directory, substance_directory]:
            os.makedirs(directory, exist_ok=True)

        # Création des sous-dossiers
        for subfolder in subfolders:
            subfolder_path = os.path.join(maya_directory, subfolder)
            os.makedirs(subfolder_path, exist_ok=True)
            if subfolder == 'scenes':
                for department in departments:
                    if department == 'ldv':
                        ldv_directory = os.path.join(houdini_directory, 'ldv')
                        os.makedirs(ldv_directory, exist_ok=True)
                    else:
                        os.makedirs(os.path.join(subfolder_path, department), exist_ok=True)

        # Dictionnaire de conversion de l'asset_type en préfixe
        asset_type_dict = {
            '01_character': 'chr',
            '02_prop': 'prp',
            '03_item': 'itm',
            '04_enviro': 'env',
            '05_module': 'mod'
        }

        # Conversion du nom de type
        asset_type_prefix = asset_type_dict.get(asset_type, "unknown")

        # Gestion de la copie du fichier LookDev dans le dossier "ldv"
        if 'ldv' in departments:
            template_path_houdini = r"\\Storage01\3D4\nordicPhone\02_ressource\Template_scenes\Houdini\NOR_ldv_template.hipnc"
            target_filename_houdini = f"NOR_{asset_type_prefix}_{asset_name}_ldv_E_001.hipnc"
            target_path_houdini = os.path.join(ldv_directory, target_filename_houdini)

            try:
                shutil.copy(template_path_houdini, target_path_houdini)
                print(f"Fichier Houdini copié avec succès : {target_path_houdini}")
            except IOError as e:
                QMessageBox.critical(self, "Erreur de copie", f"Erreur lors de la copie du fichier Houdini : {e}")

        # Gestion de la copie du fichier Maya dans le dossier "geo"
        template_path_maya = r"\\Storage01\3D4\nordicPhone\02_ressource\Template_scenes\Maya\NOR_maya_scene.ma"
        geo_directory = os.path.join(maya_directory, 'scenes', 'geo')
        os.makedirs(geo_directory, exist_ok=True)

        target_filename_maya_geo = f"NOR_{asset_type_prefix}_{asset_name}_geo_E_001.ma"
        target_path_maya_geo = os.path.join(geo_directory, target_filename_maya_geo)

        try:
            shutil.copy(template_path_maya, target_path_maya_geo)
            print(f"Fichier Maya (geo) copié avec succès : {target_path_maya_geo}")
        except IOError as e:
            QMessageBox.critical(self, "Erreur de copie", f"Erreur lors de la copie du fichier Maya (geo) : {e}")

        # Gestion de la copie du fichier Maya dans le dossier "rig" si la case rig est cochée
        if 'rig' in departments:
            rig_directory = os.path.join(maya_directory, 'scenes', 'rig')
            os.makedirs(rig_directory, exist_ok=True)

            target_filename_maya_rig = f"NOR_{asset_type_prefix}_{asset_name}_rig_E_001.ma"
            target_path_maya_rig = os.path.join(rig_directory, target_filename_maya_rig)

            try:
                shutil.copy(template_path_maya, target_path_maya_rig)
                print(f"Fichier Maya (rig) copié avec succès : {target_path_maya_rig}")
            except IOError as e:
                QMessageBox.critical(self, "Erreur de copie", f"Erreur lors de la copie du fichier Maya (rig) : {e}")

        # Ajouter une notification
        username = get_username()
        add_notification(username, "create_asset", asset_name)

        # Fermer la fenêtre après la création de l'asset
        QMessageBox.information(self, "Succès", f"L'Asset '{asset_name}' a été créé avec succès.")
        self.close()

from PySide2.QtCore import QThread, Signal

class FileSearchThread(QThread):
    files_found = Signal(list)  # Signal émis lorsqu'un fichier est trouvé

    def __init__(self, search_text, project_folder, max_results=100):
        super().__init__()
        self.search_text = search_text.lower()
        self.project_folder = project_folder
        self.max_results = max_results

    def run(self):
        matching_files = []
        for root, dirs, files in os.walk(self.project_folder):
            for file in files:
                if self.search_text in file.lower():
                    file_path = os.path.join(root, file)
                    matching_files.append(file_path)

                    # Émettre les résultats trouvés au fur et à mesure
                    if len(matching_files) % 10 == 0:
                        self.files_found.emit(matching_files)
                        matching_files.clear()

                if len(matching_files) >= self.max_results:
                    break
            if len(matching_files) >= self.max_results:
                break

        # Émettre les fichiers restants après la boucle
        if matching_files:
            self.files_found.emit(matching_files)


