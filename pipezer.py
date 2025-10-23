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
        from Packages.utils.translation import translation_manager
        print(translation_manager.get_text("messages.permissions_updated", path=folder_path))
    except Exception as e:
        from Packages.utils.translation import translation_manager
        print(translation_manager.get_text("messages.error_permissions", error=str(e)))

set_permissions_for_pipezer_folder()

from Packages.apps.standalone.standalone_app import PipeZerApp

app = PipeZerApp()
app.exec_()