#!/usr/bin/python3.8
# coding: utf-8
"""
EDT-EmploiDuTemps v3.15 - Une étude Python POO en mode graphique (TKinter) 
et Python 3.12.10 pour gérer plus facilement l'emploi du temps des AESH 
du collège. Copyright (C) 2025/2026  Bernard AMOUROUX

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
__version__ = "3.15"


from configs import *
from guitools import *

import tkinter.font as tkFont

from shutil import copyfile
from PIL import Image,ImageGrab 
from PIL import ImageDraw,ImageFont,ImageTk,ImageWin
from winprinter import Windows_InitPrinters,w32c,w32p,w32i
from platformdirs import user_documents_dir
from hlptools import Help_System
from scheduler import Scheduler
from subprocess import Popen


Init_APP:bool = True
Scalling:float = get_windows_scalling()

class Application(tk.Tk):
    """ Classe qui gère l'affichage et la gestion de l'application elle-même
        Paramètre:
            'filename': nom du fichier 'prenom.dat' des personnes dont on doit 
                        gérer les heures. Peut-être passé en paramètre de ligne
                        de commande.
    """
    def __init__(self, filename:str):  
        global Init_APP, Scalling
        
        self.master_scheduler:Scheduler = None    
        # ------- Chargement du fichier des paramètres de l'application -------
        self.app_parameters = Saveload_CFG()
        self.app_printers = Windows_InitPrinters(self)
        if self.app_parameters.cfg_load():
            self.app_options = self.app_parameters.options
            Init_APP = bool(f"{self.app_options.aesh_name.__str__()}" == "NOM..., Prénom... (AESH)")
            #print("Loaded options:"+"\n\t".join([f"{opt}" for opt in self.app_options.__dict__.values()]))
            self.__readonly = bool(self.app_options.schedulemode == "Mode Consultation")
            My_Datetime.Long = self.app_options.datelong
        else:
            print("Bad 'CFG' file. Delete it!")
            exit(1)
        
        # ---- Chargement du fichier de données passé en ligne de commande ----
        if filename and op.isfile(op.join(os.getcwd(),self.app_options.datapath,filename)):
            self.app_options.datafilename = op.basename(filename.strip())
        # ---- Chargement du fichier 'coreData.JSON' du dossier 'coreData' ----
        loadCoredata_Files() # -- classrooms, extras..., shedules, school... -- 
        # ---------------------------------------------------------------------
        super().__init__(className="Application")
        print(f" EDT v3.15 written with Python 3.12 - Tkinter(),Tcl" \
                    f"v{self.tk.exprstring('$tcl_version')} / {locale.getlocale()} / Scalling: {Scalling} / DPI: {self.winfo_fpixels('1i')}")
        # ----- update variables de l'application avec nouvelles options ------
        self.MAX_WIDTH, self.MAX_HEIGHT = self.maxsize()
        self.__filename = os.path.join(os.getcwd(),self.app_options.imagepath,self.app_options.backfilename)
        if op.isfile(self.__filename):
            background = Image.open(self.__filename, mode='r')
            self.backImage = ImageTk.PhotoImage(background.resize((self.MAX_WIDTH,self.MAX_HEIGHT), Image.Resampling.LANCZOS),master=self)
        else:
            print(f"Background file '{self.__filename}' not found. Exiting EDT v3.15")
            self.quit()
            exit(2)
        # ---------------------------------------------------------------------
        self.messageBox = Win_MessageBox(self) 
        self.help_handler = Help_System(self, self.app_options,title="EDT_AESH v3")
        # --------- Initialisation du nom d'utilisateur 1er lancement ---------
        if Init_APP:
            person, date = Name_FirstDay(self, self.app_options).go()
            if person and date:
                My_Datetime.Long = self.app_options.datelong
                self.app_options.date_rentree = date
                person = self.__get_username(person)
                self.app_options.aesh_name = person
                data_filename = correct_filename(f"EDT_{person.prenom.lower()}.dat") if person.prenom != "Prénom..." else "EDT_default.dat"
                self.app_options.datafilename = data_filename
                Init_APP = False
            else:
                print("AESH name or date of first day not set. Exiting EDT v3.15")
                self.master_scheduler = Scheduler(None, 0,0,1, {}, True)
                self.Quit()
            # --- Sauvegarde du nouvel utilisateur et date rentrée scolaire --- 
            self.app_parameters.cfg_backup()    # sauvegarde nouvelle configuration
        # ------------- Lecture du fichier de données utilisateur -------------
        self.EDT_fileHandler = Schedule_FileHandler(self.app_options)
        loaded_schedulers = self.EDT_fileHandler.load_schedule()
        if len(loaded_schedulers) < 4:
            self.dico_Q1, self.dico_Q2, dico_colors = loaded_schedulers
        else:
            self.app_options.aesh_name, self.dico_Q1, self.dico_Q2, dico_colors = loaded_schedulers
        if dico_colors: studies_colors.update(dico_colors)
        # ---------------------------------------------------------------------
        self.mnuFont = tkFont.Font(self, family='Serif', size=11, weight='normal', slant='italic')
        self.lbxFont = tkFont.Font(self, family='Courier New', size=12, weight='bold', slant='italic')
        self.eryfont = tkFont.Font(self, family='Courier New', size=10, weight='bold', slant='italic')
        self.lblFont = tkFont.Font(self, family='Sans', size=12, weight='normal', slant='italic') 
        text = "=tkFont.Font(self,family='Courier New',size=11, weight='bold', slant='roman')1234"
        self.lb_mesure = self.lblFont.measure(text)//80, self.lblFont.metrics('linespace')
        # ---------------------------------------------------------------------
        self.protocol('WM_DELETE_WINDOW',self.Quit)
        # ---------------------------------------------------------------------
        width, height = (self.MAX_WIDTH-offset_W, self.MAX_HEIGHT-offset_H)
        self.app_size = (width,height) if self.app_options.app_size==(0,0) else self.app_options.app_size
        self.geometry(f"{self.app_size[0]-offset_W}x{self.app_size[1]-offset_H}+{(width-self.app_size[0])//2}+{(height-self.app_size[1])//2}")
        self.minsize(1280-offset_W, 760-offset_H)  # - Ecran mini de 1280x760 : Mode VESA -
        self.configure(bd=0,relief="flat",bg="pale green")
        # ---------------------------------------------------------------------
        self.columnconfigure([0,1], weight=20,minsize=40)
        self.columnconfigure([6,7], weight=1,minsize=40)
        self.rowconfigure(list(range(14)), weight=1, minsize=40)
        # ---------------------------------------------------------------------
        self.title("EDT v3.15 - Emploi du Temps des AESH - (c)2025/2026 AMOUROUX Bernard")
        # ----------------- Mise en place plein écran oui/non -----------------
        self.__fullscreen:bool = self.app_options.fullscreen
        self.attributes("-fullscreen", self.__fullscreen)
        # ------ Création virtual-Event menu contextuel et sauvegarde ---------
        self.event_add("<<PopupMenu>>","<Control-M>","<Control-m>","<Button-3>")
        self.event_add("<<BackupSchedulerData>>","<Control-S>","<Control-s>")
        # -- Interception de l'Event de 'Sceduler_case' et de 'data=' par %d --
        self._cmd = self.register(self.__actualiseColor)
        self.tk.call("bind",self._w,"<<Change_StudyColor>>",f"{self._cmd} %d")
        # ----------------------- EDT main poup menu --------------------------
        commandsList = [(" Paramètres de EDT","Ctrl-M",self.parameters),
                        (" Initialiser la nouvelle année scolaire","Ctrl-R",self.raz_schoolYear),
                        ("separator","",None),
                        (" Mode Consultation/Modification","",self.change_mode),
                        ("separator","",None),
                        (" Créer/Charger un nouvel Emploi du Temps","Alt-F2",self.create_NewScheduler),
                        (" Afficher un EDT de Démonstration","",self.load_schedule_demo),
                        (" Sauvegarder les données","Ctrl-S",self.backup_schedule_data),
                        ("separator","",None),
                        (' Générer le PDF des semaines Q1/Q2',"",lambda PDF=False: self.create_PrintSchedulers(print_PDF=PDF)),
                        (' Imprimer l\'agenda des semaines Q1/Q2',"",lambda PDF=True: self.create_PrintSchedulers(print_PDF=PDF)),
                        (" Prévisualiser le PDF avant l'impression","",self.show_schedulerPNG),
                        ("separator","",None), 
                        (" Mode plein écran on/off","F11",self.__toggle_fullscreen),
                        ("separator","",None),
                        (" A propos de Emploi Du Temps (EDT)","",self.fenetre_a_propos),
                        (" Quitter EDT "," Alt-F4 ",self.Quit)]
        self.EDTmainMenu = PopupMenu(self, "EDT PopupMenu,",commandsList)
        # ---------------------------------------------------------------------
        self.bind("<<BackupSchedulerData>>", self.backup_schedule_data)
        self.bind("<Control-F12>", self.__showHide_aeshScheduler)
        self.bind("<Configure>", self.update_idletasks)
        self.bind("<Alt-F2>", self.create_NewScheduler)
        self.bind("<<PopupMenu>>", self.__menu_popup)
        self.bind("<Escape>", self.__exit_fullscreen)
        self.bind("<Control-R>", self.raz_schoolYear)
        self.bind("<F11>", self.__toggle_fullscreen)
        self.bind("<F1>", self.whole_help)
        self.bind("<Alt-F4>", self.Quit)
        # ---------------------------------------------------------------------
        self.grid_anchor("center")
        self.cree_widgets()
        if self.app_options.splashscreen: self.fenetre_a_propos()

    def __menu_popup(self, event:tk.Event=None):
        NoSel = [12,13] if not self.__no_print__() else []
        if self.app_options.default_year == now.year: NoSel.extend([3,])
        if self.master_scheduler.scheduler_demo: NoSel.extend([8,9]) 
        self.EDTmainMenu.show_Menu_Popup(event, nosel=NoSel)
                 
    def cree_widgets(self):
        self.withdraw()
        # ----- Création du tk.Canvas() pour affichage de l'image de fond -----
        self.background = tk.Canvas(self, bg="light cyan", bd=0,name="!canvas_Background",relief="flat",
                                                       height=self.cget('height'), width=self.cget('width'))
        self.back_window = self.background.create_image(0,0,image=self.backImage,anchor="nw",tags='img_background')
        self.background.grid(column=0,row=0,columnspan=8,rowspan=15,sticky="nsew")
        # ------------------- Calcul de la semaine en cours -------------------
        self.currentweek:current_weeks = self.compute_current_week(self.app_options)
        self.app_options.currentweek = self.currentweek
        # ------------ Création des 2 Scheduler (semaines Q1 et Q2) -----------
        self.create_schedulers(demo=False,_hash=True)
        # ---------------------------------------------------------------------
        self.my_now = tk.StringVar(value=My_Datetime(now.year,now.month,now.day))
        def_message = f" Info : Emploi du Temps de {self.app_options.aesh_name} - " \
                                                f"Aujourd'hui {self.my_now.get()} ({self.currentweek})"
        self.state_bar = Window_StateBar(self,"",0,col=0,row=14,cspan=6,defMessage=def_message)
        self.mode_button = tk.Button(self,bg="#EB7575",text=f"{self.app_options.schedulemode:^24}",font=self.eryfont,command=self.change_mode)
        self.mode_button.grid(column=6,row=14,columnspan=2,padx=2,pady=2,sticky="ew")
        self.deiconify()
    
    def create_schedulers(self, demo:bool=False, _hash:bool=True):
        if not hasattr(self, "scheduler_hash"): self.scheduler_hash:int = 0
        self.scheduler_Q1 = Scheduler(self,col=1,row=2,week_nbr=1,dico_week=self.dico_Q1, demo=demo)
        self.scheduler_Q1._semaine = "Semaine Q1"; self.scheduler_Q1.grid_remove()
        self.scheduler_Q2 = Scheduler(self,col=1,row=2,week_nbr=2,dico_week=self.dico_Q2, demo=demo)
        self.scheduler_Q2._semaine = "Semaine Q2"; self.scheduler_Q2.grid_remove()
        if _hash: self.scheduler_hash = hash((self.scheduler_Q1.__hash__(),self.scheduler_Q2.__hash__(),self.__colors_hash__()))
        # -- determination du scheduler correspondant à la semaine en cours ---
        self.master_scheduler = self.scheduler_Q1 if self.currentweek == "Semaine Q1" else self.scheduler_Q2
        # -------- Lecture seule des schedulers si 'Mode Consultation' --------
        if self.__readonly: self.scheduler_Q1.readonly(); self.scheduler_Q2.readonly()    
        # ----------- Affichage du scheduler de la semaine en cours -----------
        self.master_scheduler.grid()
    
    def create_NewScheduler(self, event:tk.Event=None):
        message = f"\n !!! Un redémarrage de EDT v3.15 sera nécessaire  \npour initialiser la création\n" \
                  f"du nouvel agenda.\n\n" \
                  f"Si le prénom de l'AESH saisi ci-après correspond\n" \
                  f"à un nom de fichier 'prénom.dat' existant,\nil sera chargé et l'agenda affiché.\n\n" \
                  f"\n'Non' annule le chargement/la création.  " 
        choix = My_MessageBox(self,"Redémarrage de EDT v3.15",message=message,action=0).go()
        # ------ Redémarrage du programme sans créer de nouveau process -------    
        if choix == "yes":
            self.app_options.aesh_name = Persons("Nom...", "Prénom...")
            person, date = Name_FirstDay(self, self.app_options).go()
            if person and date:
                My_Datetime.Long = self.app_options.datelong
                self.app_options.date_rentree = date
                self.app_options.aesh_name = person
                data_filename = correct_filename(f"EDT_{person.prenom.lower()}.dat")
                self.app_options.datafilename = data_filename
                # ------------- sauvegarde nouvelle configuration -------------
                self.app_parameters.cfg_backup()
                # --- Redémarrage de l'application pour prise en compte EDT ---
                python = sys.executable                # Chemin vers l'exécutable Python
                source = op.abspath(sys.argv[0])       # Nom du script python
                if "EDT_" in python:                   # Si exécutable EDT_xxxxxx.exe
                    Popen([source, self.app_parameters.options.datafilename, "normal"])  # relance l'exécutable dans un nouveau processus en mode "normal", "debug", "offline" etc ...
                else:
                    Popen([python, source, "normal"])  # relance le script dans un nouveau processus
                self.Quit()                            # Ferme proprement Tkinter()
            else:
                return 'break'    
        else:
            return 'break'    
        
    def raz_schoolYear(self, event:tk.Event=None):
        message = f" !!! Redémarrage de EDT v3.15 nécessaire\npour initialiser\n" \
                  f"la nouvelle année scolaire '{now.year}'\n"
        choix = My_MessageBox(self,"Redémarrage de EDT v3.15",message=message,action=0).go()
            # ---- Redémarrage du programme sans créer de nouveau process -----    
        if choix == "yes":
            # ------ Sauvegarde des données de l'année scolaire terminée ------
            name,ext = op.splitext(self.app_options.datafilename)
            datapath = op.join(os.getcwd(),self.app_options.datapath)
            new_name = op.join(datapath,f"{name}_{self.app_options.default_year}{ext}")
            copyfile(op.join(datapath,self.app_options.datafilename), new_name)
            # ------------- Effacement du fichier 'EDT_config.cfg' ------------
            os.remove(op.join(os.getcwd(), self.app_options.datapath, self.app_options.paramfilename))
            # ---- Redémarre le programme en relançant l'exécutable courant ---
            python = sys.executable                # Chemin vers l'exécutable Python
            source = op.abspath(sys.argv[0])       # Nom du script python
            if "EDT_" in python:                   # Si exécutable EDT_xxxxxx.exe
                Popen([source, self.app_parameters.options.datafilename, "normal"])  # relance l'exécutable dans un nouveau processus en mode "normal", "debug", "offline" etc ...
            else:
                Popen([python, source, "normal"])  # relance le script dans un nouveau processus
            self.quit()                            # Ferme proprement Tkinter()
    
    def change_mode(self):
        self.__readonly = not self.__readonly
        mode = all([scheduler.readonly(self.__readonly) for scheduler in (self.scheduler_Q1,self.scheduler_Q2)])
        mode_message = "Mode Modification" if not mode else "Mode Consultation"
        self.mode_button.configure(text=f"{mode_message.strip():^24}")
            
    def compute_current_week(self, options:App_Options) -> current_weeks:
        actual = datetime.strftime(now,"%V")
        first = datetime.strftime(options.date_rentree,"%V")
        # ---- Si (actual - first) est pair -> semaine Q1 sinon semaine Q2
        return list_curweeks[bool(abs(int(actual) - int(first)) % 2 != 0)]
    
    def __colors_hash__(self) -> int:
        return sum([v.__hash__() for v in studies_colors.values()])
    
    def __get_username(self, person:Persons) -> Persons:
        AESH1 = self.app_parameters.options.aesh_name; AESH2 = person
        message = f"Les noms du fichier de configuration et de\nl'Agenda que vous avez chargé sont différents.\n" \
                  f"\n(1): {AESH1.__str__()}\n(2): {AESH2.__str__()}\n" \
                  f"\nA quel utilisateur voulez-vous attribuer cet Agenda ?\n"
        my_choice = My_MessageBox(self,"Choix de l'utilisateur",message=message,action=(f"{AESH1.prenom} (1)", f"{AESH2.prenom} (2)")).go()          
        if my_choice =="yes":
            return AESH1
        elif my_choice =="no":
            return AESH2
        else:
            return Persons("NOM...", "Prénom...")
    
    def __actualiseColor(self, tcl_data:str):
        # -------------------------------------------------
        from json import loads
        # -------------------------------------------------
        data = loads(tcl_data); widgets:list = ([])
        color = data["color"]; study = data['subject']
        #print(f"__actualiseColor() --> color: {color} -/- study: {study}")
        # ------- On récupère TOUS les widgets de la matière recherchée -------
        [widgets.extend(list(filter(lambda s_c:s_c.dataclass.schoolsubject == study, \
                           list(map(lambda sc:sc[3], dico.dico_cases.values()))))) for dico in [self.scheduler_Q1,self.scheduler_Q2]]
        for w in widgets:
            w.configure(bg=color); w.csc_subject.configure(bg=color); w.csc_classroom.configure(bg=color)
        # --- On affecte la nouvelle couleur au dico des couleurs principal ---  
        studies_colors.update({study:color})
    
    def backup_schedule_data(self, event:tk.Event=None):
        person = self.app_options.aesh_name
        if self.EDT_fileHandler.save_schedule((person, self.scheduler_Q1.get_scheduler_data(),
                                                          self.scheduler_Q2.get_scheduler_data(), studies_colors)):
            self.scheduler_hash = hash((person.__hash__(),self.scheduler_Q1.__hash__(),self.scheduler_Q2.__hash__(),self.__colors_hash__()))
            self.state_bar.update_vltexte(' Info : Sauvegarde des données OK.',5)
        else:
            self.state_bar.update_vltexte(' Erreur : Données non sauvegardées. Erreur disque.',5)
        
    def load_schedule_demo(self):
        # --------- Création des données de démo pour les schedulers ----------
        self.dico_Q1, self.dico_Q2 = {}, {}    
        self.create_schedulers(demo=True,_hash=True)
        # --- Lors de la fermeture de EDT, aucune sauvegarde ne sera faite ----
    
    def show_schedulerPNG(self, event:tk.Event=None):
        PNGviewer = My_PNGviewer(self, self.app_options)
        
    def __grab_image(self, schedul:Scheduler) -> Image.Image:
        # --------- Capture d'écran de la fenêtre du scheduler actif ----------
        x,y,w,h = schedul.winfo_rootx(), schedul.winfo_rooty(), schedul.winfo_width(), schedul.winfo_height()
        self.after(200, None)
        image = ImageGrab.grab(bbox=(int(x*Scalling), int(y*Scalling), int(x*Scalling) + int(w*Scalling), \
                                                            int(y*Scalling) + int(h*Scalling)),all_screens=True)
        return image            
                        
    def __resize_img(self, image:Image.Image, width:int) -> Image.Image:
        ratio = width / image.width
        return image.resize((int(width), int(image.height * ratio)), Image.LANCZOS)

    def __generate_schedulers(self) -> list[Image.Image]:
        images:list = ([])
        self.scheduler_Q1.grid_remove(); self.scheduler_Q2.grid_remove()
        for scheduler in (self.scheduler_Q1, self.scheduler_Q2):
            # ----------------- Affichage du scheduleur actif -----------------
            scheduler.grid()
            self.update()
            # ------ Capture de la partie de l'écran du Scheduleur actif ------
            image = self.__grab_image(scheduler)
            # ------- Mise en cache du scheduler dans la liste 'images' -------
            scheduler.grid_remove()
            images.append(image)
        self.master_scheduler.grid()
        return images
        
    def create_PrintSchedulers(self, print_PDF:bool=True):
        # ------ Suppression de 'schedulers.png' pour pouvoir le recréer ------
        output_PNG:str = op.join(os.getcwd(),self.app_options.exportpath,corePNG_filename)
        if op.exists(output_PNG) and not print_PDF: os.remove(output_PNG)
        # ------------------- Taille A4 en pixels à 300 dpi -------------------
        a4_width, a4_height = (2480, 3508)
        top_margin, bottom_margin = 400, 100
        output_PDF:str = op.join(user_documents_dir(),f"{op.splitext(corePNG_filename)[0]}.pdf")
        # --------- Génération en cache des schedulers Semaines Q1/Q2 ---------
        (image_Q1, image_Q2) = self.__generate_schedulers() if not self.__no_print__() else (None, None)       
        # ------------- Génération du titre de la page à imprimer -------------
        titre:str = f"Emploi du Temps des Semaines Q1/Q2"        
        # ------------- Création d'une page blanche de taille A4 --------------
        pageA4 = Image.new("RGB", (a4_width, a4_height), "white")
        draw = ImageDraw.Draw(pageA4, mode=pageA4.mode)
        # -- Police ttf pour le Titre (police par défaut si aucune trouvée) ---
        try:
            titre_font = ImageFont.truetype(op.join("Windows","Fonts","Arial.ttf", size=60))
        except:
            titre_font = ImageFont.load_default(size=80)
        # --------- Impression du titre et d'une marge suppléméntaire ---------    
        text_width = draw.textlength(titre, font=titre_font)
        draw.text(((a4_width - text_width) // 2, 100), titre, font=titre_font, fill="black")
        # --------------- Impression du ou des emplois du temps ---------------
        target_width = a4_width - 200
        if all(img != None for img in(image_Q1,image_Q2)):
            # ------------------- Placer Q1 en haut de page -------------------
            image_Q1 = self.__resize_img(image=image_Q1, width=target_width)
            x_q1 = (a4_width - image_Q1.width) // 2
            pageA4.paste(image_Q1, (x_q1, top_margin))
            # ------------------- Placer Q2 en bas de page --------------------
            image_Q2 = self.__resize_img(image=image_Q2, width=target_width)
            x_q2 = (a4_width - image_Q2.width) // 2
            y_q2 = (a4_height - int(image_Q2.height*1.5) - bottom_margin)
            pageA4.paste(image_Q2, (x_q2,y_q2))
            # -- Sauvegarde en PDF dans 'Mes Documents' et PNG dans 'export' --
            pageA4.save(output_PDF, "PDF", resolution=300.0)
            pageA4.save(output_PNG, "PNG", resolution=150)
            # --- Suppression des fichiers générés devenus non nécessaires ----
            [image.close() for image in (image_Q1,image_Q2) if image != None]
            # -----------------------------------------------------------------
            statebar_msg = f" Info : Création du fichier des Emplois du Temps en PDF : 'Mes Documents\\{op.basename(output_PDF)}'"
            self.state_bar.update_vltexte(f"{statebar_msg}",10)
        if print_PDF:    
            # ----------- Impression Oui/Non du fichier PDF créé --------------
            message = f"\n{'Voulez-vous imprimer':^60}\n" \
                      f"\n{'l\'Emploi du Temps des semaines Q1 et Q2 ?':^60}\n"
            if My_MessageBox(self,"Impression des Emplois du Temps",message=message,action=0).go() == "yes":
                if self.app_printers.params_printer() == w32c.IDOK:
                    try:
                        self.print_schedulers()
                    except AttributeError as msg:
                        self.state_bar.update_vltexte(f" Info : {msg}",10)
                            
    def print_schedulers(self):
        fname = op.join(os.getcwd(),self.app_options.exportpath,corePNG_filename)
        if op.isfile(fname):
            try:
                self.app_printers.print_file(fname)
                self.state_bar.update_vltexte(" Info : Impression des Emplois du Temps Q1 et/ou Q2 terminé.")
            except Exception as msg:
                self.state_bar.update_vltexte(f" !!! Erreur d'impression : {msg}")         
        else:
            self.state_bar.update_vltexte(" Info : Le fichier des Emplois du Temps Q1/Q2 n'existe pas. Impression annulée !")

    def on_schedule_event(self, event:tk.Event=None):
        if self.scheduler_Q1.winfo_ismapped():
            self.scheduler_Q1.grid_remove()
            self.scheduler_Q2.grid()
            self.master_scheduler = self.scheduler_Q2
        elif self.scheduler_Q2.winfo_ismapped():
            self.scheduler_Q2.grid_remove()
            self.scheduler_Q1.grid()
            self.master_scheduler = self.scheduler_Q1
                
    def __showHide_aeshScheduler(self, event:tk.Event=None):
        if self.master_scheduler.winfo_ismapped():
            self.master_scheduler.grid_remove()
        else:
            self.master_scheduler.grid()
            
    def parameters(self):
        background = self.app_options.backfilename
        old_filename = op.basename(self.app_options.datafilename)
        options:App_Options = Parametre_EDT(self, self.app_options).go()
        if options:
            self.app_parameters.options = options
            new_background = bool(background != self.app_options.backfilename)
            if self.app_parameters.cfg_backup():
                #print("New options:"+"\n\t".join([f"{opt}" for opt in self.app_parameters.options.__dict__.values()]))
                self.state_bar.update_vltexte(' Info : Chargement des nouveaux paramètres effectué',2)
                My_Datetime.Long = self.app_parameters.options.datelong
                self.my_now.set(My_Datetime(now.year,now.month,now.day))
                if self.app_parameters.options.datafilename != old_filename:
                    # ---- Chargement des données et affichage nouvel EDT -----
                    self.EDT_fileHandler.filename = self.app_parameters.options.datafilename
                    try:
                        person, self.dico_Q1, self.dico_Q2, dico_colors = self.EDT_fileHandler.load_schedule()
                        studies_colors.update(dico_colors); demo = False
                    except ValueError:
                        person, self.dico_Q1, self.dico_Q2, demo = Persons("NOM...","Prénom..."), {}, {}, True
                        self.messageBox.message = f"\nFichier de données\n\tcorrompu et/ou incompatible.\t\n\nUn agenda de démonstration\nsera affiché.\n"
                    self.app_options.aesh_name = person
                    self.create_schedulers(demo=demo,_hash=False)
                message = f" Info : Emploi du Temps de {self.app_options.aesh_name} - Aujourd'hui {self.my_now.get()} ({self.currentweek})"
                self.state_bar.message = f"{message[:120]}"
                self.app_options = self.app_parameters.options
            if new_background:
                backimage = Image.open(os.path.join(os.getcwd(),self.app_parameters.options.imagepath, \
                                                           self.app_parameters.options.backfilename),mode='r')
                self.backImage = ImageTk.PhotoImage(backimage.resize((self.MAX_WIDTH,self.MAX_HEIGHT), Image.Resampling.LANCZOS),master=self)
                self.background.itemconfigure(self.back_window, image=self.backImage)
                
    def __exit_fullscreen(self, event:tk.Event=None):
        self.__fullscreen = False
        self.attributes("-fullscreen", self.__fullscreen)

    def __toggle_fullscreen(self, event:tk.Event=None):
        # ---- Contournement du bug Tkinter() ----
        self.after(150, self.deiconify)
        self.withdraw()
        super().update_idletasks()
        self.__fullscreen = not self.__fullscreen
        self.attributes("-fullscreen",self.__fullscreen)

    def update_idletasks(self, event:tk.Event=None):
        width, height = self.geometry().split('+')[0].split('x')
        self.app_options.app_size = (int(width)+offset_W, int(height)+offset_H)

    def menuhelpEDT(self, number:str):
        self.help_handler.delete_text()
        paragraphs = list(filter(lambda p:number in p.numero[0],self.help_handler.paragraphes.all_paragraph.values()))
        [self.help_handler.show_paragraph(number) for number in map(lambda p:p.numero, paragraphs)]
        self.help_handler.readonly()
    
    def __no_print__(self) -> bool:
        return op.exists(op.join(os.getcwd(),self.app_options.exportpath,corePNG_filename))
        
    def whole_help(self, event:tk.Event=None):
        self.help_handler.show_whole_help()
                
    def fenetre_a_propos(self):
        """ Fenêtre-message à propos.
            Indique le nom de l'auteurs ainsi que la licence.
        """
        message = "Emploi du Temps (EDT) v3.15"+"\nVersion AESH" \
        "\n\nUn aide à la gestion des horaires et emplois du temps pour les AESH\n" \
        "\n-/-\n\nCopyright (C)sep/2026 AMOUROUX Bernard" \
        "\nLicense : GPL Version 3, 29 June 2007"
        self.messageBox.boxtitle('À propos')
        self.messageBox.message = message
        self.messageBox.lift(self)
    
    def __save_CFG(self):
        if self.app_parameters.cfg_backup():
            self.state_bar.update_vltexte(" Info : Sauvegarde de la configuration.")
        else:
            self.state_bar.update_vltexte(" Info : ERREUR - Configuration non sauvegardée")
    
    def Quit(self, event:tk.Event=None):
        # -------------------- Si le scheduler est une demo -------------------
        if self.master_scheduler.scheduler_demo:
            #print(" ----> sortie demo <----")
            self.quit(); exit(0)
        # ------------------ Sauvegarde des paramètres de EDT -----------------
        if self.app_options.saveCFGonquit:
            self.__save_CFG()
        # ----- Sauvegarde du dictionnaire des données utilisateur de EDT -----
        ending_hash = hash((self.scheduler_Q1.__hash__(),self.scheduler_Q2.__hash__(),self.__colors_hash__()))
        if (ending_hash != self.scheduler_hash) and not self.app_options.saveEDTonquit:
            message = f"\n{'Des modifications ont été effectuées':^60}\n" \
                f"\n{'sur les Emplois du Temps.':^60}\n\n{'Sauvegarder les données avant de quitter ?':^60}\n"
            if My_MessageBox(self,"Sauvegarde des données EDT v3.15",message=message,action=0).go() == "yes":
                self.backup_schedule_data()
        elif self.app_options.saveEDTonquit:
            self.backup_schedule_data()
        self.after(500, self.quit())



if __name__ == "__main__":
    import sys
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except Exception as msg:
        print(f"Locale message: {msg}")        
    
    fname = sys.argv[1] if len(sys.argv) > 1 else None
        
    app = Application(filename=fname)
    icon = tk.PhotoImage(master=app, file=op.join(os.getcwd(),'images','edt.gif'))
    app.wm_iconphoto(True, icon)
    app.mainloop()
