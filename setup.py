# commande à taper en ligne de commande après la sauvegarde de ce fichier:
# python setup.py build
import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {
                         "packages":['scheduler','winprinter','hlptools','guitools','configs'],
                         "include_files":["./userData","./coreData","./images","./export","README.md","Licence_gpl-3.0.txt"],
                         "excludes": ["PyQt6","PySide6","old_files","setup.py","configs.py",'scheduler.py','colors.py',
                                      'hlptools.py','winprinter.py','guitools.py','heuresrec.py']
                     }

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "Projet EDT v3.15 - Emploi du Temps des AESH",
    version = "3.1.52",
    description = "Application d'aide à la gestion des emplois du temps des AESH.",
    options = {"build_exe": build_exe_options},
    executables = [Executable(  script = "EmploiDuTemps_v3.1.52.py",
                                icon = "./images/edt.ico",
                                copyright="(c) AMOUROUX Bernard 10/2026",
                                target_name="EDT_AESH-v3.exe",
                                base = base)]
      )
