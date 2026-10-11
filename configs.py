"""
configs, bibliothèque du projet Emploi_du_Temps. Fournit les objets, classes 
pour la définition des options de l'application. 
Copyright (C) 2025  Bernard AMOUROUX

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

EDT v3.15 (C) 09/2025  Bernard AMOUROUX
This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.
"""

__author__ = "Bernard AMOUROUX"
__date__ = "$Date: 2025/09/05 07:00 $"
__copyright__ = "Copyright (c) 2025 Bernard AMOUROUX"
__license__ = "GPL 3"

import locale
import os,gzip
import os.path as op
import pickle as pkdata
import win32print as w32p

from typing import Literal,get_args
from datetime import datetime


data_path:str = "userData"
core_path:str = "coreData"
images_path:str = "images"
export_path:str = 'export'

now = datetime.now()
# Année scolaire :               début  2027          grd vacances -     fin    2026
Jours_Feries = [(1,1),(3,29),(5,1),(5,6),(5,8),(5,17),(7,14),(8,15),(11,1),(11,11),(12,25),]

current_weeks = Literal["Semaine Q1","Semaine Q2"]
list_curweeks = get_args(current_weeks)
schedule_modes = Literal["Mode Modification","Mode Consultation"]
list_schedulemodes = get_args(schedule_modes)
workdays = Literal["Lundi","Mardi","Mercredi","jeudi","Vendredi"]
list_workdays = get_args(workdays)
schedules = Literal["8h10","9h05","Récré 1","10h20","11h15","Pause","13h40","14h35","Récré 2","15h50","16h45"]
list_schedules:list = ([])
classrooms = Literal["11","12","13","14","15","21","22","23","24","25","32","33","34",
                                        "41","42","43","44","T2","T3","Art","Cdi","Musique","Salle Info.","Gymnase","Salle AESH"]
list_classrooms:list = ([])
schoolsubjects = Literal[  "", "Français","Anglais","Espagnol","Mathématiques","Technologie","Art plastique", "Musique", "SVT.",
                                        "Physique-chimie","Histoire/Géo.","EPS.",     "CDI","Heure AESH","Aide aux devoirs"]
list_studsubjects:list = ([])
list_colors:list =      ["azure2","yellow","orange2",  "salmon",   "steel blue",    "khaki",       "orchid1",  "plum1","steel blue1",
                                            "sky blue",    "lime green","SlateBlue1","grey85", "brown3",    "brown1"]
studies_colors:dict = {key:value for key, value in zip(tuple(get_args(schoolsubjects))+("Nothing",),tuple(list_colors)+("azure2",))}
extraschoolwork = Literal["","Surveillance récré","Surveillance self","Pause méridienne"]
list_extraschool:list = ([])

recre_time:int = 20

default_param_filename = "EDT_config.cfg"
default_data_filename = "EDT_default.dat"
default_help_filename = "EDT_helpfile.hlp"
default_img_background = "EDT_background.gif"
coreData_filename = "EDT_coreData.json"
corePNG_filename = "schedulers.png"

offset_W, offset_H = 150, 100
COLS:int = 80           # -- nombre de colonnes pour le texte à imprimer


class Persons():
    def __init__(self, nom:str, prenom:str):
        self.__nom = nom.upper()
        self.__prenom = self.capitalise(prenom)
        self.__fonction:tuple = ("AESH","Assistant(e) aux Élèves en Situation de Handicap")
    
    @property
    def nom(self) -> str:
        return self.__nom
    @nom.setter
    def nom(self, nom:str):
        self.__nom = nom
    
    @property
    def prenom(self) -> str:
        return self.__prenom
    @prenom.setter
    def prenom(self, prenom:str):
        self.__prenom = prenom
    
    @property
    def fonction(self) -> tuple:
        return self.__fonction
    @fonction.setter
    def fonction(self, fonction:tuple):
        self.__fonction = fonction
        
    def get_name(self) -> str:
        return f"{self.nom}, {self.prenom}"    
    
    def capitalise(self, prenom:str) -> str:
        """ Pour une mise en capitale des premières lettres d'un prénom composé. """
        idx = max(prenom.find('-'), prenom.find(' '))
        if idx > 0 and prenom[idx+1].isalpha():
            return f"{prenom[:idx].capitalize()}{prenom[idx]}{prenom[idx+1:].capitalize()}" 
        return prenom.capitalize()
    
    def __eq__(self, other:"Persons") -> bool:
        return self.nom == other.nom and self.prenom == other.prenom
    
    def __hash__(self):
        return hash((self.nom.__hash__(), self.prenom.__hash__(), self.fonction.__hash__()))
    
    def __str__(self) -> str:
        return f"{self.__nom}, {self.__prenom} ({self.fonction[0]})"


class App_Size():
    def __init__(self, width:int=1366, height:int=768):
        self.__width:int = width
        self.__height:int = height

    @property
    def app_size(self) -> tuple:
        return self.__width,self.__height
    @app_size.setter
    def app_size(self, size:tuple):
        self.__width = size[0] if size[0] != None else self.__width
        self.__height = size[1] if size[1] != None else self.__height
        
    def __str__(self) -> str:
        return f"({self.width}, {self.height})"


class My_Datetime(datetime):

    Long:bool = False
    
    def __init__(self, year:int, month:int, day:int):
        super().__init__()
        self.__my_date = datetime(year=year, month=month, day=day)
        
    def __str__(self) -> str:
        return datetime.strftime(datetime(self.__my_date.year,self.__my_date.month,self.__my_date.day),"%A %d %B %Y") \
                            if My_Datetime.Long else datetime.strftime(self.__my_date.date(),"%d/%m/%Y")  


class App_Options(object):
    def __init__(self):
        # -------------------------------------------------
        self.__data_path:str = data_path
        self.__images_path:str = images_path
        self.__export_path:str = export_path
        # -------------------------------------------------
        self.__params_fname:str = default_param_filename
        self.__data_filename:str = default_data_filename
        self.__help_filename:str = default_help_filename
        self.__back_filename:str = default_img_background
        # -------------------------------------------------
        self.aesh_name = Persons("nom...", "prénom...") # -- nom et prénom de l'AESH
        self.__app_size = App_Size().app_size           # -- taille de l'application défaut: VESA (1366x768)
        self.__fullscreen:bool = False                  # -- bascule mode plein écran/fenêtré
        self.__date_long:bool = True                    # -- affichage des dates au format long (ie: lundi 4 mars 2025)
        # -------------------------------------------------
        self.__splashscreen:bool = True                 # -- fenetre à propos au démarrage       
        self.__saveCFG_on_quit:bool = False             # -- sauvegarde config en quittant
        self.__saveEDT_on_quit:bool = False             # -- sauvegarde données emploi du temps
        self.__show_scheduler:bool = True               # -- affichage fenètre emploi du temps.
        self.__date_rentree = My_Datetime(now.year,month=9,day=1).date() # -- rentrée le 1er septembre de l'année par défaut
        self.__schedule_mode:schedule_modes = "Mode Modification"
        self.__current_week:current_weeks = "Semaine Q1"
        self.__default_year:int = now.year
        # -------------------------------------------------
        #self.__studies_color:dict = {study:color for study,color in studies_colors.items()}
        # -------------------------------------------------
        self.__default_printer:str = w32p.GetDefaultPrinter()
        self.__policy_family:str = 'Consolas'
        self.__length_line:int = 92
    
    
    @property
    def schedulemode(self) -> schedule_modes:
        return self.__schedule_mode
    @schedulemode.setter
    def schedulemode(self, schedule_mode:schedule_modes):
        self.__schedule_mode = schedule_mode
    
    @property
    def currentweek(self) ->str:
        return self.__current_week
    @currentweek.setter
    def currentweek(self, currentweek:current_weeks):
        self.__current_week = currentweek
    
    @property
    def date_rentree(self) -> str:
        return self.__date_rentree
    @date_rentree.setter
    def date_rentree(self, date_rentree):
        self.__date_rentree = My_Datetime(date_rentree.year,date_rentree.month,date_rentree.day).date()
    
    @property
    def scheduler(self) -> bool:
        return self.__show_scheduler
    @scheduler.setter
    def scheduler(self, show_scheduler:bool):
        self.__show_scheduler = show_scheduler
    
    @property
    def policy_family(self) -> str:
        return self.__policy_family
    @policy_family.setter
    def policy_family(self, family:str):
        self.__policy_family = family
        
    @property
    def length_line(self) -> int:
        return self.__length_line
    @length_line.setter
    def length_line(self, length:int):
        self.__length_line = length
        
    @property
    def default_printer(self) -> str:
        return self.__default_printer
    @default_printer.setter
    def default_printer(self, prtname:str):
        if prtname != w32p.GetDefaultPrinter():
            self.__default_printer = prtname
            w32p.SetDefaultPrinter(prtname)
    
    @property
    def splashscreen(self) -> bool:
        return self.__splashscreen
    @splashscreen.setter
    def splashscreen(self, splashscreen:bool):
        self.__splashscreen = splashscreen
    
    @property
    def datelong(self) -> bool:
        return self.__date_long
    @datelong.setter
    def datelong(self, datelong:bool):
        self.__date_long = datelong
    
    @property
    def saveCFGonquit(self) -> bool:
        return self.__saveCFG_on_quit
    @saveCFGonquit.setter
    def saveCFGonquit(self, saveCFG_on_quit:bool):
        self.__saveCFG_on_quit = saveCFG_on_quit
        self.__default_year = now.year
    
    @property
    def saveEDTonquit(self) -> bool:
        return self.__saveEDT_on_quit
    @saveEDTonquit.setter
    def saveEDTonquit(self, saveEDT_on_quit:bool):
        self.__saveEDT_on_quit = saveEDT_on_quit
    
    @property
    def default_year(self) -> int:
        return self.__default_year
    @default_year.setter
    def default_year(self, defaulyear:int):
        self.__default_year = defaulyear
    
    @property
    def app_size(self) -> tuple:
        return self.__app_size
    @app_size.setter
    def app_size(self, app_size:tuple):
        self.__app_size = app_size 
    
    @property
    def fullscreen(self) -> bool:
        return self.__fullscreen
    @fullscreen.setter
    def fullscreen(self, fullscreen):
        self.__fullscreen = fullscreen
        
    @property
    def paramfilename(self) -> str:
        return self.__params_fname
    @paramfilename.setter
    def paramfilename(self, filename:str):
        self.__params_fname = filename
        
    @property
    def datapath(self) -> str:
        return self.__data_path
    @datapath.setter
    def datapath(self, pathname:str):
        self.__data_path = pathname
        
    @property
    def imagepath(self) -> str:
        return self.__images_path
    @imagepath.setter
    def imagepath(self, pathname):
        self.__images_path = pathname
    
    @property
    def exportpath(self) -> str:
        return self.__export_path
    @exportpath.setter
    def exportpath(self, pathname):
        self.__export_path = pathname
        
    @property
    def datafilename(self) -> str:
        return self.__data_filename
    @datafilename.setter
    def datafilename(self, datafilename:str):
        self.__data_filename = datafilename
        
    @property
    def helpfilename(self) -> str:
        return self.__help_filename
    @helpfilename.setter
    def helpfilename(self, filename:str):
        self.__help_filename = filename
        
    @property
    def backfilename(self) -> str:
        return self.__back_filename
    @backfilename.setter
    def backfilename(self, filename:str):
        self.__back_filename = filename
        
    def __str__(self) -> str:
        return "\n".join([f"{key.replace('_App_Options',''):17}: {getattr(self, key)}" for key in self.__dict__.keys()])
            
                
class Saveload_CFG(object):

    def __init__(self):
        self.__filename = op.join(os.getcwd(),core_path, default_param_filename)    
        # --- Constructeur 'self.__options' avec les paramètres par défaut ----
        self.__options = App_Options()
        # ---------- mise en place des options lues dans le fichier -----------
        self.__parameters = [getattr(self.__options, key) for key in self.__options.__dict__.keys()]
        # ---------------------------------------------------------------------
        self.__options.paramfilename = op.basename(self.__filename)
 
    @property
    def options(self) -> App_Options:
        return self.__options
    @options.setter
    def options(self, parameters:list|App_Options):
        if isinstance(parameters, list):
            [setattr(self.__options, key, param) for key,param in list(zip(self.__options.__dict__.keys(),parameters))]
        elif isinstance(parameters, App_Options):
            [setattr(self.__options, key, param) for key,param in parameters.__dict__.items()]
        #[print(f"@options.setter__{key}: {value} -/- {type(value)}") for key,value in self.__options.__dict__.items() if key=="aesh_name"]     
    
    @property
    def parameters(self) -> list:
        #[print(f"@property_parameters__getattr({key}) : {getattr(self.__options, key)} -/- {type(getattr(self.__options, key))}") for key in self.__options.__dict__.keys() if key=="aesh_name"]     
        return [getattr(self.__options, key) for key in self.__options.__dict__.keys()]
        
    def cfg_backup(self):
        try:
            with open(self.__filename, 'wb') as outputfic:
                pkdata.dump(self.parameters, outputfic, pkdata.HIGHEST_PROTOCOL )
        except FileNotFoundError as msg:
            print(f" backup error {os.path.basename(self.__filename)}: {msg}")
            return False
        return True
        
    def cfg_load(self):
        if not op.isfile(self.__filename):
            # ------ application data folder ------
            if not op.isdir(op.join(os.getcwd(),core_path)):
                os.mkdir(path=core_path)
            # --------- user data folder ----------
            if not op.isdir(op.join(os.getcwd(),data_path)):
                os.mkdir(path=data_path)
            # ----- application images folder -----
            if not op.isdir(op.join(os.getcwd(),images_path)):
                os.mkdir(path=images_path)
            # ----- application export folder -----
            if not op.isdir(op.join(os.getcwd(),export_path)):
                os.mkdir(path=export_path)
            self.cfg_backup()
        try:
            with open(self.__filename, 'rb') as inputfic:
                self.__parameters = pkdata.load(inputfic)
        except Exception as msg:
            print(f" load error {os.path.basename(self.__filename)}: {msg}")            
            return False
        # -------- Paramètres sauvegardés ---------
        if self.__parameters:
            self.options = self.__parameters
            return True
        # -----------------------------------------
        return False


class Schedule_FileHandler():
    def __init__(self, options:App_Options):
        self.__options = options
        self.__filename = op.join(os.getcwd(),options.datapath,options.datafilename)
    
    @property
    def filename(self) -> str:
        return self.__filename
    @filename.setter
    def filename(self, fname):
        self.__filename = op.join(os.getcwd(),self.__options.datapath,fname)
        
    def load_schedule(self) -> tuple:    
        path,name = op.split(self.__filename)
        if not op.isfile(self.__filename):
            # ------------ Si le dossier n'existe pas il est créé -------------
            if not op.isdir(path): os.mkdir(path=path)
            # -----------------------------------------------------------------
            self.save_schedule((self.__options.aesh_name, dict({}), dict({}), studies_colors))
        try:
            with gzip.open(self.__filename, 'rb', compresslevel=6) as inputfic:
                dicodata = pkdata.load(inputfic)
        except gzip.BadGzipFile as msg:
            try:
                with open(self.__filename, 'rb') as inputfic:
                    dicodata = pkdata.load(inputfic)
            except Exception as msg:
                print(f" load error {os.path.basename(self.__filename)}: {msg}")
                dicodata = (Persons("nom...","prénom..."), dict({}), dict({}), studies_colors)         
        # ------------ Chargement dictionnaire emploi du temps OK -------------
        return dicodata
        
    def save_schedule(self, dico_schedulers:tuple) -> bool:
        try:
            with gzip.open(self.__filename, 'wb', compresslevel=6) as outputfic:
                outputfic.write(pkdata.dumps(dico_schedulers, pkdata.HIGHEST_PROTOCOL))
        except Exception as msg:
            print(f" backup error {os.path.basename(self.__filename)}: {msg}")
            return False
        return True

def loadCoredata_Files():
    """ Lit les données du fichier JSON du répertoire 'coreData' """
    from json import dumps,loads
    
    jsondata, jsonfile = "", op.join(os.getcwd(),core_path,coreData_filename)
    coresData:dict = {"schedules":list_schedules,"schoolsubjects":list_studsubjects,"classrooms":list_classrooms,"extraschoolwork":list_extraschool}
    
    if not op.isfile(jsonfile):
        for corename in coresData.keys():
            coredata_fname= op.join(os.getcwd(),core_path, corename)
            if op.isfile(coredata_fname):
                coresData[corename].extend(readCoreData(coredata_fname))
            else:
                coresData[corename].extend(get_args(globals()[corename]))
        jsondata += dumps(coresData,ensure_ascii=False,indent=4)    
        with open(jsonfile, mode='wt', encoding='utf-8') as jfile:
            jfile.write(jsondata)
    else:
        with open(jsonfile, mode='rt', encoding='utf-8') as jfile:
            json_coreData = loads(jfile.read())
        [coresData[corelist].extend(json_coreData[corelist]) for corelist in json_coreData]

def readCoreData(whichData:str) -> list[str]:
    """
    Lit les fichiers texte du dossier 'coreData'
    Args:
        whichData (str): quel fichier lire
    Returns:
        list[str]: la liste des items existants
    """
    with open(file=whichData,encoding='utf8',mode='r') as inFile:
            outData = [i.strip() for i in inFile.readlines()]
    return outData

def correct_filename(filename:str) -> str:
    return "".join([c if (c.isalnum() or c in ('.','-','_')) else "_" for c in filename])


if __name__ == "__main__":
    # ------------ Pour une traduction des messages de datetime() -------------
    try:
        locale.setlocale(locale.LC_TIME, ('Fr_fr.UTF-8','French_France'))
    except locale.Error as msg:
        print(f"Locale message: {msg}")
    # -------------------------------------------------------------------------    
    config = Saveload_CFG()
    if config.cfg_load():
        print(f"Options:\n{config.options}\nParameters: {config.parameters}")
        print(f" studies_colors: {studies_colors}")
    else:
        print(f"Bad config file")
        exit(1)

    My_Datetime.Long = True
    long_date = My_Datetime(2025,5,15)
    print(f"date longue: {long_date}")
    My_Datetime.Long = False
    short_date = My_Datetime(now.year, now.month, now.day)
    print(f"date courte: {short_date}")
        
    print(correct_filename("Semaine Q1.png"))
    
    #[print(f"coreData({file}): {readCoreData(file)}") for file in ["classrooms","studies","schedules"]]
    loadCoredata_Files()
    #[print(f" ---> {core}") for core in (list_schedules,list_studsubjects,list_classrooms,list_extraschool)]