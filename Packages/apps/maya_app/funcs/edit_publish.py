import os
import shutil
from maya import cmds
import maya.api.OpenMaya as om
from PySide2.QtWidgets import QMessageBox
from Packages.apps.maya_app.funcs import playblast
from Packages.logic.filefunc import publish_funcs
from Packages.logic.filefunc import get_funcs
from Packages.logic import json_funcs
from Packages.apps.maya_app.funcs import debug_funcs
from Packages.utils.constants.constants_old import PYTHON_W


def increment_edit():
    '''
    Incrémente et sauvegarde la version du fichier en cours.
    '''
    current_file_path = cmds.file(query=True, sceneName=True)
    parent_directory = os.path.dirname(current_file_path)

    new_file_name = get_funcs.return_increment_edit(current_file_path)
    new_file_path = os.path.join(parent_directory, new_file_name)

    cmds.file(rename=new_file_path)
    cmds.file(save=True)
    om.MGlobal.displayInfo(f'{new_file_name} saved.')
    json_funcs.set_recent_file(new_file_path)

    playblast.update_thumbnail()


def publish(del_colon: bool = True, variant: str = '', usd=False):
    '''
    Publier le fichier et gérer les sauvegardes des anciennes versions.
    '''

    # 0 - Identifier le path et le name du fichier courant
    current_file_path = cmds.file(query=True, sceneName=True)
    current_file_name = os.path.basename(current_file_path)

    # 1 - Déterminer le répertoire de publication
    if usd:
        publish_directory = publish_funcs.find_publish_directory(current_file_path)
    else:
        publish_directory = os.path.dirname(current_file_path)

    print(f'Publish Directory : {publish_directory}')

    # 2 - Créer le chemin complet pour la publication
    publish_file_name = get_funcs.return_publish_name(current_file_name)
    publish_file_path = os.path.join(publish_directory, publish_file_name)

    # 3 - Vérifier si le fichier existe déjà et gérer le backup
    if os.path.exists(publish_file_path):
        # Définir le dossier de sauvegarde un niveau au-dessus
        backup_directory = os.path.join(os.path.dirname(publish_directory), "backup")
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)

        # Générer un nom unique pour la sauvegarde avec suffixe incrémenté
        base_name, ext = os.path.splitext(publish_file_name)
        index = 1
        backup_file_name = f"{base_name}_{index:03d}{ext}"
        backup_file_path = os.path.join(backup_directory, backup_file_name)

        # Incrémenter jusqu'à trouver un nom unique
        while os.path.exists(backup_file_path):
            index += 1
            backup_file_name = f"{base_name}_{index:03d}{ext}"
            backup_file_path = os.path.join(backup_directory, backup_file_name)

        # Déplacer le fichier existant dans le dossier backup avec le nouveau nom
        shutil.move(publish_file_path, backup_file_path)
        print(f"Fichier sauvegardé sous : {backup_file_path}")

    # 4 - Exporter la sélection sous le nom de publication
    cmds.file(publish_file_path, force=True, options="v=0", type="mayaAscii", exportSelected=True,
              preserveReferences=False)
    playblast.create_thumbnail(publish_file_name, increment=True)

    # Afficher un message de confirmation après l'export
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText("L'export du fichier a été réalisé avec succès.")
    msg.setInformativeText(f"Emplacement du fichier :\n{publish_file_path}")
    msg.setWindowTitle("Export réussi")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

    # 5 - Suppression des deux-points si nécessaire
    if del_colon:
        try:
            os.system(PYTHON_W, f'delete_colon.py "{publish_file_path}"')
            print('SUCCESS PYTHON W')
        except:
            print('FAILED PYTHON W')
            shading_nodes = debug_funcs.list_shading_nodes()
            debug_funcs.delete_colon(publish_file_path, shading_nodes)
