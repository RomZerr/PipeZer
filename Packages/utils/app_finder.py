import os


class AppFinder:
    
    
    PROGRAM_FILES = 'C:/Program Files'
    app_dict = {
        'blender': {'path': None, 'pref': None},
        'it': {'path': None, 'pref': None},
        'krita': {'path': None, 'pref': None},
        'houdini': {'path': None, 'pref': None},
        'mari': {'path': None, 'pref': None},
        'maya': {'path': None, 'pref': None},
        'nuke': {'path': None, 'pref': None},
        'photoshop': {'path': None, 'pref': None},
        'substance_designer': {'path': None, 'pref': None},
        'substance_painter': {'path': None, 'pref': None},
        'zbrush': {'path': None, 'pref': None},
        'unreal': {'path': None, 'pref': None},
        'resolve': {'path': None, 'pref': None},
        'mudbox': {'path': None, 'pref': None},
        'embergen': {'path': None, 'pref': None}
    }
    
    
    def __init__(self) -> None:
            
        self.app_dict['blender']['path'] = self.find_blender()
        self.app_dict['krita']['path'] = self.find_krita()
        self.app_dict['houdini']['path'] = self.find_houdini()
        self.app_dict['mari']['path'] = self.find_mari()
        self.app_dict['maya']['path'] = self.find_maya()
        self.app_dict['nuke']['path'] = self.find_nuke()
        self.app_dict['photoshop']['path'] = self.find_photoshop()
        self.app_dict['zbrush']['path'] = self.find_zbrush()
        self.app_dict['unreal']['path'] = self.find_unreal()
        self.app_dict['resolve']['path'] = self.find_resolve()
        self.app_dict['mudbox']['path'] = self.find_mudbox()
        self.app_dict['embergen']['path'] = self.find_embergen()
        self.app_dict['substance_designer']['path'] = self.find_substance_designer()
        self.app_dict['substance_painter']['path'] = self.find_substance_painter()
        
        self.app_dict['houdini']['pref'] = self.find_houdini_pref()
        self.app_dict['mari']['pref'] = self.find_mari_pref()
        self.app_dict['maya']['pref'] = self.find_maya_pref()
        self.app_dict['nuke']['pref'] = self.find_nuke_pref()
        
    
    def find_directory(self, parent_directory: str, directory_string: str, return_type: str = 'str', exclude_strings = []):
        try:
            directories: list[str] = os.listdir(parent_directory)
        except Exception:
            directories = []

        matches = []
        for directory_name in directories:
            if directory_name.startswith(directory_string):
                if directory_name in exclude_strings:
                    continue
                matches.append(directory_name)

        if return_type == 'str':
            return matches[0] if matches else None
        return matches
            
            
    def find_blender(self) -> str:
        exe: str = 'blender.exe'
        parent_dir: str = os.path.join(self.PROGRAM_FILES, 'Blender Foundation')
        dir_string: str = 'Blender '
        version_dir = self.find_directory(parent_directory=parent_dir, directory_string=dir_string)
        if not version_dir:
            return None
        path_candidate = os.path.join(parent_dir, version_dir, exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None
    
    
    def find_krita(self) -> str:
        exe: str = 'krita.exe'
        parent_dir: str = os.path.join(self.PROGRAM_FILES, 'Krita (x64)')
        return os.path.join(parent_dir, 'bin', exe).replace('\\', '/')
    
    
    def find_houdini(self) -> str:
        exe: str = 'houdini.exe'
        parent_dir: str = os.path.join(self.PROGRAM_FILES, 'Side Effects Software')
        dir_string: str = 'Houdini'
        version_dir = self.find_directory(parent_directory=parent_dir, directory_string=dir_string, exclude_strings=['Houdini Engine', 'Houdini Server'])
        if not version_dir:
            return None
        path_candidate = os.path.join(parent_dir, version_dir, 'bin', exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None
    
    
    def find_mari(self) -> str:
        mari: str = 'Mari'
        mari_root = self.find_directory(parent_directory=self.PROGRAM_FILES, directory_string=mari)
        if not mari_root:
            return None
        parent_dir: str = os.path.join(self.PROGRAM_FILES, mari_root, 'Bundle', 'bin')
        exe = self.find_directory(parent_directory=parent_dir, directory_string=mari)
        if not exe:
            return None
        path_candidate = os.path.join(parent_dir, exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None
    
    
    def find_maya(self) -> str:
        exe: str = 'maya.exe'
        parent_dir: str = os.path.join(self.PROGRAM_FILES, 'Autodesk')
        dir_string: str = 'Maya'
        version_dir = self.find_directory(parent_directory=parent_dir, directory_string=dir_string)
        if not version_dir:
            return None
        path_candidate = os.path.join(parent_dir, version_dir, 'bin', exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None
    
    
    def find_nuke(self) -> str:
        nuke: str = 'Nuke'
        nuke_root = self.find_directory(parent_directory=self.PROGRAM_FILES, directory_string=nuke)
        if not nuke_root:
            return None
        parent_dir: str = os.path.join(self.PROGRAM_FILES, nuke_root)
        files: list[str] = self.find_directory(parent_directory=parent_dir, directory_string=nuke, return_type='list')
        exe: str = None
        for file in files:
            if file.endswith('.exe'):
                exe = file
                break
        if not exe:
            return None
        path_candidate = os.path.join(parent_dir, exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None
    
    
    def find_photoshop(self) -> str:
        exe: str = 'Photoshop.exe'
        parent_dir: str = os.path.join(self.PROGRAM_FILES, 'Adobe')
        dir_string: str = 'Adobe Photoshop '
        version_dir = self.find_directory(parent_directory=parent_dir, directory_string=dir_string)
        if not version_dir:
            return None
        path_candidate = os.path.join(parent_dir, version_dir, exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None
    
    
    def find_zbrush(self) -> str:
        exe: str = 'ZBrush.exe'
        pixologic_dir = self.find_directory(parent_directory=self.PROGRAM_FILES, directory_string='Pixologic')
        if not pixologic_dir:
            return None
        parent_dir: str = os.path.join(self.PROGRAM_FILES, pixologic_dir)
        path_candidate = os.path.join(parent_dir, exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None


    def find_houdini_pref(self) -> str:
        documents_path = os.path.join(os.path.expanduser("~"), 'Documents')
        houdini_dir = self.find_directory(documents_path, 'houdini')
        return os.path.join(documents_path, houdini_dir) if houdini_dir else None
    
    
    def find_mari_pref(self) -> str:
        return os.path.join(os.path.expanduser("~"), '.mari')
    
    
    def find_maya_pref(self) -> str:
        documents_path = os.path.join(os.path.expanduser("~"), 'Documents')
        maya_dir = self.find_directory(documents_path, 'maya')
        return os.path.join(documents_path, maya_dir) if maya_dir else None
    
    
    def find_nuke_pref(self) -> str:
        return os.path.join(os.path.expanduser("~"), '.nuke')
    
    
    def find_unreal(self) -> str:
        """Trouve Unreal Engine (UE5)"""
        exe: str = 'UnrealEditor.exe'
        parent_dir: str = os.path.join(self.PROGRAM_FILES, 'Epic Games')
        dir_string: str = 'UE_'
        version_dir = self.find_directory(parent_directory=parent_dir, directory_string=dir_string)
        if not version_dir:
            return None
        path_candidate = os.path.join(parent_dir, version_dir, 'Engine', 'Binaries', 'Win64', exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None
    
    
    def find_resolve(self) -> str:
        """Trouve DaVinci Resolve"""
        exe: str = 'Resolve.exe'
        parent_dir: str = os.path.join(self.PROGRAM_FILES, 'Blackmagic Design')
        dir_string: str = 'DaVinci Resolve'
        version_dir = self.find_directory(parent_directory=parent_dir, directory_string=dir_string)
        if not version_dir:
            return None
        path_candidate = os.path.join(parent_dir, version_dir, exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None
    
    
    def find_mudbox(self) -> str:
        """Trouve Autodesk Mudbox"""
        exe: str = 'mudbox.exe'
        parent_dir: str = os.path.join(self.PROGRAM_FILES, 'Autodesk')
        dir_string: str = 'Mudbox'
        version_dir = self.find_directory(parent_directory=parent_dir, directory_string=dir_string)
        if not version_dir:
            return None
        path_candidate = os.path.join(parent_dir, version_dir, 'bin', exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None
    
    
    def find_embergen(self) -> str:
        """Trouve EmberGen"""
        exe: str = 'EmberGen.exe'
        parent_dir: str = os.path.join(self.PROGRAM_FILES, 'JangaFX')
        dir_string: str = 'EmberGen'
        version_dir = self.find_directory(parent_directory=parent_dir, directory_string=dir_string)
        if not version_dir:
            return None
        path_candidate = os.path.join(parent_dir, version_dir, exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None
    
    
    def find_substance_designer(self) -> str:
        """Trouve Substance 3D Designer"""
        exe: str = 'Adobe Substance 3D Designer.exe'
        parent_dir: str = os.path.join(self.PROGRAM_FILES, 'Adobe', 'Adobe Substance 3D Designer')
        path_candidate = os.path.join(parent_dir, exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None
    
    
    def find_substance_painter(self) -> str:
        """Trouve Substance 3D Painter"""
        exe: str = 'Adobe Substance 3D Painter.exe'
        parent_dir: str = os.path.join(self.PROGRAM_FILES, 'Adobe', 'Adobe Substance 3D Painter')
        path_candidate = os.path.join(parent_dir, exe).replace('\\', '/')
        return path_candidate if os.path.exists(path_candidate) else None


if __name__ == '__main__':
    import subprocess
    
    apps = AppFinder()
    print(apps.app_dict)
    
    for app, app_infos in apps.app_dict.items():
        exe = app_infos['path']
        if exe:
            if not os.path.exists(exe):
                continue
            print(exe)
            subprocess.Popen([exe])
