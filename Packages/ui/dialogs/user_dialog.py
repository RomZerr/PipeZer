from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class UserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Username")

        # Layout
        layout = QVBoxLayout()

        # Label
        self.label = QLabel("Please enter your username:")
        layout.addWidget(self.label)

        # Line edit to enter the username
        self.username_edit = QLineEdit(self)
        layout.addWidget(self.username_edit)

        # OK button
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def get_username(self):
        return self.username_edit.text()
