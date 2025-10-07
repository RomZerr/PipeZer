from PySide2.QtWidgets import QListWidget, QListWidgetItem

class FilteredListWidget(QListWidget):
    def __init__(self, parent=None):
        super(FilteredListWidget, self).__init__(parent)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.itemSelectionChanged.connect(self.filter_selection_changed)

    def populate_with_unique_names(self, files):
        """
        Remplit la liste avec des noms uniques extraits des noms de fichiers.
        """
        unique_names = set()
        for file in files:
            # Extraire le nom après 'anim_' et avant '_<version>'
            parts = file.split('_')
            if len(parts) >= 4:
                name = parts[3]  # Exemple: 'Bjork' ou 'Fabrice'
                unique_names.add(name)

        self.clear()
        for name in sorted(unique_names):
            self.addItem(QListWidgetItem(name))

    def filter_selection_changed(self):
        """
        Fonction à appeler lorsque la sélection change.
        """
        selected_items = self.selectedItems()
        if selected_items:
            name = selected_items[0].text()
            self.parent().filter_files_by_name(name)
