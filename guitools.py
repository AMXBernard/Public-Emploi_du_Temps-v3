"""
GUITools, bibliothèque du projet Emploi_du_Temps. Fournit les classes 
pour la définition des objets graphiques de l'application. 
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
__date__ = "$Date: 2025/9/05 07:00 $"
__copyright__ = "Copyright (c) 2025 Bernard AMOUROUX"
__license__ = "GPL 3"


import os
import ctypes
import os.path as op
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import tkinter.filedialog as tkFileDialog
#import tkinter.scrolledtext as tkText

from datetime import datetime
from configs import now,core_path,list_schedulemodes
from configs import App_Options,My_Datetime,Persons
from ctypes import wintypes


class My_LabelFrame(tk.LabelFrame):
    def __init__(self,master, col=0,row=0,cspan=1,rspan=1,pad=(0,0,0,0),sticky='nsew', *args, **kwargs):

        tab_options:dict = {'bg':'ivory', 'bd':3, 'relief':'groove', 'labelanchor':'n'}
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)

        tk.LabelFrame.__init__(self,master,*args,**kwargs)        

        self.grid(column=col, row=row, columnspan=cspan, rowspan=rspan,
                                  padx=pad[0], pady=pad[1], ipadx=pad[2], ipady=pad[3], sticky=sticky)
        self.grid_columnconfigure(list(range(cspan)), weight=1)
        self.grid_rowconfigure(list(range(rspan)), weight=1)

    def name(self):
        return f"{self.master}."+self._name


class Window_StateBar(tk.Frame):
    def __init__(self, master, message, waitime, col=0, row=0, cspan=1, sticky="nsew",
                        defMessage:str=' Info : ', defTime:int=10, txtfont=None, *args, **kwargs):
        
        self.__master = master
        self.__message = message
        self.__waitnbr:int = None
        self.__defaultTime = defTime*1000
        self.__defaultMsg = defMessage
        self.__vl_texte = tk.StringVar()
        self.__wait = waitime

        tab_options:dict = {'bd':1, 'bg':'tan2', 'relief':'groove'}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        
        lblfont = ("Courier New",10 ,'bold','italic') if not txtfont else txtfont
        self.grid(column=col,row=row,columnspan=cspan,padx=2,pady=2,ipady=3,sticky=sticky)
        tk.Label(self,bd=0,bg=self.cget('bg'),anchor="sw",height=1,
                                font=lblfont,textvariable=self.__vl_texte).grid()
        self.update_vltexte(defMessage if not message else message, waitime)
        self.grid_anchor("w")

    @property
    def message(self) -> str:
        return self.__vl_texte.get().rstrip()
    @message.setter
    def message(self, default_msg:str):
        self.__defaultMsg = default_msg
        self.__raz_vltexte__() 
        
        
    def __raz_vltexte__(self):
        self.__vl_texte.set(self.__defaultMsg)
        self.__waitnbr = None
    
    def update_vltexte(self, msg:str, wait=10):
        if self.__waitnbr != None:
            self.after_cancel(id=self.__waitnbr)
        if wait == 0: 
            self.__raz_vltexte__()
        if wait > 1:
            self.__waitnbr = self.after(self.__defaultTime if wait==None else (wait*1000) , self.__raz_vltexte__)
        if msg: self.__vl_texte.set(msg)
        super().update_idletasks()


class Win_MessageBox(tk.Toplevel):
    def __init__(self, master:tk.Tk, message:str=None, *args, **kwargs):
        
        self.__master = master
        self.__name__ = '!win_messagebox'
        self.__vmessage = tk.StringVar(value=message)
        
        tab_options:dict = {'bd':3, 'bg':'wheat', 'relief':'ridge', 'pady':5}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        
        self.protocol("WM_DELETE_WINDOW", self.Quit)
        
        self.wm_attributes("-topmost", 1)    # - Fenetre popup toujours au premier plan
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.resizable(False, False)
        
        tk.Message(self,bg='wheat',width=500,aspect=100,justify=tk.CENTER,font=("Courier",14,"bold","italic"),
                                bd=3,relief="groove",textvariable=self.__vmessage).grid(padx=10,pady=10,sticky="nsew")
        tk.Button(self,width = 8,bg='tan',text='Ok',font=('TkDefaultFont 12 bold italic'),
                                                        command=self.Quit).grid(pady=20,sticky="s")
        self.bind('<Return>', self.Quit)
        self.withdraw()
    
    @property
    def message(self)->str:
        return self.__vmessage.get()
    @message.setter
    def message(self, message):
        self.__vmessage.set(message)
        if not self.winfo_ismapped():
            self.deiconify()
            self.lift(self.__master)
            self.grab_set()
        self.update()
        
    def boxtitle(self, title:str):
        self.title(title) 
    
    def Quit(self, event=None):
        self.boxtitle(" Message ")
        self.grab_release()
        self.withdraw()    
   

class My_MessageBox(tk.Toplevel):
    def __init__(self, master:tk.Tk, title:str, message:str=None, action:int=0, *args, **kwargs):
        
        self.__master = master
        self.__vtitle = tk.StringVar(value=title)
        self.__vmessage = tk.StringVar(value=message)
        tab_action = [("Oui","Non"),(" Valider "," Annuler "),(" Button1 "," Button2 "),]
        # ---------------------------------------------------------------------
        tab_options:dict = {'bd':3,'bg':'wheat','relief':'ridge','name':"!my_MessageBox"}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        # ---------------------------------------------------------------------        
        self.protocol("WM_DELETE_WINDOW", self.choose_cancel)
        self.wm_attributes("-topmost", 1)    # - Fenetre popup toujours au premier plan
        msg_font = ('Courier New',12,'bold','italic')
        btn_font = ('Courier New',14,'bold','italic')
        self.bind("<Escape>", self.no_command)
        self.bind("<Return>", self.ok_command)
        self.title(self.__vtitle.get())
        self.resizable(False, False)
        # ---------------------------------------------------------------------
        self.withdraw()
        if isinstance(action, int):
            title1,title2 = tab_action[action][0], tab_action[action][1]
        elif isinstance(action, tuple):
            title1,title2 = action[0], action[1]
        else:
            title1,title2 = tab_action[2][0], tab_action[2][1]
        # ---------------------------------------------------------------------
        tk.Message(self,bg='wheat',width=600,aspect=100,justify=tk.CENTER,font=msg_font,
                                               textvariable=self.__vmessage).grid(padx=10,pady=10,
                                                      column=0,row=0,columnspan=6,rowspan=4,sticky="nsew")
        self.playButton = tk.Button(self,text=title1,width=12,font=btn_font,state="active",
                                            activebackground="lightgreen",command=self.ok_command,padx=10)
        self.playButton.grid(column=1,row=4,pady=10,sticky="nw")
        self.quitButton = tk.Button(self,text=title2,width=12,font=btn_font,
                                            activebackground="tan",command=self.no_command,padx=10)
        self.quitButton.grid(column=3,row=4,pady=10,sticky="ne")
        # ---------------------------------------------------------------------
        self.deiconify()
        self.focus_set()

    def go(self):
        """ Methode qui permet de garder le focus sur la fenetre de choix
            et qui renvoi l'action choisie parmi 'tab_actions' sur chaque
            bouton puis ferme la fenetre Toplevel.
        """
        self.lift(self.__master)        # mise au premier plan de la Toplevel
        self.wait_visibility()
        self.grab_set() 
        self.how = self.choose_ok       # Nom de la procédure exécutée en sortie
        self.mainloop()                 # Sortie de la Boucle principale par "self.quit(how)"
        self.destroy()                  # Fermeture de la fenetre Toplevel
        return self.how

    def choose_ok(self) -> str:
        return "yes"

    def choose_nok(self) -> str:
        return "no"
    
    def choose_cancel(self):
        self.Quit(None)
        
    def ok_command(self, event=None):
        self.Quit(self.choose_ok())
        
    def no_command(self, event=None):
        self.Quit(self.choose_nok())
        
    def Quit(self, how=None):
        """ Sortie de la boucle principale et non fermeture de la fenetre
            Exécution de la methode "how" qui permet de récupérer la
            donnée voulue en sotie en fin de méthode "go()"
        """
        self.how = how
        self.quit()                     # Exit mainloop()


class PopupMenu(tk.Menu):
    """ Classe Menu popup paramétrable.
        Les parametres du contructeur sont:
            'master': widget appelant dont le parent est un tk.Toplevel()
            'title' : titre du popup menu mis en surbrillance continue.
            Les 2 paramètres suivants indiquent les actions du menu.
            'commandsList': tuple de la forme (label_cmd:str, accel_cmd:str, commande:list[callable])
            'nosel' : list[int] liste des indices des rubrique dont l'état sera 'disabled'
        Les méthodes de la classe sont:
            show_Menu_popup(): affiche le menu popup à l'endroit du clic droit souris.
            nomenupopup(NoSel)    : prend en paramètre une liste contenant les numéros des rubriques à dévalider.
        La propriété 'NoSel' getter/setter sert de paramètre à la méthode 'nomenupopup()'.
    """
    def __init__(self, master:tk.Tk, title:str, commandsList:tuple=None, nosel:list=[]):
        
        self.__master = master
        self.__commandList = commandsList
        self.__title = title.split(',')
        self.__NoSel = nosel
        
        super().__init__(master,tearoff=0,font=('Arial 12 bold italic'),postcommand=lambda :self.nomenupopup(self.__NoSel))
            
    def show_Menu_Popup(self, event:tk.Event, nosel:list):
        self.delete(0, 'end')   # -- reset de la liste des commandes ajoutées -
        if len(self.__title) == 1: self.__title = (self.__title, " ")
        self.add_command(label=self.__title[0],accelerator=self.__title[1],background='orange',activebackground='orange')
        self.configure(background="ivory", activebackground='tan',borderwidth=2,relief="solid")
        self.add_separator()
        self.add_Popup_Commands(commands=self.__commandList)
        self.nomenupopup(nosel=nosel)
        try:
            self.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"Erreur interne : {e}")
            self.grab_release()
    
    @property
    def NoSel(self) -> list:
        return self.__NoSel
    @NoSel.setter
    def NoSel(self, nosel:list):
        self.__NoSel = nosel
             
    def nomenupopup(self,nosel:list):                
        [self.entryconfigure(i, state = 'disabled') for i in nosel]

    def add_Popup_Commands(self, commands:tuple):
        for command in commands:
            if command[0] == "separator":
                self.add_separator()
            else:
                self.add_command(label=command[0],accelerator=command[1],command=command[2])   
    

class Name_FirstDay(tk.Toplevel):
    def __init__(self, master:tk.Tk, options:App_Options, *args, **kwargs):
        self.__master = master
        self.__options = options
        My_Datetime.Long = False
        self.__person:Persons = options.aesh_name
        self.vnomentry = tk.StringVar(value=self.__person.nom.capitalize())
        self.vprenomentry = tk.StringVar(value=self.__person.prenom.capitalize())
        self.vfoncentry = tk.StringVar(value=self.__person.fonction[0])
        self.vdescentry = tk.StringVar(value="Assistant(e) aux Élèves en Situation de Handicap" \
                                if self.__person.fonction[0]=="AESH" else self.__person.fonction[1])
        date = datetime.strptime(str(options.date_rentree),"%Y-%m-%d")
        self.vdatentry = tk.StringVar(value=datetime.strftime(date,"%d/%m/%Y"))
        self.vlongdate = tk.StringVar(value=f"{datetime.strftime(date,'%A %d %B %Y'):^36}")
        # ---------------------------------------------------------------------
        tab_options:dict = {'bd':3, 'bg':'wheat1', 'relief':'ridge', 'pady':2}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, name="!addModify_Person", *args, **kwargs)
        # ---------------------------------------------------------------------
        self.lblFont = tkFont.Font(family='Sans', size=11, weight='normal', slant='italic')
        self.etyFont = tkFont.Font(family='Courier New', size=11, weight='bold', slant='italic')
        self.btnFont = tkFont.Font(family='Courier', size=11, weight='bold', slant='italic')
        # ---------------------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.__cancel_command)            
        self.wm_attributes("-topmost", 1)    # - Fenetre popup toujours au premier plan
        self.title("Initialisation du Personnel et de la date de la Rentrée à son Emploi du Temps")
        self.resizable(False, False)
        self.minsize(620,280)
        self.grid_anchor("nw")
        self.cree_widgets()
    
    def cree_widgets(self):
        lbltext = f"Veuillez saisir ci-dessous les nom, prénom et fonction " \
                  f"du personnel à créer ou à modifier ainsi que la date de la rentrée scolaire"
        # ---------------------------------------------------------------------
        tk.Label(self,bg="#FDF2DD",bd=3,text=lbltext,justify="center",relief='ridge',font=self.lblFont,
                    wraplength=self.minsize()[0]-70).grid(column=0,row=0,ipadx=10,ipady=10,sticky='nsew')
        frame = tk.Frame(self,bg="wheat2",bd=3,relief="ridge")
        frame.grid(column=0, row=1, pady=5, sticky="nsew")
        tk.Label(frame,bg=frame.cget('bg'),text=f" Nom\t: ",font=self.lblFont).grid(column=0,row=0,sticky="nsew")
        self.nom_entry = tk.Entry(frame, bg="ivory", font=self.etyFont, textvariable=self.vnomentry)
        self.nom_entry.grid(column=1,row=0,columnspan=2,padx=3,pady=3,sticky="nsew")
        tk.Label(frame, bg=frame.cget('bg'), text=f"\tPrénom\t: ",font=self.lblFont).grid(column=3,row=0,sticky="nsew")
        self.prenom_entry = tk.Entry(frame,bg="ivory",font=self.etyFont,textvariable=self.vprenomentry,width=21)
        self.prenom_entry.grid(column=4,row=0,columnspan=2,padx=3,pady=3,sticky="nsew")
        frame1 = tk.Frame(self,bg="wheat2",bd=3,relief="ridge")
        frame1.grid(column=0, row=2, sticky="nsew")
        tk.Label(frame1,bg=frame1.cget('bg'), text=f" Fonction\t\t: ",font=self.lblFont).grid(column=0,row=0,sticky="nsew")
        self.fonc_entry = tk.Entry(frame1,bg="ivory",font=self.etyFont,textvariable=self.vfoncentry)
        self.fonc_entry.grid(column=1,row=0,padx=3,pady=3,sticky="nsew")
        tk.Label(frame1,bg=frame1.cget('bg'), text=f" Descriptif\t: ",font=self.lblFont).grid(column=0,row=1,sticky="nsew")
        self.desc_entry = tk.Entry(frame1,bg="ivory",font=self.etyFont,width=51,textvariable=self.vdescentry)
        self.desc_entry.grid(column=1,row=1,columnspan=6,padx=3,pady=3,sticky="nsew")
        # ---------------------------------------------------------------------
        frame2 = tk.Frame(self,bg="wheat2",bd=3,relief="ridge")
        frame2.grid(column=0,row=3,columnspan=4, sticky="nsew")
        tk.Label(frame2,bg=frame2.cget('bg'), text=f" Date de la Rentrée scolaire :",anchor="w",
                                    font=self.lblFont).grid(column=0,row=0,columnspan=2,pady=3,sticky="nsew")
        self.date_entry = tk.Entry(frame2,bg="ivory2",font=self.etyFont,width=16,textvariable=self.vdatentry)
        self.date_entry.event_add("<<Valid_Date>>","<Double-Button-1>","<Return>","<KP_Enter>")
        self.date_entry.bind("<<Valid_Date>>",self.__verif_date_rentree)
        self.date_entry.grid(column=2,row=0,padx=3,pady=3,sticky="w")
        self.lbl_longdate = tk.Label(frame2,bg=frame2.cget('bg'), textvariable=self.vlongdate,
                disabledforeground="red",anchor="w",relief="sunken",font=('Consolas 10 normal italic'))
        self.lbl_longdate.grid(column=3,row=0,columnspan=3,pady=3,sticky="nsew")
        texte = "  La saisie de la date doit être de la forme 'jj/mm/aaaa' pour être prise en compte."
        tk.Label(frame2,bg=frame2.cget('bg'),font=('Consolas 10 normal italic'),
                               text=texte).grid(column=0,row=1,pady=0,columnspan=4,sticky="nsew")
        # ---------------------------------------------------------------------
        self.valid_button = tk.Button(self,text="Valider",font=self.lblFont,bg='dark khaki',width=12,
                                activebackground='lime green',state="disabled",command=self.__ok_command)
        self.valid_button.grid(column=0,row=6,padx=50,pady=15,sticky="w")
        tk.Button(self,text="Annuler",font=self.lblFont,bg="#FFCD83",activebackground='orange red',
                        command=self.__cancel_command,width=12).grid(column=0,row=6,padx=50,pady=15,sticky="e")    
        # ---------------------------------------------------------------------
        defmessage = " Entrée/Dbl-Gauch. pour vérifier la date de rentrée et activer le bouton 'Valider'"
        self.state_bar = Window_StateBar(self,"",0,row=7,cspan=10,pady=2,bd=3,relief="ridge",
                                       bg='#FDF2DD',txtfont="Consolas 10 bold italic",defMessage=defmessage)

    def go(self):
        """ Methode qui permet de garder le focus sur la fenetre de choix
            lors de la validation renvoi le nom,prenom,datetime et ferme
            la boite de dialogue.
        """
        self.lift(self.__master)            # mise au premier plan de la Toplevel
        self.grab_set()                     # prise en compte des évènements
        self.how = self.__valid_parameters  # Nom de la procédure exécutée en sortie
        self.mainloop()                     # Sortie de la Boucle principale par "self.quit(how)"
        self.destroy()                      # Fermeture de la fenetre Toplevel
        return self.how
    
    def __verif_date_rentree(self, event:tk.Event=None) -> bool:
        try:
            day,month,year = self.vdatentry.get().split('/')
            year = datetime.now.year if int(year) < 100 else int(year)
            date = My_Datetime(year,int(month),int(day))
            if date.weekday() in [5,6]: 
                self.vlongdate.set(f"{My_Datetime.strftime(date,'%A %d %B %Y'):^36}")
                self.lbl_longdate.configure(state="disabled")
                return False
            self.vdatentry.set(My_Datetime(int(year),int(month),int(day)))
            self.vlongdate.set(f"{My_Datetime.strftime(date,'%A %d %B %Y'):^36}")
            self.valid_button.configure(state="normal",background="pale green")
            self.lbl_longdate.configure(state="normal")
            return True
        except ValueError:
            self.valid_button.configure(state="disabled",background="red")
            self.lbl_longdate.configure(state="disabled")
            self.after(1000, self.__valid_btn_state)
            self.vlongdate.set(f"{'-/-':^36}")
            self.vdatentry.set("dd/mm/aaaa")
            return False
    
    def __valid_btn_state(self, event:tk.Event=None):
        self.valid_button.configure(background="dark khaki")

    def __valid_parameters(self, event:tk.Event=None):
        person = Persons(self.vnomentry.get(), self.vprenomentry.get())
        person.fonction = (self.vfoncentry.get(), self.vdescentry.get())
        date = datetime.strptime(self.vdatentry.get(),"%d/%m/%Y").date()
        return person, date
    
    def __ok_command(self, event=None):
        if self.__verif_date_rentree():
            self.Quit(self.__valid_parameters())

    def __cancel_command(self):
        self.Quit()
                
    def Quit(self, how=(None, None)):
        """ Sortie de la boucle principale et non fermeture de la fenetre
            Exécution de la methode "how" qui permet de récupérer la
            donnée voulue en sotie en fin de méthode "go()"
        """
        self.how = how
        self.quit()                     # Exit mainloop()
    
        
class List_popup(tk.Toplevel):
    """ Affichage d'une fenetre popup toujours au premier plan sans boutons système.
        Se ferme après avoir choisi un élément dans la liste ou par un clic souris
        hors de la fenètre (perte du focus). Dans ce cas renvoi 'None'.
        Constructeur:
            master: Fenetre parent de l'affichage
            liste : un tk.StringVar() contenant la liste des rubriques à visualiser.             
    """
    def __init__(self, master, liste:tk.StringVar, *args, **kwargs):
        
        self.__master = master
        self.lst_font = tk.font.Font(family='Courier New',size=10,weight='bold',slant='italic')    
        width,height = self.__get_width_listbox(liste=liste)        # - largeur maxi de la listbox
        self.mousexy = self.__master.winfo_pointerxy() #;print(f"mousexy: {self.mousexy}")
        
        tab_options:dict = {'bd':2, 'bg':'orange', 'relief':'flat', 'name':'!list_Popup'}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        
        if not liste.get(): return
        
        self.wm_attributes("-topmost", 1)                       # - Fenetre popup toujours au premier plan
        self.bind_class(self,'<Button3-Motion>',self.motion)    # - Bouton droit pour déplacer la fenètre popup
        self.bind_class(self,"<FocusOut>",self.cancel_command)  # - pour quitter la List_popup pas perte du focus
        self.overrideredirect(1)                                # - Aucun bouton systeme sur la fenetre   
        
        frame1 = My_LabelFrame(self, bd=0, bg='ivory', relief='flat')
        self.lst = tk.Listbox(frame1,bg='ivory',bd=0,listvariable=liste,selectmode="browse",
                                 activestyle="dotbox",font=self.lst_font,relief='flat',width=width,height=height)
        self.lst.event_add("<<Select_Item>>",'<Double-Button-1>','<KP_Enter>','<Return>')
        self.lst.bind("<<Select_Item>>",self.select_item)     # - click gauche/Enter pour selectionner le codon 
        self.lst.grid(sticky='nsew'); self.lst.update()
        self.lst.activate(0)
        self.lst.focus()     

    def __get_width_listbox(self,liste:tk.StringVar) -> int:
        """ Renvoi un tuple(2) contenant la longeur max des rubriques 
            de la liste et le nombre d'éléments de cette meme liste.
        """
        max_length:int = 0
        my_liste = liste.get().replace("(","").replace(")","").replace("'","").split(', ')
        for item in my_liste:
            if len(item) > max_length:
                max_length = len(item)
        return max_length+1, min(10, len(my_liste)+2)
        
    def motion(self, event):
        mousexy = self.__master.winfo_pointerxy()
        self.geometry(f"{self.lst_pos}+{mousexy[0]}+{mousexy[1]}")

    def get_selection(self):
        return self.lst.get(self.lst.curselection()[0])

    def go(self) -> str:
        """ Methode qui permet de garder le focus sur la fenetre de choix
            de l'huile qui lors du choix renvoi le nom de l'huile choisie
            et ferme la fenetre Toplevel.
        """
        self.lift(self.__master)        # mise au premier plan de la Toplevel    
        #self.grab_set()                # à valider pour que le popup intercepte tous les évènementsh
        self.update_position()          # actualise la position de la fenetre popup
        self.how = self.get_selection   # Nom de la procédure exécutée en sortie
        self.mainloop()                 # Entrée dans la Boucle principale, sortie par "self.quit(how)"
        self.destroy()                  # Fermeture de la fenetre Toplevel
        return self.how

    def select_item(self, event):
        self.ok_command()
        
    def ok_command(self):
        self.Quit(self.get_selection())

    def cancel_command(self, event):
        """ Sortie de la Toplevel avec "None" en retour """
        self.Quit(None)
    
    def update_position(self,event:tk.Event=0):
        pos = self.geometry(); self.lst_pos = f"{pos[:pos.find('+')]}"
        self.geometry(f"{self.lst_pos}+{self.mousexy[0]}+{self.mousexy[1]-100}")
        
    def Quit(self, how=None):
        """ Sortie de la boucle principale et non fermeture de la fenetre
            Exécution de la methode "how" qui permet de récupérer la
            donnée voulue en sotie en fin de méthode "go()"
        """
        self.how = how
        self.quit()              # Exit mainloop()
            
    
class Parametre_EDT(tk.Toplevel):    
    def __init__(self, master, parameters:App_Options, *args, **kwargs):    
        self.__master = master
        self.__parameters = parameters
        self.__aesh_name = parameters.aesh_name
        self.vcore_path = tk.StringVar(value=core_path) 
        # ---------------------------------------------------------------------
        self.vdata_path = tk.StringVar(value=parameters.datapath)
        self.vimages_path = tk.StringVar(value=parameters.imagepath)
        self.vexport_path = tk.StringVar(value=parameters.exportpath)
        self.vparams_fname = tk.StringVar(value=parameters.paramfilename)
        self.vdata_filename = tk.StringVar(value=parameters.datafilename)
        self.vhelp_filename = tk.StringVar(value=parameters.helpfilename)
        self.vback_filename = tk.StringVar(value=parameters.backfilename)
        self.vapp_width = tk.IntVar(value=parameters.app_size[0])          # -- largeur de la fenètre
        self.vapp_height = tk.IntVar(value=parameters.app_size[1])         # -- hauteur de la fenètre
        self.vfullscreen = tk.IntVar(value=int(parameters.fullscreen))     # -- bascule mode plein écran/fenêtré
        self.vdatelong = tk.IntVar(value=int(parameters.datelong))
        self.vsplashscr = tk.IntVar(value=int(parameters.splashscreen))    # -- fenetre à prpos au lancement 
        self.vsaveCFGoq = tk.IntVar(value=int(parameters.saveCFGonquit))   # -- sauvegarde config en quittant
        self.vsaveEDToq = tk.IntVar(value=int(parameters.saveEDTonquit))   # -- sauvegarde données équipe éducative
        self.vshow_scheduler = tk.IntVar(value=int(parameters.scheduler))  # -- afficher/cacher l'emploi du temps 
        self.vaesh_name = tk.StringVar(value=parameters.aesh_name.__str__())
        self.vschedule_mode = tk.StringVar(value=parameters.schedulemode)  # -- mode Modification/Consultation (readonly) 
        self.vdate_rentree = tk.StringVar(value=parameters.date_rentree) 
        self.vcurrent_week = tk.StringVar(value=parameters.currentweek)
        self.vdefault_year = tk.IntVar(value=parameters.default_year)
        self.__prt_list = list(master.app_printers.dico_printers.keys())
        #self.vdefault_printer = tk.StringVar(value=master.app_printers.default_printer)
        self.vdefault_printer = tk.StringVar(value=parameters.default_printer)
        self.vpolicy_family = tk.StringVar(value=parameters.policy_family)
        self.vlength_line = tk.IntVar(value=parameters.length_line)
        # ---------------------------------------------------------------------
        tab_options:dict = {'bd':3, 'bg':'wheat2', 'relief':'ridge', 'padx':2, 'pady':2}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, name="!add_Heuresup", *args, **kwargs)
        # ---------------------------------------------------------------------
        self.lblFont = tkFont.Font(family='Courier', size=13, weight='bold', slant='italic')
        self.etyFont = tkFont.Font(family='Sans', size=11, weight='normal', slant='italic')
        self.btnFont = tkFont.Font(family='Courier New', size=12, weight='bold', slant='italic')
        self.chxFont = tkFont.Font(family='Sans Serif', size=10, weight='normal', slant='italic')
        # ---------------------------------------------------------------------
        self.title(f"Modification des paramètres de EDT -/- ( Fichier config: {self.vparams_fname.get()} )")
        self.protocol("WM_DELETE_WINDOW", self.__cancel_command)    
        self.wm_attributes("-topmost", 1)    # - Fenetre popup toujours au premier plan
        self.event_add("<<ValidModif>>","<Return>","<KP_Enter>")
        self.bind("<<ValidModif>>", self.__ok_command)
        self.resizable(False, False)
        self.minsize(640, 180)
        self.grid_anchor("w")
        self.cree_widgets()
            
    def cree_widgets(self):
        frame = tk.Frame(self, bg='wheat1',bd=2,relief="raised")
        frame.grid(column=0,row=1,columnspan=20,rowspan=19,padx=2,pady=2,sticky="nsew")
        # ---------------------------------------------------------------------        
        frame1 = tk.Frame(frame, bg='wheat2',bd=2,relief="ridge")
        frame1.grid(column=0,row=0,columnspan=20,padx=2,pady=2,sticky="nsew")
        texte1 = f"Paramètre EDT v3.15 - Emploi Du Temps de {self.vaesh_name.get()}"
        date = datetime.strftime(datetime.strptime(self.vdate_rentree.get(),"%Y-%m-%d"),"%A %d %B %Y  (semaine %V -> Q1)")
        texte2 = f"Année scolaire {self.vdefault_year.get()} - Date de la rentrée : {date}"
        tk.Label(frame1,bg=frame1.cget('bg'),text=f"{texte1[:85]:^85}",font='Courier 15 bold italic',
                                anchor="center").grid(column=0, row=0, columnspan=19, pady=1, sticky="nsew")
        tk.Label(frame1,bg=frame1.cget('bg'),text=f"{texte2[:102]:^102}",font=self.lblFont,
                                anchor="center").grid(column=0,row=1,columnspan=19,pady=1,sticky="nsew")
        texte=" Définition des chemins d'accès aux fichiers de données et aux images "
        frame2 = tk.LabelFrame(frame, bg='wheat',bd=2,relief="ridge",
                                  font="Consolas 10 bold italic",text=texte,labelanchor="n")
        frame2.grid(column=0,row=1,columnspan=20,rowspan=2,padx=5,pady=2,sticky="nsew")
        # -------------------------- chemin Données ---------------------------
        frame22 = tk.Frame(frame2,bg=frame2.cget('bg'),bd=2,relief='groove')
        frame22.grid(column=0,row=0,columnspan=10,rowspan=2,padx=3,sticky="nsew")
        tk.Label(frame22,bg=frame2.cget('bg'),text="Dossier des données: ",font=self.lblFont,
                                          anchor="sw").grid(column=0,row=0,columnspan=3,pady=2,sticky="nsew")
        tk.Entry(frame22,bg='ivory2',textvariable=self.vdata_path,
                                        font=self.etyFont).grid(column=3,row=0,pady=5,columnspan=2,sticky="w")
        tk.Button(frame22,bg='light goldenrod',text="Choisir",border=2,font=self.chxFont,width=11,
                      activebackground='goldenrod',command=lambda: self.__choose_path(self.vdata_path)) \
                                                  .grid(column=5,row=0,columnspan=2,padx=5,pady=3,sticky="w")
        # --------------------------- chemin Images ---------------------------
        tk.Label(frame22,bg=frame2.cget('bg'),text="Dossier des images: ",font=self.lblFont,
                                          anchor="sw").grid(column=0,row=1,columnspan=3,pady=2,sticky="nsew")
        tk.Entry(frame22,bg='ivory2',textvariable=self.vimages_path,
                                        font=self.etyFont).grid(column=3,row=1,pady=5,columnspan=2,sticky="w")
        tk.Button(frame22,bg='light goldenrod',text="Choisir",border=2,font=self.chxFont,width=11,
                    activebackground='goldenrod',command=lambda: self.__choose_path(self.vimages_path)) \
                                                   .grid(column=5,row=1,columnspan=2,padx=5,pady=3,sticky="w")
        # --------------------------- chemin Exports --------------------------
        tk.Label(frame22,bg=frame2.cget('bg'),text="Dossier des exports: ",font=self.lblFont,
                                          anchor="sw").grid(column=0,row=2,columnspan=3,pady=2,sticky="nsew")
        tk.Entry(frame22,bg='ivory2',textvariable=self.vexport_path,
                                        font=self.etyFont).grid(column=3,row=2,pady=5,columnspan=2,sticky="w")
        tk.Button(frame22,bg='light goldenrod',text="Choisir",border=2,font=self.chxFont,width=11,
                    activebackground='goldenrod',command=lambda: self.__choose_path(self.vexport_path)) \
                                                   .grid(column=5,row=2,columnspan=2,padx=5,pady=3,sticky="w")
        # -------------------------- fichier équipe ---------------------------
        frame23 = tk.Frame(frame2,bg=frame2.cget('bg'),bd=2,relief='groove')
        frame23.grid(column=10,row=0,columnspan=10,rowspan=3,padx=2,sticky="nsew")
        tk.Label(frame23,bg=frame2.cget('bg'),text="Fichier des données: ",font=self.lblFont,
                                          anchor="sw").grid(column=0,row=0,columnspan=3,pady=2,sticky="nsew")
        tk.Entry(frame23,bg='ivory2',textvariable=self.vdata_filename,state="normal",width=21,
                                        font=self.etyFont).grid(column=3,row=0,pady=5,columnspan=2,sticky="w")
        tk.Button(frame23,bg='light goldenrod',text="Choisir",border=2,state="normal",
                                        font=self.chxFont,width=11,activebackground='goldenrod',
                                            command=lambda: self.__choose_file(self.vdata_filename)) \
                                                .grid(column=5,row=0,columnspan=2,padx=5,pady=3,sticky="w")
        # ------------------ fichier image fond (background) ------------------
        tk.Label(frame23,bg=frame2.cget('bg'),text="Fichier image de fond: ",font=self.lblFont,
                                          anchor="sw").grid(column=0,row=1,columnspan=3,pady=2,sticky="nsew")
        tk.Entry(frame23,bg='ivory2',textvariable=self.vback_filename,width=21,
                                        font=self.etyFont).grid(column=3,row=1,pady=5,columnspan=2,sticky="w")
        tk.Button(frame23,bg='light goldenrod',text="Choisir",border=2,font=self.chxFont,width=11,
                  activebackground='goldenrod',command=lambda :self.__choose_file(self.vback_filename)) \
                                                .grid(column=5,row=1,columnspan=2,padx=5,pady=3,sticky="w")
        # ------------------------ Fichier d'aide EDT -------------------------
        tk.Label(frame23,bg=frame2.cget('bg'),text="Fichier d'aide de EDT: ",font=self.lblFont,
                                          anchor="sw").grid(column=0,row=2,columnspan=3,pady=2,sticky="nsew")
        tk.Entry(frame23,bg='ivory2',textvariable=self.vhelp_filename,width=21,
                                        font=self.etyFont).grid(column=3,row=2,pady=5,columnspan=2,sticky="w")
        tk.Button(frame23,bg='light goldenrod',text="Choisir",border=2,font=self.chxFont,width=11,
                  activebackground='goldenrod',command=lambda :self.__choose_file(self.vhelp_filename)) \
                                                .grid(column=5,row=2,columnspan=2,padx=5,pady=3,sticky="w")
        # ---------------------------------------------------------------------
        splashtext = " : Fenètre 'A propos' au lancement de EDT v3.15"
        screensize = f"{self.vapp_width.get():<4}x{self.vapp_height.get():<4}"
        longdate = f" : Format date long. ie: {datetime.strftime(now,'%A %d %B %Y'):<25}"
        frame3 = tk.LabelFrame(frame, bg="#FCF1C0",bd=2,relief="ridge",text="",labelanchor="n")
        frame3.grid(column=0,row=4,columnspan=20,rowspan=3,padx=2,pady=2,sticky="nsew")
        tk.Checkbutton(frame3,bg=frame3.cget('bg'),variable=self.vfullscreen,padx=10,font=self.lblFont,
                 activebackground=frame3.cget('bg'),text=f" : Mode plein écran/Fenêtré (ie: {screensize})",
                      indicatoron=1,bd=0,anchor='sw',).grid(column=0,row=0,columnspan=10,pady=2,sticky='nsew')
        # ---------------------------------------------------------------------
        tk.Checkbutton(frame3,bg=frame3.cget('bg'),variable=self.vsaveCFGoq,padx=10,font=self.lblFont,
                    activebackground=frame3.cget('bg'),bd=0,text=" : Sauver la configuration en quittant",
                          indicatoron=1,anchor='sw',).grid(column=0,row=1,columnspan=10,pady=3,sticky='nsew')
        tk.Checkbutton(frame3,bg=frame3.cget('bg'),variable=self.vsaveEDToq,padx=10,font=self.lblFont,
                    background=frame3.cget('bg'),bd=0,text=" : Sauver le fichier de données en quittant",
                          indicatoron=1,anchor='sw',).grid(column=0,row=2,columnspan=10,pady=5,sticky='nsew')
        tk.Checkbutton(frame3,bg=frame3.cget('bg'),variable=self.vdatelong,padx=10,font=self.lblFont,
                            activebackground=frame3.cget('bg'),background=frame3.cget('bg'),text=longdate,
                        indicatoron=1,bd=0,anchor='sw').grid(column=12,row=1,columnspan=8,pady=2,sticky='nsew')
        tk.Checkbutton(frame3,bg=frame3.cget('bg'),variable=self.vsplashscr,padx=10,font=self.lblFont,
                        activebackground=frame3.cget('bg'),background=frame3.cget('bg'),indicatoron=1,bd=0,
                           anchor='sw',text=splashtext).grid(column=12,row=2,columnspan=8,pady=2,sticky='nsew')
        tk.Label(frame3,bg=frame3.cget('bg'),text=" EDT - Mode de saisie au lancement : ",anchor="e",
                                                font=self.lblFont).grid(column=12,row=0,columnspan=6,sticky="nsew")
        self.spb_schedulemode = tk.Spinbox(frame3,bg="ivory2",values=list_schedulemodes,wrap=True,width=22,
                          bd=3,textvariable=self.vschedule_mode,state="readonly",font='Consolas 10 bold italic')
        self.spb_schedulemode.grid(column=18,row=0,columnspan=2,pady=2,sticky="nsew")
        while self.spb_schedulemode.get() != self.__parameters.schedulemode: self.spb_schedulemode.invoke('buttonup')
        # ---------------------------------------------------------------------
        prt_text = " Impression de l'Emploi du Temps Semaine Q1 et Semaine Q2 sur : "
        frame4 = tk.LabelFrame(frame,bg=frame2.cget('bg'),bd=2,relief="ridge",labelanchor="n")
        frame4.configure(text=prt_text,font="Consolas 10 bold italic")
        frame4.grid(column=0,row=7,columnspan=20,rowspan=2,padx=2,pady=2,sticky="nsew")
        tk.Label(frame4,text=" Imprimante défaut du système :",font=self.lblFont,
                          bg=frame4.cget('bg')).grid(column=0,row=0,columnspan=4,pady=3,sticky="nsew")
        tk.Label(frame4,text=f"{self.vdefault_printer.get()[:39]:<39}",font=self.etyFont,
            bd=2,fg="grey10",relief="sunken",bg="ivory2").grid(column=4,row=0,columnspan=4,sticky="ew")    
        tk.Label(frame4,bg=frame4.cget('bg'),font=self.lblFont,
                 text=" - Imprimer sur :").grid(column=8,row=0,columnspan=4,pady=3,sticky="nsew")
        self.spblist_printers = tk.Spinbox(frame4,bg="ivory2",bd=2,font='Consolas 10 bold italic',width=33,
                          values=self.__prt_list,textvariable=self.vdefault_printer,wrap=True,state="readonly")
        self.spblist_printers.grid(column=12,row=0,columnspan=8,pady=3,sticky="ew")
        while self.spblist_printers.get()!=self.__parameters.default_printer: self.spblist_printers.invoke('buttonup')    
        # ---------------------------------------------------------------------
        tk.Button(self, text="Valider",width=12,font=self.btnFont,bg='ivory3',activebackground='lawn green',
                                            command=self.__ok_command).grid(column=3,row=20,pady=25,sticky="nsew")
        tk.Button(self, text="Annuler",width=12,font=self.btnFont,bg="#F5C19F",activebackground='red',
                                            command=self.__cancel_command).grid(column=16,row=20,pady=25,sticky="nsew")

    def __choose_path(self, varpath:tk.StringVar):
        title = "Choisir le dossier des fichiers de données utilisateur"
        pname = tkFileDialog.askdirectory(parent=self,title=title,initialdir=varpath.get(), initialfile=None)
        if op.isdir(pname): varpath.set(op.basename(pname))
    
    def __choose_file(self, varfile:tk.StringVar):
        title = "Choisir le fichier des données de l'AESH"
        path = self.vdata_path.get() if varfile == self.vdata_filename \
                        else self.vimages_path.get() if varfile == self.vback_filename else self.vcore_path.get()
        imgtype = (("EDT Data file", "*.dat"),) if varfile == self.vdata_filename \
                                  else (("Images file", "*.gif"), ("Images file", "*.png")) \
                                            if varfile == self.vback_filename else (("Help file", "*.hlp"),)
        filename = tkFileDialog.askopenfilename(parent=self,initialdir = op.join(os.getcwd(),path),
                                    initialfile=varfile.get(),title = title,filetypes = imgtype)
        if filename and op.isfile(filename):
            varfile.set(op.basename(filename))
    
    """
    def __verif_date_rentree(self, date_rentree:tk.StringVar):
        try:
            day,month,year = date_rentree.get().split('/')
            datetime(int(year),int(month),int(day))
            return My_Datetime(int(year),int(month),int(day)).date()
        except ValueError:
            return My_Datetime(now.year, 9, 1).date()
    """

    def __valid_parametres(self, event=None) -> App_Options:
        self.__parameters.datapath =  self.vdata_path.get()
        self.__parameters.imagepath = self.vimages_path.get()
        self.__parameters.exportpath = self.vexport_path.get()
        # -------------------------------------------------
        self.__parameters.paramfilename = self.vparams_fname.get()
        self.__parameters.datafilename = self.vdata_filename.get()
        self.__parameters.helpfilename = self.vhelp_filename.get()
        self.__parameters.backfilename = self.vback_filename.get()
        # -------------------------------------------------
        self.__parameters.app_size = (int(self.vapp_width.get()), int(self.vapp_height.get()))
        self.__parameters.fullscreen = bool(int(self.vfullscreen.get()))
        # -------------------------------------------------
        self.__parameters.datelong = bool(self.vdatelong.get())
        self.__parameters.splashscreen = bool(self.vsplashscr.get())   # -- fenetre à propos au lancement 
        self.__parameters.saveCFGonquit = bool(self.vsaveCFGoq.get())  # -- sauvegarde config en quittant
        self.__parameters.saveEDTonquit = bool(self.vsaveEDToq.get())  # -- sauvegarde données équipe éducative
        self.__parameters.scheduler = bool(self.vshow_scheduler.get())
        self.__parameters.schedulemode = self.vschedule_mode.get()
        self.__parameters.currentweek = self.vcurrent_week.get()
        # -------------------------------------------------
        self.__parameters.default_printer = self.vdefault_printer.get()
        self.__parameters.policy_family = self.vpolicy_family.get()
        self.__parameters.length_line = self.vlength_line.get()
        # -------------------------------------------------
        self.__parameters.default_year = self.vdefault_year.get()
        self.__parameters.aesh_name = self.__aesh_name
        return self.__parameters

        
    def go(self):
        """ Methode qui permet de garder le focus sur la fenetre de choix
            de l'huile qui lors du choix renvoi le nom de l'huile choisie
            et ferme la fenetre Toplevel.
        """
        self.lift(self.__master)            # mise au premier plan de la Toplevel
        #self.grab_set()                     # prise en compte des évènements
        self.how = self.__valid_parametres  # Nom de la procédure exécutée en sortie
        self.mainloop()                     # Sortie de la Boucle principale par "self.quit(how)"
        self.destroy()                      # Fermeture de la fenetre Toplevel
        return self.how

    def __ok_command(self, event=None):
        self.Quit(self.__valid_parametres())

    def __cancel_command(self):
        self.Quit(None)
                
    def Quit(self, how=None):
        """ Sortie de la boucle principale et non fermeture de la fenetre
            Exécution de la methode "how" qui permet de récupérer la
            donnée voulue en sotie en fin de méthode "go()"
        """
        self.how = how
        self.quit()                     # Exit mainloop()


class My_PNGviewer(tk.Toplevel):
    
    from PIL import Image,ImageTk
    
    def __init__(self, master:tk.Tk, options:App_Options, *args, **kwargs):
        
        from configs import corePNG_filename
        
        self.__master = master
        self.__options = options
        self.__filename = op.join(os.getcwd(),options.exportpath,corePNG_filename)
        self.__PNG_image = self.Image.Image
        self.__photo_cache:dict = {}
        self.__ZOOM = (1.0, 1.0)
        self.__zoom_job = None
        # ---------------------------------------------------------------------
        tab_options:dict = {'bd':2, 'bg':'wheat1', 'relief':'ridge'}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, name="!my_PNGviewer", *args, **kwargs)
        # ---------------------------------------------------------------------
        self.lblFont = tkFont.Font(family='Sans', size=11, weight='normal', slant='italic')
        self.etyFont = tkFont.Font(family='Courier New', size=11, weight='bold', slant='italic')
        self.btnFont = tkFont.Font(family='Courier', size=11, weight='bold', slant='italic')
        # ---------------------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.Quit)            
        #self.wm_attributes("-topmost", 1)    # - Fenetre popup toujours au premier plan
        # ---------------------------------------------------------------------
        if self.__filename:
            self.__PNG_image = self.Image.open(fp=self.__filename, mode='r', formats=("PNG",)).convert("RGBA")
        else:
            self.Quit()    
        # ---------------------------------------------------------------------
        self.bind('<MouseWheel>' ,self.__updateZoom)  # pour Linux "<Button4>" & "<Button5>"
        self.title("Prévisualisation de l'Agendas Semaines Q1/Q2 avant impression")
        self.grid_columnconfigure(list(range(10)), weight=1)
        self.grid_rowconfigure(list(range(10)), weight=1)
        self.resizable(False, False)
        self.grid_anchor("nw")
        self.create_widgets()
    
    def create_widgets(self):
        # ---------- chargement Image PNG / Largeur, Hauteur fenètre ----------
        self.PNG_imageTK = self.__preload_Image(self.__PNG_image, zoom=self.__ZOOM[0])
        width, height = self.PNG_imageTK.width(), self.PNG_imageTK.height()
        # --- Création du tk.Canvas() pour affichage de l'image de l'Agenda ---
        self.scheduler = tk.Canvas(self, bg="wheat", bd=0,name="!canvas_Scheduler",relief="flat",width=width,height=height)
        self.PNG_scheduler = self.scheduler.create_image(1,1,image=self.PNG_imageTK,anchor="nw",tags='img_scheduler')
        self.scheduler.grid(column=0,row=0,columnspan=9,rowspan=10,sticky="nsew")
        self.mainloop()
    
    def __preload_Image(self, image: Image.Image, zoom: float):
        ratio = (image.info.get("dpi", (int(300 + 40 * zoom),))[0] + 40 * zoom) / 96
        size = tuple(max(1, round(dimension / ratio)) for dimension in image.size)
        # ---- vérification d'un image pré-existante dans le dictionnaire -----
        cached = self.__photo_cache.get(size)
        if cached is not None: return cached
        # --------- Si elle n'existe pas, création et mise en mémoire ---------
        resized = image.resize(size, self.Image.Resampling.BILINEAR)
        photo = self.ImageTk.PhotoImage(resized, master=self)
        # ---------------- Limitation mémoire cache par FIFO ------------------
        if len(self.__photo_cache) >= 8: self.__photo_cache.pop(next(iter(self.__photo_cache)))
        # ---------------------------------------------------------------------
        self.__photo_cache[size] = photo
        return photo
    
    def __updateZoom(self, event: tk.Event = None):
        sens = event.delta // 120 * 0.1
        self.__ZOOM = (max(-1.0, min(self.__ZOOM[0]-sens, 3.0)),max(-1.0, min(self.__ZOOM[1]-sens, 3.0)))
        if self.__zoom_job is not None:
            self.after_cancel(self.__zoom_job)
        self.__zoom_job = self.after(120, self.__renderZoom)

    def __renderZoom(self):
        self.__zoom_job = None
        self.zoomed_img = self.__preload_Image(self.__PNG_image, self.__ZOOM[0])
        self.scheduler.configure(width=self.zoomed_img.width(), height=self.zoomed_img.height())
        self.scheduler.itemconfigure(self.PNG_scheduler, image=self.zoomed_img)    
        
    def Quit(self, event:tk.Event=None):
        self.destroy()
        self.quit()


# -----------------------------------------------------------------------------

def get_windows_scalling(hwnd=None) -> float:
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)
    try:
        shcore = ctypes.WinDLL('shcore')
    except OSError:
        shcore = None

    # si aucun hwnd fourni, prends la fenêtre au premier plan
    if hwnd is None:
        hwnd = user32.GetForegroundWindow()

    # 1) GetDpiForWindow (Windows 10+)
    try:
        GetDpiForWindow = user32.GetDpiForWindow
        GetDpiForWindow.restype = wintypes.UINT
        dpi = GetDpiForWindow(hwnd)
        return float(dpi) / 96.0
    except AttributeError:
        pass

    # 2) GetDpiForSystem (Windows 10+)
    try:
        GetDpiForSystem = user32.GetDpiForSystem
        GetDpiForSystem.restype = wintypes.UINT
        dpi = GetDpiForSystem()
        return float(dpi) / 96.0
    except AttributeError:
        pass

    # 3) GetDpiForMonitor via shcore (Windows 8.1+)
    if shcore is not None:
        MDT_EFFECTIVE_DPI = 0
        try:
            MonitorFromWindow = user32.MonitorFromWindow
            MonitorFromWindow.restype = wintypes.HMONITOR
            monitor = MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
            GetDpiForMonitor = shcore.GetDpiForMonitor
            GetDpiForMonitor.argtypes = (wintypes.HMONITOR, ctypes.c_int,
                                         ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint))
            GetDpiForMonitor.restype = ctypes.HRESULT
            x = ctypes.c_uint()
            y = ctypes.c_uint()
            res = GetDpiForMonitor(monitor, MDT_EFFECTIVE_DPI, ctypes.byref(x), ctypes.byref(y))
            if res == 0:
                return float(x.value) / 96.0
        except Exception:
            pass

    # 4) Fallback : GetDeviceCaps (peut renvoyer 96 si process non-DPI-aware)
    LOGPIXELSX = 88
    hdc = user32.GetDC(0)
    try:
        dpi = gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
        return float(dpi) / 96.0
    finally:
        user32.ReleaseDC(0, hdc)
            
    
if __name__ == "__main__":
    
    from configs import *
    from random import choice
    from winprinter import Windows_InitPrinters
    from platformdirs import user_documents_dir
    from PIL import Image, ImageTk
        
    try:
        locale.setlocale(locale.LC_TIME, ('fr_FR.UTF-8','French_France'))
    except locale.Error:
        print(f"Locale Française non installée sur ce système")
            
            
    def popup_win(event:tk.Event=None):
        my_list = tk.StringVar(value=get_args(schoolsubjects))
        popup = List_popup(root,my_list).go()
        print(f"popup: {popup}")
    
    
    root = tk.Tk()
    root.grid_anchor("n")
    
    config = Saveload_CFG()
    options = config.options if config.cfg_load() else App_Options()
    root.app_printers = Windows_InitPrinters(root)
    print(f"Echelle écran: {get_windows_scalling()}")
    backimage = op.join(os.getcwd(),"images","papillon.gif")
    root.backImage = Image.open(backimage, mode='r').resize((768,576), Image.Resampling.LANCZOS)
    root.image = ImageTk.PhotoImage(root.backImage,master=root)
    canvas = tk.Canvas(root,bg="grey85",bd=2,relief="groove",width=770,height=580)
    canvas.create_image(4,6,anchor="nw",image=root.image)
    canvas.grid(column=0,row=0,sticky="nsew")
    
    root.bind("<Button-3>", popup_win)
    
    #person, date_rentree = Name_FirstDay(root, App_Options()).go()
    #print(f"Person: {person}, Date de rentrée: {date_rentree}")
    
    #schedul = My_PNGviewer(root, config.options)
    
    """
    if config.cfg_load():
        print("Config.cfg_load() OK")
        options = config.options
        my_PDF = My_PDFviewer(root)
        pdfile = op.join(user_documents_dir(),f"{op.splitext(corePNG_filename)[0]}.pdf")
        my_PDF.pdf_view(pdf_file=pdfile,pages=0,zoom=(1.1,1.1))
    
    person = Persons("AMOUROUX","Pascale")
    date_rentree = My_Datetime(2026,8,31)
    if person and config.cfg_load():
        app_options = config.options
        app_options.aesh_name = person
        app_options.date_rentree = date_rentree
    else:
        app_options = App_Options()
    app_options.default_printer = root.app_printers.default_printer
    # -------------------------------------------------------------------------    
    handler = Schedule_FileHandler(app_options)
    dico_Q1, dico_Q2, colors = handler.load_schedule()
    # -------------------------------------------------------------------------
    root.mainloop()
    """
    
    new_options = Parametre_EDT(root, options).go()
    if new_options:
        #config.options = new_options
        #if config.cfg_backup():
        #    print("Nouvelles options OK:")
        [print(f"\t{key.replace('_App_Options',''):18}: {value}") for key,value in new_options.__dict__.items()]
        #else:
        #    print("Problème d'écriture du fichier config.")
    else:
        print("Annulation de la configuration")
    
