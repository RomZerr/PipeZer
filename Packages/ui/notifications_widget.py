"""
Widget de notifications moderne
"""

from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QListWidget, QListWidgetItem
)
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QFont, QIcon

from Packages.ui.base_main_window import get_username


class NotificationItem(QFrame):
    """Widget pour un élément de notification"""
    
    def __init__(self, title, message, notification_type="info", parent=None):
        super().__init__(parent)
        self.setup_ui(title, message, notification_type)
        
    def setup_ui(self, title, message, notification_type):
        """Configure l'interface de la notification"""
        self.setObjectName("notification_item")
        self.setFixedHeight(80)
        
        # Layout principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # Icône selon le type
        icon_map = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✗"
        }
        
        icon_label = QLabel(icon_map.get(notification_type, "ℹ"))
        icon_label.setObjectName("notification_icon")
        icon_label.setFixedSize(30, 30)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.get_icon_color(notification_type)};
                border-radius: 15px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        
        # Contenu de la notification
        content_layout = QVBoxLayout()
        content_layout.setSpacing(5)
        
        # Titre
        title_label = QLabel(title)
        title_label.setObjectName("notification_title")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        # Message
        message_label = QLabel(message)
        message_label.setObjectName("notification_message")
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                color: #A0A0A0;
                font-size: 12px;
            }
        """)
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(message_label)
        
        # Bouton de fermeture
        close_button = QPushButton("×")
        close_button.setObjectName("close_button")
        close_button.setFixedSize(25, 25)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #A0A0A0;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: #3C3C4F;
                border-radius: 12px;
            }
        """)
        close_button.clicked.connect(self.close_notification)
        
        # Ajouter au layout
        layout.addWidget(icon_label)
        layout.addLayout(content_layout)
        layout.addStretch()
        layout.addWidget(close_button)
        
    def get_icon_color(self, notification_type):
        """Retourne la couleur de l'icône selon le type"""
        color_map = {
            "info": "#3B82F6",
            "success": "#22C55E",
            "warning": "#F59E0B",
            "error": "#EF4444"
        }
        return color_map.get(notification_type, "#3B82F6")
        
    def close_notification(self):
        """Ferme la notification"""
        self.hide()
        self.deleteLater()


class NotificationsWidget(QWidget):
    """
    Widget de notifications moderne
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_style()
        
        # Charger les notifications existantes
        self.load_notifications()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Titre
        title_layout = QHBoxLayout()
        
        title_label = QLabel("🔔 Notifications")
        title_label.setObjectName("notifications_title")
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        # Bouton pour marquer tout comme lu
        mark_all_read_button = QPushButton("Mark all as read")
        mark_all_read_button.setObjectName("mark_all_read_button")
        mark_all_read_button.setStyleSheet("""
            QPushButton {
                background-color: #4A3B66;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 12px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #5A4B76;
            }
        """)
        mark_all_read_button.clicked.connect(self.mark_all_as_read)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(mark_all_read_button)
        
        main_layout.addLayout(title_layout)
        
        # Zone de défilement pour les notifications
        scroll_area = QScrollArea()
        scroll_area.setObjectName("notifications_scroll")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget de contenu pour les notifications
        self.notifications_content = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_content)
        self.notifications_layout.setContentsMargins(0, 0, 0, 0)
        self.notifications_layout.setSpacing(10)
        
        scroll_area.setWidget(self.notifications_content)
        main_layout.addWidget(scroll_area)
        
        # Message si aucune notification
        self.no_notifications_label = QLabel("No notifications")
        self.no_notifications_label.setObjectName("no_notifications")
        self.no_notifications_label.setAlignment(Qt.AlignCenter)
        self.no_notifications_label.setStyleSheet("""
            QLabel {
                color: #A0A0A0;
                font-size: 16px;
                padding: 40px;
            }
        """)
        self.notifications_layout.addWidget(self.no_notifications_label)
        
    def setup_style(self):
        """Configuration du style"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E2E;
            }
            
            QScrollArea#notifications_scroll {
                background-color: transparent;
                border: none;
            }
            
            QScrollBar:vertical {
                background-color: #3C3C4F;
                width: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #4A3B66;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #5A4B76;
            }
            
            QFrame#notification_item {
                background-color: #2D2D44;
                border: 1px solid #3C3C4F;
                border-radius: 8px;
            }
            
            QFrame#notification_item:hover {
                background-color: #3C3C4F;
            }
        """)
        
    def load_notifications(self):
        """Charge les notifications existantes"""
        # Pour l'instant, créer quelques notifications d'exemple
        self.add_notification("Welcome!", f"Welcome to PipeZer, {get_username()}!", "success")
        self.add_notification("System Ready", "All systems are operational", "info")
        
    def add_notification(self, title, message, notification_type="info"):
        """Ajoute une nouvelle notification"""
        # Masquer le message "no notifications" s'il est visible
        if self.no_notifications_label.isVisible():
            self.no_notifications_label.hide()
            
        # Créer la notification
        notification = NotificationItem(title, message, notification_type, self)
        self.notifications_layout.addWidget(notification)
        
    def mark_all_as_read(self):
        """Marque toutes les notifications comme lues"""
        # Supprimer toutes les notifications
        for i in reversed(range(self.notifications_layout.count())):
            item = self.notifications_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
                
        # Afficher le message "no notifications"
        self.no_notifications_label.show()
        
    def clear_notifications(self):
        """Efface toutes les notifications"""
        self.mark_all_as_read()
