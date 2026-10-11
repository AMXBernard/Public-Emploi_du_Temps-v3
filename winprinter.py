"""
winprinter, bibliothèque du projet EDT. Fournit les objets, classes 
pour la définition des impressions gérées par l'application. 
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

EDT v3.15 Copyright (C) 09/2025  Bernard AMOUROUX
This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.
"""

__author__ = "Bernard AMOUROUX"
__date__ = "$Date: 2025/09/05 07:00 $"
__copyright__ = "Copyright (c) 2025 Bernard AMOUROUX"
__license__ = "GPL 3"


from configs import *

import win32ui as w32i
import win32api as w32a
import win32print as w32p
import tkinter.font as tkFont
import win32con as w32c
import tkinter as tk
import tempfile

from guitools import My_LabelFrame


class Windows_InitPrinters():

    def __init__(self, master):

        self.__master = master
        self.__dico_printers:dict = ({})
        self.__default_printer = w32p.GetDefaultPrinter()
        self.__active_printer = self.__default_printer

        __tuple_dicos = w32p.EnumPrinters(2,None,2)
        __tuple_drivers = w32p.EnumPrinterDrivers(None, None, 2)
        # ----------- Création du dictionnaires de toutes les imprimantes du système -----------
        for i in range(len(__tuple_dicos)):
            key = __tuple_dicos[i][list(__tuple_dicos[i].keys())[1]]
            self.__dico_printers[key] = __tuple_dicos[i]
            self.__dico_printers[key]['Version'] = __tuple_drivers[i]['Version']
    
    @property
    def default_printer(self) -> str:
        return self.__default_printer
    
    @property
    def active_printer(self) -> str:
        return self.__active_printer
    @active_printer.setter
    def active_printer(self, active_printer:str):
        self.__active_printer = active_printer
    
    @property
    def dico_printers(self) -> dict:
        return self.__dico_printers 
          
    def __open_Printer(self):
        printer = self.__dico_printers[f"{self.active_printer}"]        # printer est le dictionnaire des options de l'imprimante active
        PRINTER_DEFAULTS = {"DesiredAccess":w32p.PRINTER_ALL_ACCESS}    # None or --> .PRINTER_ACCESS_USE / .PRINTER_ACCESS_ADMINISTER / .PRINTER_ALL_ACCESS
        # ----- Ouverture de l'imprimante active et création du PyPrinterHANDLE : hprinter -----
        try:
            hprinter = w32p.OpenPrinter(printer['pPrinterName'], PRINTER_DEFAULTS)
        except Exception:
            self.master.update_vltexte(f"Ouverture imprimante {self.active_printer} impossible - Droits Utilisateur insuffisants",20)
            return None, None
        # --------------------------------------------------------------------------------------
        return hprinter, printer
          
    def params_printer(self) -> bool:
        """ Modification des paramètres de l'imprimante 'active' et si pas d'imprimante
            déclarée active ce seront alors les paramètres de celle par défaut.
            Constants from wingdi.h :
                DM_OUT_BUFFER = 0x02, DM_IN_BUFFER = 0x08, DM_IN_PROMPT = 0x04
                DM_DEFAULT_SOURCE = 0x200
                if mode = DM_IN_PROMPT, retour de la boite de configuration :
                    IDOK = 0x01
                    IDCANCEL = 0x02
        """
        hprinter, printer = self.__open_Printer()
        
        if hprinter and printer:
            properties = w32p.GetPrinter(hprinter, 2)
            devmode, cfgwin = properties['pDevMode'], 2
            # ------------------ Boite d'options Imprimante -------------------
            cfgwin = w32p.DocumentProperties(0, hprinter, self.active_printer, 
                                        devmode, devmode, w32c.DM_IN_PROMPT | w32c.DM_OUT_BUFFER)        
            # ------- Sauvegarde/Enregistrement des nouveaux paramètres -------
            if cfgwin == 1:
                try:
                    w32p.SetPrinter(hprinter, 2, properties, 0)
                except Exception as msg:
                    self.__master.state_bar.update_vltexte(f" PARAMETRAGE : {msg}",5)
            else:
                if __name__ == "__main__":
                    print(f" Info : Paramètres non sauvegardés")
                else: 
                    self.__master.state_bar.update_vltexte(f"{' Info : Paramètres non sauvegardés':<120}",5)
            w32p.ClosePrinter(hprinter)
        return bool(cfgwin == w32c.IDOK)
    
    def __font_for_cols(self, hdc:w32i.CreateDC, width:int, dpi:int, cols:int, family:str="Consolas"):
        """ Calcul taille police caractères pour un nombre de caractères donnés """
        for pt in range(20, 5, -1):
            height_px = -int(pt * dpi / 72)
            test_font = w32i.CreateFont({"name": family,"height": height_px,"weight": 400,})
            old = hdc.SelectObject(test_font)
            w, _ = hdc.GetTextExtent("X" * cols)
            hdc.SelectObject(old)
            if w <= width: 
                return test_font
        return w32i.CreateFont({"name": family,"height": -int(6 * dpi / 72),"weight": 400,})
    
    def __wrap_line(self, hdc:w32i.CreateDC, width:int, line:str):
        """ Simple calacul de retour à la ligne fonction taille de la police """
        out, courant = [], ""
        for c in line:
            test = courant + c 
            w, _ = hdc.GetTextExtent(test)
            if w <= width:
                courant = test
            else:
                out.append(courant)
                courant = c
        if courant:
            out.append(courant)
        return out
            
    def print_text(self, cols:int=COLS, family:str='Consolas', textToPrint:str=""):
        # -------------- Création du contexte d'impression ----------------
        hdc = w32i.CreateDC()
        hdc.CreatePrinterDC(self.active_printer)
        hdc.SetMapMode(w32c.MM_TEXT)
        # --------------------- Métriques imprimante ----------------------
        HORZRES, VERTRES = 8, 10
        LOGPIXELSX, LOGPIXELSY = 88, 90
        px_w   = hdc.GetDeviceCaps(HORZRES)
        px_h   = hdc.GetDeviceCaps(VERTRES)
        dpi_x  = hdc.GetDeviceCaps(LOGPIXELSX)
        dpi_y  = hdc.GetDeviceCaps(LOGPIXELSY)
        margin_x = int(0.254 * dpi_x)
        margin_y = int(0.254 * dpi_y)
        printable_w = px_w - 2 * margin_x
        printable_h = px_h - 2 * margin_y
        # -----------------------------------------------------------------
        font = self.__font_for_cols(hdc, printable_w, dpi_y, cols, family)
        old_font = hdc.SelectObject(font)
        _, line_h = hdc.GetTextExtent("Ag")
        line_h += 2
        # ---------------------- Impression du texte ----------------------
        hdc.StartDoc("Impression EDT 3.0")
        hdc.StartPage()
        x, y = margin_x, margin_y
        for raw in textToPrint.splitlines(keepends=True):
            for line in self.__wrap_line(hdc, printable_w, raw):
                if "\f" in line or (y + line_h > margin_y + printable_h):
                    hdc.EndPage()
                    hdc.StartPage()
                    y = margin_y
                if "\f" in line: continue
                hdc.TextOut(x, y, line)
                y += line_h
        # -----------------------------------------------------------------
        hdc.EndPage()
        hdc.EndDoc()
        # -----------------------------------------------------------------
        hdc.SelectObject(old_font)

    def print_file(self, fname:str=None):
        # ---------------------------------------------------------------------
        from PIL import Image,ImageWin
        # ---------------------------------------------------------------------
        if fname is not None and op.isfile(fname): 
            # ----------- Charger le fichier comme une 'PIL.Image' ------------
            page = Image.open(fname, mode='r')    
            # --------- Initialise l'imprimante par défaut du système ---------
            printer = self.active_printer
            hprinter = w32p.OpenPrinter(printer)
            # -- Création du contexte d'impression Windows (Device Context) ---
            hdc = w32i.CreateDC()
            hdc.CreatePrinterDC(printer)
            # ------------- Démarrage de l'impression du document -------------
            hdc.StartDoc(f"Impression {op.basename(fname)}")
            hdc.StartPage()
            # ----- Dessin de l'image sur le contexte de l'imprimante -----
            dib = ImageWin.Dib(page)
            # Ajuster aux dimensions imprimables (0, 0, largeur, hauteur) -
            width = hdc.GetDeviceCaps(110) # PHYSICALWIDTH
            height = hdc.GetDeviceCaps(111) # PHYSICALHEIGHT
            dib.draw(hdc.GetHandleOutput(), (0, 0, width, height))
            hdc.EndPage()
            hdc.EndDoc()
            # ---- Fin de l'impression / fermeture du handle d'imprimante -----
            hdc.DeleteDC()
            w32p.ClosePrinter(hprinter)
        else:
            return None

    def print_text_old(self, textToPrint:str=None):
        # ---------------------------------------------------------------------
        text2print = """
            This is a test to see if I can get this text to actually print\n
            
            It will be multiple lines...\n

            Watch and see
                    """
        properties = self.params_printer()
        Tempfile:tempfile.NamedTemporaryFile = None
        if not textToPrint: textToPrint = text2print
        with tempfile.NamedTemporaryFile(mode='w+t',suffix='.txt',
                                            encoding='utf-8',delete=False) as Tempfile:
            Tempfile.write(textToPrint)
        # --------- hprinter : Ouverture de l'imprimante défaut/active --------
        hprinter, printer = self.__open_Printer()
        data_type ='XPS_PASS' if printer['Version']==4 else printer['pDatatype']
        #print(f"printer: {printer} -/- data type: {data_type}\ntemp file: {Tempfile.name}")
        # ------------------- Création du job et impression -------------------
        hJob = w32p.StartDocPrinter(hprinter,1,('HSR_personal',None,data_type))
        try:
            w32a.ShellExecute(0, "print", Tempfile.name, None, ".", 0)
        except Exception as msg:
            self.__master.update_vltexte(f" IMPRESSION : {msg}",20)
        finally:
            w32p.EndDocPrinter(hprinter)
            w32p.ClosePrinter(hprinter)
        Tempfile.close()    
    
class ChoosePrinters(tk.Toplevel):

    def __init__(self, master=None, wpd:Windows_InitPrinters=None, *args, **kwargs):

        self.master = master
        self.printers = wpd.dico_printers
        self.listPrinters = list(self.printers.keys())

        self.vselected = tk.StringVar(None,'','!vselected')
        self.vactive = tk.StringVar(value=wpd.active_printer,name='!vactive')
        self.vdefault = tk.StringVar(value=wpd.default_printer,name='!vdefault')
        self.vprtlist = tk.StringVar(None,['Liste des imprimantes du système',],'!vprtlist')
        
        self.C_ACTIVE,self.C_DEFAULT,self.C_NORMAL = 'orange1','light goldenrod','ivory1'

        tab_options:dict = {'bd':3,'bg':'wheat','relief':'ridge','name':'!showPrinters_Win'}
        for key in list(tab_options.keys()):            # -- On remplace les options définies par défaut de l'objet bouton.
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)

        tk.Toplevel.__init__(self, master, *args, **kwargs)
        # ---------------------------------------------------------------------
        self.tle_font = tkFont.Font(family='Courier New', size=14, weight='bold', slant='italic')
        self.lbx_font = tkFont.Font(family='Courier', size=11, weight='bold', slant='roman')
        self.lbl_font = tkFont.Font(family='Verdana', size=10, weight='normal', slant='italic')
        # ---------------------------------------------------------------------
        self.title = "Fenêtre de choix de l'imprimante à utiliser"
        self.minsize(int(master.winfo_width()*0.6), int(master.winfo_height()*0.3))
        self.resizable(width= False, height= False)
        # -------------- Interception fermeture fenetre système ---------------
        self.protocol('WM_DELETE_WINDOW', self.__cancel_cmd)    
        # ---------------------------------------------------------------------
        self.event_add("<<SelectedPrinter>>","<Double-Button-1>","<Return>")
        # ---------------------------------------------------------------------
        self.grid_anchor('center')
        self.cree_widgets()

    def cree_widgets(self):
        # ------------------------ Titre des colonnes -------------------------
        nprt=" Nom de l'Imprimante"; pprt='Driver/Port'; jprt='Job(s)'
        lboxTitle = f"{nprt:^96}{pprt:^70}{jprt:^8}"
        # ---------------------------------------------------------------------
        lframe = My_LabelFrame(self, bg='wheat1', font=self.tle_font,cspan=8,pad=(2,2,0,0),
                                      text=' Liste des imprimantes du Système ',sticky='nsew')
        tk.Label(lframe,bg=lframe.cget('bg'),font=('Courier New', 12, 'bold' ,'italic' ,'underline'),
            text='Imprimante par défaut :').grid(column=0,row=0,columnspan=2,pady=5,sticky='nsew')
        frame1 = My_LabelFrame(lframe, col=2,row=0,bg='ivory3',pad=(2,5,0,0),
                                                        cspan=6,name='!frame1_defaultprinter')
        tk.Label(frame1,textvariable=self.vdefault,bg='ivory1',width=68,anchor='n',
                           font=self.lbl_font).grid(column=2,row=0,columnspan=6,padx=1,sticky='nsew')
        self.vprtlist.set(self.__fmtlboxString())
        # ---------------------------------------------------------------------
        frame_lbox = tk.LabelFrame(lframe,bg='wheat2',text=lboxTitle,font=('Verdana 9 italic'))
        frame_lbox.grid(column=0,row=1,columnspan=8,sticky="nsew")
        self.my_LboxPrt = tk.Listbox(frame_lbox,listvariable=self.vprtlist,
                            name='!my_listboxPrt',font=self.lbx_font,width=88,bg='ivory1',
                                activestyle="dotbox",selectforeground='black',selectbackground='tan')
        self.my_LboxPrt.bind("<<SelectedPrinter>>", self.__selectActive)
        self.my_LboxPrt.grid(sticky="nsew")
        # ---------------------------------------------------------------------
        frame2 = My_LabelFrame(lframe, col=0,row=2,bg='wheat2',pad=(2,5,0,0),
                                                          cspan=9,name='!frame2_Zone3boutons')
        tk.Button(frame2,text="Définir par défaut",highlightbackground='chocolate1',
                        font=self.lbl_font,command=self.__selectDefault,bg=self.C_DEFAULT,
                            width=16).grid(column=1,row=0,columnspan=3,padx=50,pady=3,sticky='nsew')
        tk.Button(frame2,text="Définir Active",activebackground='chocolate1',
                    font=self.lbl_font, command=self.__selectActive,bg=self.C_ACTIVE,
                        width=16).grid(column=4,row=0,padx=86,columnspan=3,pady=3,sticky='nsew')
        tk.Button(frame2,text="Valider",activebackground='chocolate1',
                    font=self.lbl_font, command=self.__ok_command,bg='ivory2',
                        width=16).grid(column=7,row=0,padx=50,columnspan=3,pady=3,sticky='nsew')
        # ---------- Mise à jour couleurs imprimante défaut et active ---------
        for svar, color in [(self.vactive,self.C_ACTIVE), (self.vdefault,self.C_DEFAULT)]:
            [self.my_LboxPrt.itemconfig(i,background=color) for i,item in enumerate(self.listPrinters) if svar.get() in item]
        self.my_LboxPrt.focus_set()
        self.__colorActivate()
        
    def __colorDefault(self):
        idx = [idx for idx,item in enumerate(self.listPrinters) if self.vdefault.get() in item][0]
        [self.my_LboxPrt.itemconfig(i,background=self.C_DEFAULT) if i==idx \
                             else self.my_LboxPrt.itemconfig(i,background=self.C_NORMAL) \
             for i in range(self.my_LboxPrt.size()) if self.my_LboxPrt.itemcget(i,'background') != self.C_ACTIVE]

    def __selectDefault(self):
        if self.my_LboxPrt.curselection():
            w32p.SetDefaultPrinter(self.listPrinters[self.my_LboxPrt.curselection()[0]])
            self.vdefault.set(w32p.GetDefaultPrinter())
            self.__colorDefault()
        
    def __selectActive(self, event=None):
        if self.my_LboxPrt.curselection():
            self.vactive.set(self.listPrinters[self.my_LboxPrt.curselection()[0]])
            self.__colorActivate()
            #self.__ok_command()
        
    def __colorActivate(self):
        idx = [idx for idx,item in enumerate(self.listPrinters) if self.vactive.get() in item][0]
        [self.my_LboxPrt.itemconfig(i,background=self.C_ACTIVE) \
           if i==idx and self.my_LboxPrt.itemcget(i,'background')!=self.C_DEFAULT \
                             else self.my_LboxPrt.itemconfig(i,background=self.C_NORMAL) \
               for i in range(self.my_LboxPrt.size()) if self.my_LboxPrt.itemcget(i,'background')!=self.C_DEFAULT]
        self.my_LboxPrt.activate(idx)
        
    def __fmtlboxString(self):
        """
            {'pServerName': None,  'pPrinterName': 'OneNote for Windows 10',
            'pShareName': '',      'pPortName': 'Microsoft.Office.OneNote_16001.14326.21452.0_x64__8wekyb3d8bbwe_microsoft.onenoteim_S-1-5-21-2311905880-3110614635-1917815049-1030',
            'pDriverName': 'Microsoft Software Printer Driver',                 'pComment': '',
            'pLocation': '',       'pDevMode': <PyDEVMODEW object at 0x0000022492A4BBF0>,
            'pSepFile': '',        'pPrintProcessor': 'winprint',               'pDatatype': 'RAW',
            'pParameters': '',     'pSecurityDescriptor': None,                 'Attributes': 4194368,
            'Priority': 1,         'DefaultPriority': 0,                        'StartTime': 1380,
            'UntilTime': 1380,     'Status': 0,            'cJobs':             'AveragePPM': 0}
        """
        stringList = []
        for key in self.listPrinters:
            dummy = self.printers[key].get('pLocation'," -/- ") 
            name = f"{self.printers[key].get('pPrinterName', ' -/- ')[:38]:<46}"
            port = f"{dummy[:36]:<36}" if dummy else f"{self.printers[key].get('pDriverName',' -/- ')[:36]:<36}"
            job = f"{self.printers[key].get('cJobs',' -/- '):^5}"
            stringList.append(f"{name}{port}{job}")
        return stringList
            
    def go(self):
        """ Methode qui permet de garder le focus sur la fenetre de choix
            de l'huile qui lors du choix renvoi un tuple (nom imprimante par
            défaut, nom imprimante active) et ferme la fenetre Toplevel.
        """
        self.lift(self.master)              # mise au premier plan de la Toplevel
        self.grab_set()                     # prise en compte des évènements
        self.how = self.__valid_printers    # Nom de la procédure exécutée en sortie
        self.mainloop()                     # Sortie de la Boucle principale par "self.quit(how)"
        self.destroy()                      # Fermeture de la fenetre Toplevel
        return self.how

    def __valid_printers(self):
        return self.vdefault.get(),self.vactive.get() 

    def __ok_command(self, event=None):
        self.Quit(self.__valid_printers())

    def __cancel_cmd(self):
        self.Quit(None)
                    
    def Quit(self, how=None):
        """ Sortie de la boucle principale et non fermeture de la fenetre
            Exécution de la methode "how" qui permet de récupérer la
            donnée voulue en sotie en fin de méthode "go()"
        """
        self.how = how
        self.quit()                     # Exit mainloop()

if __name__ == "__main__":

    root = tk.Tk()
    
    Wpd = Windows_InitPrinters(root)
    # -------------- Création du dictionnaires des drivers de ces imprimantes --------------
    print(f"\nListe des imprimantes:")
    [print(f"\t{item}") for item in Wpd.dico_printers.keys()]
    print(f" --> Default printer : {Wpd.default_printer}")
    print(f" --> Active printer  : {Wpd.active_printer}")
     
    print(ChoosePrinters(root, Wpd).go())
    
    #print(Wpd.params_printer())
    





                            
