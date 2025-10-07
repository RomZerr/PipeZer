import os
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from Packages.utils.constants.preferences import CURRENT_PROJECT_JSON_PATH
from Packages.utils.funcs import get_current_value


class ConstructPipelineDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Construct Pipeline')
        self.setMinimumSize(380, 160)

        self.project_root = get_current_value(CURRENT_PROJECT_JSON_PATH, 'current_project', '')

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.info_label = QLabel(f'Project: {self.project_root or "<unset>"}')
        self.main_layout.addWidget(self.info_label)

        row = QHBoxLayout()
        self.auto_btn = QPushButton('Create default folders')
        self.map_btn = QPushButton('Map existing folders')
        row.addWidget(self.auto_btn)
        row.addWidget(self.map_btn)
        self.main_layout.addLayout(row)

        self.auto_btn.clicked.connect(self.create_defaults)
        self.map_btn.clicked.connect(self.map_existing)

    def ensure_project_root(self) -> str:
        if self.project_root and os.path.isdir(self.project_root):
            return self.project_root
        root = QFileDialog.getExistingDirectory(self, 'Select project root')
        if not root:
            return ''
        self.project_root = root.replace('\\', '/')
        self.info_label.setText(f'Project: {self.project_root}')
        return self.project_root

    def create_defaults(self):
        root = self.ensure_project_root()
        if not root:
            return
        for folder in ['04_asset', '05_shot', '02_ressource']:
            path = os.path.join(root, folder)
            os.makedirs(path, exist_ok=True)
        QMessageBox.information(self, 'Done', 'Default pipeline folders created.')
        self.accept()

    def map_existing(self):
        root = self.ensure_project_root()
        if not root:
            return
        # Ask user to pick existing folders to map
        asset_dir = QFileDialog.getExistingDirectory(self, 'Select Asset folder', root)
        shot_dir = QFileDialog.getExistingDirectory(self, 'Select Shot folder', root)
        res_dir = QFileDialog.getExistingDirectory(self, 'Select Ressource folder', root)

        # Create target canonical names if needed and junction/map if different
        mapping = {
            '04_asset': asset_dir,
            '05_shot': shot_dir,
            '02_ressource': res_dir,
        }

        for canonical, picked in mapping.items():
            if not picked:
                continue
            canonical_path = os.path.join(root, canonical)
            if os.path.normcase(os.path.abspath(picked)) == os.path.normcase(os.path.abspath(canonical_path)):
                # Already matches target name
                if not os.path.exists(canonical_path):
                    os.makedirs(canonical_path, exist_ok=True)
                continue
            # Ensure target name exists as a junction to picked folder (Windows)
            try:
                if os.path.exists(canonical_path):
                    continue
                # Create junction via mklink /J
                import subprocess
                subprocess.check_call(['cmd', '/c', 'mklink', '/J', canonical_path, picked])
            except Exception:
                # Fallback: just create the canonical folder if junction fails
                os.makedirs(canonical_path, exist_ok=True)
        QMessageBox.information(self, 'Done', 'Folders mapped/created.')
        self.accept()


