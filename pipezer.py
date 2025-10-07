import os
import stat

os.environ['QT_PLUGIN_PATH'] = r"C:\Program Files\Pixar\RenderManProServer-26.2\lib\plugins"

def set_permissions_for_pipezer_folder():
    folder_path = os.path.expanduser('~/.pipezer')
    try:
        for root, dirs, files in os.walk(folder_path):
            os.chmod(root, stat.S_IRWXU)  # Répertoires
            for file in files:
                file_path = os.path.join(root, file)
                os.chmod(file_path, stat.S_IRWXU)  # Fichiers
        print(f"Les permissions pour {folder_path} ont été mises à jour.")
    except Exception as e:
        print(f"Erreur lors de la modification des permissions : {e}")

set_permissions_for_pipezer_folder()

from Packages.apps.standalone.standalone_app import PipeZerApp

app = PipeZerApp()
app.exec_()