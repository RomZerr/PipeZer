import os
import re
import concurrent.futures
from PySide2.QtCore import Qt, Signal, QRect
from PySide2.QtGui import QFont, QIcon, QPainter, QPen, QColor
from PySide2.QtWidgets import (QTableWidget, QTableWidgetItem, QAbstractItemView, 
                               QHeaderView, QMenu, QAction, QInputDialog, QMessageBox)
from Packages.utils.translations import translation_manager
from Packages.logic.filefunc import get_version_num, get_file_modification_date_time
from Packages.logic.json_funcs import get_file_data
from Packages.logic.filefunc import get_files
from Packages.ui.widgets.image_widget import ImageWidget
from Packages.utils.funcs import get_size, forward_slash
from Packages.utils.constants.project_files import ICON_PATH
from Packages.utils.constants.preferences import UI_PREFS_JSON_PATH
from Packages.utils.funcs import get_current_value
from PySide2.QtGui import QBrush, QColor, QIcon, QPixmap




def extract_version_from_filename(filename):
    """Extracts version from filename in '_XXX.' format"""
    match = re.search(r'_(\d{3}).', filename)
    if match:
        return match.group(1)
    return None


class CustomTableWidget(QTableWidget):
    file_renamed = Signal(str, str)
    file_duplicated = Signal(str, str)
    open_in_explorer = Signal(str)

    def __init__(self, parent=None):
        super(CustomTableWidget, self).__init__(parent)

        self.setMouseTracking(True)
        
        self._hovered_row = -1
        self._user_has_selected = False
        
        self.cellClicked.connect(self.onCellClicked)
        self.itemSelectionChanged.connect(self.onSelectionChanged)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def onCellClicked(self, row, column):
        """Forces row selection when clicking on a cell"""
        self._user_has_selected = True
        self.selectRow(row)
        self._apply_row_selection_style(row)
    
    def onSelectionChanged(self):
        """Handles selection change to clean old selections"""
        for row in range(self.rowCount()):
            if row != self.currentRow():
                self._clear_row_selection_style(row)
        
        current_row = self.currentRow()
        if current_row >= 0:
            self._apply_row_selection_style(current_row)
    
    def _apply_row_selection_style(self, row):
        """Applies selection style to all cells in the row"""
        if row < 0 or row >= self.rowCount():
            return
            
        selection_text_color = QColor(230, 237, 243)
        
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setSelected(True)
                item.setForeground(QBrush(selection_text_color))
            
            widget = self.cellWidget(row, col)
            if widget:
                widget.setStyleSheet("""
                    QLabel {
                        background-color: transparent;
                        border: none;
                        padding: 4px;
                    }
                """)
        
        self.viewport().update()
    
    def _clear_row_selection_style(self, row):
        """Removes selection style from all cells in the row"""
        if row < 0 or row >= self.rowCount():
            return
            
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setSelected(False)
                item.setBackground(QBrush(QColor(28, 28, 28)))
                item.setForeground(QBrush(QColor(255, 255, 255)))
            
            widget = self.cellWidget(row, col)
            if widget:
                widget.setStyleSheet("""
                    QLabel {
                        background-color: transparent;
                        border: none;
                        padding: 4px;
                    }
                """)
        
        self.viewport().update()
    
    def mouseMoveEvent(self, event):
        """Handles mouse movement for row hover"""
        super().mouseMoveEvent(event)
        
        index = self.indexAt(event.pos())
        new_hovered_row = index.row() if index.isValid() else -1
        
        if new_hovered_row != self._hovered_row:
            if self._hovered_row >= 0:
                self._clear_row_hover_style(self._hovered_row)
            
            self._hovered_row = new_hovered_row
            if self._hovered_row >= 0 and self._hovered_row != self.currentRow():
                self._apply_row_hover_style(self._hovered_row)
    
    def leaveEvent(self, event):
        """Handles mouse leaving the widget"""
        super().leaveEvent(event)
        if self._hovered_row >= 0:
            self._clear_row_hover_style(self._hovered_row)
            self._hovered_row = -1
    
    def _apply_row_hover_style(self, row):
        """Applies hover style to the entire row"""
        if row < 0 or row >= self.rowCount():
            return
        
        self.viewport().update()
    
    def _clear_row_hover_style(self, row):
        """Removes hover style from a row"""
        if row < 0 or row >= self.rowCount():
            return
        
        self.viewport().update()
    
    def paintEvent(self, event):
        """Draws table and adds border and background for selected row"""
        current_row = self.currentRow()
        if current_row >= 0 and self._user_has_selected:
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.Antialiasing)
            
            first_col_rect = self.visualRect(self.model().index(current_row, 0))
            last_col_rect = self.visualRect(self.model().index(current_row, self.columnCount() - 1))
            
            row_rect = QRect(
                first_col_rect.left(),
                first_col_rect.top(),
                last_col_rect.right() - first_col_rect.left(),
                first_col_rect.height()
            )
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(70, 70, 80))
            painter.drawRoundedRect(row_rect, 4, 4)
            
            painter.end()
        
        super().paintEvent(event)
        
        # Enfin, dessiner la bordure PAR-DESSUS tout
        if current_row >= 0 and self._user_has_selected:
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Recalculer le rectangle
            first_col_rect = self.visualRect(self.model().index(current_row, 0))
            last_col_rect = self.visualRect(self.model().index(current_row, self.columnCount() - 1))
            
            row_rect = QRect(
                first_col_rect.left(),
                first_col_rect.top(),
                last_col_rect.right() - first_col_rect.left(),
                first_col_rect.height()
            )
            
            # Dessiner la bordure
            pen = QPen(QColor(99, 102, 241))  # Couleur bleue
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)  # Pas de remplissage
            painter.drawRoundedRect(row_rect, 4, 4)
            
            painter.end()

    def clear_table(self):
        """Clears all table rows"""
        while self.rowCount() > 0:
            self.removeRow(0)

    def set_data(self, data):
        """Fills table with provided data"""
        self.setRowCount(len(data))
        for row, file_info in enumerate(data):
            for col, value in enumerate(file_info):
                self.setItem(row, col, QTableWidgetItem(value))

    def set_table(self, columns: list, widths: list):
        """
        Exemple :
        self.set_table(['File Name', 'Image', 'Version', 'Comment', 'Infos'], [200, 50, None, 100, 100])
        """

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setShowGrid(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSortingEnabled(True)
        self.horizontalHeader().setCascadingSectionResizes(False)
        self.horizontalHeader().setDefaultSectionSize(150)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setCascadingSectionResizes(False)
        self.verticalHeader().setHighlightSections(False)
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.setStyleSheet("""
            QTableWidget {
                background-color: #1C1C1C;
                alternate-background-color: #1C1C1C;
                selection-background-color: transparent;
                gridline-color: transparent;
                border: 1px solid #2A2A2A;
                border-radius: 4px;
                show-decoration-selected: 0;
                outline: none;
            }
            QTableWidget::item {
                background-color: transparent;
                border-bottom: 1px solid #2A2A2A;
                border-right: none;
                border-left: none;
                padding: 8px;
                outline: none;
            }
            QTableWidget::item:selected {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QTableWidget::item:hover {
                background-color: transparent;
                outline: none;
            }
            QTableWidget::item:pressed {
                background-color: transparent;
                outline: none;
            }
            QTableWidget::item:focus {
                background-color: transparent;
                border: none;
                outline: none;
            }
        """)

        column_count = len(columns)
        self.setColumnCount(column_count)

        for index, column in enumerate(columns):
            row = QTableWidgetItem()
            self.setHorizontalHeaderItem(index, row)
            self.horizontalHeaderItem(index).setText(column)

            # Utiliser QHeaderView.Stretch pour faire en sorte que toutes les colonnes prennent la largeur disponible
            self.horizontalHeader().setSectionResizeMode(index, QHeaderView.Stretch)

    from PySide2.QtGui import QBrush, QColor, QIcon, QPixmap, QFont

    from PySide2.QtGui import QBrush, QColor, QFont

    def add_item(self, filepath: str, parallel: bool = True):
        """
        Ajoute un élément dans le tableau avec les informations du fichier.
        """

        filepath = forward_slash(filepath)
        filename = os.path.basename(filepath)

        row_position = self.rowCount()
        self.insertRow(row_position)
        self.setRowHeight(row_position, 101)

        file_name_item = QTableWidgetItem(filename)
        file_name_item.setData(32, filepath)
        file_name_item.setFlags(Qt.ItemIsEnabled)

        def _image_item():
            img_exts = ['.png', '.jpg', '.tex', '.exr']
            ext = os.path.splitext(filename)[-1]

            image_item = ImageWidget(filepath=filepath, image=ext in img_exts)
            image_item.setData(32, filepath)
            return image_item

        def _version_item():
            version_item = QTableWidgetItem()
            version_item.setData(32, filepath)
            version_item.setFlags(Qt.ItemIsEnabled)
            version_item.setTextAlignment(Qt.AlignCenter)
            font = QFont()
            font.setPointSize(12)
            version_item.setFont(font)

            keywords = {
                "_geoT": "GEO Temporaire",
                "_geo": "GEO",
                "_Asset": "ASSET ASSEMBLY",
                "_layout": "LAYOUT",
                "_lighting": "LIGHTING",
                "_camera": "CAMERA",
                "_fx": "FX",
                "_groom": "GROOM",
                "_cfx": "CFX",
                "_conformity": "CONFORMITY",
                "_materials": "MATERIAL",
                "_Card_materials": "CARDS MATERIAL"
            }

            if filename.endswith((".usd", ".usda")):
                for key, value in keywords.items():
                    if key in filename:
                        version_item.setText(value)
                        break
                else:
                    version_item.setText("USD")

            elif "_P." in filename:
                version_item.setText("PUBLISH")

            else:
                version = extract_version_from_filename(filename)
                version_item.setText(version if version else "N/A")

            if os.path.splitext(filename)[-1] in ('.usd', '.usda'):
                self._add_icon(version_item, 'usd')

            return version_item

        # 3 - Comment
        def _comment_item():
            comment_item = QTableWidgetItem()
            comment_item.setData(32, filepath)
            comment_item.setFlags(Qt.ItemIsEnabled)
            comment_data = get_file_data(filepath)['comment']
            comment_item.setText(comment_data)
            return comment_item

        # 4 - Infos
        def _user_item():
            user_item = QTableWidgetItem()
            user_item.setData(32, filepath)
            user_item.setFlags(Qt.ItemIsEnabled)
            user_item.setTextAlignment(Qt.AlignCenter)
            user_data = f"{get_file_data(filepath)['user']}\n{get_file_modification_date_time(filepath)}\n{get_size(filepath)}"
            user_item.setText(user_data)
            return user_item

        if parallel:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                version_item = executor.submit(_version_item)
                comment_item = executor.submit(_comment_item)
                user_item = executor.submit(_user_item)

                version_item = version_item.result()
                comment_item = comment_item.result()
                user_item = user_item.result()

            image_item = _image_item()

        else:
            image_item = _image_item()
            version_item = _version_item()
            comment_item = _comment_item()
            user_item = _user_item()

        self.setItem(row_position, 0, file_name_item)  # Colonne "File Name"
        self.setCellWidget(row_position, 1, image_item)  # Colonne "Image"
        self.setItem(row_position, 2, version_item)  # Colonne "Version"
        self.setItem(row_position, 3, comment_item)  # Colonne "Comment"
        self.setItem(row_position, 4, user_item)  # Colonne "Infos"

    def update_file_items(self, directory):
        """Updates file items in table from directory"""

        self.setRowCount(0)

        if isinstance(directory, str):
            file_list = get_files(directory)

            if not file_list:
                return

            if get_current_value(UI_PREFS_JSON_PATH, 'reverse_sort_file'):
                file_list = sorted(file_list, reverse=True)
            file_list = file_list[:get_current_value(UI_PREFS_JSON_PATH, 'num_files')]

            if not file_list:
                return

            file_path_list = [os.path.join(directory, file) for file in file_list]

        elif isinstance(directory, list):
            file_path_list = directory

        else:
            raise TypeError('wrong argument.')

        for file_path in file_path_list:
            self.add_item(file_path)
        
        self.clearSelection()
        self.setCurrentCell(-1, -1)
        self._user_has_selected = False

    def _add_icon(self, widget, text="", bw: bool = False):
        """Adds icon to table widget"""

        bw_dict = {True: '_bw', False: ''}

        icon_file_path = os.path.join(ICON_PATH, f'{text.lower()}{bw_dict[bw]}_icon.ico')
        if not os.path.exists(icon_file_path):
            return

        icon = QIcon(icon_file_path)
        widget.setIcon(icon)

    def filter_files_by_name(self, name):
        """
        Filtre les fichiers affichés dans le tableau en fonction du nom sélectionné.
        """
        all_files = self.get_all_files()
        filtered_files = [file for file in all_files if name in file]

        self.clearContents()
        self.setRowCount(0)

        for file in filtered_files:
            self.add_file_to_table(file)
    
    def show_context_menu(self, position):
        """Shows context menu on right click"""
        current_row = self.currentRow()
        if current_row < 0:
            return
        
        file_path_item = self.item(current_row, 0)
        if not file_path_item:
            return
        
        file_path = file_path_item.data(32)
        if not file_path or not os.path.exists(file_path):
            return
        
        context_menu = QMenu(self)
        
        # Action Renommer
        rename_action = QAction(translation_manager.get_text('rename'), self)
        rename_action.triggered.connect(lambda: self.rename_file(file_path))
        context_menu.addAction(rename_action)
        
        # Action Dupliquer
        duplicate_action = QAction(translation_manager.get_text('duplicate'), self)
        duplicate_action.triggered.connect(lambda: self.duplicate_file(file_path))
        context_menu.addAction(duplicate_action)
        
        # Action Ouvrir dans l'explorateur
        explorer_action = QAction(translation_manager.get_text('open_in_explorer'), self)
        explorer_action.triggered.connect(lambda: self.open_in_explorer_action(file_path))
        context_menu.addAction(explorer_action)
        
        # Afficher le menu
        context_menu.exec_(self.mapToGlobal(position))
    
    def rename_file(self, file_path):
        """Renomme le fichier sélectionné"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Erreur", "Le fichier n'existe pas.")
            return
        
        current_name = os.path.basename(file_path)
        directory = os.path.dirname(file_path)
        
        new_name, ok = QInputDialog.getText(
            self, 
            "Renommer le fichier", 
            f"Nouveau nom pour '{current_name}':",
            text=current_name
        )
        
        if ok and new_name and new_name != current_name:
            new_path = os.path.join(directory, new_name)
            
            if os.path.exists(new_path):
                QMessageBox.warning(self, "Erreur", "Un fichier avec ce nom existe déjà.")
                return
            
            try:
                os.rename(file_path, new_path)
                self.file_renamed.emit(file_path, new_path)
                QMessageBox.information(self, "Succès", f"Le fichier a été renommé en '{new_name}'.")
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de renommer le fichier: {str(e)}")
    
    def duplicate_file(self, file_path):
        """Duplicates selected file with automatic version increment"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Erreur", "Le fichier n'existe pas.")
            return
        
        try:
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            import re
            version_match = re.search(r'(\d{3})$', name)
            
            if version_match:
                current_version = int(version_match.group(1))
                new_version = current_version + 1
                new_name = re.sub(r'\d{3}$', f"{new_version:03d}", name)
            else:
                new_name = f"{name}_001"
            
            new_filename = f"{new_name}{ext}"
            new_path = os.path.join(directory, new_filename)
            
            counter = 1
            original_new_path = new_path
            while os.path.exists(new_path):
                if version_match:
                    new_version += 1
                    new_name = re.sub(r'\d{3}$', f"{new_version:03d}", name)
                else:
                    new_name = f"{name}_{counter:03d}"
                new_filename = f"{new_name}{ext}"
                new_path = os.path.join(directory, new_filename)
                counter += 1
            
            import shutil
            shutil.copy2(file_path, new_path)
            
            self.file_duplicated.emit(file_path, new_path)
            
            QMessageBox.information(self, "Succès", f"Le fichier a été dupliqué en '{os.path.basename(new_path)}'.")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de dupliquer le fichier: {str(e)}")
    
    def open_in_explorer_action(self, file_path):
        """Ouvre l'explorateur Windows à l'emplacement du fichier"""
        try:
            # Émettre le signal pour ouvrir dans l'explorateur
            self.open_in_explorer.emit(file_path)
        except Exception as e:
            print(f"Erreur lors de l'ouverture de l'explorateur: {str(e)}")

