"""
Widget de bouton de navigation avec drag & drop et menu contextuel
"""

from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu, QInputDialog, QSizePolicy
from PySide2.QtCore import Qt, Signal, QMimeData, QPoint
from PySide2.QtGui import QDrag, QCursor


class DraggableNavButton(QWidget):
    """
    Bouton de navigation avec support du drag & drop et menu contextuel
    """
    
    # Signaux
    clicked = Signal()
    renamed = Signal(str)  # Émet le nouveau nom
    deleted = Signal()  # Demande la suppression
    drag_started = Signal()
    
    def __init__(self, icon_text, label_text, button_id, parent=None):
        super().__init__(parent)
        
        self.button_id = button_id
        self.icon_text = icon_text
        self.label_text = label_text
        self.is_custom = button_id.startswith('custom_')  # Garder pour savoir si on peut supprimer
        
        # Position de départ du drag
        self.drag_start_position = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface du bouton - EXACTEMENT comme l'original"""
        # Copier le design exact de create_nav_button de modern_main_window.py
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # Layout principal (horizontal comme l'original)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Bouton principal
        self.button = QPushButton()
        self.button.setObjectName(f"nav_button_{self.button_id}")
        self.button.setCheckable(True)
        self.button.setFocusPolicy(Qt.NoFocus)
        self.button.setMinimumHeight(36)
        
        # Layout du bouton (vertical pour icône + texte)
        button_layout = QVBoxLayout(self.button)
        button_layout.setContentsMargins(10, 8, 10, 8)
        button_layout.setSpacing(5)
        
        # Label pour l'icône (si présente)
        if self.icon_text:
            self.icon_label = QLabel(self.icon_text)
            self.icon_label.setObjectName("nav_icon")
            self.icon_label.setAlignment(Qt.AlignCenter)
            button_layout.addWidget(self.icon_label)
        else:
            self.icon_label = None
        
        # Label pour le texte
        self.text_label = QLabel(self.label_text)
        self.text_label.setObjectName("nav_text")
        self.text_label.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(self.text_label)
        
        # Ajouter le bouton au layout principal
        main_layout.addWidget(self.button)
        
        # Point de notification
        self.notification_dot = QLabel("●")
        self.notification_dot.setObjectName("notification_dot")
        self.notification_dot.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.notification_dot.hide()
        
        # Connecter le clic
        self.button.clicked.connect(self.clicked.emit)
        
        # Activer le contexte menu pour TOUS les boutons
        self.button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.button.customContextMenuRequested.connect(self.show_context_menu)
        
        # Installer un filtre d'événements sur le bouton pour intercepter les événements de souris
        self.button.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Filtre les événements pour gérer le drag depuis le bouton"""
        if obj == self.button:
            if event.type() == event.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self.drag_start_position = event.pos()
            
            elif event.type() == event.MouseMove:
                if (event.buttons() & Qt.LeftButton) and self.drag_start_position:
                    # Vérifier si on a bougé suffisamment pour déclencher un drag
                    if (event.pos() - self.drag_start_position).manhattanLength() > 10:
                        # Créer le drag
                        drag = QDrag(self)
                        mime_data = QMimeData()
                        mime_data.setText(self.button_id)
                        drag.setMimeData(mime_data)
                        
                        # Émettre le signal
                        self.drag_started.emit()
                        
                        # Exécuter le drag
                        drag.exec_(Qt.MoveAction)
                        
                        # Réinitialiser
                        self.drag_start_position = None
                        return True  # Événement géré
        
        return super().eventFilter(obj, event)
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel pour renommer/supprimer - pour TOUS les boutons"""
        menu = QMenu(self)
        
        # Action Renommer (pour tous)
        rename_action = menu.addAction("✏️ Renommer")
        
        # Action Supprimer (seulement pour les custom)
        delete_action = None
        if self.is_custom:
            # Séparateur
            menu.addSeparator()
            # Action Supprimer
            delete_action = menu.addAction("🗑️ Supprimer")
        
        # Afficher le menu et récupérer l'action choisie
        action = menu.exec_(self.button.mapToGlobal(position))
        
        if action == rename_action:
            self.rename_shortcut()
        elif action == delete_action and self.is_custom:
            self.delete_shortcut()
    
    def rename_shortcut(self):
        """Demande un nouveau nom pour le raccourci"""
        new_name, ok = QInputDialog.getText(
            self,
            "Renommer le raccourci",
            "Nouveau nom :",
            text=self.label_text
        )
        
        if ok and new_name and new_name != self.label_text:
            self.label_text = new_name
            self.text_label.setText(new_name)
            self.renamed.emit(new_name)
    
    def delete_shortcut(self):
        """Demande la suppression du raccourci"""
        from PySide2.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Supprimer le raccourci",
            f"Voulez-vous vraiment supprimer le raccourci '{self.label_text}' ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.deleted.emit()
    
    def set_checked(self, checked):
        """Définit l'état coché du bouton"""
        self.button.setChecked(checked)

