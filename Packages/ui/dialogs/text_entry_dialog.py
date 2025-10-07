from PySide2.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QPushButton
from PySide2.QtGui import QTextCursor


class TextEntryDialog(QDialog):
    def __init__(self, parent=None, text='', title=''):
        super(TextEntryDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.text_edit = QTextEdit(self)
        self.text_edit.setText(text)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Ajouter le QTextEdit à la mise en page
        layout.addWidget(self.text_edit)

        # Placer le curseur à la fin du texte
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)  # Utilisation correcte de QTextCursor.End
        self.text_edit.setTextCursor(cursor)

        # Ajouter un bouton de validation
        self.button = QPushButton("OK", self)
        layout.addWidget(self.button)
        self.button.clicked.connect(self.accept)

    def get_entered_text(self):
        # Renvoyer le texte saisi par l'utilisateur
        return self.text_edit.toPlainText()
