import maya.cmds as cmds
import os

# Chemin réseau où se trouvent les séquences et shots
BASE_PATH = r"\\Storage01\3d4\nordicPhone\05_shot"

def export_camera_ui():
    """Affiche l'interface utilisateur pour l'export de caméra."""
    sequences_and_shots = get_sequences_and_shots()
    if not sequences_and_shots:
        cmds.error("No sequences or shots found in the base path.")

    # Crée une fenêtre pour l'interface utilisateur
    if cmds.window("ExportCameraWindow", exists=True):
        cmds.deleteUI("ExportCameraWindow")

    window = cmds.window("ExportCameraWindow", title="Export Camera to Alembic or Maya Ascii", sizeable=True,
                         widthHeight=(500, 400))
    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="Select Sequence and Shot", align="center")
    sequence_menu = cmds.optionMenu(label="Sequence", changeCommand=lambda seq: update_shots_menu(seq, shot_menu))
    for sequence in sorted(sequences_and_shots.keys()):
        cmds.menuItem(label=sequence)

    shot_menu = cmds.optionMenu(label="Shot")
    cmds.menuItem(label="Select a sequence first")  # Placeholder

    cmds.checkBox("layout_checkbox", label="Layout", value=True, changeCommand=lambda _: toggle_options("layout"))
    cmds.checkBox("anim_checkbox", label="Anim", value=False, changeCommand=lambda _: toggle_options("anim"))
    cmds.checkBox("master_checkbox", label="Master", value=True, changeCommand=lambda _: toggle_master_multishot("master"))
    cmds.checkBox("multishot_checkbox", label="MultiShot", value=False, changeCommand=lambda _: toggle_master_multishot("multishot"))
    cmds.checkBox("alembic_checkbox", label="Alembic", value=True)
    cmds.checkBox("maya_ascii_checkbox", label="Maya Ascii", value=True)

    cmds.text(label="Set Start and End Frames", align="center")
    start_frame_field = cmds.intFieldGrp(label="Start Frame", value1=1001)
    end_frame_field = cmds.intFieldGrp(label="End Frame", value1=1100)

    cmds.button(label="Export Camera",
                command=lambda _: export_camera(start_frame_field, end_frame_field, sequence_menu, shot_menu,
                                                sequences_and_shots))

    cmds.showWindow(window)

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

def toggle_options(selected_option):
    """Gère l'état des cases Layout et Anim."""
    if selected_option == "layout":
        cmds.checkBox("anim_checkbox", edit=True, value=False)
    elif selected_option == "anim":
        cmds.checkBox("layout_checkbox", edit=True, value=False)

def toggle_master_multishot(selected_option):
    """Gère l'état des cases Master et MultiShot."""
    if selected_option == "master":
        cmds.checkBox("multishot_checkbox", edit=True, value=False)
    elif selected_option == "multishot":
        cmds.checkBox("master_checkbox", edit=True, value=False)

def ensure_directory_exists(path):
    """Crée le dossier si nécessaire et affiche un message."""
    if not os.path.exists(path):
        os.makedirs(path)
        cmds.confirmDialog(title="Directory Created",
                           message=f"The directory was missing and has been created:\n{path}", button=["OK"])
    return path

def export_camera_with_parent(start_frame, end_frame, transform, save_path, alembic=True):
    """Exporte une caméra en utilisant un parent logique comme racine."""
    if not cmds.objExists(transform):
        cmds.error(f"Object {transform} does not exist.")
        return

    parent = cmds.listRelatives(transform, parent=True, fullPath=True)
    export_node = parent[0] if parent else transform

    if alembic:
        alembic_path = save_path + ".abc"
        try:
            cmds.AbcExport(j=f"-frameRange {start_frame} {end_frame} -step 1 -worldSpace -root {export_node} -file {alembic_path}")
            cmds.confirmDialog(title="Export Success", message=f"Camera exported to Alembic:\n{alembic_path}", button=["OK"])
        except Exception as e:
            cmds.error(f"Failed to export: {e}")
    else:
        maya_path = save_path + ".ma"
        try:
            cmds.file(maya_path, force=True, type="mayaAscii", exportSelected=True)
            cmds.confirmDialog(title="Export Success", message=f"Camera exported to Maya Ascii:\n{maya_path}", button=["OK"])
        except Exception as e:
            cmds.error(f"Failed to export: {e}")

def export_camera(start_frame_field, end_frame_field, sequence_menu, shot_menu, sequences_and_shots):
    """Exporte la caméra en fonction des paramètres spécifiés."""
    start_frame = cmds.intFieldGrp(start_frame_field, query=True, value1=True)
    end_frame = cmds.intFieldGrp(end_frame_field, query=True, value1=True)
    selected_sequence = cmds.optionMenu(sequence_menu, query=True, value=True)
    selected_shot = cmds.optionMenu(shot_menu, query=True, value=True)
    is_layout = cmds.checkBox("layout_checkbox", query=True, value=True)
    is_anim = cmds.checkBox("anim_checkbox", query=True, value=True)
    is_master = cmds.checkBox("master_checkbox", query=True, value=True)
    is_multishot = cmds.checkBox("multishot_checkbox", query=True, value=True)
    export_alembic = cmds.checkBox("alembic_checkbox", query=True, value=True)
    export_maya_ascii = cmds.checkBox("maya_ascii_checkbox", query=True, value=True)

    if (is_master and is_multishot) or (is_layout and is_anim):
        cmds.error("Invalid configuration: Please select only one option between Master and MultiShot, or Layout and Anim.")
        return

    if is_layout:
        if is_master:
            save_path = os.path.join(BASE_PATH, f"sq{selected_sequence}", f"sq{selected_sequence}_master", "camera",
                                     f"NOR_sq{selected_sequence}_camera_master_layout")
        else:  # MultiShot
            save_path = os.path.join(BASE_PATH, f"sq{selected_sequence}", f"sq{selected_sequence}_multiShot", "camera",
                                     f"NOR_sq{selected_sequence}_sh{selected_shot}_camera_layout")
            # Additional MultiShot path
            additional_path = os.path.join(BASE_PATH, f"sq{selected_sequence}", f"sq{selected_sequence}_sh{selected_shot}", "camera",
                                           f"NOR_sq{selected_sequence}_sh{selected_shot}_camera_layout")
    else:  # is_anim
        if is_master:
            save_path = os.path.join(BASE_PATH, f"sq{selected_sequence}", f"sq{selected_sequence}_master", "camera",
                                     f"NOR_sq{selected_sequence}_camera_anim")
        else:  # MultiShot
            save_path = os.path.join(BASE_PATH, f"sq{selected_sequence}", f"sq{selected_sequence}_multiShot", "camera",
                                     f"NOR_sq{selected_sequence}_sh{selected_shot}_camera_anim")
            # Additional MultiShot path
            additional_path = os.path.join(BASE_PATH, f"sq{selected_sequence}", f"sq{selected_sequence}_sh{selected_shot}", "camera",
                                           f"NOR_sq{selected_sequence}_sh{selected_shot}_camera_anim")

    ensure_directory_exists(os.path.dirname(save_path))

    selection = cmds.ls(selection=True)
    if not selection:
        cmds.error("No object selected. Please select a camera.")
        return

    transform = selection[0]

    if export_alembic:
        export_camera_with_parent(start_frame, end_frame, transform, save_path, alembic=True)

    if export_maya_ascii:
        ascii_path = save_path + ".ma"
        ensure_directory_exists(os.path.dirname(ascii_path))
        try:
            cmds.file(ascii_path, force=True, type="mayaAscii", exportSelected=True)
            cmds.confirmDialog(title="Export Success", message=f"Camera additionally exported to Maya Ascii:\n{ascii_path}", button=["OK"])
        except Exception as e:
            cmds.error(f"Failed to export Maya Ascii: {e}")

    if is_multishot:
        if export_alembic:
            ensure_directory_exists(os.path.dirname(additional_path))
            export_camera_with_parent(start_frame, end_frame, transform, additional_path, alembic=True)
        if export_maya_ascii:
            additional_ascii_path = additional_path + ".ma"
            ensure_directory_exists(os.path.dirname(additional_ascii_path))
            try:
                cmds.file(additional_ascii_path, force=True, type="mayaAscii", exportSelected=True)
                cmds.confirmDialog(title="Export Success", message=f"Camera additionally exported to Maya Ascii:\n{additional_ascii_path}", button=["OK"])
            except Exception as e:
                cmds.error(f"Failed to export additional MultiShot Maya Ascii: {e}")

# Exécute le script
export_camera_ui()