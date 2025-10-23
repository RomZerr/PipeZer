"""
Container pour la sidebar avec support du drag & drop pour réorganiser les boutons
"""

from PySide2.QtWidgets import QWidget, QVBoxLayout, QFrame
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QPainter, QColor


class DraggableSidebarContainer(QWidget):
    """
    Container qui gère le drag & drop pour réorganiser les boutons
    """
    
    # Signal émis quand l'ordre des boutons change
    order_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout pour les boutons
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)  # Réduit de 18 à 8
        
        # Liste des widgets de boutons
        self.button_widgets = []
        
        # Position de drop actuelle
        self.drop_index = -1
        
        # Activer le drop
        self.setAcceptDrops(True)
        
    def add_button_widget(self, button_widget):
        """Ajoute un widget de bouton au container"""
        self.button_widgets.append(button_widget)
        self.layout.addWidget(button_widget)
        
        # Connecter le signal de drag
        button_widget.drag_started.connect(lambda: self.on_drag_started(button_widget))
    
    def insert_button_widget(self, index, button_widget):
        """Insère un widget de bouton à une position spécifique"""
        self.button_widgets.insert(index, button_widget)
        self.layout.insertWidget(index, button_widget)
        
        # Connecter le signal de drag
        button_widget.drag_started.connect(lambda: self.on_drag_started(button_widget))
    
    def remove_button_widget(self, button_widget):
        """Supprime un widget de bouton"""
        if button_widget in self.button_widgets:
            self.button_widgets.remove(button_widget)
            self.layout.removeWidget(button_widget)
            button_widget.setParent(None)
            button_widget.deleteLater()
    
    def on_drag_started(self, button_widget):
        """Quand un drag commence, stocker le widget source"""
        self.dragged_widget = button_widget
    
    def dragEnterEvent(self, event):
        """Accepte le drag pour TOUS les boutons"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """Calcule où insérer le bouton pendant le drag"""
        if not event.mimeData().hasText():
            return
        
        # Trouver l'index où on devrait insérer le bouton
        drop_y = event.pos().y()
        self.drop_index = self.calculate_drop_index(drop_y)
        
        # Forcer le redessin pour montrer l'indicateur de drop
        self.update()
        
        event.acceptProposedAction()
    
    def dragLeaveEvent(self, event):
        """Nettoie l'indicateur de drop quand on quitte la zone"""
        self.drop_index = -1
        self.update()
    
    def dropEvent(self, event):
        """Réorganise les boutons quand on drop - pour TOUS les boutons"""
        if not event.mimeData().hasText():
            return
        
        button_id = event.mimeData().text()
        
        # Trouver le widget source
        source_widget = None
        source_index = -1
        for i, widget in enumerate(self.button_widgets):
            if widget.button_id == button_id:
                source_widget = widget
                source_index = i
                break
        
        if source_widget is None or self.drop_index == -1:
            self.drop_index = -1
            self.update()
            return
        
        # Ajuster l'index de drop si on déplace vers le bas
        target_index = self.drop_index
        if source_index < target_index:
            target_index -= 1
        
        # Ne rien faire si on drop au même endroit
        if source_index == target_index:
            self.drop_index = -1
            self.update()
            return
        
        # Retirer le widget de sa position actuelle
        self.button_widgets.pop(source_index)
        self.layout.removeWidget(source_widget)
        
        # L'insérer à la nouvelle position
        self.button_widgets.insert(target_index, source_widget)
        self.layout.insertWidget(target_index, source_widget)
        
        # Réinitialiser l'indicateur de drop
        self.drop_index = -1
        self.update()
        
        # Émettre le signal de changement d'ordre
        self.order_changed.emit()
        
        event.acceptProposedAction()
    
    def calculate_drop_index(self, drop_y):
        """Calcule l'index où insérer le bouton basé sur la position Y"""
        if not self.button_widgets:
            return 0
        
        for i, widget in enumerate(self.button_widgets):
            widget_center_y = widget.y() + widget.height() / 2
            
            if drop_y < widget_center_y:
                return i
        
        # Si on est après tous les widgets, insérer à la fin
        return len(self.button_widgets)
    
    def paintEvent(self, event):
        """Dessine un indicateur de drop"""
        super().paintEvent(event)
        
        if self.drop_index >= 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Couleur de l'indicateur
            pen_color = QColor(99, 102, 241)  # Violet moderne
            painter.setPen(pen_color)
            
            # Calculer la position Y de l'indicateur
            if self.drop_index == 0:
                y = 0
            elif self.drop_index >= len(self.button_widgets):
                last_widget = self.button_widgets[-1]
                y = last_widget.y() + last_widget.height() + self.layout.spacing()
            else:
                widget = self.button_widgets[self.drop_index]
                y = widget.y()
            
            # Dessiner la ligne
            painter.drawLine(10, y, self.width() - 10, y)
            
            # Dessiner des petits cercles aux extrémités
            painter.setBrush(pen_color)
            painter.drawEllipse(5, y - 3, 6, 6)
            painter.drawEllipse(self.width() - 11, y - 3, 6, 6)
            
            painter.end()
    
    def get_button_order(self):
        """Retourne la liste ordonnée des button_ids"""
        return [widget.button_id for widget in self.button_widgets]

