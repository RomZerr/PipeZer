import maya.cmds as cmds
import os
import shutil
from Packages.utils.constants.project_pipezer_data import CURRENT_PROJECT

# Chemin dynamique vers le dossier 05_shot du projet courant
BASE_PATH = os.path.join(CURRENT_PROJECT, "05_shot")


def export_animation_ui():
    """Affiche l'interface utilisateur pour l'export d'animation."""
    sequences_and_shots = get_sequences_and_shots()
    if not sequences_and_shots:
        cmds.error("No sequences or shots found in the base path.")

    # Récupère le nom de la sélection actuelle
    selection = cmds.ls(selection=True)
    default_name = selection[0] if selection else ""

    # Crée une fenêtre pour l'interface utilisateur
    if cmds.window("ExportAnimationWindow", exists=True):
        cmds.deleteUI("ExportAnimationWindow")

    window = cmds.window("ExportAnimationWindow", title="Export Animation to USD", sizeable=True,
                         widthHeight=(500, 500))
    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="Select Sequence and Shot", align="center")
    sequence_menu = cmds.optionMenu(label="Sequence", changeCommand=lambda seq: update_shots_menu(seq, shot_menu))
    for sequence in sorted(sequences_and_shots.keys()):
        cmds.menuItem(label=sequence)

    shot_menu = cmds.optionMenu(label="Shot")
    cmds.menuItem(label="Select a sequence first")  # Placeholder

    cmds.textFieldGrp("name_field", label="Name", text=default_name)

    cmds.text(label="Set Start and End Frames", align="center")
    start_frame_field = cmds.intFieldGrp(label="Start Frame", value1=1001)
    end_frame_field = cmds.intFieldGrp(label="End Frame", value1=1100)

    cmds.button(label="Manual Export",
                command=lambda _: export_animation_manual(start_frame_field, end_frame_field))

    cmds.button(label="Auto Export",
                command=lambda _: export_animation(start_frame_field, end_frame_field, sequence_menu, shot_menu,
                                                   sequences_and_shots))

    cmds.showWindow(window)


def export_animation_manual(start_frame_field, end_frame_field):
    """Permet un export manuel en choisissant un emplacement et un nom de fichier."""
    frameStart = cmds.intFieldGrp(start_frame_field, query=True, value1=True)
    frameEnd = cmds.intFieldGrp(end_frame_field, query=True, value1=True)

    # Ouvre une boîte de dialogue pour choisir l'emplacement et le nom du fichier
    file_path = cmds.fileDialog2(fileMode=0, caption="Enregistrer l'animation en USD", fileFilter="USD Files (*.usd)")

    if not file_path:
        cmds.warning("Export annulé.")
        return

    usd_filePath = file_path[0]

    # Utilise la sélection actuelle sans filtrage
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.error("No objects selected. Please select something to export.")
        return

    try:
        cmds.select(selection)
        cmds.file(
            usd_filePath,
            typ='USD Export',
            es=1,
            options=f'exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportDisplayColor=0;filterTypes=nurbsCurve;exportColorSets=0;exportComponentTags=0;defaultMeshScheme=catmullClark;animation=1;eulerFilter=0;staticSingleSample=0;startTime={frameStart};endTime={frameEnd};frameStride=1;frameSample=0.0;defaultUSDFormat=usdc;parentScope=;shadingMode=useRegistry;convertMaterialsTo=[];exportInstances=0;exportVisibility=0;mergeTransformAndShape=1;stripNamespaces=1;materialsScopeName=mtl',
            preserveReferences=0,
            force=1
        )

        cmds.confirmDialog(title="Export Success", message=f"Animation exported to:\n{usd_filePath}", button=["OK"])
    except Exception as e:
        cmds.error(f"Failed to export USD: {e}")


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


def export_animation(start_frame_field, end_frame_field, sequence_menu, shot_menu, sequences_and_shots):
    """Exporte l'animation sélectionnée avec les paramètres spécifiés."""
    frameStart = cmds.intFieldGrp(start_frame_field, query=True, value1=True)
    frameEnd = cmds.intFieldGrp(end_frame_field, query=True, value1=True)
    selected_sequence = cmds.optionMenu(sequence_menu, query=True, value=True)
    selected_shot = cmds.optionMenu(shot_menu, query=True, value=True)
    custom_name = cmds.textFieldGrp("name_field", query=True, text=True)

    if not custom_name:
        cmds.error("Please enter a valid name in the Name field.")
        return

    # Nom du fichier
    file_name = f"NOR_sq{selected_sequence}_sh{selected_shot}_{custom_name}_anim.usd"

    # Chemin d’enregistrement
    target_path = os.path.join(BASE_PATH, f"sq{selected_sequence}", f"sq{selected_sequence}_sh{selected_shot}", "usd", "anim")
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    usd_filePath = os.path.join(target_path, file_name)

    # Utilise la sélection actuelle sans filtrage
    selection = cmds.ls(selection=True)
    if not selection:
        cmds.error("No objects selected. Please select something to export.")
        return

    try:
        cmds.select(selection)
        cmds.file(
            usd_filePath,
            typ='USD Export',
            es=1,
            options=f'exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportDisplayColor=0;filterTypes=nurbsCurve;exportColorSets=0;exportComponentTags=0;defaultMeshScheme=catmullClark;animation=1;eulerFilter=0;staticSingleSample=0;startTime={frameStart};endTime={frameEnd};frameStride=1;frameSample=0.0;defaultUSDFormat=usdc;parentScope=;shadingMode=useRegistry;convertMaterialsTo=[];exportInstances=0;exportVisibility=0;mergeTransformAndShape=1;stripNamespaces=1;materialsScopeName=mtl',
            preserveReferences=0,
            force=1
        )

        # Vérifie si le chemin source et destination sont différents
        if os.path.abspath(usd_filePath) != os.path.abspath(os.path.join(target_path, file_name)):
            shutil.copy2(usd_filePath, os.path.join(target_path, file_name))

        cmds.confirmDialog(title="Export Success", message=f"Animation exported to:\n{usd_filePath}", button=["OK"])
    except Exception as e:
        cmds.error(f"Failed to export USD: {e}")


# Exécute le script
export_animation_ui()