# -- encode utf-8 --
"""
hlptools, bibliothèque du projet EDT_AESH v3.15 Fournit les objets,
classes pour l'aide intégré à l'application. 
Copyright (C) 2026  Bernard AMOUROUX

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

GPL3 License - CARDDB (c) 2026 Jan AMOUROUX 
GPL3 License - CARDDB Handler GUI (c) 2026 Bernard AMOUROUX

This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.
"""
__author__ = "Bernard AMOUROUX"
__date__ = "$Date: 2026/08/01 07:00 $"
__copyright__ = "Copyright (c) 2026 Bernard AMOUROUX"
__license__ = "GPL 3"

import os
import locale, re
import tkinter as tk
import os.path as osp
import tkinter.scrolledtext as tkText

from PIL import Image,ImageTk
from tkinter.font import Font
from itertools import chain

from configs import App_Options
from guitools import core_path
from math import nan

        
class Help_StateBar(tk.Frame):
    """ Classe créant une barre d'état configurable qui permet l'affichege d'un message
        d'état pendant une durée déterminée, indéterminée ou immédiate.
        Méthodes de la classe:
            update_vltexte : 
                msg  : message à afficher
                wait : temps d'affichge du message. défaut 10s
            tips: wait à 1 pour que le message s'affiche en permanence sans changer defMessage    
            message :
                getter : extrait le message en cours.
                setter : définit le message par défaut
            tips: pour que le message par défaut soit affiché imméditement, exécuter 'update_vltexte("",0)'                              
    """
    def __init__(self, master, col=0, row=0, cspan=1, sticky="nsew",
                          defMessage:str=' Info : ', defTime:int=10, txtfont=None, *args, **kwargs):
        """
        Attributs du constructeur:
            master     : Fenètre appelant, objet tkinter.Tk()
            col, row   : colone et ligne pour le placement dans la grille de la fenètre principale
            rspan, cspan, sticky : paramètres d'extension des lignes et colones dans la grille
            defMessage : message défaut qui s'affiche dès la tempo message terminée.
            defTime    : durée d'affichage des message par défaut 
            txtfont    : police de caractères pour l'affichage des messages
        """
        self.__waitnbr:int = None
        self.__defaultTime = defTime
        self.__defaultMsg = defMessage
        self.__vl_texte = tk.StringVar()

        tab_options:dict = {'bd':1, 'bg':'tan2', 'relief':'groove'}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, *args, **kwargs)
        
        lblfont = ("Courier New",10 ,'bold','italic') if not txtfont else txtfont
        
        self.grid(column=col,row=row,columnspan=cspan,padx=2,pady=2,sticky=sticky)
        
        tk.Label(self,bd=0,bg=self.cget('bg'),anchor="sw",height=1,font=lblfont,textvariable=self.__vl_texte).grid()
        self.update_vltexte(defMessage, 0)

    def __raz_vltexte__(self):
        """ methode privée de mise au message par défaut """
        self.__vl_texte.set(self.__defaultMsg)
        self.__waitnbr = None
    
    def update_vltexte(self, msg:str, wait=10):
        """ méthode de chargement d'un nouveau message pour affichage le temps désiré """
        if self.__waitnbr != None:
            self.after_cancel(self.__waitnbr)
        if wait == 0:
            self.__raz_vltexte__()
        elif wait > 1:
            self.__waitnbr = self.after(self.__defaultTime if wait==None else (wait*1000) , self.__raz_vltexte__)
        if msg: self.__vl_texte.set(msg)            
        super().update_idletasks()

    @property
    def message(self) -> str:
        return self.__vl_texte.get().rstrip()
    @message.setter
    def message(self, message:str):
        self.__defaultMsg = message


class Patterns():
    """ Classe définissant le pattern qui permet de créer et classer à partir d'un fichier texte
        un très léger système d'aide simple à utiliser.
    """
    @property
    def whole_paragraph(self) -> str:
        return r'-([\d.]*?)__([\s\S]*?):([\s\S]*?)EOP'
    
    @property
    def items_title(self) -> str:
        return r"[\s]{1}('[\w /_\'\-]+?'[\s]*?:)+?"
    
    @property
    def item_words(self) -> str:
        return r'[\s]{1}(\"[\w /_\'\.:=+?!\-]+?\")[\s|,|.]{1}'
    
    @property
    def imageInText(self) -> str:
        return r"##Image[\d]{1,2}:[\s\S]+?.png##"

class Paragraphe():
    """ Classe définissant la structure d'un paragraphe du système d'aide """
    
    @classmethod
    def Null_Paragraph(cls, number:float=nan) -> "Paragraphe":
        return Paragraphe((number," Index de paragraphe invalide","",0,0))
    
    def __init__(self, paragraph:tuple):
        if isinstance(paragraph,(tuple,list)) and len(paragraph)==5:
            self.numero:float = float(paragraph[0])
            self.isTitle:bool = f"{self.numero}".find('.0') != -1
            self.title = f"{paragraph[1]} :"
            self.text = paragraph[2].strip('\n')
            self.span = paragraph[3],paragraph[4]
        else:
            raise ValueError("Bad tuple format, must be a 5 tuple (number,title,text,span1,span2)") 
    
    def __eq__(self, other:"Paragraphe") -> bool:
        return self.numero == other.numero and self.span == other.span
      
    def __hash__(self) -> int:
        return hash((self.numero, self.span, self.text))
    
    def __str__(self) -> str:
        return f"Chapitre {self.numero} : {self.title}{self.text if not self.isTitle else ' -> TITLE\t'} span: {self.span}"

class Paragraphes():
    """ Classe qui lit un fichier texte pré-formaté et crée un dictionnaire dans lequel on
        retrouve tous les paragraphes extraits du fichier texte.
        Propriétés:
            all_paragraph : construit et renvoi le dictionnaire complet des objets 'Paragraphe'
        Méthodes (publiques):
            get_paragraph(number): renvoi la valeur de la clé 'number' qui est un objet
            de la classe 'Paragraphe'   
    """
    def __init__(self, filename:str=None):
        self.__pattern = Patterns()
        self.__handler_file:os.TextIOWrapper
        self.__wholeTextParagraph:dict =({})
        # - Lecture fichier d'aide et création du dictionnaire des chapitres --
        if osp.isfile(filename):
            self.__handler_file = open(filename, mode="rt", encoding="utf-8")
            self.__readText(self.__handler_file)
        else:
            raise FileExistsError(f"File '{filename}' does not exist!")
            
    @property
    def all_paragraph(self) -> dict:
        return self.__wholeTextParagraph
    @all_paragraph.setter
    def all_paragraph(self, paragraph:tuple):
        self.__wholeTextParagraph.update({paragraph[0]:Paragraphe(paragraph)})

    def __find_whole_paragraph(self, wholetext:str) -> list:
        return list(re.finditer(self.__pattern.whole_paragraph,wholetext,flags=re.MULTILINE | re.DOTALL))    
        
    def __readText(self, handlerfile):
        paragraphs = self.__find_whole_paragraph(handlerfile.read())
        for paragraph in paragraphs:
            self.all_paragraph = tuple(chain.from_iterable((paragraph.groups(), paragraph.span())))
        handlerfile.close()
    
    def get_paragraph(self, number:float) -> Paragraphe:
        #return self.all_paragraph.get(number, Paragraphe((number,"Bad number","No paragraph text",0,0)))
        return self.all_paragraph.get(number, Paragraphe.Null_Paragraph(number))
    
    def __str__(self) -> str:
        return '\n'.join([f"{item.__str__()}" for item in list(self.all_paragraph.values())])    


class Help_System(tk.Toplevel):
    
    def __init__(self, master:tk.Tk, options:App_Options, title:str, *args, **kwargs):
        
        self.__title = title
        self.__options = options
        self.__pattern = Patterns()
        self.__help_images:dict = ({})
        self.__helpText:tkText.ScrolledText
        # ----------- Mise en place et lecture du fichier d'aide --------------
        fname = options.helpfilename if options else "default.hlp"
        self.paragraphes = Paragraphes(osp.join(os.getcwd(),core_path,fname))
        # ------- Création de la liste des rubriques 'titre' de l'aide --------
        self.Titles_List = list(filter(lambda p:not p.isTitle, self.paragraphes.all_paragraph.values()))
        self.__vlstTitles = tk.StringVar(value=list(map(lambda t:t.title.split(' :')[0], self.Titles_List)))
        # ---------------------------------------------------------------------
        tab_options:dict = {'bd':3, 'bg':'LightSteelBlue1', 'relief':'ridge', 'padx':2, 'pady':2}        
        for key in list(tab_options.keys()):
            if kwargs.get(key, None) == None: kwargs[key] = tab_options.get(key, None)
        super().__init__(master, name="!help_Window", *args, **kwargs)
        # ---------------------------------------------------------------------
        self.lblFont = Font(family='Courier New', size=13, weight='bold', slant='italic')
        self.txtFont = Font(family='Consolas', size=12, weight='normal', slant='italic')
        self.btnFont = Font(family='Sans', size=11, weight='normal', slant='italic')
        # ---------------------------------------------------------------------
        self.title(f" Aide {self.__title} ")
        self.protocol("WM_DELETE_WINDOW", self.Quit)    
        #self.wm_attributes("-topmost", 1)    # - Fenetre popup toujours au premier plan
        self.grid_columnconfigure(list(range(10)), weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.bind("<Escape>", self.Quit)
        self.minsize(640, 280)
        self.grid_anchor("nw")
        self.cree_widgets()
        self.withdraw()
        
    def cree_widgets(self):
        self.title_bar = Help_StateBar(self,0,0,cspan=10,txtfont=self.lblFont,sticky="nsew",
                                                                       defMessage=" Rubrique ",bg='azure2',pady=3)
        self.__helpList = tk.Listbox(self,bg='LightCyan',bd=2,font=('Consolas 10 bold italic'),width=35,
                              activestyle="dotbox",height=20,selectmode="extended",listvariable=self.__vlstTitles)
        self.__helpList.grid(column=0, row=1, columnspan=2, sticky="nsew")
        self.__helpText = tkText.ScrolledText(self,bg='ivory',bd=2,relief="sunken",font=self.txtFont,wrap="word")
        # ------- Création des Tag_texte pour mise en évidence du texte -------
        self.__helpText.tag_configure("title_nbr", font=('Consolas 14 bold italic'), lmargin1=2, spacing1=2,
                                                   spacing3=2, relief="flat", border=0, background="orange")
        self.__helpText.tag_configure("number", font=('Consolas 14 bold italic'), lmargin1=10, spacing1=2,
                                                   spacing3=3, relief="sunken", border=2, background="azure2")
        self.__helpText.tag_configure("texte", background="ivory", spacing1=5, lmargin2=5, rmargin=10)
        self.__helpText.tag_configure("title", font=self.lblFont, background="DarkOliveGreen1")
        self.__helpText.tag_configure("txtle", font=('Consolas 12 bold italic'))
        self.__helpText.tag_configure("image", elide=True)
        # ---------------------------------------------------------------------
        self.__helpText.grid(column=2, row=1, columnspan=8, sticky="nsew")
        self.state_bar = Help_StateBar(self,0,2,cspan=10,pady=3,txtfont=self.txtFont,sticky="nsew", bg='wheat',
            defMessage=" Info : F1 pour l'aide complet, Ctrl-F1 pour l'aide contextuel, 'Echap' ferme la fenètre.", defTime=5)
        self.bind("<<ListboxSelect>>", self.on_paragraph_select)

    def __preload_help_Image(self, fname:str) -> Image.Image:
        filename = osp.join(os.getcwd(),self.__options.imagepath,fname)
        if osp.isfile(filename):
            image = Image.open(fp=filename, mode='r', formats=('PNG',)).convert("RGBA")
            image.thumbnail((600,600), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image=image, master=self)
        return None

    def on_paragraph_select(self, event):
        selection = event.widget.curselection() 
        if selection:
            # ------- Recherche du numéro du paragraphe par son 'Titre' -------
            data = f"{event.widget.get(selection[0])} :"
            number = list(filter(lambda p:p.title==data, self.paragraphes.all_paragraph.values()))[0].numero
            # -- Recherche de l'index relatif du paragraphe par son tag texte -
            index = int(f"{self.__helpText.tag_ranges(f'paragraph_{number}')[0]}".split('.')[0])
            # -- Placement du paragraphe relativement au 1/4 haut de l'écran --
            self.__helpText.yview_pickplace(index-3)
    
    def show_paragraph(self, number:float, state="normal"):
        paragraph = self.paragraphes.get_paragraph(number)
        if paragraph.isTitle:
            self.__helpText.insert(tk.END, f"{int(paragraph.numero)}"+' - '+paragraph.title+'\n', (f"paragraph_{number}", "title_nbr"))
        else:
            self.__helpText.insert(tk.END, f"{paragraph.numero}"+' - '+paragraph.title, f"paragraph_{number}")
            self.__helpText.mark_set("end_number", "end-1c")
            linT,colT = self.__helpText.index("end_number").split('.')
        # ---------------------------------------------------------------------
        if not paragraph.text.isspace():
            # --- Insertion du texte dans le widget Tkinter.ScrolledText() ----
            self.__helpText.mark_set("deb_txt", "end-1c"); deb_txt = self.__helpText.index('deb_txt')
            self.__helpText.insert('deb_txt', f"{paragraph.text}\n", (f"paragraph_{number}", "texte"))
            # ---- Recherche des mises en evidence de texte "'xxxxx'   :" -----
            spans = list(map(lambda sp:(self.__getIdx__(deb_txt,sp.span()[0]), self.__getIdx__(deb_txt,sp.span()[1])), \
                                                           re.finditer(self.__pattern.items_title,paragraph.text,flags=0)))
            [self.__helpText.tag_add('txtle', span[0], span[1]) for span in spans]
            #print(f"items_title spans: {spans}")
            # ------- Recherche des mises en evidence de texte "xxxxx" --------
            spans = list(map(lambda sp:(self.__getIdx__(deb_txt,sp.span()[0]), self.__getIdx__(deb_txt,sp.span()[1])), \
                                                           re.finditer(self.__pattern.item_words,paragraph.text,flags=0)))
            [self.__helpText.tag_add('txtle', span[0], span[1]) for span in spans]
            #print(f"item_words spans: {spans}")
            # --- Recherche des descripteurs d'images "##ImageXX:fname.PNG" ---
            imgs = list(map(lambda sp:(self.__getIdx__(deb_txt,sp.span()[0]), self.__getIdx__(deb_txt,sp.span()[1]),
                       sp.group().split(':')[1][:-2]), re.finditer(self.__pattern.imageInText,paragraph.text,flags=re.IGNORECASE)))
            # --- Affichage des images sur les emplacements des descripteurs --
            for img in imgs[::-1]:
                self.__helpText.tag_add('image', img[0], img[1])
                if self.__help_images.get(img[2], -1) == -1:
                    self.__help_images[img[2]] = self.__preload_help_Image(img[2])
                self.__helpText.image_create(img[0],image=self.__help_images[img[2]],align="top",name=img[2])
            #print(f"imgs: {imgs}")
            # -----------------------------------------------------------------
            self.__helpText.tag_add("title", f"{linT}.0", f"{linT}.end+1c")
            self.__helpList.selection_set('active')
            if state != "normal":
                self.__helpList.configure(state=state)
                self.readonly(state=state)
        self.wm_deiconify()
        
    def __getIdx__(self, end:str, span:int) -> str:
        return self.__helpText.index(f"{end}+{span}c")
    
    def show_whole_help(self):
        self.delete_text()
        self.__helpList.configure(state="normal")
        [self.show_paragraph(number) for number in self.paragraphes.all_paragraph]
        self.title_bar.update_vltexte(f"  Aide de {self.__title} ",1)
        self.__helpText.configure(state='disabled')
            
    def show_strait_help(self):
        self.title_bar.update_vltexte(f"  Aide de {self.__title} ",1)
        self.__helpText.insert('end', self.paragraphes.__str__()+'\n')
        self.__helpText.configure(state='disabled')
        self.__helpList.config(state="disabled")
        self.wm_deiconify()
    
    def delete_text(self):
        self.__helpText.configure(state='normal')
        self.__helpText.delete("1.0",'end')        
    
    def readonly(self, state='disabled'):
        self.__helpText.configure(state=state)
        
    def Quit(self, event=None):
        self.delete_text()
        self.withdraw() 
        

if __name__ == "__main__":
    
    # ------------ Pour une traduction des messages de datetime() -------------
    try:
        locale.setlocale(locale.LC_TIME, ('Fr_fr.UTF-8','French_France'))
    except locale.Error as msg:
        print(f"Locale message: {msg}")
    # -------------------------------------------------------------------------
    root = tk.Tk()
    options = App_Options()
    options.helpfilename = "EDT_helpfile.hlp"
    
    helper = Help_System(root, options=options, title="EDT_AESH v3.15")
    print(helper.paragraphes.get_paragraph("5.1"))
    
    #print(helper.paragraphes.__str__())
    #print(helper.paragraphes.get_paragraph("2.1"))
    #[print(item.__str__()) for key,item in helper.paragraphes.all_paragraph.items()]
    
    #helper.show_paragraph("3.2", state="disabled")
    #helper.readonly(state='normal')
    #root.after(2000,helper.show_paragraph,"1.5","disabled")
    #helper.show_strait_help()
    
    root.after(40, helper.show_whole_help())
    root.mainloop()
    root.quit()