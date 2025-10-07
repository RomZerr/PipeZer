import os
import shutil
import json
from datetime import datetime

from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont

from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT

NOTIF_FILE_PATH = os.path.join(CURRENT_PROJECT, '.pipezer_data', 'notifs.json')

def add_notification(username, action, file_name):
    """
    Ajoute une notification dans le fichier JSON.
    """
    notification = {
        "username": username,
        "action": action,
        "file": file_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formatage de la date et heure
    }

    try:
        # Charger les notifications existantes
        if os.path.exists(NOTIF_FILE_PATH):
            with open(NOTIF_FILE_PATH, 'r') as notif_file:
                data = json.load(notif_file)
                if not isinstance(data, list):
                    print("Format de données invalides dans notifs.json. Réinitialisation.")
                    data = []
        else:
            data = []

        # Ajouter la nouvelle notification
        data.append(notification)

        # Sauvegarder les notifications mises à jour
        with open(NOTIF_FILE_PATH, 'w') as notif_file:
            json.dump(data, notif_file, indent=4)

        print(f"Notification ajoutée : {notification}")

    except Exception as e:
        print(f"Erreur lors de l'ajout d'une notification : {e}")


def get_username():
    """
    Récupère le nom d'utilisateur depuis user.json ou utilise le nom par défaut.
    """
    user_home_dir = os.path.expanduser("~")
    pipezer_dir = os.path.join(user_home_dir, '.pipezer')
    user_file_path = os.path.join(pipezer_dir, 'user.json')

    try:
        if os.path.exists(user_file_path):
            print(f"Chargement de {user_file_path} pour récupérer le nom d'utilisateur.")
            with open(user_file_path, 'r') as user_file:
                data = json.load(user_file)
                username = data.get("username")
                if username:
                    print(f"Nom d'utilisateur trouvé dans user.json : {username}")
                    return username
                else:
                    print("Clé 'username' absente dans user.json.")
        else:
            print(f"Fichier user.json introuvable à : {user_file_path}")
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur : {e}")

    # Retour par défaut si user.json est absent ou invalide
    default_username = os.getenv("USERNAME", "unknown_user")
    print(f"Utilisation du nom par défaut : {default_username}")
    return default_username


class CreateShotDialog(QDialog):
    def __init__(self, parent=None):
        super(CreateShotDialog, self).__init__(parent)
        self.setWindowTitle("Create Shot")
        self.setGeometry(300, 200, 400, 200)

        # Définir la police plus grande
        font = QFont()
        font.setPointSize(10)

        # Layout principal
        layout = QVBoxLayout()

        # Ligne pour entrer le numéro de séquence (label et input sur la même ligne)
        sequence_layout = QHBoxLayout()
        self.sequence_label = QLabel('SEQUENCE:')
        self.sequence_label.setFont(font)
        self.sequence_input = QLineEdit()
        self.sequence_input.setFont(font)
        self.sequence_input.setPlaceholderText('XXXX')
        sequence_layout.addWidget(self.sequence_label)
        sequence_layout.addWidget(self.sequence_input)
        layout.addLayout(sequence_layout)

        # Ligne pour entrer le numéro de shot (label et input sur la même ligne)
        shot_layout = QHBoxLayout()
        self.shot_label = QLabel('SHOT:')
        self.shot_label.setFont(font)
        self.shot_input = QLineEdit()
        self.shot_input.setFont(font)
        self.shot_input.setPlaceholderText('XXXX')
        shot_layout.addWidget(self.shot_label)
        shot_layout.addWidget(self.shot_input)
        layout.addLayout(shot_layout)

        # Bouton pour créer le shot
        self.create_button = QPushButton("Créer Shot")
        self.create_button.setFont(font)
        self.create_button.setFixedSize(200, 60)
        self.create_button.clicked.connect(self.create_shot)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_shot(self):
        sequence_number = self.sequence_input.text().strip()
        shot_number = self.shot_input.text().strip()

        if not self.validate_input(sequence_number, shot_number):
            return

        sequence = f"sq{sequence_number}"
        shot = f"sh{shot_number}"

        # Utiliser CURRENT_PROJECT pour le chemin de base
        base_path = os.path.join(CURRENT_PROJECT, "05_shot")
        sequence_folder = os.path.join(base_path, sequence)
        shot_folder = os.path.join(sequence_folder, f"{sequence}_{shot}")

        try:
            # Créer le dossier 05_shot s'il n'existe pas
            os.makedirs(base_path, exist_ok=True)
            # Créer les dossiers nécessaires
            self.create_sequence_folders(sequence_folder)
            os.makedirs(shot_folder, exist_ok=True)
            self.create_shot_subfolders(shot_folder)

            # Ajouter une notification
            username = get_username()
            add_notification(username, "create_shot", f"{shot} de la {sequence}")

            # Message de succès
            QMessageBox.information(self, "Succès", f"Shot '{sequence}_{shot}' créé avec succès!")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la création du shot: {str(e)}")

        self.accept()

    def validate_input(self, sequence_number, shot_number):
        if not sequence_number.isdigit() or len(sequence_number) != 4:
            QMessageBox.warning(self, "Erreur", "Le numéro de séquence doit être un nombre de 4 chiffres (ex: 0020).")
            return False
        if not shot_number.isdigit() or len(shot_number) != 4:
            QMessageBox.warning(self, "Erreur", "Le numéro de shot doit être un nombre de 4 chiffres (ex: 0010).")
            return False
        return True

    def create_sequence_folders(self, sequence_folder):
        master_folder = os.path.join(sequence_folder, f"{os.path.basename(sequence_folder)}_master")
        multi_shot_folder = os.path.join(sequence_folder, f"{os.path.basename(sequence_folder)}_multiShot")

        if not os.path.exists(master_folder):
            os.makedirs(master_folder)
            self.create_master_subfolders(master_folder)

        if not os.path.exists(multi_shot_folder):
            os.makedirs(multi_shot_folder)
            self.create_multi_shot_subfolders(multi_shot_folder)

    def create_master_subfolders(self, master_folder):
        subfolders = [
            "camera",
            "houdini/layout",
            "houdini/lighting",
            "usd"
        ]

        layout_template = os.path.join(CURRENT_PROJECT, "02_ressource", "Template_scenes", "Houdini", "NOR_master_layout.hipnc")
        lighting_template = os.path.join(CURRENT_PROJECT, "02_ressource", "Template_scenes", "Houdini", "NOR_master_lighting.hipnc")
        sequence_number = os.path.basename(master_folder).split('_')[0]

        for subfolder in subfolders:
            os.makedirs(os.path.join(master_folder, subfolder), exist_ok=True)

        if not self.copy_and_rename_file(layout_template, os.path.join(master_folder, "houdini/layout"), f"NOR_{sequence_number}_master_layout_E_001.hip"):
            return
        if not self.copy_and_rename_file(lighting_template, os.path.join(master_folder, "houdini/lighting"), f"NOR_{sequence_number}_master_lighting_E_001.hip"):
            return

    def create_multi_shot_subfolders(self, multi_shot_folder):
        subfolders = [
            "camera",
            "houdini/conformity",
            "houdini/layout"
        ]

        conformity_template = os.path.join(CURRENT_PROJECT, "02_ressource", "Template_scenes", "Houdini", "NOR_multiShot_conformity.hipnc")
        layout_template = os.path.join(CURRENT_PROJECT, "02_ressource", "Template_scenes", "Houdini", "NOR_multiShot_layout.hipnc")
        sequence_number = os.path.basename(multi_shot_folder).split('_')[0]

        for subfolder in subfolders:
            os.makedirs(os.path.join(multi_shot_folder, subfolder), exist_ok=True)

        if not self.copy_and_rename_file(conformity_template, os.path.join(multi_shot_folder, "houdini/conformity"), f"NOR_{sequence_number}_multiShot_conformity_E_001.hip"):
            return
        if not self.copy_and_rename_file(layout_template, os.path.join(multi_shot_folder, "houdini/layout"), f"NOR_{sequence_number}_multiShot_layout_E_001.hip"):
            return

    def copy_and_rename_file(self, source_file, destination_folder, new_filename):
        if os.path.exists(source_file):
            os.makedirs(destination_folder, exist_ok=True)
            destination_file = os.path.join(destination_folder, new_filename)
            shutil.copy(source_file, destination_file)
            print(f"Fichier copié : {source_file} → {destination_file}")
        else:
            print(f"Le fichier template est introuvable : {source_file}")
            # Demander à l'utilisateur s'il veut continuer sans template
            reply = QMessageBox.question(
                self, 
                'Template manquant', 
                f'Le template "{os.path.basename(source_file)}" est introuvable.\nVoulez-vous continuer sans ce template ?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.No:
                return False
        return True

    def create_shot_subfolders(self, shot_folder):
        shot_number = self.shot_input.text().strip()

        subfolders = [
            "camera",
            "houdini/fx", "houdini/groom", "houdini/render",
            "maya/data", "maya/playblast", "maya/scene/anim",
            "nuke/input/3D", "nuke/output", "nuke/input/2D",
            "usd/anim", "usd/groom", "usd/fx", "usd/conformity", "usd/render", "usd/groom/curves", "usd/layout",
            "render/CHARA_BEAUTY", "render/PROPS_SHADOWS","render/PROPS_INTEGRATOR","render/MOTION_BLUR","render/logs",
            "render/GROOM_INTEGRATOR", "render/FX_SHADOWS","render/FX_INTEGRATOR","render/FOG_INTEGRATOR","render/ENV_INTEGRATOR",
            "render/CHARA_SHADOWS","render/CHARA_INTEGRATOR", "render/CARDS_INTEGRATOR", "render/GROOM_BEAUTY", "render/PROPS_BEAUTY",
            "render/cryptomattes", "render/CARDS_BEAUTY", "render/ENV_BEAUTY", "render/FX_BEAUTY", "render/FOG_BEAUTY"
        ]

        anim_template = os.path.join(CURRENT_PROJECT, "02_ressource", "Template_scenes", "Maya", "NOR_anim_template.ma")
        lighting_template = os.path.join(CURRENT_PROJECT, "02_ressource", "Template_scenes", "Houdini", "NOR_multiShot_lighting.hipnc")
        render_template = os.path.join(CURRENT_PROJECT, "02_ressource", "Template_scenes", "Houdini", "NOR_multiShot_render.hipnc")
        sequence_number = os.path.basename(shot_folder).split('_')[0]

        for subfolder in subfolders:
            os.makedirs(os.path.join(shot_folder, subfolder), exist_ok=True)

        if not self.copy_and_rename_file(anim_template, os.path.join(shot_folder, "maya/scene/anim"),f"NOR_{sequence_number}_{shot_number}_anim_E_001.ma"):
            return
        if not self.copy_and_rename_file(lighting_template, os.path.join(shot_folder, "houdini/lighting"),f"NOR_{sequence_number}_{shot_number}_lighting_E_001.hipnc"):
            return
        if not self.copy_and_rename_file(render_template, os.path.join(shot_folder, "houdini/render"), f"NOR_{sequence_number}_{shot_number}_render_E_001.hipnc"):
            return


