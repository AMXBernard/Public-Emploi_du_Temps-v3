"""
schedulers, bibliothèque du projet Emploi_du_Temps. Fournit les objets, classes 
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

EDT v3.15 (C) 9/2025  Bernard AMOUROUX
This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.
"""

__author__ = "Bernard AMOUROUX"
__date__ = "$Date: 2025/09/05 07:00 $"
__copyright__ = "Copyright (c) 2025 Bernard AMOUROUX"
__license__ = "GPL 3"

import locale, re
import tkinter as tk
import tkinter.font as tkFont
import tkinter.colorchooser as tkColor

from configs import *
from guitools import List_popup
from random import choice


class Classroom():
    """ Classe qui renseigne:
            self.schoolsubject : la matière étudiée en cours
            self.classnumber   : numéro de la classe dans laquelle se déroule le cours
            self.specialcourse : si le cours doit être marqué 'spécial'
        Le constructeur demande:
            schoolsubject : la matière étudiée
            classnumber   : un numero de classe
            specialcourse : option, par défaut à 'False'
    """
    def __init__(self, schoolsubject:schoolsubjects, classnumber:classrooms, specialcourse:bool):
        self.__schoolsubject = schoolsubject
        self.__classnumber = classnumber
        self.__specialcourse = specialcourse
    
    @property
    def schoolsubject(self) -> str:
        return self.__schoolsubject
    @schoolsubject.setter
    def schoolsubject(self, schoolsubject:schoolsubjects):
        self.__schoolsubject = schoolsubject
        
    @property
    def classnumber(self) -> str:
        return self.__classnumber
    @classnumber.setter
    def classnumber(self, classnumber:classrooms):
        self.__classnumber = classnumber        

    @property
    def specialcourse(self) -> bool:
        return self.__specialcourse
    @specialcourse.setter
    def specialcourse(self, specialcourse:bool):
        self.__specialcourse = specialcourse

    def is_empty(self) -> bool:
        return bool(self.schoolsubject == "" and self.classnumber == "")

    def __eq__(self, other:"Classroom") -> bool:
        return bool(self.schoolsubject==other.schoolsubject and self.classnumber==other.classnumber) 

    def __hash__(self):
        return sum(map(ord, self.schoolsubject + self.classnumber))

    def __str__(self) -> str:
        return f"{self.schoolsubject} - Salle {self.classnumber} - VIP:{self.specialcourse}"


class Scheduler_case(tk.Frame):
    
    def __init__(self, master, col:int, row:int, dataclass:Classroom, *args, **kwargs):
        self.__master = master
        self.__readonly:bool = False
        self.vcsc_subject = tk.StringVar(value=dataclass.schoolsubject)
        self.vcsc_classroom = tk.StringVar(value=dataclass.classnumber)
        self.vcsc_special = tk.BooleanVar(value=dataclass.specialcourse)
        # --------- Couleur du contour principal de toutes les cases ----------
        color = studies_colors.get(self.vcsc_subject.get(),"DarkOliveGreen4")       
        # ---------------------------------------------------------------------
        tab_options:dict = {'bd':2, 'bg':color, 'relief':'groove'}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        self.csc_font = tkFont.Font(family='Consolas',size=11,weight='normal',slant='italic')
        # ---------------------------------------------------------------------
        # - donne la couleur de fond de toutes les cases des cours ou autre 
        room_color = studies_colors.get(self.vcsc_subject.get(),"azure2")
        # ---------------------------------------------------------------------
        self.bind_class('Entry','<Control-Button-1>', self.__select_special)
        self.bind_class('Entry',"<Alt-Button-1>", self.__choose_color)
        self.bind_class('Entry',"<Button-2>", self.__choose_color)
        self.bind("<Configure>", self.update_idletasks)
        self.grid(column=col,row=row,sticky="nsew")
        # ---------------------------------------------------------------------        
        self.csc_subject = tk.Entry(self,relief="sunken" if not dataclass.is_empty() else "ridge",
                                            bg=room_color,readonlybackground=room_color,justify="center",
                                                  textvariable=self.vcsc_subject,width=20,font=self.csc_font)
        self.csc_subject.bind("<Button-3>", self.__select_subject)
        self.csc_subject.grid(column=0,row=0,padx=1,sticky="nsew")
        # ---------------------------------------------------------------------
        self.csc_classroom = tk.Entry(self,relief="sunken" if not dataclass.is_empty() else "ridge",width=20,
                    bg=room_color,readonlybackground=room_color,textvariable=self.vcsc_classroom,justify="center")
        if not row in [4,7,10]:
            self.csc_classroom.bind("<Button-3>", self.__select_classroom)
            self.csc_classroom.grid(column=0,row=1,padx=1,ipady=2,sticky="nsew")
        else:
            self.csc_classroom.bind("<Button-3>", self.__select_extraschool)
            self.csc_classroom.grid(column=0,row=0,padx=1,ipady=3,sticky="nsew")
        self.update()    
    
    @property
    def dataclass(self) -> Classroom:
        return Classroom(self.vcsc_subject.get(),self.vcsc_classroom.get(),self.vcsc_special.get())
    @dataclass.setter
    def dataclass(self, dataclassroom:Classroom):
        self.vcsc_subject.set(dataclassroom.schoolsubject)
        self.vcsc_classroom.set(dataclassroom.classnumber)
        self.vcsc_special.set(dataclassroom.specialcourse)
        
    def get_readonly(self) -> bool:
        return self.__readonly
                    
    def readonly(self, readonly:bool):
        self.__readonly = readonly
        self.csc_subject.configure(state="readonly" if readonly else "normal")
        self.csc_classroom.configure(state="readonly" if readonly else "normal")
        return self.__readonly
    
    def __clean_case(self):
        self.vcsc_classroom.set("")
        self.vcsc_subject.set("")
    
    def __choose_color(self, event:tk.Event=None):
        # -------------------------------------------------
        from json import dumps
        # -------------------------------------------------
        if not self.__readonly and event:
            w:"Scheduler_case" = self.nametowidget(re.findall(r'(.![\S]+?case[\d]{0,2}).!',f"{event.widget}",flags=0)[0])
            color = tkColor.askcolor(initialcolor=w.cget('bg'),parent=self.__master,title="Choisissez une couleur pour la matière")
            # ------- Le choix de la couleur est différent de 'Cancel' --------
            if color != (None, None):
                data = dumps({"color":color[1], "subject":w.vcsc_subject.get()})
                self.__master.master.event_generate("<<Change_StudyColor>>",when="tail",data=data)
            else:
                return 'break'    
        
    def __select_subject(self, event:tk.Event):
        if self.__readonly: return 'break'
        subjects = tk.StringVar(value=(list_studsubjects))
        subject = List_popup(self.__master,subjects).go()    
        # ------------- On ne change rien car rien n'a été choisi -------------
        if subject == None: return 'break'
        # ------ Un choix a été fait, nouvelle matière ou on efface tout ------
        self.vcsc_subject.set(subject) if subject else self.__clean_case()
        self.update_idletasks()
        return 'break'
                             
    def __select_classroom(self, event:tk.Event):
        if self.__readonly: return 'break'
        rooms = tk.StringVar(value=list_classrooms)
        room = List_popup(self.__master,rooms).go()
        if room != None: self.vcsc_classroom.set(room)
        self.update_idletasks()
        return 'break'
    
    def __select_extraschool(self, event:tk.Event):
        if self.__readonly: return 'break'
        extras = tk.StringVar(value=list_extraschool)
        extra = List_popup(self.__master,extras).go()
        if extra != None: self.vcsc_classroom.set(extra)
        self.update_idletasks()
        return 'break'
        
    def __select_special(self, event:tk.Event=None):
        if event and not self.__readonly:
            w:"Scheduler_case" = self.nametowidget(re.findall(r'(.![\S]+?case[\d]{0,2}).!',f"{event.widget}",flags=0)[0])
            if not w.dataclass.is_empty():
                self.vcsc_special.set(not self.vcsc_special.get())
                w.configure(relief="solid") if self.vcsc_special.get() else w.configure(relief="ridge",bg=event.widget.cget('bg'))
                w.vcsc_special.set(self.vcsc_special.get())   
        return 'break'
    
    def update_idletasks(self, event:tk.Event=0):
        if self.dataclass.is_empty():
            self.configure(bg=studies_colors["Nothing"], relief="flat")
            self.csc_classroom.configure(relief="ridge",bg=studies_colors["Nothing"])
            self.csc_subject.configure(relief="ridge",bg=studies_colors["Nothing"])
            self.vcsc_special.set(False)
        else:
            self.configure(bg=studies_colors.get(self.vcsc_subject.get(),"azure2"), relief="ridge")
            self.csc_subject.configure(bg=studies_colors.get(self.csc_subject.get(),"azure2"), relief="sunken")
            self.csc_classroom.configure(bg=self.csc_subject.cget('bg'),relief="sunken")
        # ----------------- mise en place du visuel 'spécial' ----------------- 
        if self.vcsc_special.get(): self.configure(relief="solid")
    
    def __str__(self) -> str:
        return f"{self.vcsc_subject.get()} en salle {self.vcsc_classroom.get()}, Special:{self.vcsc_special.get()}"


class Schedule_day():
    """ Classe qui gère une journée d'emploi du temps.
        Le constructeur demande le jour à créer qui doit être du type 'workdays'
        Le dictionnaire contient le dictionnaire des données (horaires: Classroom(cours,salle,special))
        de la journée. Rempli de façon aléatoire pour tester la classe si 'workday' est à None.
        La méthode 'get_school_subjects(schedule)' renvoi la matière et la salle pour l'horaire
        demandé. 
    """
    def __init__(self, working_day:workdays, demo:bool=False):
        self.__work_day = working_day
        self.__day_hours:dict = ({})
        # ------- Construction aléatoire ou non des cours et des salles -------
        #subjects_and_extra = list(chain.from_iterable((list_studsubjects, list_extraschool)))
        if not demo:
            self.__day_hours:dict = {key:Classroom(f"{working_day[:3]} Matière", f"xx à {key}", False) for key in list_schedules}
        else:
            self.__day_hours:dict = {key:Classroom(choice(list_studsubjects),choice(list_classrooms),
                                                                                 choice([True,False])) for key in list_schedules}
        self.__day_hours.update({key:Classroom([], choice(["Surveillance self","Pause méridienne",""]),False) for key in ["Pause",]})
        self.__day_hours.update({key:Classroom([], choice(["Surveillance récré",""]),False) for key in ["Récré 1","Récré 2"]})

    @property
    def day_hours(self) -> dict:
        return self.__day_hours
    @day_hours.setter
    def day_hours(self, day_hours:dict):
        self.__day_hours.update({key:value for key,value in day_hours.items()})
    
    def get_workday(self) -> str:
        return self.__work_day
    
    def get_school_subjects(self, schedule:schedules) -> Classroom:
        return  self.__day_hours.get(schedule, Classroom("Matière","Salle",False))   
    
    def __str__(self) -> str:
        return f"{self.__work_day} :\n\t" + ' / '.join([key+': '+value.schoolsubject+ \
                        ' - salle '+value.classnumber+' ('+str(value.specialcourse)+')' for key,value in self.__day_hours.items()])


class Schedule_Week():
    """ Classe qui gère une semaine de cours. Du Lundi au Vendredi.
        Le constructeur va lire les donées à partir du fichier xxxxxxx.dat qui est
        référencé par 'options.datafilename'.
        Le dictionnaire contient les données (workday:SchoolSubject_by_day(workday))
        de la semaine et rempli les cases de l'emploi du temps.
    """
    def __init__(self, dico_week:dict, demo:bool=False):
        self.__week_hours:dict = ({})
        if not dico_week:    
            self.__week_hours:dict = {workday: Schedule_day(workday,demo=demo) for workday in list_workdays}
        else:
            self.weekschedule = dico_week
            print(f"Lecture du fichier de donnée OK") 
            
    @property 
    def weekschedule(self) -> dict:
        return self.__week_hours
    @weekschedule.setter
    def weekschedule(self, week_hours:dict):
        self.__week_hours.update({key:value for key,value in week_hours.items()})
    
    def get_schoolsubject_by_day_and_time(self, workday:workdays, schedule:schedules):
        return f"{workday} à {schedule} -> {self.__week_hours.get(workday, None).get_school_subjects(schedule)}"

    def __str__(self) -> str:
        return "\n".join([workday.__str__() for workday in self.weekschedule.values()])


class Scheduler(tk.Frame):
    """ Classe qui gère l'affichage de l'emploi du temps sur la semaine
        Les variables du constructeur sont:
            self.__master    : pointe sur l'application principale tk.Tk()
            self.__options   : variable de la classe 'App_Options' qui sont
            les paramètres/options du programme.
            self.__dico_week : dictionnaire de dictionnaire de Schedule_days
    """
    def __init__(self, master:tk.Tk, col:int, row:int, week_nbr:int, dico_week:dict, demo:bool=False, *args, **kwargs):
        self.__master = master
        self.dico_cases:dict = ({})
        self.__dico_week = dico_week
        self.__scheduler_demo:bool = demo
        self.vweek_btn_name = tk.StringVar(value=f"Semaine Q{week_nbr}")
        # ---------------------------------------------------------------------
        tab_options:dict = {'bd':3,'bg':'DarkOliveGreen1','relief':'ridge','padx':2,'pady':2}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        # ---------------------------------------------------------------------
        self.workdayfont = tkFont.Font(family='Courier',size=12,weight="bold",slant="italic")
        # ---------------------------------------------------------------------     

        # -- Interception de l'Event de 'Sceduler_case' et de 'data=' par %d --
        self._cmd = self.register(self.__actualiseColor)
        self.tk.call("bind",self._w,"<<Change_StudyColor>>",f"{self._cmd} %d")
        # ---------------------------------------------------------------------

        self.grid_configure(column=col,row=row,columnspan=6,rowspan=11,sticky="w")
        self.grid_anchor("center")
        # ---------------------------------------------------------------------
        if not dico_week:
            self.scheduler_week = Schedule_Week(dico_week=None, demo=demo)
            self.__dico_week.update({key:value for key,value in self.scheduler_week.weekschedule.items()})
            self.__scheduler_demo = demo
        # ---------------------------------------------------------------------
        self.cree_widgets()
        
    def cree_widgets(self):
        self.week_button = tk.Button(self,bg="light pink",activebackground="light pink",
                                        state="active",font=('Consolas 10 bold italic'),relief="groove",
                                               bd=3,command=self.__on_button1,textvariable=self.vweek_btn_name)
        self.week_button.grid(column=0,row=0,sticky="nsew")
        # ----------- Création de la ligne des jours de la semaine ------------
        for idx,day in enumerate(list_workdays):
            self.frameday = tk.Frame(self,bg="PaleGreen4",bd=2,relief="ridge")
            self.frameday.grid(row=0,column=idx+1,padx=0,sticky="nsew")
            tk.Label(self.frameday,text=f"{day:^16}",font=self.workdayfont).grid(sticky="nsew")
        # ---------------- Création de la colone des horaires -----------------
        for idx,schedule in enumerate(list_schedules[:-1]):
            self.frameschedule = tk.Frame(self,bg="PaleGreen4",bd=2,relief="ridge")
            self.frameschedule.grid(row=idx+2,column=0,padx=0,rowspan=1,sticky="nsew")
            tk.Label(self.frameschedule,text=f"{schedule:^12}",
                font=self.workdayfont).grid(ipady=10 if schedule not in ("Récré 1","Récré 2","Pause") else 0,sticky="nsew")
        # ----- Création des cases de l'emploi du temps chargé en mémoire -----
        for j in range(0,len(list_schedules)-1):       # -- lignes   = horaires
            for i in range(0,len(list_workdays)):      # -- colones  = jours
                case_ID = j * 5 + i if j != 0 else i
                classe:Classroom = self.__dico_week[list_workdays[i]].day_hours[list_schedules[j]]
                self.dico_cases[case_ID] = (case_ID,list_workdays[i],
                                                list_schedules[j],Scheduler_case(self,i+1,j+2,classe))
        # ---------------------------------------------------------------------
        #[print(self.dico_cases[case][3]) for case in self.dico_cases.keys() if self.dico_cases[case][3].is_Empty()]
        self.update()
    
    @property
    def scheduler_demo(self) -> bool:
        return self.__scheduler_demo
    @scheduler_demo.setter
    def scheduler_demo(self, schedulerdemo:bool):
        self.__scheduler_demo = schedulerdemo
    
    def __hash__(self):
        return super().__hash__() + sum(map(lambda c:c[3].dataclass.__hash__(), self.dico_cases.values()))
    
    def readonly(self, readonly:bool=True) -> bool:
        return all([self.dico_cases[key][3].readonly(readonly) for key in self.dico_cases.keys()])
            
    def get_scheduler_data(self) -> dict:
        for day in list_workdays:
            day_data = list(map(lambda d_c:(d_c[2],d_c[3].dataclass), 
                                                list(filter(lambda c:c[1]==day, self.dico_cases.values()))))
            #print(f"day_data ({day}): {day_data[0][0]} - {day_data[0][1].__str__()}")
            schedule_day = Schedule_day(day)
            schedule_day.day_hours = {key:data for key,data in day_data}
            self.__dico_week[day] = schedule_day        
        return self.__dico_week


    def __actualiseColor(self, tcl_data:str):
        # -------------------------------------------------
        from json import loads
        # -------------------------------------------------
        data = loads(tcl_data); widgets:list = ([])
        color = data["color"]; study = data['subject']
        # ------- On récupère TOUS les widgets de la matière recherchée -------
        [widgets.extend(list(filter(lambda s_c:s_c.dataclass.schoolsubject == study, \
                           list(map(lambda sc:sc[3], dico.dico_cases.values()))))) for dico in [self.scheduler_Q1,self.scheduler_Q2]]
        for w in widgets:
            w.configure(bg=color); w.csc_subject.configure(bg=color); w.csc_classroom.configure(bg=color)
        # --- On affecte la nouvelle couleur au dico des couleurs principal ---  
        studies_colors.update({study:color})

    
    def __on_button1(self):
        if __name__ == 'scheduler': self.__master.on_schedule_event()
            
        
if __name__ == "__main__":
    # ------------ Pour une traduction des messages de datetime() -------------
    try:
        locale.setlocale(locale.LC_TIME, ('Fr_fr.UTF-8','French_France'))
    except locale.Error as msg:
        print(f"Locale message: {msg}")
    # -------------------------------------------------------------------------
    config = Saveload_CFG()
    if not config.cfg_load():
        exit(1)
    
    
    root = tk.Tk()
    dico_week:dict = ({})
    root.EDT_fileHandler = Schedule_FileHandler(config.options)
    person, dico_Q1, dico_Q2, colors = root.EDT_fileHandler.load_schedule()
    if colors: studies_colors.update(colors)
    loadCoredata_Files()    # -- lit le 'json' du dossier 'coreData'
    demo = bool(person.nom == "NOM..."); print(f"person.nom: {person.nom} -/- demo: {demo}")
    schedul1 = Scheduler(root, col=0, row=0, week_nbr=1, dico_week={}, demo=True)   #, options=config.options)
    print(f"schedul1.scheduler_demo: {schedul1.scheduler_demo}")
    #schedul2 = Scheduler(root, col=0, row=0, week_nbr=1, dico_week=dico_Q2, demo=True)   #, options=config.options)
    #print(f"schedul.get_scheduler_data():\n{schedul.get_scheduler_data()['Lundi']}")
    #print(f"schedul.dico_cases['0']: {schedul.dico_cases[0]}")
    #schedul.get_scheduler_data()['Lundi']
    #print(f"schedule.get_readonly: {schedul.readonly()}")
    #print(f"schedule_hash: {schedul.__hash__()}")
    #classroom = Scheduler_case(schedul,1,1,Classroom("essai matière","essai classe", True))
    #classroom.dataclass = Classroom("Matière 1","Salle xx",True)
    #print(classroom)
    
    root.mainloop()
    #print(f"schedul.get_scheduler_data():\n{schedul2.get_scheduler_data()['Lundi']}")
    """
    while True:
        schedule = choice(list_schedules)
        if schedule not in ["Récré"]: break
    print(scheduler_week.get_schoolsubject_by_day_and_time("Lundi",schedule))
    print(scheduler_week.get_schoolsubject_by_day_and_time(choice(list_workdays),schedule))
    scheduler_week.EDT_fileHandler.save_schedule(scheduler_week.weekschedule)
    """
    
