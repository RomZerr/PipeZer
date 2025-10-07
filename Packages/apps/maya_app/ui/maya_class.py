from PySide2.QtWidgets import QLabel
from Packages.apps.maya_app.ui.maya_button_widget import MayaButtonWidget
from Packages.ui.base_main_window import BaseMainWindow
from Packages.apps.maya_app.ui.maya_main_window import maya_main_window
from Packages.logic.json_funcs import get_recent_files

class MayaPipeZer(BaseMainWindow):
    
    def __init__(self, parent = maya_main_window()):
        super(MayaPipeZer, self).__init__(parent)
        
        self.move_main_window(parent)
        print(0)
        # TEMP
        maya_tools_label = QLabel("Maya Tools")
        print(0.1)
        maya_tools_label.setStyleSheet("color: #ffffff; font-size: 16px;")
        print(0.2)
        maya_tools_label.setMinimumHeight(25)
        print(0.3)
        self.tool_layout.addWidget(maya_tools_label)
        print(0.4)

    def create_widgets(self):
        print(1)
        super().create_widgets()
        self.maya_button_widget = MayaButtonWidget()
        self.recent_maya_button_widget = MayaButtonWidget()

    def create_layout(self):
        print(2)
        super().create_layout()
        self._browser_file_layout.addWidget(self.maya_button_widget)
        self._recent_file_layout.addWidget(self.recent_maya_button_widget)
        self._search_file_layout.addWidget(self.recent_maya_button_widget)

    def create_connections(self):
        print(3)
        super().create_connections()
        self.maya_button_widget.maya_button.clicked.connect(self.get_maya_file)
        self.recent_maya_button_widget.maya_button.clicked.connect(self.get_maya_file)
        
    def on_recent_tab_active(self):
        print(4)
        super().on_recent_tab_active()
        recent_files = get_recent_files(ext = ['.ma', '.mb', '.obj', '.fbx', '.abc'])
        self._recent_file_table.update_file_items(recent_files)
        
    def populate_list_01(self, tree_item, column):
        print(5)
        super().populate_list_01(tree_item, column)
        
        self._select_item_from_text(self.list_01, 'maya'.capitalize())

    def populate_list_02(self, parent_directory: str):
        print(6)
        super().populate_list_02(parent_directory)
        self._select_item_from_text(self.list_01, 'scenes'.capitalize())

    def get_maya_file(self):
        print(7)
        if self.maya_button_widget.maya_button.mode in ['import custom namespace', 'reference custom namespace']:
            custom_namespace = self.maya_button_widget._field_custom_namspace.text()
            self.maya_button_widget.maya_button.get_file(file_path = self.status_bar.get_text(), custom_namespace = custom_namespace)

        else:
            self.maya_button_widget.maya_button.get_file(file_path = self.status_bar.get_text())
