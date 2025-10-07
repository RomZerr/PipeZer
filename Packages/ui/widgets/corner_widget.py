from PySide2.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMessageBox, QLabel
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt, QSize
import json
import os

NOTIF_FILE_PATH = r"\\Storage01\3D4\nordicPhone\.pipezer_data\notifs.json"

class CornerWidget(QWidget):
    """
    Widget personnalisé pour afficher une icône utilisateur, un label et un bouton de notification.
    """

    def __init__(self, parent=None, label_text: str = ''):
        super(CornerWidget, self).__init__(parent)

        # Create layout
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 10, 0)

        # Create label
        self.label_pixmap = QLabel()  # Utilisation de QLabel temporaire si CustomLabel pose problème
        self.label_pixmap.setObjectName("user_icon_label")
        self.label = QLabel(label_text)
        self.label.setObjectName("user_label")
        self.main_layout.addWidget(self.label)

        # Create Notifications button with an icon
        self.notifications_button = QPushButton()
        self.notifications_button.setObjectName("notifications_button")
        self.notifications_button.setIcon(QIcon(r"C:\Program Files\PipeZer\ProjectFiles\Icons\alerts.png"))
        self.notifications_button.setIconSize(QSize(24, 24))  # Adjust icon size
        self.notifications_button.setToolTip("Afficher les notifications")
        self.notifications_button.setFlat(True)  # Removes button border
        self.notifications_button.clicked.connect(self.show_notifications)
        self.main_layout.addWidget(self.notifications_button)

    def show_notifications(self):
        """
        Charge et affiche les notifications depuis notifs.json.
        """
        if not os.path.exists(NOTIF_FILE_PATH):
            QMessageBox.warning(self, "Aucune notification", "Aucune notification trouvée.")
            return

        try:
            with open(NOTIF_FILE_PATH, 'r') as notif_file:
                notifications = json.load(notif_file)

            if not notifications:
                QMessageBox.information(self, "Aucune notification", "Aucune notification disponible.")
                return

            # Construire le message formaté avec HTML
            message = "<div style='font-size: 14px;'>"
            for index, notif in enumerate(notifications):
                username = notif.get("username", "Inconnu")
                action = notif.get("action", "fait une action")
                file_name = notif.get("file", "un fichier")
                timestamp = notif.get("timestamp", "Date inconnue")  # Récupérer la date et l'heure

                if action == "create_asset":
                    color = "#ff443e"  # Rouge
                elif action == "create_shot":
                    color = "#00aaff"  # Bleu
                else:
                    color = "#d1a024"  # Jaune

                # Gestion spécifique pour `create_shot` avec "de la"
                if action == "create_shot" and "de la" in file_name:
                    parts = file_name.split("de la")
                    formatted_file_name = (
                        f"<b style='color: {color};'>{parts[0].strip()}</b> de la "
                        f"<b style='color: {color};'>{parts[1].strip()}</b>"
                    )
                else:
                    formatted_file_name = f"<b style='color: {color};'>{file_name}</b>"

                # Formater chaque notification
                message += (
                    f"<b>{username}</b> a "
                    f"<i>{action}</i> sur {formatted_file_name}<br>"
                    f"<small style='color: gray;'>Le {timestamp}</small><br>"
                )

                # Ajouter une ligne de séparation sauf pour la dernière notification
                if index < len(notifications) - 1:
                    message += "<hr style='border: 10px solid lightgray;'>"

            message += "</div>"

            # Utiliser une boîte de dialogue personnalisée avec QScrollArea
            from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QPushButton

            dialog = QDialog(self)
            dialog.setWindowTitle("Notifications")
            dialog.setFixedSize(400, 600)  # Taille fixe pour empêcher l'agrandissement

            layout = QVBoxLayout(dialog)

            # Ajouter un QScrollArea pour gérer le défilement
            scroll_area = QScrollArea(dialog)
            scroll_area.setWidgetResizable(True)

            # Ajouter le contenu HTML dans un QLabel
            label = QLabel(message, scroll_area)
            label.setTextFormat(Qt.RichText)  # Permet le formatage HTML
            label.setWordWrap(True)

            scroll_area.setWidget(label)
            layout.addWidget(scroll_area)

            # Ajouter un bouton de fermeture
            close_button = QPushButton("Fermer", dialog)
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)

            dialog.setLayout(layout)
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger les notifications : {str(e)}")

