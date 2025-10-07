import maya.cmds as cmds
import os
import shutil
from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT

# Chemin dynamique vers le dossier 05_shot du projet courant
BASE_PATH = os.path.join(CURRENT_PROJECT, "05_shot")


def export_groom_ui():
    """Affiche l'interface utilisateur pour l'export d'animation en Alembic."""
    sequences_and_shots = get_sequences_and_shots()
    if not sequences_and_shots:
        cmds.error("No sequences or shots found in the base path.")

    # Crée une fenêtre pour l'interface utilisateur
    if cmds.window("ExportGroomWindow", exists=True):
        cmds.deleteUI("ExportGroomWindow")

    window = cmds.window("ExportGroomWindow", title="Export Groom to Alembic", sizeable=True,
                         widthHeight=(500, 500))
    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="Select Sequence and Shot", align="center")
    sequence_menu = cmds.optionMenu(label="Sequence", changeCommand=lambda seq: update_shots_menu(seq, shot_menu))
    for sequence in sorted(sequences_and_shots.keys()):
        cmds.menuItem(label=sequence)

    shot_menu = cmds.optionMenu(label="Shot")
    cmds.menuItem(label="Select a sequence first")  # Placeholder

    # Radio buttons pour Barbe et Moustache (exclusifs)
    type_group = cmds.radioButtonGrp(label="Groom Type", labelArray2=["Barbe", "Moustache"], numberOfRadioButtons=2,
                                     select=1, onCommand1=lambda x: update_name_field(type_group, character_menu),
                                     onCommand2=lambda x: update_name_field(type_group, character_menu))

    # Menu déroulant pour les personnages
    character_menu = cmds.optionMenu(label="Character",
                                     changeCommand=lambda x: update_name_field(type_group, character_menu))
    characters = ["Bjork", "Pyromaniac", "Lazy01", "Lazy02", "Sculptor", "Tribe07", "Tribe08", "Tribe09", "Tribe10", "Tribe11"]
    for char in characters:
        cmds.menuItem(label=char)

    # Champ Name mis à jour dynamiquement
    name_field = cmds.textFieldGrp("name_field", label="Name", text="crv_Barbe_Bjork",
                                   changeCommand=lambda x: None)  # Désactive l'édition manuelle directe

    cmds.text(label="Set Start and End Frames", align="center")
    start_frame_field = cmds.intFieldGrp(label="Start Frame", value1=870)
    end_frame_field = cmds.intFieldGrp(label="End Frame", value1=1100)

    cmds.button(label="Manual Export",
                command=lambda _: export_groom_manual(start_frame_field, end_frame_field))

    cmds.button(label="Auto Export",
                command=lambda _: export_groom(start_frame_field, end_frame_field, sequence_menu, shot_menu,
                                               sequences_and_shots))

    cmds.showWindow(window)


def update_name_field(type_group, character_menu):
    """Met à jour le champ Name en fonction des sélections."""
    groom_type = "Barbe" if cmds.radioButtonGrp(type_group, query=True, select=True) == 1 else "Moustache"
    character = cmds.optionMenu(character_menu, query=True, value=True)
    new_name = f"crv_{groom_type}_{character}"
    cmds.textFieldGrp("name_field", edit=True, text=new_name)


def export_groom_manual(start_frame_field, end_frame_field):
    """Permet un export manuel en choisissant un emplacement et un nom de fichier pour Alembic."""
    frameStart = cmds.intFieldGrp(start_frame_field, query=True, value1=True)
    frameEnd = cmds.intFieldGrp(end_frame_field, query=True, value1=True)

    # Ouvre une boîte de dialogue pour choisir l'emplacement et le nom du fichier
    file_path = cmds.fileDialog2(fileMode=0, caption="Enregistrer le groom en Alembic",
                                 fileFilter="Alembic Files (*.abc)")

    if not file_path:
        cmds.warning("Export annulé.")
        return

    abc_filePath = file_path[0]

    # Utilise la sélection actuelle sans filtrage
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.error("No objects selected. Please select something to export.")
        return

    try:
        # Prépare les arguments pour la commande Alembic
        root_args = " ".join([f"-root {obj}" for obj in selection])
        abc_command = f"-fr {frameStart} {frameEnd} -stripNamespaces -uvWrite -worldSpace {root_args} -file {abc_filePath}"

        # Exécute l'export Alembic
        cmds.AbcExport(j=abc_command)

        cmds.confirmDialog(title="Export Success", message=f"Groom exported to:\n{abc_filePath}", button=["OK"])
    except Exception as e:
        cmds.error(f"Failed to export groom: {e}")


def get_sequences_and_shots():
    """Parcourt les dossiers pour récupérer les séquences et shots."""
    sequences = {}
    if not os.path.exists(BASE_PATH):
        cmds.error(f"Base path {BASE_PATH} does not exist.")
        return sequences

    for folder in os.listdir(BASE_PATH):
        if folder.startswith("sq") and folder[2:].isdigit():
            sequence = folder[2:]
            sequence_path = os.path.join(BASE_PATH, folder)
            shots = []

            for subfolder in os.listdir(sequence_path):
                if subfolder.startswith(f"{folder}_sh") and subfolder.split("_sh")[-1].isdigit():
                    shots.append(subfolder.split("_sh")[-1])

            sequences[sequence] = shots
    return sequences


def update_shots_menu(selected_sequence, shot_menu):
    """Met à jour le menu déroulant des shots en fonction de la séquence sélectionnée."""
    sequences_and_shots = get_sequences_and_shots()

    for item in cmds.optionMenu(shot_menu, query=True, itemListLong=True) or []:
        cmds.deleteUI(item)

    for shot in sorted(sequences_and_shots.get(selected_sequence, [])):
        cmds.menuItem(label=shot, parent=shot_menu)


def export_groom(start_frame_field, end_frame_field, sequence_menu, shot_menu, sequences_and_shots):
    """Exporte le groom sélectionné en Alembic avec les paramètres spécifiés."""
    frameStart = cmds.intFieldGrp(start_frame_field, query=True, value1=True)
    frameEnd = cmds.intFieldGrp(end_frame_field, query=True, value1=True)
    selected_sequence = cmds.optionMenu(sequence_menu, query=True, value=True)
    selected_shot = cmds.optionMenu(shot_menu, query=True, value=True)
    custom_name = cmds.textFieldGrp("name_field", query=True, text=True)

    if not custom_name:
        cmds.error("Please ensure a valid name is set in the Name field.")
        return

    # Nom du fichier
    file_name = f"NOR_sq{selected_sequence}_sh{selected_shot}_{custom_name}_groom.abc"

    # Chemin d’enregistrement avec dossier "groom"
    target_path = os.path.join(BASE_PATH, f"sq{selected_sequence}", f"sq{selected_sequence}_sh{selected_shot}", "usd", "groom", "curves")
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    abc_filePath = os.path.join(target_path, file_name)

    # Utilise la sélection actuelle sans filtrage
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.error("No objects selected. Please select something to export.")
        return

    try:
        # Prépare les arguments pour la commande Alembic
        root_args = " ".join([f"-root {obj}" for obj in selection])
        abc_command = f"-fr {frameStart} {frameEnd} -stripNamespaces -uvWrite -worldSpace {root_args} -file {abc_filePath}"

        # Exécute l'export Alembic
        cmds.AbcExport(j=abc_command)

        cmds.confirmDialog(title="Export Success", message=f"Groom exported to:\n{abc_filePath}", button=["OK"])
    except Exception as e:
        cmds.error(f"Failed to export groom: {e}")


# Exécute le script
export_groom_ui()