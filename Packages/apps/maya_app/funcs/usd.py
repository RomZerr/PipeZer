import os
import re
import shutil
import json
from maya import mel, cmds
import maya.api.OpenMaya as om
from Packages.apps.maya_app.funcs import playblast
from Packages.logic.filefunc import publish_funcs
from Packages.logic.filefunc import get_funcs
from Packages.utils.funcs import forward_slash
from PySide2 import QtWidgets
from PySide2.QtWidgets import QFileDialog, QMessageBox

# Assurez-vous que le chemin de mayaUSD est ajouté à sys.path
import sys
import glob

# Chercher le chemin de mayaUSD dynamiquement
mayausd_paths = glob.glob('C:\\Program Files\\Autodesk\\MayaUSD\\Maya*\\*\\mayausd\\MayaUSD\\lib\\python')
if mayausd_paths and mayausd_paths[0] not in sys.path:
    sys.path.append(mayausd_paths[0])

# Essayez d'importer mayaUSD pour confirmer le chargement
try:
    import mayaUsd
    print("mayaUsd importé avec succès")
except ImportError as e:
    print("Erreur lors de l'import de mayaUsd:", e)

# Chemin vers le fichier de notifications (utiliser CURRENT_PROJECT)
from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT
NOTIF_FILE_PATH = os.path.join(CURRENT_PROJECT, '.pipezer_data', 'notifs.json')

def get_username():
    """
    Récupère le nom d'utilisateur depuis user.json ou utilise le nom par défaut.
    """
    user_home_dir = os.path.expanduser("~")
    pipezer_dir = os.path.join(user_home_dir, '.pipezer')
    user_file_path = os.path.join(pipezer_dir, 'user.json')

    print(f"Chemin complet pour user.json : {user_file_path}")

    try:
        if os.path.exists(user_file_path):
            print("Fichier user.json trouvé. Contenu :")
            with open(user_file_path, 'r') as user_file:
                data = json.load(user_file)
                print(f"Données chargées depuis user.json : {data}")
                username = data.get("username")
                if username:
                    print(f"Nom d'utilisateur extrait : {username}")
                    return username
                else:
                    print("Clé 'username' absente dans user.json.")
        else:
            print("Fichier user.json introuvable.")
    except Exception as e:
        print(f"Erreur lors de la lecture de user.json : {e}")

    # Retour par défaut si user.json est absent ou invalide
    default_username = os.getenv("USERNAME", "unknown_user")
    print(f"Utilisation du nom par défaut : {default_username}")
    return default_username


from datetime import datetime

def add_notification(username, action, file_name):
    """
    Ajoute une notification dans le fichier JSON.
    """
    print("Ajout d'une notification...")
    print(f"Username: {username}, Action: {action}, File: {file_name}")

    notification = {
        "username": username,
        "action": action,
        "file": file_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formatage de la date et heure
    }

    try:
        # Charger les notifications existantes
        if os.path.exists(NOTIF_FILE_PATH):
            print(f"Fichier {NOTIF_FILE_PATH} trouvé, chargement...")
            with open(NOTIF_FILE_PATH, 'r') as notif_file:
                data = json.load(notif_file)
        else:
            print(f"Fichier {NOTIF_FILE_PATH} non trouvé, création d'une nouvelle liste.")
            data = []

        # Ajouter la nouvelle notification
        data.append(notification)

        # Sauvegarder les notifications mises à jour
        with open(NOTIF_FILE_PATH, 'w') as notif_file:
            json.dump(data, notif_file, indent=4)

        print("Notification ajoutée avec succès :", notification)

    except Exception as e:
        print(f"Erreur lors de l'ajout d'une notification : {e}")


def confirm_overwrite(file_path):
    """Affiche une boîte de dialogue de confirmation si le fichier existe déjà."""
    message = "Un fichier USD existe déjà avec le même nom.\nVoulez-vous l'écraser ?"
    dialog = QtWidgets.QMessageBox()
    dialog.setIcon(QtWidgets.QMessageBox.Question)
    dialog.setWindowTitle("Confirmer l'écrasement")
    dialog.setText(message)
    dialog.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    response = dialog.exec_()
    return response == QtWidgets.QMessageBox.Yes


def export_usd(output_file_path: str, use_catmull_clark=True):
    """
    Exporte la sélection en USD avec ou sans Catmull Clark.
    """
    output_file_path = output_file_path.replace('\\', '/')
    selected_objects = cmds.ls(selection=True)
    if not selected_objects:
        om.MGlobal.displayError('Nothing is selected.')
        return

    cmds.undoInfo(openChunk=True)
    try:
        for obj in selected_objects:
            cmds.makeIdentity(obj, apply=True, scale=True, translate=True, rotate=True, normal=False)
            cmds.delete(obj, constructionHistory=True)
            cmds.xform(obj, worldSpace=True, pivots=(0, 0, 0))
            cmds.setAttr(obj + ".scaleX", 0.01)
            cmds.setAttr(obj + ".scaleY", 0.01)
            cmds.setAttr(obj + ".scaleZ", 0.01)
            cmds.makeIdentity(obj, apply=True, scale=True, translate=True, rotate=True, normal=False)
            cmds.delete(obj, constructionHistory=True)

        # Modifier `defaultMeshScheme` selon l'état de la case
        mesh_scheme = "catmullClark" if use_catmull_clark else "none"
        export_command = (
            f'file -force -options ";exportUVs=1;shadingMode=none;defaultMeshScheme={mesh_scheme};USD_kind=scope" '
            f'-typ "USD Export" -pr -es "{output_file_path}";'
        )

        print(f"Export Command: {export_command}")
        try:
            mel.eval(export_command)
            om.MGlobal.displayInfo(f'USD exported: {output_file_path}')
        except RuntimeError as e:
            om.MGlobal.displayError(f'Failed to export USD: {str(e)}')

    finally:
        cmds.undoInfo(closeChunk=True)
        cmds.undo()


def publish_usd_asset(start_frame=1, end_frame=1, use_catmull_clark=True):
    """
    Publie la scène actuelle en tant que fichier USD avec ou sans Catmull Clark.
    """
    # Identifie le chemin et le nom du fichier actuel
    current_file_path = cmds.file(query=True, sceneName=True)
    current_file_name = os.path.basename(current_file_path)
    current_directory = os.path.dirname(current_file_path)

    # Construire les répertoires de publication pour geo et asset
    geo_directory = os.path.abspath(os.path.join(current_file_path, "../../../../usd/geo"))
    asset_directory = os.path.abspath(os.path.join(current_file_path, "../../../../usd/assembly"))

    # Créer les répertoires s'ils n'existent pas
    os.makedirs(geo_directory, exist_ok=True)
    os.makedirs(asset_directory, exist_ok=True)

    # Générer les noms des fichiers
    geo_file_name = re.sub(r'(_E_\d+|_P)', '', current_file_name).replace(".ma", "T.usd")
    asset_file_name = geo_file_name.replace("_geoT", "")  # Supprime le suffixe "_geo"

    geo_file_path = os.path.join(geo_directory, geo_file_name)
    asset_file_path = os.path.join(asset_directory, asset_file_name)

    # Vérifier si l'un des fichiers USD existe déjà
    files_to_overwrite = []
    if os.path.exists(geo_file_path):
        files_to_overwrite.append(geo_file_path)
    if os.path.exists(asset_file_path):
        files_to_overwrite.append(asset_file_path)

    # Demander confirmation uniquement si un ou plusieurs fichiers existent déjà
    if files_to_overwrite:
        file_list = "\n".join(files_to_overwrite)
        message = f"Les fichiers suivants existent déjà :\n{file_list}\n\nVoulez-vous les écraser ?"
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Question)
        dialog.setWindowTitle("Confirmer l'écrasement")
        dialog.setText(message)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        response = dialog.exec_()
        if response != QMessageBox.Yes:
            om.MGlobal.displayInfo("Export USD annulé par l'utilisateur.")
            return

    # Exporter les fichiers USD
    export_usd(geo_file_path, use_catmull_clark=use_catmull_clark)
    export_usd(asset_file_path, use_catmull_clark=use_catmull_clark)

    # Obtenir le nom de l'utilisateur
    username = get_username()

    # Ajouter des notifications pour les deux fichiers exportés
    add_notification(username, "export", os.path.basename(geo_file_path))
    add_notification(username, "export", os.path.basename(asset_file_path))

    # Créer des miniatures pour les fichiers USD
    playblast.create_thumbnail(geo_file_name, increment=True, ext='.usd')
    playblast.create_thumbnail(asset_file_name, increment=True, ext='.usd')

    # Afficher une boîte de dialogue pour confirmer les exports
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(
        f"Fichiers USD enregistrés avec succès !\n"
        f"Emplacements :\n- {geo_file_path}\n- {asset_file_path}"
    )
    msg.setWindowTitle("Export USD")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()



