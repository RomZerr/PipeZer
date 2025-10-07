from cx_Freeze import setup, Executable

executables = [Executable("pipezer.py", icon = "ProjectFiles/Icons/pipezer_icon.ico")]

setup(
    name="pipezer",
    version="Beta",
    description="",
    executables=executables,
    options={
        "build_exe": {
            "includes": ["PySide2", "PIL"]
        }
    }
)
