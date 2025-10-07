import hou
import os
from PIL import Image
from Packages.utils.constants.constants_old import CURRENT_PROJECT_PREVIEW_FOLDER


def save_thumbnail(output_path=None):
    print("Démarrage de la capture via flipbook...")

    # Récupérer le desktop actif
    cur_desktop = hou.ui.curDesktop()
    print(f"Desktop actif récupéré : {cur_desktop.name()}")
    panetab = cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer)
    if not panetab:
        raise hou.Error("Aucun SceneViewer trouvé dans le desktop actif.")
    print(f"PaneTab trouvé : {panetab.name()}")

    viewport = panetab.curViewport()
    print(f"Viewport actif : {cur_desktop.name()}.{panetab.name()}.{viewport.name()}")

    # Préparer le chemin de sortie basé sur le nom du fichier Houdini
    if output_path is None:
        hip_name = os.path.basename(hou.hipFile.path())  # Récupère le nom complet du fichier
        file_name = os.path.splitext(hip_name)[0]  # Enlève l'extension
        output_path = os.path.join(CURRENT_PROJECT_PREVIEW_FOLDER, f"{file_name}.hipnc.png")  # Ajoute .hipnc.png
    temp_output = output_path + ".temp.png"  # Fichier temporaire avant compression
    print(f"Tentative de sauvegarde à : {output_path}")

    # Vérifier et créer le dossier si nécessaire
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        print(f"Le dossier {output_dir} n'existe pas, création en cours...")
        os.makedirs(output_dir)
    else:
        print(f"Le dossier {output_dir} existe déjà.")

    # Supprimer les fichiers existants
    for path in [output_path, temp_output]:
        if os.path.exists(path):
            print(f"Fichier existant trouvé à {path}, suppression...")
            os.remove(path)
        else:
            print(f"Aucun fichier existant à {path}.")

    # Configurer les options de flipbook
    settings = panetab.flipbookSettings()
    current_frame = int(hou.frame())
    settings.frameRange((current_frame, current_frame))
    settings.output(temp_output)
    settings.resolution((960, 540))  # Résolution réduite pour fichier plus léger
    settings.useResolution(True)
    settings.beautyPassOnly(True)

    # Lancer la capture
    print("Lancement de la capture flipbook...")
    panetab.flipbook(settings=settings)

    # Fermer MPlay
    try:
        hou.session.mplay_close()
        print("Fenêtre MPlay fermée avec succès.")
    except:
        print("Aucune fenêtre MPlay à fermer ou erreur lors de la fermeture.")

    # Compression du PNG
    if os.path.exists(temp_output):
        try:
            with Image.open(temp_output) as img:
                img.save(output_path, "PNG", optimize=True, quality=75)  # Compression plus forte
            os.remove(temp_output)
            print(f"Image compressée sauvegardée à : {output_path}")
        except Exception as e:
            print(f"Erreur lors de la compression : {e}")
            if os.path.exists(temp_output):
                os.rename(temp_output, output_path)

    # Vérifier le résultat
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"Thumbnail sauvegardé : {output_path} (Taille : {file_size} octets)")
        if file_size == 0:
            print("Erreur : Le fichier est vide !")
    else:
        print(f"Échec de la création du fichier à : {output_path}")


if __name__ == "__main__":
    save_thumbnail()