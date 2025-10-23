"""
Modern dialog for creating assets
"""

import os
import shutil
import json
from datetime import datetime
from PySide2.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QComboBox, QFormLayout, QGroupBox,
    QWidget, QGridLayout, QCheckBox, QRadioButton
)
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QFont, QIcon

from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT
from Packages.utils.translations import translation_manager

class ModernCreateAssetDialog(QDialog):
    """Modern dialog for creating pipeline assets with software-specific project structures"""
    
    asset_created = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = "dark"
        self.setup_ui()
        self.setup_theme()
        
    def setup_ui(self):
        self.setWindowTitle('Create Asset')
        self.setFixedSize(950, 600)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        title = QLabel("Create Asset")
        title.setObjectName("dialog_title")
        main_layout.addWidget(title)
        
        form_widget = QWidget()
        form_widget.setObjectName("form_widget")
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(25)
        form_layout.setContentsMargins(25, 25, 25, 25)
        
        name_section = QWidget()
        name_layout = QVBoxLayout(name_section)
        name_layout.setSpacing(8)
        name_layout.setContentsMargins(0, 0, 0, 0)
        
        self.asset_name_label = QLabel('Asset Name')
        self.asset_name_label.setObjectName("section_label")
        self.asset_name_line_edit = QLineEdit('')
        self.asset_name_line_edit.setObjectName("input_field")
        self.asset_name_line_edit.setPlaceholderText("Enter the asset name...")
        
        name_layout.addWidget(self.asset_name_label)
        name_layout.addWidget(self.asset_name_line_edit)
        form_layout.addWidget(name_section)
        
        type_section = QWidget()
        type_layout = QVBoxLayout(type_section)
        type_layout.setSpacing(8)
        type_layout.setContentsMargins(0, 0, 0, 0)
        
        self.asset_type_label = QLabel('Asset Type')
        self.asset_type_label.setObjectName("section_label")
        type_layout.addWidget(self.asset_type_label)
        
        type_container = QWidget()
        type_grid = QHBoxLayout(type_container)
        type_grid.setSpacing(15)
        
        self.asset_type_checkboxes = []
        asset_base_path = os.path.join(CURRENT_PROJECT, "04_asset")
        
        if os.path.exists(asset_base_path):
            for folder in sorted(os.listdir(asset_base_path)):
                folder_path = os.path.join(asset_base_path, folder)
                if os.path.isdir(folder_path):
                    checkbox = QCheckBox(folder)
                    checkbox.setObjectName("checkbox")
                    checkbox.setMinimumWidth(100)
                    self.asset_type_checkboxes.append(checkbox)
                    type_grid.addWidget(checkbox)
        
        if not self.asset_type_checkboxes:
            default_types = ['01_character', '02_prop', '03_item', '04_enviro', '05_module']
            for type_name in default_types:
                checkbox = QCheckBox(type_name)
                checkbox.setObjectName("checkbox")
                checkbox.setMinimumWidth(100)
                self.asset_type_checkboxes.append(checkbox)
                type_grid.addWidget(checkbox)
        
        type_grid.addStretch()
        
        type_layout.addWidget(type_container)
        form_layout.addWidget(type_section)
        
        departments_section = QWidget()
        departments_section_layout = QVBoxLayout(departments_section)
        departments_section_layout.setSpacing(8)
        departments_section_layout.setContentsMargins(0, 0, 0, 0)
        
        self.department_label = QLabel('Departments & Software')
        self.department_label.setObjectName("section_label")
        departments_section_layout.addWidget(self.department_label)
        
        departments_widget = QWidget()
        departments_layout = QVBoxLayout(departments_widget)
        departments_layout.setSpacing(12)
        departments_layout.setContentsMargins(0, 0, 0, 0)
        
        geo_layout = QHBoxLayout()
        geo_layout.setSpacing(15)
        self.geo_cb = QCheckBox('Geometry')
        self.geo_cb.setObjectName("checkbox")
        self.geo_cb.setChecked(True)
        self.geo_cb.setMinimumWidth(100)
        self.geo_combo = QComboBox()
        self.geo_combo.setObjectName("combo_box")
        self.geo_combo.addItems(['None', 'Maya', 'Houdini', 'Blender', 'ZBrush', 'Cinema 4D'])
        self.geo_combo.setCurrentText('Maya')
        self.geo_combo.setMinimumWidth(150)
        geo_layout.addWidget(self.geo_cb)
        geo_layout.addWidget(self.geo_combo)
        geo_layout.addStretch()
        departments_layout.addLayout(geo_layout)
        
        ldv_layout = QHBoxLayout()
        ldv_layout.setSpacing(15)
        self.ldv_cb = QCheckBox('LookDev')
        self.ldv_cb.setObjectName("checkbox")
        self.ldv_cb.setChecked(True)
        self.ldv_cb.setMinimumWidth(100)
        self.ldv_combo = QComboBox()
        self.ldv_combo.setObjectName("combo_box")
        self.ldv_combo.addItems(['None', 'Maya', 'Houdini', 'Blender', 'ZBrush', 'Cinema 4D'])
        self.ldv_combo.setCurrentText('Maya')
        self.ldv_combo.setMinimumWidth(150)
        ldv_layout.addWidget(self.ldv_cb)
        ldv_layout.addWidget(self.ldv_combo)
        ldv_layout.addStretch()
        departments_layout.addLayout(ldv_layout)
        
        rig_layout = QHBoxLayout()
        rig_layout.setSpacing(15)
        self.rig_cb = QCheckBox('Rigging')
        self.rig_cb.setObjectName("checkbox")
        self.rig_cb.setMinimumWidth(100)
        self.rig_combo = QComboBox()
        self.rig_combo.setObjectName("combo_box")
        self.rig_combo.addItems(['None', 'Maya', 'Houdini', 'Blender', 'ZBrush', 'Cinema 4D'])
        self.rig_combo.setCurrentText('Maya')
        self.rig_combo.setMinimumWidth(150)
        rig_layout.addWidget(self.rig_cb)
        rig_layout.addWidget(self.rig_combo)
        rig_layout.addStretch()
        departments_layout.addLayout(rig_layout)
        
        departments_section_layout.addWidget(departments_widget)
        form_layout.addWidget(departments_section)
        
        self.department_list = [
            (self.geo_cb, self.geo_combo),
            (self.ldv_cb, self.ldv_combo),
            (self.rig_cb, self.rig_combo)
        ]
        
        self.geo_cb.toggled.connect(lambda checked: self.geo_combo.setVisible(checked))
        self.ldv_cb.toggled.connect(lambda checked: self.ldv_combo.setVisible(checked))
        self.rig_cb.toggled.connect(lambda checked: self.rig_combo.setVisible(checked))
        
        main_layout.addWidget(form_widget)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setFixedSize(120, 45)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.run_button = QPushButton('Create')
        self.run_button.setObjectName("create_button")
        self.run_button.setFixedSize(120, 45)
        self.run_button.clicked.connect(self.create_asset)
        button_layout.addWidget(self.run_button)
        
        main_layout.addLayout(button_layout)
        
    def setup_theme(self):
        if self.current_theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #0D1117, stop:1 #161B22);
                color: #E6EDF3;
            }
            
            QLabel#title_icon {
                font-size: 32px;
                margin-right: 10px;
            }
            
            QLabel#dialog_title {
                color: #E6EDF3;
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 10px;
            }
            
            QLabel#dialog_description {
                color: #8B949E;
                font-size: 14px;
                margin-bottom: 20px;
                line-height: 1.4;
            }
            
            QWidget#form_widget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #161B22, stop:1 #21262D);
                border: 1px solid #30363D;
                border-radius: 16px;
            }
            
            QLabel#section_label {
                color: #E6EDF3;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            
            QLineEdit#input_field {
                background-color: #0D1117;
                border: 2px solid #30363D;
                border-radius: 10px;
                color: #E6EDF3;
                font-size: 14px;
                padding: 14px 18px;
                selection-background-color: #6366F1;
            }
            
            QLineEdit#input_field:focus {
                border-color: #6366F1;
                background-color: #161B22;
            }
            
            QRadioButton#radio_button {
                color: #E6EDF3;
                font-size: 12px;
                font-weight: 500;
                spacing: 10px;
                padding: 6px 0px;
            }
            
            QRadioButton#radio_button::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #30363D;
                background-color: transparent;
            }
            
            QRadioButton#radio_button::indicator:checked {
                border-color: #6366F1;
                background-color: #6366F1;
            }
            
            QRadioButton#radio_button:hover {
                color: #6366F1;
            }
            
            QCheckBox#checkbox {
                color: #E6EDF3;
                font-size: 12px;
                font-weight: 500;
                spacing: 10px;
                padding: 4px 0px;
            }
            
            QCheckBox#checkbox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 2px solid #30363D;
                background-color: transparent;
            }
            
            QCheckBox#checkbox::indicator:checked {
                border-color: #6366F1;
                background-color: #6366F1;
            }
            
            QCheckBox#checkbox:hover {
                color: #6366F1;
            }
            
            QComboBox#combo_box {
                background-color: #0D1117;
                border: 2px solid #30363D;
                border-radius: 8px;
                color: #E6EDF3;
                font-size: 12px;
                font-weight: 500;
                padding: 6px 12px;
                min-width: 120px;
            }
            
            QComboBox#combo_box:hover {
                border-color: #6366F1;
            }
            
            QComboBox#combo_box:focus {
                border-color: #6366F1;
                background-color: #161B22;
            }
            
            QComboBox#combo_box::drop-down {
                border: none;
                width: 30px;
            }
            
            QComboBox#combo_box::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #E6EDF3;
                margin-right: 8px;
            }
            
            QComboBox#combo_box QAbstractItemView {
                background-color: #161B22;
                border: 2px solid #30363D;
                border-radius: 8px;
                color: #E6EDF3;
                selection-background-color: #6366F1;
                selection-color: white;
                padding: 4px;
            }
            
            QPushButton#create_button {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6366F1, stop:1 #5B5BD6);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: 600;
                padding: 14px 28px;
            }
            
            QPushButton#create_button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #5B5BD6, stop:1 #4F46E5);
            }
            
            QPushButton#create_button:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4F46E5, stop:1 #3730A3);
            }
            
            QPushButton#cancel_button {
                background-color: transparent;
                border: 2px solid #30363D;
                border-radius: 10px;
                color: #E6EDF3;
                font-size: 16px;
                font-weight: 500;
                padding: 14px 28px;
            }
            
            QPushButton#cancel_button:hover {
                background-color: #30363D;
                border-color: #6366F1;
                color: #6366F1;
            }
            
            /* Styles pour QMessageBox */
            QMessageBox {
                background-color: #161B22;
                color: #E6EDF3;
            }
            
            QMessageBox QLabel {
                color: #E6EDF3;
                font-size: 14px;
                min-width: 300px;
            }
            
            QMessageBox QPushButton {
                background-color: #6366F1;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 20px;
                min-width: 80px;
            }
            
            QMessageBox QPushButton:hover {
                background-color: #5B5BD6;
            }
        """)
    
    def apply_light_theme(self):
        """Applique le thème clair"""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                color: #1E1E2E;
            }
            
            QLabel#dialog_title {
                color: #1E1E2E;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            
            QLabel#dialog_description {
                color: #6B7280;
                font-size: 14px;
                margin-bottom: 20px;
            }
            
            QGroupBox#form_group {
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
                color: #1E1E2E;
            }
            
            QGroupBox#form_group::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QLineEdit#asset_name_edit,
            QLineEdit#description_edit {
                background-color: #F3F4F6;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px 12px;
                color: #374151;
                font-size: 14px;
            }
            
            QLineEdit#asset_name_edit:focus,
            QLineEdit#description_edit:focus {
                border-color: #6366F1;
                background-color: #FFFFFF;
            }
            
            QComboBox#asset_type_combo {
                background-color: #F3F4F6;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px 12px;
                color: #374151;
                font-size: 14px;
            }
            
            QComboBox#asset_type_combo:focus {
                border-color: #6366F1;
            }
            
            QComboBox#asset_type_combo::drop-down {
                border: none;
            }
            
            QComboBox#asset_type_combo::down-arrow {
                image: none;
                border: none;
            }
            
            QPushButton#create_button {
                background-color: #6366F1;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 12px 24px;
            }
            
            QPushButton#create_button:hover {
                background-color: #5B5BD6;
            }
            
            QPushButton#create_button:pressed {
                background-color: #4F46E5;
            }
            
            QPushButton#cancel_button {
                background-color: transparent;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                color: #374151;
                font-size: 14px;
                font-weight: 500;
                padding: 12px 24px;
            }
            
            QPushButton#cancel_button:hover {
                background-color: #F3F4F6;
                border-color: #6366F1;
            }
        """)
    
    def set_theme(self, theme):
        self.current_theme = theme
        self.setup_theme()
    
    def create_asset(self):
        """Creates asset folders with department subfolders and software templates"""
        asset_name = self.asset_name_line_edit.text().strip()
        
        if not asset_name:
            QMessageBox.warning(self, "Error", "Asset name is required.")
            return
        
        selected_types = [cb for cb in self.asset_type_checkboxes if cb.isChecked()]
        if not selected_types:
            QMessageBox.warning(self, "Error", "Please select at least one asset type.")
            return
        
        try:
            created_assets = []
            
            for type_cb in selected_types:
                asset_type_folder = type_cb.text()
                asset_path = os.path.join(CURRENT_PROJECT, "04_asset", asset_type_folder, asset_name)
                
                if os.path.exists(asset_path):
                    QMessageBox.warning(self, "Error", f"Asset '{asset_name}' already exists in '{asset_type_folder}'.")
                    continue
                
                os.makedirs(asset_path, exist_ok=True)
                
                dept_folder_mapping = {
                    'Geometry': 'geo',
                    'LookDev': 'ldv',
                    'Rigging': 'rig'
                }
                
                for dept_cb, dept_combo in self.department_list:
                    if dept_cb.isChecked():
                        dept_display_name = dept_cb.text()
                        dept_folder_name = dept_folder_mapping.get(dept_display_name, dept_display_name.lower())
                        dept_path = os.path.join(asset_path, dept_folder_name)
                        os.makedirs(dept_path, exist_ok=True)
                
                self.copy_software_templates(asset_name, asset_path)
                created_assets.append(f"{asset_type_folder}/{asset_name}")
            
            if created_assets:
                from Packages.utils.notification_utils import add_notification, get_username
                username = get_username()
                add_notification(username, "create_asset", asset_name)
                
                success_msg = f"Asset '{asset_name}' created successfully in:\n\n" + "\n".join(created_assets)
                QMessageBox.information(self, "Success", success_msg)
                
                self.asset_created.emit(asset_name)
                self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating asset: {str(e)}")
    
    def create_software_project_structure(self, dept_path, software_name):
        """Creates software-specific folder structures (Maya workspace, Houdini hip/geo, etc.)"""
        software_structures = {
            'Maya': [
                'scenes',
                'sourceimages',
                'images',
                'data',
                'movies',
                'scripts',
                'sound',
                'clips',
                'cache',
                'assets'
            ],
            'Houdini': [
                'hip',
                'geo',
                'sim',
                'render',
                'comp',
                'scripts',
                'otls',
                'backup',
                'tex'
            ],
            'Blender': [
                'blend',
                'textures',
                'renders',
                'cache',
                'scripts',
                'libraries'
            ],
            'ZBrush': [
                'projects',
                'exports',
                'references'
            ],
            'Cinema 4D': [
                'scenes',
                'tex',
                'lib',
                'render',
                'scripts'
            ]
        }
        
        if software_name in software_structures:
            for subfolder in software_structures[software_name]:
                subfolder_path = os.path.join(dept_path, subfolder)
                os.makedirs(subfolder_path, exist_ok=True)
    
    def copy_software_templates(self, asset_name, asset_path):
        """Copies template files for selected software per department"""
        pipezer_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        template_dir = os.path.join(pipezer_root, "template")
        
        if not os.path.exists(template_dir):
            print(f"Template directory not found: {template_dir}")
            return
        
        software_mapping = {
            'Maya': ('maya_template.ma', '.ma', 'scenes'),
            'Houdini': ('houdini_template.hiplc', '.hiplc', 'hip'),
            'Blender': ('blender_template.blend', '.blend', 'blend'),
            'ZBrush': ('zbrush_template.zbr', '.zbr', 'projects'),
            'Cinema 4D': ('cinema4D_template.c4d', '.c4d', 'scenes'),
            'None': (None, None, None)
        }
        
        dept_folder_mapping = {
            'Geometry': 'geo',
            'LookDev': 'ldv',
            'Rigging': 'rig'
        }
        
        for dept_cb, dept_combo in self.department_list:
            if dept_cb.isChecked():
                dept_display_name = dept_cb.text()
                dept_folder_name = dept_folder_mapping.get(dept_display_name, dept_display_name.lower())
                software_name = dept_combo.currentText()
                
                if software_name in software_mapping and software_name != 'None':
                    template_file, extension, target_subfolder = software_mapping[software_name]
                    
                    if template_file and target_subfolder:
                        dept_path = os.path.join(asset_path, dept_folder_name)
                        self.create_software_project_structure(dept_path, software_name)
                        source_path = os.path.join(template_dir, template_file)
                        
                        if os.path.exists(source_path):
                            target_folder = os.path.join(dept_path, target_subfolder)
                            dest_filename = f"{asset_name}_{dept_folder_name}_E_001{extension}"
                            dest_path = os.path.join(target_folder, dest_filename)
                            shutil.copy(source_path, dest_path)
                            print(f"Template copied: {source_path} → {dest_path}")
                        else:
                            print(f"Template file not found: {source_path}")
                            QMessageBox.warning(
                                self,
                                "Template Missing",
                                f"Template file for {software_name} not found:\n{template_file}\n\nDepartment '{dept_folder_name}' created without template."
                            )
    
    def center_on_screen(self):
        from PySide2.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
