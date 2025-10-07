import os
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QLabel, QVBoxLayout, QCheckBox, QComboBox,  QPushButton, QLineEdit, QHBoxLayout
from Packages.apps.maya_app.ui.maya_main_window import maya_main_window
from Packages.apps.maya_app.funcs.edit_publish import publish
from Packages.apps.maya_app.funcs.usd import publish_usd_asset
from Packages.logic.filefunc.get_funcs import return_publish_name
from Packages.ui.widgets import OkCancelWidget
from Packages.utils.constants.constants_old import ICON_PATH
from Packages.utils.funcs import forward_slash
from Packages.logic.json_funcs import update_file_data, json_to_dict
from Packages.logic.filefunc.get_funcs import get_file_base_folder
from maya import cmds
from Packages.utils.constants.constants_old import VARIANTS_JSON_PATH


class PublishDialog(QDialog):

    def __init__(self, parent=maya_main_window(), file_path=None, usd=False):
        super().__init__(parent)

        self.USD = usd
        self.use_catmull_clark = True  # Par défaut, Catmull Clark est activé
        self._CURRENT_FILE_PATH = file_path if file_path else cmds.file(query=True, sceneName=True)
        self._CURRENT_FILE = os.path.basename(self._CURRENT_FILE_PATH)

        if self.USD:
            self.setWindowIcon(QIcon(os.path.join(ICON_PATH, 'usd_icon.ico')))

        self._NEXT_FILE_PATH = return_publish_name(self._CURRENT_FILE, usd=self.USD)
        self._NEXT_FILE = os.path.basename(self._NEXT_FILE_PATH)

        self.setWindowTitle('Publish as')
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self._init_ui()
        self.create_connections()

        if cmds.ls(selection=True):
            self.exec_()
        else:
            cmds.error('Nothing is selected.')

    def publish_as(self):
        """Publier le fichier sans utiliser les paramètres de frame."""
        if self.USD:
            from Packages.apps.maya_app.funcs.usd import publish_usd_asset
            publish_usd_asset(use_catmull_clark=self.use_catmull_clark)  # Passer l'état de la case
        else:
            from Packages.apps.maya_app.funcs.edit_publish import publish
            publish(del_colon=True)

        self.close()

    def _init_ui(self):
        self._main_layout = QVBoxLayout()
        self.setLayout(self._main_layout)

        self._current_file_label = QLabel(f'Current file : {os.path.basename(cmds.file(query=True, sceneName=True))}')
        self._main_layout.addWidget(self._current_file_label)
        self._current_file_label.setStyleSheet("font-size: 20px;")

        self._next_file_label = QLabel(f'Save as : {return_publish_name(self._CURRENT_FILE, usd=self.USD)}')
        self._next_file_label.setStyleSheet("color: rgb(128, 192, 255); font-weight: bold; font-size: 20px;")
        self._main_layout.addWidget(self._next_file_label)

        # Ajouter une case à cocher pour Catmull Clark
        if self.USD:
            self.catmull_clark_checkbox = QCheckBox("Catmull Clark")
            self.catmull_clark_checkbox.setChecked(True)  # Par défaut, activée
            self._main_layout.addWidget(self.catmull_clark_checkbox)

        self.publish_button = QPushButton('Publish as')
        self.cancel_button = QPushButton('Cancel')
        self._main_layout.addWidget(self.publish_button)
        self._main_layout.addWidget(self.cancel_button)

    def create_connections(self):
        if self.USD:
            self.catmull_clark_checkbox.stateChanged.connect(self.update_catmull_clark)
        self.publish_button.clicked.connect(self.publish_as)
        self.cancel_button.clicked.connect(self.close)

    def update_catmull_clark(self, state):
        """Met à jour l'état de Catmull Clark selon la case à cocher."""
        self.use_catmull_clark = state == Qt.Checked
