#Name: Prestopronto.py
# Purpose: Gui to perform XAFS data reduction.
# Author: C. Prestipino based
#
# Copyright 2009 ESRF
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL ILLINOIS INSTITUTE OF TECHNOLOGY BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of ESRF
# shall not be used in advertising or otherwise to promote
# the sale, use or other dealings in this Software without prior written
# authorization from ESRF.

import ttk
from   Tkinter import *
import tkFileDialog
import bm29                                                                           
import numpy
import utility as ut
import bm29_tools as bt
import exapy
import os
import ConfigParser
#import zipfile for zipped files
import text
from scipy import interpolate
from PyMca.specfile import Specfile

import PPset
import PPInput
import PPAvesel
import PPXanes
import PPExafs
import PPFit



      
global __verbose__                                                                    
__verbose__=False#True#
global __version__
__version__= "b.0.9.0"
global inivarst
inivar=ConfigParser.ConfigParser()
global num_deriv
num_deriv=True

######################################################################################################
##################################       Menu    #####################################################
class mymenu():
    def __init__(self,genitore):
        self.genitore=genitore
        self.menubar = Menu(genitore)
        # create a pulldown menu, and add it to the menu bar
        self.filemenu = Menu(self.menubar, tearoff=0)


        self.filemenu.add_command(label="Open singlefile", command=self.opensfile)
        self.filemenu.add_command(label="Exit", command=self.quit1)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        
        ##########################single file#########################################################
        self.optionmenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Option", menu=self.optionmenu)
        
        self.singlefile = Menu(self.optionmenu, tearoff=0)         
        self.optionmenu.add_cascade(label="singlefile", menu=self.singlefile)
 
        self.singlefile.add_radiobutton(label="singlefile_on   ", command=self.singlefile_on )
        self.singlefile.add_radiobutton(label="singlefile_off  ", command=self.singlefile_off)
        self.singlefile.invoke(index=0)
        
        self.derivative = Menu(self.optionmenu, tearoff=0)         
        self.optionmenu.add_cascade(label="derivative", menu=self.derivative)
 
        self.derivative.add_radiobutton(label="Numeric_Deriv   ", command= lambda x=True: self.num_deriv(x) )
        self.derivative.add_radiobutton(label="Spline_Deriv    ", command= lambda x=False: self.num_deriv(x) )
        self.derivative.invoke(index=0)        
        ##########################single file#########################################################        
        
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About", command=self.version)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        
        # display the menu
        genitore.config(menu=self.menubar)
    def num_deriv(self, x): 
        global num_deriv
        if PPset.x: num_deriv=True
        else: num_deriv=False
    def singlefile_on(self):  
        ut.__singlefile__=True
    def singlefile_off(self):
        ut.__singlefile__=False
        
    def version(self):
        print "\n version %s \n" %__version__
        
    def quit1(self):
            print "\n\nfinally Santiago read the menu ; )\nthank you again Carmelo\n"
            writeini()
            self.genitore.quit()
    def opensfile(self):
        global filesel_spectra
        PPset.filesel_spectra=[]        
        filenames=ut.browse_single()
        os.chdir(os.path.dirname(filenames))
        buffero=bm29.disperati(filenames)
        buffero.energy=buffero.data[:,0]
        buffero.bm29ize()
        PPset.filesel_spectra=PPset.listum(buffero.spectra)
        del buffero       


#########################################################################################################
####################################     QE cal      ####################################################

#
#########################################################################################################
##################################       Avesel     #####################################################
#see module PPAvesel
#########################################################################################################
####################################     XANES       ####################################################
#see module PPXANES
####################################   EXAFS/FT #########################################################
#see module PPExafs
####################################   FIT    ########################################################
#see module PPFIT
#######################################################################################################
class XDEF:
    def __init__(self, genitore):
              #-------------------------------    declare    ----------------------------------------------
        self.synch_title =StringVar()          #define the label of plot
        self._plot =StringVar()                #define the type of plot
        self.prop_label= ('index')             #,'elapsed time: min','elapsed time: sec'
      #---------------------------------  set      ------------------------------------------
        self.synch_title.set("")
        self._plot.set("index")
        self.prop_label= ('index')             #,'elapsed time: min','elapsed time: sec'
      #---------------------------------  plot T1      ------------------------------------------
        self.quadro_plot = LabelFrame(genitore, text = "synch. plot")    #,text = "Correction"
        self.quadro_plot.pack(side = TOP,  fill = X, pady= 3, ipadx = 5, ipady = 3)
        self.combo_plot= ttk.Combobox(self.quadro_plot , state="readonly",   textvariable=self._plot, 
                     values=self.prop_label)    
        self.combo_plot.bind('<<ComboboxSelected>>',self.Synchplot)

        self.combo_plot.pack(side = LEFT ,anchor = E, pady=5, padx = 5, ipadx = 1)
        self.Plot_PlSa_But=ut.PloteSaveB(self.quadro_plot, ext="" ,comment= None, title= "pippo ") #str(self.synch_title))
      #---------------------------------------------------------------------------



    def Synchplot(self, evt):
        xset= evt
        if isinstance(xset, Event): 
                   xset=self._plot.get()
        #print "defined x " ,self._x.get()        
        print "defined y " ,xset, "\n"
        self.Plot_PlSa_But.x_array= [PPset.x]
        self.Plot_PlSa_But.comments=[]
        self.Plot_PlSa_But.comments.append(PPset.spectra.header)

        if xset=="index":
            y=range(1,len(PPset.spectra)+1)
            self.Plot_PlSa_But.y_array= [y]
            self.Plot_PlSa_But.title= xset+" vs   index"
        else:
            y=PPset.spectra.other_pro[xset]
            self.Plot_PlSa_But.y_array= [y]
            self.Plot_PlSa_But.title= xset+" vs   index"
            
        self.Plot_PlSa_But.comments[0].append( "#  index" +xset+"\n")#
        
        
        
        
        

#######################################################################################################
class Tscan:
    def __init__(self, genitore):
        global path
        global Dis_coeff
        global inivar
        
        
        
        
        readini()
             

        Dis_coeff=[None,None,None]
        path=list()
        x=[]

        #menu
        self.menu=mymenu(genitore)
        self.menu.filemenu.entryconfig(index=0, command= lambda : self.Setlimit("opensf")) 
        self.menu.derivative.entryconfig(index=0, command= lambda : self.num_deriv(True)) 
        self.menu.derivative.entryconfig(index=1, command= lambda : self.num_deriv(False))         



        self.nb = ttk.Notebook(genitore)
        self.nb.pack()


        # beamline
        self.p1 = Frame(self.nb)
        self.nb.add(self.p1 , text="beamline")

        self.nb_beamline = ttk.Notebook(self.p1)
        self.nb_beamline.pack(expand=Y, fill=Y)
        #----------------------------------------------------------------------
        self.p_QE_generic =Frame(self.nb_beamline)  
        self.nb_beamline.add(self.p_QE_generic, text="Generic QEXAFS")
        self.QE_gen= PPInput.Gen_QE(self.p_QE_generic)
        self.QE_gen.filesel.pulsanteA.configure(command= lambda i="QE_GEN": self.Setlimit(i))
        #----------------------------------------------------------------------
        #self.p_QE_spec =Frame(self.nb_beamline)  
        #self.nb_beamline.add(self.p_QE_spec, text="SPEC single")
        #self.QE_spec= Spec_QE(self.p_QE_spec)
        #self.QE_spec.filesel.pulsanteA.configure(command= lambda i="SPEC": self.Setlimit(i))
        #----------------------------------------------------------------------
        #self.p_bm29 =Frame(self.nb_beamline) 
        #self.nb_beamline.add(self.p_bm29, text="BM29")
        #self.QEcal= QEcal(self.p_bm29)
        #self.QEcal.filesel.pulsanteA.configure(command= lambda i="BM29f": self.Setlimit(i))   
        #self.QEcal.dirsel.pulsanteA.configure(command= lambda i="BM29d": self.Setlimit(i))   
        #----------------------------------------------------------------------
        #self.p_samba =Frame(self.nb_beamline)  
        #self.nb_beamline.add(self.p_samba, text="SAMBA")
        #
        #self.Samba= SambaQE(self.p_samba)
        #self.Samba.filesel.pulsanteA.configure(command= lambda i="SAMBAf": self.Setlimit(i))   
        #self.Samba.dirsel.pulsanteA.configure(command= lambda i="SAMBAd": self.Setlimit(i))   
        #----------------------------------------------------------------------
        self.p_id24 =Frame(self.nb_beamline) 
        self.nb_beamline.add(self.p_id24, text="ID24")

        self.Disp_calibration = PPInput.DispCal(self.p_id24)
        self.Disp_calibration.filesel.pulsanteA.configure(command= lambda i="ID24": self.Setlimit(i))
        
       #  Averages
        self.p2 = Frame(self.nb)
        self.nb.add(self.p2, text="Averages")
        self.Avesel= PPAvesel.Avesel(self.p2)
        self.Avesel.pulsante_Aver.configure(command = self.SelAver2)
       #  XANES
        self.p3 = Frame(self.nb)
        self.nb.add(self.p3, text="XANES")
        self.XAN= PPXanes.XANES(self.p3)
        self.nb.pack()
       #  EXAFS-FT
        self.p4=Frame(self.nb)
        self.nb.add(self.p4, text="EXAFS-FT")
        self.EXAFT= PPExafs.EXAFT(self.p4)
       # FIT
        self.p5=Frame(self.nb)
        self.nb.add(self.p5, text="FIT")       
        self.EXAFIT= PPFit.FIT(self.p5)
       # DefineX
        self.p6=Frame(self.nb)
        self.nb.add(self.p6, text="DEFINE X")
        self.XDEF= XDEF(self.p6)
      #-------------------------------------set page-------------------------
        #self.nb.raise_page("page1")


################################ functions global ############################################

    def Setlimit(self,beamline):
        if beamline=="BM29f":
            self.QEcal.browse_command2("Fil") 
        elif beamline=="BM29d":
            self.QEcal.browse_command2("Dir")              
        if beamline=="SPEC":
            self.QE_spec.browse_command2()            
        elif beamline=="SAMBAf":
            self.Samba.browse_command2("Fil") 
        elif beamline=="SAMBAd":
            self.Samba.browse_command2("Dir")             
        elif beamline=="QE_GEN":
            self.QE_gen.browse_command2()
        elif beamline=="ID24":
            self.Disp_calibration.browse_command2()            
        elif beamline=="opensf":
            self.menu.opensfile()
            self.nb.select(1)
        self.Avesel._from_tof.set("1-"+str(len(PPset.filesel_spectra)))
        self.Avesel.before.set((min(PPset.filesel_spectra[0].E)))
        self.Avesel.after.set((max(PPset.filesel_spectra[0].E)))
        pass

    def SelAver2(self):
        self.Avesel.Perform()
        if len(PPset.spectra)>0:
            self.XAN._deriv_start.set(round(min(PPset.spectra[0].E),3))
            self.XAN._deriv_end.set(round(max(PPset.spectra[0].E),3))
            self.XAN._INTxan_start.set(round(min(PPset.spectra[0].E),3))
            self.XAN._INTxan_end.set(round(max(PPset.spectra[0].E),3))
            self.XDEF.combo_plot.config(values=PPset.spectra.other_pro.keys())
            
            
        pass
    
    def num_deriv(self,x):
        self.menu.num_deriv(x)
        for wgt in self.p3.pack_slaves():
            wgt.destroy()
        del self.XAN
        self.XAN= PPXanes.XANES(self.p3)
        self.nb.pack()
        if spectra != []:
            self.XAN._deriv_start.set(round(min(PPset.spectra[0].E),3))
            self.XAN._deriv_end.set(round(max(PPset.spectra[0].E),3))
            self.XAN._TCW_start.set(round(min(PPset.spectra[0].E),3))
            self.XAN._TCW_end.set(round(max(PPset.spectra[0].E),3))
            self.XAN._INTxan_start.set(round(min(PPset.spectra[0].E),3))
            self.XAN._INTxan_end.set(round(max(PPset.spectra[0].E),3))        
        
    

        
#########################################################################################################
##############   Inizialization   ############################################################  
def readini():
    global inivar
    if os.name =="nt":
         path_local_data=os.path.join(os.environ['APPDATA'],"PrestoPronto")
    elif os.name =="posix":
         path_local_data="~/.local/bin"
    else :
        if __verbose__:
            print os.name, "  sistem not defined"     
            
    inifile=os.path.join(path_local_data,"PrestoPronto.ini")
    if __verbose__:  print inifile
    #try:
    inivar.read(inifile)
    if __verbose__ : print os.getcwd()
    #except :
    #    if __verbose__ : print "no ini file found"
    #    inivar=ConfigParser.ConfigParser()
    #    inivar.add_section("PrestoPronto")
    #    inivar.set("PrestoPronto", "PrestoPronto_Dir", os.getcwd())
    #    writeini() 
    #    return
        
    if inivar.has_section("PrestoPronto"):
        if os.access(inivar.get("PrestoPronto", "Start_Dir"), os.F_OK):
            os.chdir(inivar.get("PrestoPronto", "Start_Dir"))
        else:
            os.chdir(os.path.join(os.environ['HOMEDRIVE'],os.environ['HOMEPATH']))
    else:
       inivar.add_section("PrestoPronto")
       inivar.set("PrestoPronto", "PrestoPronto_Dir", os.getcwd())
       os.chdir(os.path.join(os.environ['HOMEDRIVE'],os.environ['HOMEPATH']))
    return    
           
#################   Inizialization   ############################################################ 
def writeini():
    global inivar
    inivar.set("PrestoPronto", "Start_Dir", os.getcwd())
    if os.name =="nt":
         path_local_data=os.path.join(os.environ['APPDATA'],"PrestoPronto")
    elif os.name =="posix":
         path_local_data="~/.local/bin"
    if not(os.access(path_local_data, os.F_OK)):
         os.mkdir(path_local_data)   
         
    inifile=os.path.join(path_local_data,"PrestoPronto.ini")     
    with open(inifile, 'w') as configfile:
        inivar.write(configfile)     
        configfile.close
    pass    


def destroy():
    print "\n\n\n\nhave a nice day.....  ;-) \n\n"
    writeini()
    radice.quit()


if __name__ == "__main__":
   radice = Tk()
   radice.title("PrestoPronto GUI")
   pippo = Tscan(radice)
   radice.protocol("WM_DELETE_WINDOW", destroy)
   radice.mainloop()
   


   
   
