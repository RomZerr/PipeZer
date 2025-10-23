"""
Helper pour migrer le contenu existant vers la nouvelle interface moderne
"""

import os
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QMessageBox
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from Packages.utils.explorer_utils import open_in_explorer

from Packages.ui.base_main_window import BaseMainWindow, CreateAssetDialogStandalone
from Packages.ui.widgets import OpenFileWidget
from Packages.ui.dialogs.create_shot_dialog import CreateShotDialog


class ContentMigrator:
    """
    Classe helper pour migrer le contenu existant
    """
    
    @staticmethod
    def create_browser_content(parent, current_directory):
        """Crée le contenu du browser avec navigation complète comme l'ancienne app"""
        from PySide2.QtWidgets import QButtonGroup, QHBoxLayout, QWidget as QWidgetBase, QSplitter, QVBoxLayout as QVBoxLayoutBase, QAbstractItemView
        from PySide2.QtCore import Qt
        from Packages.utils.translation import translation_manager
        from Packages.ui.widgets.custom_table_widget import CustomTableWidget
        from Packages.ui.widgets.custom_list_widget import CustomListWidget
        from Packages.ui.widgets.custom_tree_widget import CustomTreeWidget
        from Packages.ui.widgets.filtered_list_widget import FilteredListWidget
        from Packages.ui.widgets import StatusBar
        from Packages.utils.funcs import get_current_value
        from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Obtenir le chemin du projet courant
        project_path = get_current_value(json_file=CURRENT_PROJECT_JSON_PATH, key='current_project')
        if not project_path:
            project_path = current_directory
        
        # Créer les boutons de raccourcis (comme dans l'ancien système)
        # Les boutons de raccourcis ont été supprimés car ils sont maintenant dans la sidebar
        
        # === NOUVELLE DISPOSITION : Blocs en haut, fichiers en bas ===
        
        # Créer le splitter principal vertical (navigation en haut, fichiers en bas)
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setHandleWidth(1)  # Réduire la largeur de la poignée du splitter
        
        # === PANEL HAUT : Navigation horizontale ===
        navigation_widget = QWidget()
        navigation_widget.setStyleSheet("background-color: transparent;")  # Pas de fond supplémentaire
        navigation_layout = QHBoxLayout(navigation_widget)
        navigation_layout.setContentsMargins(10, 10, 10, 10)
        navigation_layout.setSpacing(5)
        
        # Créer les listes de navigation (sans limite de hauteur pour prendre tout l'espace)
        list_01 = CustomListWidget(max_height=None)
        list_02 = CustomListWidget(max_height=None)
        list_03 = CustomListWidget(max_height=None)
        list_04 = CustomListWidget(max_height=None)
        list_05 = CustomListWidget(max_height=None)
        list_06 = CustomListWidget(max_height=None)
        list_07 = CustomListWidget(max_height=None)
        
        # Ajouter les widgets de navigation au panel haut
        navigation_layout.addWidget(list_01)
        navigation_layout.addWidget(list_02)
        navigation_layout.addWidget(list_03)
        navigation_layout.addWidget(list_04)
        navigation_layout.addWidget(list_05)
        navigation_layout.addWidget(list_06)
        navigation_layout.addWidget(list_07)
        
        # Masquer initialement tous les blocs sauf le premier
        list_02.hide()
        list_03.hide()
        list_04.hide()
        list_05.hide()
        list_06.hide()
        list_07.hide()
        
        # === PANEL BAS : Affichage des fichiers avec fond sombre ===
        files_widget = QWidget()
        files_widget.setObjectName("files_widget")
        files_layout = QVBoxLayoutBase(files_widget)
        files_layout.setContentsMargins(0, 0, 0, 0)
        files_layout.setSpacing(0)
        
        # Créer le tableau de fichiers (comme dans l'ancien système)
        browser_file_table = CustomTableWidget()
        browser_file_table.set_table(['File Name', 'Image', 'Version', 'Comment', 'Infos'],
                                    [180, 100, 100, 150, 100])
        
        # Connecter les signaux du menu contextuel
        browser_file_table.file_renamed.connect(lambda old_path, new_path: on_file_renamed(old_path, new_path))
        browser_file_table.file_duplicated.connect(lambda old_path, new_path: on_file_duplicated(old_path, new_path))
        browser_file_table.open_in_explorer.connect(lambda file_path: on_open_in_explorer(file_path))
        
        # Créer le widget OpenFileWidget pour l'ouverture de fichiers (AVANT la fonction de sélection)
        open_file_widget_browser = OpenFileWidget(parent=None, file_directory=current_directory)
        open_file_widget_browser.setObjectName("_open_file_widget_browser")
        
        # Fonctions de gestion des signaux du menu contextuel
        def on_file_renamed(old_path, new_path):
            """Gère le renommage d'un fichier"""
            try:
                # Mettre à jour le tableau si nécessaire
                # Ici on pourrait rafraîchir la liste des fichiers
                print(f"Fichier renommé: {old_path} -> {new_path}")
            except Exception as e:
                QMessageBox.critical(None, "Erreur", f"Erreur lors du renommage: {str(e)}")
        
        def on_file_duplicated(old_path, new_path):
            """Gère la duplication d'un fichier"""
            try:
                print(f"Fichier dupliqué: {old_path} -> {new_path}")
                # Mettre à jour le tableau si nécessaire
                # Ici on pourrait rafraîchir la liste des fichiers
            except Exception as e:
                QMessageBox.critical(None, "Erreur", f"Erreur lors de la duplication: {str(e)}")
        
        def on_open_in_explorer(file_path):
            """Ouvre l'explorateur Windows à l'emplacement du fichier"""
            try:
                open_in_explorer(file_path)
            except Exception as e:
                # Ne pas afficher d'erreur, l'explorateur s'ouvre quand même
                print(f"Erreur lors de l'ouverture de l'explorateur: {str(e)}")
        
        # Gérer la sélection générale de ligne
        def on_item_selection_changed():
            """Gère la sélection des éléments du tableau"""
            try:
                # Récupérer la ligne sélectionnée
                current_row = browser_file_table.currentRow()
                
                if current_row >= 0:
                    # Récupérer l'item de la première colonne (File Name)
                    item = browser_file_table.item(current_row, 0)
                    
                    if item:
                        file_path = item.data(32)
                        
                        if file_path and os.path.isfile(file_path):
                            # Mettre à jour le widget d'ouverture
                            open_file_widget_browser.update_buttons(file_path)
            except Exception as e:
                print(f"Erreur lors de la sélection: {e}")
        
        # Connecter le signal de sélection
        browser_file_table.itemSelectionChanged.connect(on_item_selection_changed)
        
        files_layout.addWidget(browser_file_table)
        
        # Extensions de fichiers autorisées
        ALLOWED_EXTENSIONS = {
            # Maya
            '.ma', '.mb',
            # Houdini
            '.hip', '.hipnc',
            # Images
            '.png', '.jpg', '.jpeg',
            # Nuke
            '.nk', '.nuke', '.nukex',
            # Blender
            '.blend',
            # Substance
            '.sbs', '.sbsar', '.spp',
            # Photoshop
            '.psd', '.psb',
            # ZBrush
            '.zpr', '.ztl',
            # Cinema 4D
            '.c4d',
            # Unreal Engine
            '.uasset', '.umap',
            # Text
            '.txt'
        }
        
        # Fonction pour filtrer les fichiers selon les extensions
        def get_filtered_files(directory):
            """Récupère seulement les fichiers avec les extensions autorisées"""
            try:
                if not os.path.exists(directory):
                    return []
                
                files = []
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        _, ext = os.path.splitext(item)
                        if ext.lower() in ALLOWED_EXTENSIONS:
                            files.append(item)
                
                return sorted(files)
            except Exception as e:
                print(f"Erreur lors du filtrage des fichiers: {e}")
                return []
        
        # Fonction pour mettre à jour le tableau avec les fichiers filtrés
        def update_filtered_file_table(directory):
            """Met à jour le tableau avec seulement les fichiers autorisés"""
            try:
                browser_file_table.setRowCount(0)
                
                filtered_files = get_filtered_files(directory)
                if not filtered_files:
                    return
                
                # Ajouter les fichiers au tableau
                for file_name in filtered_files:
                    file_path = os.path.join(directory, file_name)
                    browser_file_table.add_item(file_path)
                
                # Sélectionner automatiquement le premier fichier
                if browser_file_table.rowCount() > 0:
                    # Définir la cellule courante pour que currentRow() fonctionne
                    browser_file_table.setCurrentCell(0, 0)
                    browser_file_table.selectRow(0)
                    
                    # Mettre à jour le widget d'ouverture avec le premier fichier
                    first_file_path = os.path.join(directory, filtered_files[0])
                    open_file_widget_browser.update_buttons(first_file_path)
                    
                    # Déclencher manuellement le signal de sélection
                    on_item_selection_changed()
                    
            except Exception as e:
                print(f"Erreur lors de la mise à jour du tableau: {e}")
        
        # Ajouter les panneaux au splitter principal
        main_splitter.addWidget(navigation_widget)
        main_splitter.addWidget(files_widget)
        main_splitter.setSizes([150, 600])  # Hauteur relative des panneaux
        
        # Ajouter les widgets au layout principal
        layout.addWidget(main_splitter)
        layout.addWidget(open_file_widget_browser)
        
        # La barre de statut a été supprimée pour que le bouton Open file aille jusqu'en bas
        
        # Stocker les références pour accès ultérieur
        widget.open_file_widget_browser = open_file_widget_browser
        widget.browser_file_table = browser_file_table
        widget.main_splitter = main_splitter
        widget.list_01 = list_01
        widget.list_02 = list_02
        widget.list_03 = list_03
        widget.list_04 = list_04
        widget.list_05 = list_05
        widget.list_06 = list_06
        widget.list_07 = list_07
        widget.current_directory = project_path
        widget.current_base_path = project_path  # Chemin de base pour la navigation
        
        # Fonction pour gérer l'affichage des blocs selon le niveau de navigation
        def show_blocks_up_to_level(level):
            """Affiche les blocs jusqu'au niveau spécifié et masque les autres"""
            lists = [list_01, list_02, list_03, list_04, list_05, list_06, list_07]
            
            for i, list_widget in enumerate(lists, 1):
                if i <= level:
                    list_widget.show()
                else:
                    list_widget.hide()
        
        # Fonction pour remplir une liste avec les dossiers d'un répertoire
        def populate_list_with_directories(list_widget, directory):
            """Remplit une liste avec les dossiers d'un répertoire"""
            try:
                list_widget.clear()
                if not os.path.exists(directory):
                    return
                
                # Obtenir tous les éléments du répertoire
                items = os.listdir(directory)
                directories = []
                
                # Séparer les dossiers des fichiers
                for item in items:
                    item_path = os.path.join(directory, item)
                    if os.path.isdir(item_path):
                        directories.append(item)
                
                # Trier les dossiers par nom
                directories.sort()
                
                # Ajouter les dossiers à la liste
                for directory_name in directories:
                    list_widget.addItem(directory_name)
                    
            except Exception as e:
                print(f"Erreur lors du remplissage de la liste: {e}")
        
        # Fonction pour gérer la sélection dans une liste
        def on_list_selection(list_widget, next_list_widget, level):
            """Gère la sélection dans une liste et met à jour la suivante"""
            try:
                selected_items = list_widget.selectedItems()
                if not selected_items:
                    return
                
                selected_folder = selected_items[0].text()
                
                # Déterminer le chemin de base selon le niveau
                if level == 1:
                    # Niveau 1 : partir du répertoire de base actuel
                    base_path = getattr(widget, 'current_base_path', project_path)
                elif level == 2:
                    # Niveau 2 : partir du dossier sélectionné dans la liste 1
                    if list_01.selectedItems():
                        level1_folder = list_01.selectedItems()[0].text()
                        base_path = os.path.join(getattr(widget, 'current_base_path', project_path), level1_folder)
                    else:
                        return
                elif level == 3:
                    # Niveau 3 : partir du dossier sélectionné dans la liste 2
                    if list_01.selectedItems() and list_02.selectedItems():
                        level1_folder = list_01.selectedItems()[0].text()
                        level2_folder = list_02.selectedItems()[0].text()
                        base_path = os.path.join(getattr(widget, 'current_base_path', project_path), level1_folder, level2_folder)
                    else:
                        return
                elif level == 4:
                    # Niveau 4 : partir du dossier sélectionné dans la liste 3
                    if list_01.selectedItems() and list_02.selectedItems() and list_03.selectedItems():
                        level1_folder = list_01.selectedItems()[0].text()
                        level2_folder = list_02.selectedItems()[0].text()
                        level3_folder = list_03.selectedItems()[0].text()
                        base_path = os.path.join(getattr(widget, 'current_base_path', project_path), level1_folder, level2_folder, level3_folder)
                    else:
                        return
                elif level == 5:
                    # Niveau 5 : partir du dossier sélectionné dans la liste 4
                    if list_01.selectedItems() and list_02.selectedItems() and list_03.selectedItems() and list_04.selectedItems():
                        level1_folder = list_01.selectedItems()[0].text()
                        level2_folder = list_02.selectedItems()[0].text()
                        level3_folder = list_03.selectedItems()[0].text()
                        level4_folder = list_04.selectedItems()[0].text()
                        base_path = os.path.join(getattr(widget, 'current_base_path', project_path), level1_folder, level2_folder, level3_folder, level4_folder)
                    else:
                        return
                elif level == 6:
                    # Niveau 6 : partir du dossier sélectionné dans la liste 5
                    if list_01.selectedItems() and list_02.selectedItems() and list_03.selectedItems() and list_04.selectedItems() and list_05.selectedItems():
                        level1_folder = list_01.selectedItems()[0].text()
                        level2_folder = list_02.selectedItems()[0].text()
                        level3_folder = list_03.selectedItems()[0].text()
                        level4_folder = list_04.selectedItems()[0].text()
                        level5_folder = list_05.selectedItems()[0].text()
                        base_path = os.path.join(getattr(widget, 'current_base_path', project_path), level1_folder, level2_folder, level3_folder, level4_folder, level5_folder)
                    else:
                        return
                elif level == 7:
                    # Niveau 7 : partir du dossier sélectionné dans la liste 6
                    if list_01.selectedItems() and list_02.selectedItems() and list_03.selectedItems() and list_04.selectedItems() and list_05.selectedItems() and list_06.selectedItems():
                        level1_folder = list_01.selectedItems()[0].text()
                        level2_folder = list_02.selectedItems()[0].text()
                        level3_folder = list_03.selectedItems()[0].text()
                        level4_folder = list_04.selectedItems()[0].text()
                        level5_folder = list_05.selectedItems()[0].text()
                        level6_folder = list_06.selectedItems()[0].text()
                        base_path = os.path.join(getattr(widget, 'current_base_path', project_path), level1_folder, level2_folder, level3_folder, level4_folder, level5_folder, level6_folder)
                    else:
                        return
                else:
                    return
                
                # Construire le nouveau chemin
                new_path = os.path.join(base_path, selected_folder)
                # Normaliser le chemin pour éviter les problèmes de séparateurs
                new_path = os.path.normpath(new_path)
                
                # Vérifier si le chemin existe
                if not os.path.exists(new_path):
                    return
                
                # Mettre à jour le répertoire courant
                widget.current_directory = new_path
                
                # La barre de statut a été supprimée - pas besoin de la mettre à jour
                
                # Mettre à jour l'affichage des fichiers avec filtrage
                update_filtered_file_table(new_path)
                
                # Mettre à jour le widget d'ouverture de fichiers
                open_file_widget_browser.update_buttons(new_path)
                
                # Vider et remplir la liste suivante
                if next_list_widget:
                    populate_list_with_directories(next_list_widget, new_path)
                    # Afficher les blocs jusqu'au niveau suivant
                    show_blocks_up_to_level(level + 1)
                else:
                    # Si c'est le dernier niveau, afficher seulement jusqu'au niveau actuel
                    show_blocks_up_to_level(level)
                
                # Vider toutes les listes suivantes selon le niveau
                if level == 1:
                    list_03.clear()
                    list_04.clear()
                    list_05.clear()
                    list_06.clear()
                    list_07.clear()
                elif level == 2:
                    list_04.clear()
                    list_05.clear()
                    list_06.clear()
                    list_07.clear()
                elif level == 3:
                    list_05.clear()
                    list_06.clear()
                    list_07.clear()
                elif level == 4:
                    list_06.clear()
                    list_07.clear()
                elif level == 5:
                    list_07.clear()
                    
            except Exception as e:
                print(f"Erreur lors de la sélection niveau {level}: {e}")
        
        # Fonction pour mettre à jour la navigation (boutons de raccourcis)
        def update_navigation(directory):
            """Met à jour la navigation quand on clique sur un bouton de raccourci"""
            try:
                if not os.path.exists(directory):
                    return
                
                # Mettre à jour le répertoire courant
                widget.current_directory = directory
                
                # La barre de statut a été supprimée - pas besoin de la mettre à jour
                
                # Mettre à jour l'affichage des fichiers avec filtrage
                update_filtered_file_table(directory)
                
                # Mettre à jour le widget d'ouverture de fichiers
                open_file_widget_browser.update_buttons(directory)
                
                # Remplir la première liste avec les dossiers du répertoire sélectionné
                populate_list_with_directories(list_01, directory)
                
                # Vider les autres listes
                list_02.clear()
                list_03.clear()
                list_04.clear()
                list_05.clear()
                list_06.clear()
                list_07.clear()
                
                # Afficher seulement le bloc 1 au début
                show_blocks_up_to_level(1)
                
                # Mettre à jour le chemin de base pour la navigation
                widget.current_base_path = directory
                
            except Exception as e:
                print(f"Erreur lors de la mise à jour de la navigation: {e}")
        
        # Fonction pour gérer la sélection dans la liste 1
        def on_list1_selection():
            on_list_selection(list_01, list_02, 1)
        
        # Fonction pour gérer la sélection dans la liste 2
        def on_list2_selection():
            on_list_selection(list_02, list_03, 2)
        
        # Fonction pour gérer la sélection dans la liste 3
        def on_list3_selection():
            on_list_selection(list_03, list_04, 3)
        
        # Fonction pour gérer la sélection dans la liste 4
        def on_list4_selection():
            on_list_selection(list_04, list_05, 4)
        
        # Fonction pour gérer la sélection dans la liste 5
        def on_list5_selection():
            on_list_selection(list_05, list_06, 5)
        
        # Fonction pour gérer la sélection dans la liste 6
        def on_list6_selection():
            on_list_selection(list_06, list_07, 6)
        
        # Fonction pour gérer la sélection dans la liste 7
        def on_list7_selection():
            on_list_selection(list_07, None, 7)
        
        # Connecter les signaux des listes
        list_01.itemSelectionChanged.connect(on_list1_selection)
        list_02.itemSelectionChanged.connect(on_list2_selection)
        list_03.itemSelectionChanged.connect(on_list3_selection)
        list_04.itemSelectionChanged.connect(on_list4_selection)
        list_05.itemSelectionChanged.connect(on_list5_selection)
        list_06.itemSelectionChanged.connect(on_list6_selection)
        list_07.itemSelectionChanged.connect(on_list7_selection)
        
        # Les connexions des boutons de raccourcis ont été supprimées car ils sont maintenant dans la sidebar
        
        # Initialiser avec le répertoire du projet
        update_navigation(project_path)
        
        # Exposer la fonction update_navigation pour qu'elle soit accessible depuis l'extérieur
        widget.update_navigation = update_navigation
        
        return widget
    
    @staticmethod
    def create_recent_content(parent):
        """Crée le contenu des fichiers récents"""
        import json
        import os
        from PySide2.QtWidgets import QVBoxLayout, QWidget, QLabel
        from PySide2.QtCore import Qt
        from Packages.ui.widgets.custom_table_widget import CustomTableWidget
        from Packages.ui.widgets.open_file_widget import OpenFileWidget
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Créer le tableau de fichiers récents (même style que browser)
        recent_file_table = CustomTableWidget()
        recent_file_table.set_table(['File Name', 'Image', 'Version', 'Comment', 'Infos'],
                                   [180, 100, 100, 150, 100])
        
        # Connecter les signaux du menu contextuel
        recent_file_table.file_renamed.connect(lambda old_path, new_path: on_file_renamed_recent(old_path, new_path))
        recent_file_table.file_duplicated.connect(lambda old_path, new_path: on_file_duplicated_recent(old_path, new_path))
        recent_file_table.open_in_explorer.connect(lambda file_path: on_open_in_explorer_recent(file_path))
        
        # Créer le widget OpenFileWidget pour l'ouverture de fichiers
        open_file_widget_recent = OpenFileWidget(parent=None, file_directory="")
        open_file_widget_recent.setObjectName("_open_file_widget_recent")
        
        # Cacher le bouton de préférences
        open_file_widget_recent.prefs_button.hide()
        
        # Fonctions de gestion des signaux du menu contextuel pour Recent
        def on_file_renamed_recent(old_path, new_path):
            """Gère le renommage d'un fichier dans Recent"""
            try:
                print(f"Fichier renommé dans Recent: {old_path} -> {new_path}")
                # Recharger la liste des fichiers récents
                load_recent_files()
            except Exception as e:
                QMessageBox.critical(None, "Erreur", f"Erreur lors du renommage: {str(e)}")
        
        def on_file_duplicated_recent(old_path, new_path):
            """Gère la duplication d'un fichier dans Recent"""
            try:
                print(f"Fichier dupliqué dans Recent: {old_path} -> {new_path}")
                # Recharger la liste des fichiers récents
                load_recent_files()
            except Exception as e:
                QMessageBox.critical(None, "Erreur", f"Erreur lors de la duplication: {str(e)}")
        
        def on_open_in_explorer_recent(file_path):
            """Ouvre l'explorateur Windows à l'emplacement du fichier dans Recent"""
            try:
                open_in_explorer(file_path)
            except Exception as e:
                # Ne pas afficher d'erreur, l'explorateur s'ouvre quand même
                print(f"Erreur lors de l'ouverture de l'explorateur: {str(e)}")
        
        # Fonction pour charger les fichiers récents depuis recent_files.json
        def load_recent_files():
            """Charge les fichiers récents depuis recent_files.json"""
            try:
                recent_file_table.setRowCount(0)
                
                # Chemin vers le fichier recent_files.json
                pipezer_dir = os.path.expanduser("~/.pipezer")
                recent_file_path = os.path.join(pipezer_dir, "recent_files.json")
                
                if not os.path.exists(recent_file_path):
                    return
                
                # Charger le fichier JSON
                with open(recent_file_path, 'r', encoding='utf-8') as f:
                    recent_data = json.load(f)
                
                # Ajouter les fichiers au tableau
                for file_path in recent_data.get('files', []):
                    if os.path.exists(file_path):
                        recent_file_table.add_item(file_path)
                
                # Sélectionner automatiquement le premier fichier
                if recent_file_table.rowCount() > 0:
                    recent_file_table.setCurrentCell(0, 0)
                    recent_file_table.selectRow(0)
                    
                    # Mettre à jour le widget d'ouverture avec le premier fichier
                    first_item = recent_file_table.item(0, 0)
                    if first_item:
                        first_file_path = first_item.data(32)
                        if first_file_path:
                            open_file_widget_recent.update_buttons(first_file_path)
                    
            except Exception as e:
                print(f"Erreur lors du chargement des fichiers récents: {e}")
        
        # Gérer la sélection générale de ligne
        def on_recent_item_selection_changed():
            """Gère la sélection des éléments du tableau récent"""
            try:
                current_row = recent_file_table.currentRow()
                
                if current_row >= 0:
                    item = recent_file_table.item(current_row, 0)
                    
                    if item:
                        file_path = item.data(32)
                        
                        if file_path and os.path.isfile(file_path):
                            open_file_widget_recent.update_buttons(file_path)
            except Exception as e:
                print(f"Erreur lors de la sélection récente: {e}")
        
        # Connecter le signal de sélection
        recent_file_table.itemSelectionChanged.connect(on_recent_item_selection_changed)
        
        # Charger les fichiers récents
        load_recent_files()
        
        # Ajouter les widgets au layout
        layout.addWidget(recent_file_table)
        layout.addWidget(open_file_widget_recent)
        
        # Stocker les références
        widget.recent_file_table = recent_file_table
        widget.open_file_widget_recent = open_file_widget_recent
        widget.load_recent_files = load_recent_files  # Exposer la fonction pour recharger
        
        return widget
    
    @staticmethod
    def create_search_content(parent):
        """Crée le contenu de recherche"""
        import os
        from PySide2.QtWidgets import QVBoxLayout, QWidget, QLabel
        from PySide2.QtCore import Qt
        from Packages.ui.widgets.custom_table_widget import CustomTableWidget
        from Packages.ui.widgets.open_file_widget import OpenFileWidget
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Créer le tableau de résultats de recherche (même style que browser)
        search_file_table = CustomTableWidget()
        search_file_table.set_table(['File Name', 'Image', 'Version', 'Comment', 'Infos'],
                                   [180, 100, 100, 150, 100])
        
        # Connecter les signaux du menu contextuel
        search_file_table.file_renamed.connect(lambda old_path, new_path: on_file_renamed_search(old_path, new_path))
        search_file_table.file_duplicated.connect(lambda old_path, new_path: on_file_duplicated_search(old_path, new_path))
        search_file_table.open_in_explorer.connect(lambda file_path: on_open_in_explorer_search(file_path))
        
        # Créer le widget OpenFileWidget pour l'ouverture de fichiers
        open_file_widget_search = OpenFileWidget(parent=None, file_directory="")
        open_file_widget_search.setObjectName("_open_file_widget_search")
        
        # Cacher le bouton de préférences
        open_file_widget_search.prefs_button.hide()
        
        # Fonctions de gestion des signaux du menu contextuel pour Search
        def on_file_renamed_search(old_path, new_path):
            """Gère le renommage d'un fichier dans Search"""
            try:
                print(f"Fichier renommé dans Search: {old_path} -> {new_path}")
                # Recharger les résultats de recherche
                # Note: On ne peut pas recharger automatiquement car on n'a pas le texte de recherche
            except Exception as e:
                QMessageBox.critical(None, "Erreur", f"Erreur lors du renommage: {str(e)}")
        
        def on_file_duplicated_search(old_path, new_path):
            """Gère la duplication d'un fichier dans Search"""
            try:
                print(f"Fichier dupliqué dans Search: {old_path} -> {new_path}")
                # Note: On ne peut pas recharger automatiquement car on n'a pas le texte de recherche
            except Exception as e:
                QMessageBox.critical(None, "Erreur", f"Erreur lors de la duplication: {str(e)}")
        
        def on_open_in_explorer_search(file_path):
            """Ouvre l'explorateur Windows à l'emplacement du fichier dans Search"""
            try:
                open_in_explorer(file_path)
            except Exception as e:
                # Ne pas afficher d'erreur, l'explorateur s'ouvre quand même
                print(f"Erreur lors de l'ouverture de l'explorateur: {str(e)}")
        
        # Fonction pour mettre à jour les résultats de recherche
        def update_search_results(search_text):
            """Met à jour les résultats de recherche"""
            try:
                search_file_table.setRowCount(0)
                
                if not search_text or len(search_text.strip()) < 2:
                    return
                
                # Obtenir le chemin du projet courant
                from Packages.utils.funcs import get_current_value
                from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
                
                project_path = get_current_value(json_file=CURRENT_PROJECT_JSON_PATH, key='current_project')
                if not project_path:
                    project_path = os.getcwd()
                
                # Extensions de fichiers autorisées (même que dans browser)
                ALLOWED_EXTENSIONS = {
                    '.ma', '.mb', '.hip', '.hipnc', '.png', '.jpg', '.jpeg', 
                    '.nk', '.nuke', '.nukex', '.blend', '.sbs', '.sbsar', 
                    '.spp', '.psd', '.psb', '.zpr', '.ztl', '.c4d', 
                    '.uasset', '.umap', '.txt'
                }
                
                # Fonction récursive pour chercher les fichiers
                def search_files(directory, search_term):
                    found_files = []
                    try:
                        for root, dirs, files in os.walk(directory):
                            for file in files:
                                if search_term.lower() in file.lower():
                                    file_path = os.path.join(root, file)
                                    file_ext = os.path.splitext(file)[1].lower()
                                    if file_ext in ALLOWED_EXTENSIONS:
                                        found_files.append(file_path)
                    except Exception as e:
                        print(f"Erreur lors de la recherche: {e}")
                    return found_files
                
                # Effectuer la recherche
                found_files = search_files(project_path, search_text)
                
                # Ajouter les fichiers trouvés au tableau
                for file_path in found_files[:50]:  # Limiter à 50 résultats
                    if os.path.exists(file_path):
                        search_file_table.add_item(file_path)
                
                # Sélectionner automatiquement le premier fichier
                if search_file_table.rowCount() > 0:
                    search_file_table.setCurrentCell(0, 0)
                    search_file_table.selectRow(0)
                    
                    # Mettre à jour le widget d'ouverture avec le premier fichier
                    first_item = search_file_table.item(0, 0)
                    if first_item:
                        first_file_path = first_item.data(32)
                        if first_file_path:
                            open_file_widget_search.update_buttons(first_file_path)
                    
            except Exception as e:
                print(f"Erreur lors de la mise à jour des résultats de recherche: {e}")
        
        # Gérer la sélection générale de ligne
        def on_search_item_selection_changed():
            """Gère la sélection des éléments du tableau de recherche"""
            try:
                current_row = search_file_table.currentRow()
                
                if current_row >= 0:
                    item = search_file_table.item(current_row, 0)
                    
                    if item:
                        file_path = item.data(32)
                        
                        if file_path and os.path.isfile(file_path):
                            open_file_widget_search.update_buttons(file_path)
            except Exception as e:
                print(f"Erreur lors de la sélection de recherche: {e}")
        
        # Connecter le signal de sélection
        search_file_table.itemSelectionChanged.connect(on_search_item_selection_changed)
        
        # Ajouter les widgets au layout
        layout.addWidget(search_file_table)
        layout.addWidget(open_file_widget_search)
        
        # Stocker les références
        widget.search_file_table = search_file_table
        widget.open_file_widget_search = open_file_widget_search
        widget.update_search_results = update_search_results  # Exposer la fonction pour mettre à jour
        
        return widget
    
    @staticmethod
    def create_asset_content(parent):
        """Crée le contenu Create Asset - Supprimé, utilise les nouveaux dialogues modernes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Message indiquant que les dialogues sont maintenant séparés
        message = QLabel("Les dialogues Create Asset et Create Shot sont maintenant des fenêtres séparées.\nUtilisez les boutons dans l'en-tête pour les ouvrir.")
        message.setObjectName("info_message")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        
        return widget
    
    @staticmethod
    def create_shot_content(parent):
        """Crée le contenu Create Shot - Supprimé, utilise les nouveaux dialogues modernes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Message indiquant que les dialogues sont maintenant séparés
        message = QLabel("Les dialogues Create Asset et Create Shot sont maintenant des fenêtres séparées.\nUtilisez les boutons dans l'en-tête pour les ouvrir.")
        message.setObjectName("info_message")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        
        return widget
    
    @staticmethod
    def create_crash_content(parent):
        """Crée le contenu Crash avec les fichiers du dossier temp"""
        import json
        import os
        import tempfile
        from PySide2.QtWidgets import QVBoxLayout, QWidget, QLabel
        from PySide2.QtCore import Qt
        from Packages.ui.widgets.custom_table_widget import CustomTableWidget
        from Packages.ui.widgets.open_file_widget import OpenFileWidget
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Créer le tableau de fichiers crash (même style que browser)
        crash_file_table = CustomTableWidget()
        crash_file_table.set_table(['File Name', 'Image', 'Version', 'Comment', 'Infos'],
                                   [180, 100, 100, 150, 100])
        
        # Connecter les signaux du menu contextuel
        crash_file_table.file_renamed.connect(lambda old_path, new_path: on_file_renamed_crash(old_path, new_path))
        crash_file_table.file_duplicated.connect(lambda old_path, new_path: on_file_duplicated_crash(old_path, new_path))
        crash_file_table.open_in_explorer.connect(lambda file_path: on_open_in_explorer_crash(file_path))
        
        # Créer le widget OpenFileWidget pour l'ouverture de fichiers
        open_file_widget_crash = OpenFileWidget(parent=None, file_directory="")
        open_file_widget_crash.setObjectName("_open_file_widget_crash")
        open_file_widget_crash.prefs_button.hide()
        
        # Extensions de fichiers compatibles avec PipeZer
        compatible_extensions = ['.ma', '.mb', '.hip', '.hipnc', '.nk', '.blend', '.kra', '.fbx', '.obj', '.psd', '.drp', '.uasset', '.zpr']
        
        # Fonctions de gestion des signaux du menu contextuel pour Crash
        def on_file_renamed_crash(old_path, new_path):
            """Gère le renommage d'un fichier dans Crash"""
            try:
                print(f"Fichier renommé dans Crash: {old_path} -> {new_path}")
                # Recharger la liste des fichiers crash
                load_crash_files()
            except Exception as e:
                QMessageBox.critical(None, "Erreur", f"Erreur lors du renommage: {str(e)}")
        
        def on_file_duplicated_crash(old_path, new_path):
            """Gère la duplication d'un fichier dans Crash"""
            try:
                print(f"Fichier dupliqué dans Crash: {old_path} -> {new_path}")
                # Recharger la liste des fichiers crash
                load_crash_files()
            except Exception as e:
                QMessageBox.critical(None, "Erreur", f"Erreur lors de la duplication: {str(e)}")
        
        def on_open_in_explorer_crash(file_path):
            """Ouvre l'explorateur Windows à l'emplacement du fichier dans Crash"""
            try:
                open_in_explorer(file_path)
            except Exception as e:
                # Ne pas afficher d'erreur, l'explorateur s'ouvre quand même
                print(f"Erreur lors de l'ouverture de l'explorateur: {str(e)}")
        
        # Fonction pour charger les fichiers du dossier temp
        def load_crash_files():
            """Charge les fichiers compatibles du dossier temp"""
            try:
                crash_file_table.setRowCount(0)
                
                # Obtenir le dossier temp
                temp_dir = tempfile.gettempdir()
                
                if not os.path.exists(temp_dir):
                    return
                
                # Parcourir récursivement le dossier temp
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_ext = os.path.splitext(file)[1].lower()
                        
                        # Vérifier si l'extension est compatible
                        if file_ext in compatible_extensions:
                            crash_file_table.add_item(file_path)
                
                # Sélectionner automatiquement le premier fichier
                if crash_file_table.rowCount() > 0:
                    crash_file_table.setCurrentCell(0, 0)
                    crash_file_table.selectRow(0)
                    
                    # Mettre à jour le widget d'ouverture avec le premier fichier
                    first_item = crash_file_table.item(0, 0)
                    if first_item:
                        first_file_path = first_item.data(32)
                        if first_file_path:
                            open_file_widget_crash.update_buttons(first_file_path)
                        
            except Exception as e:
                print(f"Erreur lors du chargement des fichiers crash: {e}")
        
        # Gérer la sélection générale de ligne
        def on_crash_item_selection_changed():
            """Gère la sélection des éléments du tableau crash"""
            try:
                current_row = crash_file_table.currentRow()
                
                if current_row >= 0:
                    item = crash_file_table.item(current_row, 0)
                    
                    if item:
                        file_path = item.data(32)
                        
                        if file_path and os.path.isfile(file_path):
                            open_file_widget_crash.update_buttons(file_path)
            except Exception as e:
                print(f"Erreur lors de la sélection crash: {e}")
        
        # Connecter le signal de sélection
        crash_file_table.itemSelectionChanged.connect(on_crash_item_selection_changed)
        
        # Charger les fichiers crash
        load_crash_files()
        
        # Ajouter les widgets au layout
        layout.addWidget(crash_file_table)
        layout.addWidget(open_file_widget_crash)
        
        # Stocker les références
        widget.crash_file_table = crash_file_table
        widget.open_file_widget_crash = open_file_widget_crash
        widget.load_crash_files = load_crash_files  # Exposer la fonction pour recharger
        
        return widget
    
    @staticmethod
    def open_temp_folder():
        """Ouvre le dossier temp du système"""
        import subprocess
        import platform
        
        try:
            if platform.system() == "Windows":
                temp_path = os.environ.get('TEMP', os.environ.get('TMP', ''))
                if temp_path:
                    subprocess.Popen(f'explorer "{temp_path}"')
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(['open', '/tmp'])
            else:  # Linux
                subprocess.Popen(['xdg-open', '/tmp'])
        except Exception as e:
            print(f"Erreur lors de l'ouverture du dossier temp: {e}")
