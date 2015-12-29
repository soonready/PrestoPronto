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
import Rebin
import Exapy
import os
import ConfigParser
#import zipfile for zipped files
import text
from scipy import interpolate
from PyMca.specfile import Specfile

      
global __verbose__                                                                    
__verbose__=False#True#
global __version__
__version__= "b.0.8.4"
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
    def num_deriv(self,x): 
        global num_deriv
        if x: num_deriv=True
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
        filesel_spectra=[]        
        filenames=ut.browse_single()
        os.chdir(os.path.dirname(filenames))
        buffero=bm29.disperati(filenames)
        buffero.energy=buffero.data[:,0]
        buffero.bm29ize()
        filesel_spectra=buffero.spectra
        del buffero       


#########################################################################################################
####################################     QE cal      ####################################################
class Col_line_Gen:
    def __init__(self, genitore, label, array, row): 
      #-----------------------------      Declare      --------------------------------------------------
        self._check= IntVar()
        self._label=label
        self._position= IntVar()
        self._compo=IntVar()

      #-----------------------------      Define       --------------------------------------------------  
        self.array=array 
        row= row
        self._check.set(False)
      #-----------------------------      Structure    --------------------------------------------------
        self.check = Checkbutton(genitore, variable=self._check, width=2)#, command=self.underline )
        self.check.grid(row= row, column=0)
        
        self.label= Label(genitore, text=self._label)
        self.label.grid(row= row, column=1)       
        
        self.column= Spinbox(genitore, from_ = 1, to = self.array.shape[1], 
                             textvariable= self._position, width = 3)      
        self.column.grid(row= row, column=2)
        
        self.pulsante_Plot = Button(genitore ,
                                      command = self.plot,
                                      text = "Plot",
                                      background = "DeepPink2",
                                      width = 7,
                                      padx = "1m",
                                      pady = "1m")
        self.pulsante_Plot.grid(row= row, column=3)   
        
      #-----------------------------      Functios    --------------------------------------------------
    def plot(self): 
        title= "{0:s}  column {1:d}".format(self._label, int(self._position.get()))
        x_array=[numpy.arange(self.array.shape[0])]
        y_array=[self.array[:,int(self._position.get())-1]]
        graph = ut.Graph()
        graph.plot(x_array, y_array, title= title)
















class Column_Window:
    def __init__(self,filenames):
        global filesel_spectra
      #--------------------------   Declare-------------------------------------------------
        self.filenames=filenames
        self._ChaCom=StringVar()
        self._mode=StringVar()
      #--------------------------   Define--------------------------------------------------  
        self.column_names=["E", "Mu", "Ref", "I0", "I1", "I2"]
        self.column_list=[]
        self._ChaCom.set("#")
        self._mode.set("transmission")
      #--------------------------  Top level + reload--------------------------------------------------        
        #self.top_txt = Toplevel()
        #self.top_txt.title("view  first file")         

        

        self.top = Toplevel(takefocus=True)
        self.top.title("define column of interest")    

        


        self.win_text = Frame(self.top) 
        self.win_text.pack(side=LEFT,expand=YES, fill=BOTH)
        text.ScrolledText( parent=self.win_text, file=self.filenames[0],hor=True, active=False)

        self.top_con= Frame(self.top) 
        self.top_con.pack(side=LEFT,expand=YES)

        self.win_comment = Frame(self.top_con)
        self.win_comment.pack(side=TOP,expand=YES)
        self.win_comment.focus()

        Label(self.win_comment,text="Comment character").grid(row= 0, column=0) 
        self.Entry_Value =Entry(self.win_comment, textvariable =  self._ChaCom, width=8, justify=CENTER )
        self.Entry_Value.grid(row= 0, column=1) 
        self.Reload_B = Button(self.win_comment, text="Reload array" ,
                                      command = self.load,
                                      background = "Violet",
                                      width = 13,
                                      padx = "3m",
                                      pady = "2m").grid(row= 0, column=2)
      #--------------------------   Params  Entries--------------------------------------------------
        self.win_column = Frame(self.top_con)
        self.win_column.pack(side=TOP,expand=YES)
      #--------------------------   Mode array --------------------------------------------------        

        self.quadro_mode = Frame(self.win_column)
        self.quadro_mode.pack(side = TOP, anchor=W, fill = X, pady= 0, ipadx = 0, ipady = 0, expand = N)
        
        #Label(self.quadro_mode,text="Mode    ").pack(side = LEFT)
        self.combo_type= ttk.Combobox(self.quadro_mode , textvariable=self._mode, state ="readonly",
                    values=("transmission", "fluorescence"))
        self.combo_type.pack(side = LEFT)       
        
        self.quadro_column = Frame(self.win_column)
        self.quadro_column.pack(side = TOP,  fill = X)
        
      #--------------------------   Header-------------------------------------------------- 
      
        Label(self.quadro_column, text="Use       ").grid(row=0, column=0) 
        Label(self.quadro_column, text="   ").grid(row=0, column=1)        
        Label(self.quadro_column, text="Column   ").grid(row=0, column=2)
        Label(self.quadro_column, text="    ").grid(row=0, column=3)  
        Label(self.quadro_column, text="   ").grid(row=0, column=4)  
      #--------------------------   Set lines --------------------------------------------------        
        self.load()

      #--------------------------   Button --------------------------------------------------
        self.quadro_buttonp = Frame(self.win_column)      
        self.quadro_buttonp.pack(side = TOP,  fill = X) 
        self.buttonMu = Button(self.quadro_buttonp,
                                      command = self.Muplot,
                                      text = "plot Mu",
                                      background = "Violet",
                                      width = 13,
                                      padx = "3m",
                                      pady = "3m")
        self.buttonMu.pack(side = LEFT, anchor = W,pady = 10, padx=5)
        self.buttonRef = Button(self.quadro_buttonp,
                                      command = self.Refplot,
                                      text = "plot Ref",
                                      background = "Violet",
                                      width = 13,
                                      padx = "3m",
                                      pady = "3m")
        self.buttonRef.pack(side = LEFT, anchor = W,pady = 10, padx=5) 
      #--------------------------   Button --------------------------------------------------        
        self.quadro_button = Frame(self.win_column)      
        self.quadro_button.pack(side = TOP,  fill = X) 
        self.save_cons = Button(self.quadro_button,
                                      command = self.opens,
                                      text = "Define Column",
                                      background = "Green",
                                      width = 13,
                                      padx = "3m",
                                      pady = "3m")
        self.save_cons.pack(side = LEFT, anchor = W,pady = 10, padx=5) 
      #--------------------------   Wait --------------------------------------------------    
        self.top_con.wait_window()
      #--------------------------   Function --------------------------------------------------
    
    def read_comment(self,n_file):
        infile=open(n_file)
        comment=[]
        CC="1"
        while CC==self._ChaCom.get():
            comment.append(infile.readline())
            CC=comment[-1][0]
        comment=comment[:-1]
        comment=comment if comment!=[] else ["# Generic\n"]
        comment.append("# spectra  "+n_file+ "\n")
        comment.append("#  ---------------------------------"+ "\n")
        comment.append("#L E  Mu"+ "\n") 
        return comment         
            
    
    def load(self):
        if self.column_list==[]:
            try:
                self.array=numpy.loadtxt(fname=self.filenames[0],comments=self._ChaCom.get())
            except:
                print  "\n"*5+"ERROR-----"*10+"\n\nERROR  change comment character\n\n"+"ERROR-----"*10+"\n"*5 
                return                
            for i,item in enumerate(self.column_names):
                    self.column_list.append(Col_line_Gen(self.quadro_column, label=item, array=self.array,
                                         row=i+1))          
        return

    def Muplot(self):
        E=self.array[:,int(self.column_list[0]._position.get())-1]
        if self.column_list[1]._check.get():
            Mu=self.array[:,int(self.column_list[1]._position.get())-1]
        elif self.column_list[3]._check.get() and self.column_list[4]._check.get():
            I0=self.array[:,int(self.column_list[3]._position.get())-1] 
            I1=self.array[:,int(self.column_list[4]._position.get())-1]           
            if self._mode.get()=="transmission":Mu=numpy.log(I0/I1)
            elif self._mode.get()=="fluorescence":Mu=I1/I0
        else: raise ValueError("\n\nneither Mu nor I0-I1 defined\n\n") 
        graph = ut.Graph()
        graph.plot( [E],[Mu], title= "Mu")
        
   
        
    def Refplot(self):    
        E=self.array[:,self.column_list[0]._position.get()-1]
        if self.column_list[2]._check.get():
            Ref=self.array[:,int(self.column_list[2]._position.get())-1] 
        elif self.column_list[5]._check.get() and self.column_list[4]._check.get():
            I1=self.array[:,int(self.column_list[4]._position.get())-1] 
            I2=self.array[:,int(self.column_list[5]._position.get())-1]
            Ref=numpy.log(I1/I2)
        graph = ut.Graph()
        graph.plot( [E], [Ref], title= "Ref")


    def opens(self):
        global filesel_spectra
        filesel_spectra=[]
        for item in self.filenames:
            self.array=numpy.loadtxt(fname=item,comments=self._ChaCom.get())
            E=self.array[:,int(self.column_list[0]._position.get())-1]
            if self.column_list[1]._check.get():
                Mu=self.array[:,int(self.column_list[1]._position.get())-1]
            elif self.column_list[3]._check.get() and self.column_list[4]._check.get():
                I0=self.array[:,int(self.column_list[3]._position.get())-1] 
                I1=self.array[:,int(self.column_list[4]._position.get())-1]           
                if self._mode.get()=="transmission":Mu=numpy.log(I0/I1)
                elif self._mode.get()=="fluorescence":Mu=I1/I0
            else: raise ValueError("neither Mu nor I0-I1 defined") 
            
            filesel_spectra.append(bm29.bm29file([E,Mu]))
            filesel_spectra[-1].comments=self.read_comment(item)

            if self.column_list[3]._check.get():
                filesel_spectra[-1].I0=self.array[:,int(self.column_list[3]._position.get())-1]
            if self.column_list[2]._check.get():
                filesel_spectra[-1].ref=self.array[:,int(self.column_list[2]._position.get())-1]   
            elif self.column_list[5]._check.get() and self.column_list[4]._check.get():
                I2=self.array[:,int(self.column_list[5]._position.get())-1] 
                I1=self.array[:,int(self.column_list[4]._position.get())-1]
                filesel_spectra[-1].ref=numpy.log(I1/I2)
            
        pass
        E=max(numpy.gradient(filesel_spectra[0].Mu))
        dspac=  3.13467 if E<22500 else 1.63702
        for item in filesel_spectra: item.dspac=dspac
        self.top.destroy()
        del self
      

class Column_Window_spec(Column_Window):
    def read_comment(self,n_file):
        comment= ["# SPECfile\n"]
        comment.append("# spectra  "+str(n_file.number())+ "\n")
        comment.append("#  ---------------------------------"+ "\n")
        comment.append("#L E  Mu"+ "\n") 
        return comment 
        
    def opens(self):
        global filesel_spectra
        filesel_spectra=[]
        DATAsource=Specfile(*self.filenames)
        for item in DATAsource:
            self.array=item.data().T
            E=self.array[:,int(self.column_list[0]._position.get())-1]
            if self.column_list[1]._check.get():
                Mu=self.array[:,int(self.column_list[1]._position.get())-1]
            elif self.column_list[3]._check.get() and self.column_list[4]._check.get():
                I0=self.array[:,int(self.column_list[3]._position.get())-1] 
                I1=self.array[:,int(self.column_list[4]._position.get())-1]           
                if self._mode.get()=="transmission":Mu=numpy.log(I0/I1)
                elif self._mode.get()=="fluorescence":Mu=I1/I0
            else: raise ValueError("neither Mu nor I0-I1 defined") 
            
            filesel_spectra.append(bm29.bm29file([E,Mu]))
            filesel_spectra[-1].comments=self.read_comment(item)

            if self.column_list[3]._check.get():
                filesel_spectra[-1].I0=self.array[:,int(self.column_list[3]._position.get())-1]
            if self.column_list[2]._check.get():
                filesel_spectra[-1].ref=self.array[:,int(self.column_list[2]._position.get())-1]   
            elif self.column_list[5]._check.get() and self.column_list[4]._check.get():
                I2=self.array[:,int(self.column_list[5]._position.get())-1] 
                I1=self.array[:,int(self.column_list[4]._position.get())-1]
                filesel_spectra[-1].ref=numpy.log(I1/I2)
            
        pass
        E=max(numpy.gradient(filesel_spectra[0].Mu))
        dspac=  3.13467 if E<22500 else 1.63702
        for item in filesel_spectra: item.dspac=dspac
        self.top.destroy()
        del self    
            
                
                
      
      

#


class Gen_QE():
    def __init__(self, genitore):
      #-----------------------------      Declare      --------------------------------------------------
        self.before = StringVar()
        self.after  = StringVar()
        #self.energy = StringVar()
        self._function= StringVar()
        self._function_p= StringVar()
        self._All_spectra= StringVar()
        self._c_range = IntVar()
      #-----------------------------      Define       --------------------------------------------------
        self._function.set("Ref.der.")
        self._function_p.set("Ref")        
        self._All_spectra.set("first spectra     ")        
        labelpack =  {"side" : LEFT,  "fill" :BOTH , "anchor" : N,"ipadx" : 0} #,"expand" : YES, "ipady" : 5
        entrypack = {"side" : LEFT, "padx" : 1 , "fill" : None}#"ipady" : 3
      #-----------------------------      Windows       --------------------------------------------------
        self.filesel = ut.Browse_filename(genitore, "Filenames", 0)
        self.filesel.pulsanteA.configure(command= self.browse_command2)
      #--------------------------- Quadro correction ---------------------------------------------- 
        self.quadro_Define = LabelFrame(genitore,  text = "Allign spectra respect to")
        self.quadro_Define.pack(side = TOP, anchor=W, fill = X, pady= 3, ipadx = 5, ipady = 3, expand = N)   #, expand = YES
       #--------------------------- Quadro correction 1---------------------------------------------- 
        self.quadro_Define1 = Frame(self.quadro_Define)
        self.quadro_Define1.pack(side = TOP, anchor=W, fill = X, pady= 0, ipadx = 0, ipady = 0, expand = N)        
        self.combo_All= ttk.Combobox(self.quadro_Define1 , state ="readonly",
                                     textvariable=self._All_spectra,values=('first spectra     ', 'Calibration sample'))
        self.combo_All.pack(side=LEFT)

        
        Label(self.quadro_Define1, text=" using ").pack(side = LEFT)
        self.combo_Cal= ttk.Combobox(self.quadro_Define1 ,   textvariable=self._function,
                         values=( 'Ref.der.','Ref','-I0','Cal. Mu','Cal. der.'))
        self.combo_Cal.pack(side=LEFT)
        #self.combo_Cal.insert(0, 'Ref.der.')
    
        Frame(self.quadro_Define1).pack(side = LEFT, anchor=W, fill = X, pady= 2, ipadx = 10, padx=5, ipady = 3, expand = Y)
        Button(self.quadro_Define1,
              command = self.plot_set_Energy,
              text = "Plot  correction ",
              background = "violet",
              width = 15,
              padx = "1m",
              pady = "2m").pack(side = LEFT, anchor = W)
       #--------------------------- Quadro correction 2----------------------------------------------  
        self.quadro_Define2 = Frame(self.quadro_Define)
        self.quadro_Define2.pack(side = TOP, anchor=W, fill = X, pady= 3, ipadx = 0, ipady = 3, expand = N)  
        Label(self.quadro_Define2, text="In the range").pack(side = LEFT)    
        self.check_range=Checkbutton(self.quadro_Define2, variable=self._c_range )
        self.check_range.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1)
        Label(self.quadro_Define2, text=" between ").pack(side = LEFT)
        self.Define_before = Entry(self.quadro_Define2,   textvariable= self.before, width = 10 )#
        self.Define_before.pack(side = LEFT, padx = 5, ipadx =5  ,ipady = 3)
        Label(self.quadro_Define2, text=" and ").pack(side = LEFT)
        self.Define_after = Entry(self.quadro_Define2,   textvariable= self.after, width = 10 )
        self.Define_after.pack(side = LEFT, padx = 5,  ipadx = 5 ,ipady = 3)  
        Label(self.quadro_Define2, text=" eV ").pack(side = LEFT)
       #--------------------------- Quadro correction 3----------------------------------------------  
        self.quadro_Define3 = Frame(self.quadro_Define)
        self.quadro_Define3.pack(side = TOP, anchor=W, fill = X, pady= 0, ipadx = 0, ipady = 0, expand = N)         
        
        self.calibsel = ut.Browse_file(self.quadro_Define3, "Calibration Sample", 1)
    
      #--------------------------- Quadro plot cor ----------------------------------------------         
        self.quadro_plot = LabelFrame(genitore, text="Plot ")
        self.quadro_plot.pack(side = TOP, expand = YES, fill = X, pady = 10,
                                  ipadx = 5, ipady = 5)
        self.combo_Plot= ttk.Combobox(self.quadro_plot ,  state ="readonly",
                        textvariable=self._function_p,        values=('Ref.der.', 'Ref','-I0')  )
        self.combo_Plot.pack(side=LEFT)
   
        self.pulsante_Plot_nc = Button(self.quadro_plot ,
                                      command = lambda x= "not": self.plot_all(x),
                                      text = "not corrected",
                                      background = "DeepPink2",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Plot_nc.pack(side = LEFT, anchor = W)
        self.pulsante_Plot_c = Button(self.quadro_plot ,
                                      command = lambda z= "cor": self.plot_all(z),
                                      text = "  corrected  ",
                                      background = "DeepPink2",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m",
                                      relief="ridge",#"solid",#"groove",#"flat",
                                      state=DISABLED)
        self.pulsante_Plot_c.pack(side = LEFT, anchor = W)
      #--------------------------- Quadro perform ----------------------------------------------
        self.quadro_buttonp3 = LabelFrame(genitore, text="Apply correction")
        self.quadro_buttonp3.pack(side = TOP, expand = YES, fill = X, pady = 10,
                                  ipadx = 5, ipady = 5)
        self.pulsante_Defcor = Button(self.quadro_buttonp3,
                                      command = self.correct,
                                      text = "Apply correction",
                                      background = "Violet",
                                      width = 10,
                                      padx = "5m",
                                      pady = "2m")
        self.pulsante_Defcor.pack(side = LEFT, anchor = W)
        self.pulsante_Remcor = Button(self.quadro_buttonp3, 
                                      command = self.rem_correct,
                                      text = "Remove correction",
                                      background = "Violet",
                                      width = 10,
                                      padx = "5m",
                                      pady = "2m")
        self.pulsante_Remcor.pack(side = LEFT, anchor = W)


    ##########################function################################################################
    def browse_command2(self):
        global filesel_spectra
        self.filesel.browse_command()
        filesel_spectra=[]
        colwin=Column_Window(self.filesel.filenames)
        #colwin.top_con.wait_window()
        self.pulsante_Defcor.configure(relief="raised")
        try:
            filesel_spectra[0].bm29derRef()
            Eo_test=bt.max_range(filesel_spectra[0].E, filesel_spectra[0].E_RefFp)
            self.before.set(round(Eo_test-50))
            self.after.set(round(Eo_test+50))  
            self._c_range.set(1)
        except:
            pass
        return
        


    def plot_all(self, ptype): 
        if ptype=="not":
            if hasattr(filesel_spectra[0], "oldE"):
                x_array=[item.oldE for item in filesel_spectra]
            else:
                x_array=[item.E for item in filesel_spectra]
        if ptype=="cor":
            if hasattr(filesel_spectra[0], "oldE"):
                x_array=[item.E for item in filesel_spectra]
            else: 
                print "\nCorrection still not applied\n\
                        press the button\n"
                return
        if self._function_p.get()=='Ref.der.':   
            try:
                for item in  filesel_spectra: item.bm29derRef()
                y_array=[item.E_RefFp for item in filesel_spectra]
                title="derivate reference"
            except:
                print "reference not measured"
                return            
            
        elif self._function_p.get()=='Ref':            
            try:
                y_array=[item.ref for item in filesel_spectra]
                title="reference"                
            except:
                print "reference not measured"
                return
        elif self._function_p.get()=='-I0':    
                y_array=[item.I0 for item in filesel_spectra]
                title= "I0"
        if ptype== "cor": title=title+" corrected"   
        self.graph = ut.Graph()
        self.graph.plot(x_array, y_array, title= title)
    



    def set_Energy(self):
        self.Energy_row=[]
        self._function.get()
        if self._c_range.get():
            before =float(self.before.get())
            after=float(self.after.get())
        else:
            before, after= None, None
        if self._function.get() == "-I0":
            Y= lambda x: -x.I0/abs(max(-x.I0))
        elif self._function.get() == 'Ref.':
            Y= lambda x: x.ref
        elif self._function.get() == 'Ref.der.':
            for item in filesel_spectra: item.bm29derRef()
            Y= lambda x: x.E_RefFp/max(x.E_RefFp)
        elif self._function.get() == 'Cal. Mu':
            Y= lambda x: x.Mu
        elif self._function.get() == 'Cal. der.':
            self.calibsel.spectra[0].bm29derRef()
            Y= lambda x: x.E_Fp/max(x.E_MuFp)            
            
        if  self._c_range.get():
            L = lambda objecto,x: x.compress((objecto.E>before)&(objecto.E<after))
        else:
            L = lambda objecto,x: x        
        if self._All_spectra.get() =='first spectra     ':
            if self._function.get() =='Cal. Mu' or self._function.get() =='Cal. der.':
                print "\nnot clear input\nasking to use first sample and calibration...."
            splinex1y1 = interpolate.splrep(filesel_spectra[0].E,Y(filesel_spectra[0]))
        elif self._All_spectra.get() =='Calibration sample':
            if self._function.get() =='Ref.' or self._function.get() =='Ref.der.':
                print "\nATTENTION you are using reference of calibration file\n"
                raise ValueError()
            try:
                splinex1y1 = interpolate.splrep(self.calibsel.spectra[0].E,Y(self.calibsel.spectra[0]))
            except:
                self.calibsel.spectra[0]=bm29.bm29file(self.calibsel.spectra[0].data)
            self.calibsel.spectra[0].bm29derE()
            if self._function.get() == 'Ref.':
                splinex1y1 = interpolate.splrep(self.calibsel.spectra[0].E, self.calibsel.spectra[0].Mu)
            elif self._function.get() == 'Ref.der.':    
                splinex1y1 = interpolate.splrep(self.calibsel.spectra[0].E, self.calibsel.spectra[0].E_MuFp)
        self.standard_Energy=bt.max_range(filesel_spectra[0].E, Y(filesel_spectra[0]),before,after) 
           
        for item in  filesel_spectra:
            self.Energy_row.append(float(ut.fitcalibration(x2=L(item,item.E), y2=L(item,Y(item)),
                                                     param=[0],splinex1y1=splinex1y1)))
           

        
    def plot_set_Energy(self):
        self.set_Energy()
        x_array= [range(len(filesel_spectra))]
        y_array= [self.Energy_row]
        self.graph = ut.Graph()
        self.graph.plot(x_array, y_array, title= "Energy shift")   

    def correct(self):
        self.set_Energy()
        if hasattr(filesel_spectra[0], "oldE"):            
            pass
        else:  
            for item in filesel_spectra: item.oldE=item.E
        for i,item in enumerate(filesel_spectra):
            item.E= bt.MvEAshift(item.E,item.dspac, self.standard_Energy-self.Energy_row[i],
                                 self.standard_Energy)
        print "\nCorrection applyed\n"            
        self.pulsante_Defcor.configure(relief="sunken")
        self.pulsante_Plot_c.configure(relief="raised",state=NORMAL)
        
    def rem_correct(self):
        for item in filesel_spectra:
            item.E=item.oldE
            del item.oldE    
        self.pulsante_Defcor.configure(relief="raised")
        self.pulsante_Plot_c.configure(relief="ridge",state=DISABLED)        
        print "\nCorrection removed\n"
            
       
#########################################################################################################
class Spec_QE(Gen_QE):
    def browse_command2(self):
        global filesel_spectra
        self.filesel.browse_command()
        filesel_spectra=[]
        colwin=Column_Window_spec(self.filesel.filenames)
        #colwin.top_con.wait_window()
        self.pulsante_Defcor.configure(relief="raised")
        try:
            filesel_spectra[0].bm29derRef()
            Eo_test=bt.max_range(filesel_spectra[0].E, filesel_spectra[0].E_RefFp)
            self.before.set(round(Eo_test-50))
            self.after.set(round(Eo_test+50))  
            self._c_range.set(1)
        except:
            pass
        return

##################################       DispCal    #####################################################
class DispCal():
    def __init__(self, genitore):
      #-----------------------------      Declare      --------------------------------------------------
        self.A = StringVar()
        self.B = StringVar()
        self.C = StringVar()
        self._r =StringVar()
        self.v = IntVar()
        self.v.set(2)


      #-----------------------------      Define      --------------------------------------------------
        self.A.set(0)
        self.B.set(1)
        self.C.set(0)
      #-----------------------------      geometry      --------------------------------------------------
        self.Cal_sel = ut.Browse_filename(genitore, "Calibration sample", 1)
        self.Disp_sel = ut.Browse_filename(genitore, "Dispersive Calibration sample", 1)
        self.quadro_Title = Frame(genitore)
        self.quadro_Title.pack(side = TOP, anchor= W, expand = Y, fill = BOTH)
        Label(self.quadro_Title, text= " Energy = A + B*Pixel + C*Pixel**2             ").pack(side=LEFT, anchor=N)
        Radiobutton(self.quadro_Title, text="Write text",
                                        variable=self.v,
                                        value=1,
                                        command= self.radio_command
                                        ).pack(side=LEFT,   anchor=N)
        Radiobutton(self.quadro_Title, text="Use sliders",
                                        variable=self.v,
                                        value=2,
                                        command= self.radio_command
                                        ).pack(side=LEFT,  anchor=N)
      #-----------------------------      Calibration---------------------------------------------
        self.quadro_sliders = Frame(genitore)
        self.quadro_sliders.pack(side = TOP, anchor= W, expand = Y, fill = BOTH)
        self.quadro_A = Frame(self.quadro_sliders)
        self.quadro_A.pack(side =TOP, fill=BOTH)
        self.Aslider = Scale( self.quadro_A, from_=-.05, to=.05,
                                            command= self.setredraw_A,
                                            variable= self.A,
                                            resolution=0.0000001,
                                            orient=HORIZONTAL, # label= "A",
                                            showvalue=0
                                            )
        self.Aslider.pack(side = LEFT,fill = X, anchor = W,pady = 3, ipady = 0, expand = Y)
        Label(self.quadro_A,text= " A ").pack(side=LEFT)#, anchor = SW
        #self.entry_A= Entry(self.quadro_A, width = 9, textvariable = self.A)
        #self.entry_A.pack(side = LEFT, ipadx = 5, ipady = 1, fill = Y, pady= 2)
        #self.entry_A.bind("<Key>", self.keymove)
        #self.entry_A.bind("<Return>", self.keyenter)
        self.quadro_B = Frame(self.quadro_sliders)
        self.quadro_B.pack(side =TOP, fill =BOTH)
        self.Bslider = Scale( self.quadro_B,
                                     from_=0, to=1.5,
                                     command= self.setredraw_B,
                                     variable= self.B,
                                     resolution=0.00001,
                                     orient=HORIZONTAL,#label= "Angular shift"
                                     showvalue=0,
                                     )
        self.Bslider.pack(side = LEFT,fill = X, anchor = W,pady = 3, ipady = 0, expand = Y)
        Label(self.quadro_B,text= " B ").pack(side=LEFT)
        self.quadro_C = Frame(self.quadro_sliders)
        self.quadro_C.pack(side =TOP, fill=BOTH)
        self.Cslider = Scale( self.quadro_C, from_=-.00005, to=.00005,
                             command= self.setredraw_B,
                             variable= self.C,
                             resolution=0.00000001,
                             orient=HORIZONTAL,
                             showvalue=0,
                             )
        self.Cslider.pack(side = LEFT,fill = X, anchor = W,pady = 3, ipady = 0, expand = Y)
        Label(self.quadro_C,text= " C ").pack(side=LEFT)



        self.quadro_ABCtext = Frame(genitore)
        self.quadro_ABCtext.pack(side = TOP, expand = N, fill = X, pady = 2,
                                  ipadx = 5, ipady = 5)
        self.entry_A= Entry(self.quadro_ABCtext, width = 9, textvariable = self.A, state='readonly')
        self.entry_A.pack(side = LEFT, ipadx = 5, ipady = 1, fill = None, pady= 2)
        Label(self.quadro_ABCtext, text= " A   ").pack(side=LEFT)
        self.entry_B= Entry(self.quadro_ABCtext, width = 9, textvariable = self.B, state='readonly')
        self.entry_B.pack(side = LEFT, ipadx = 5, ipady = 1, fill = None, pady= 2)
        Label(self.quadro_ABCtext, text= " B   ").pack(side=LEFT)
        self.entry_C= Entry(self.quadro_ABCtext, width = 9, textvariable = self.C, state='readonly')
        self.entry_C.pack(side = LEFT, ipadx = 5, ipady = 1, fill = None, pady= 2)
        Label(self.quadro_ABCtext, text= " C   ").pack(side=LEFT)




        self.quadro_buttonp1 = Frame(genitore)
        self.quadro_buttonp1.pack(side = TOP, expand = N, fill = X, pady = 2,
                                  ipadx = 5, ipady = 5)
        self.pulsante_plot = Button(self.quadro_buttonp1,
                                      command = self.plot,
                                      text = "Plot Mu",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_plot.pack(side = LEFT, anchor = W)
        self.pulsante_dplot = Button(self.quadro_buttonp1,
                                      command = self.dplot,
                                      text = "Plo Derivative",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_dplot.pack(side = LEFT, anchor = W)
        self.pulsante_Fitder = Button(self.quadro_buttonp1,
                                      command = self.fitder,
                                      text = "Fit Derivative",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Fitder.pack(side = LEFT, anchor = W)        
        
        


        self.pulsante_Select = Button(self.quadro_buttonp1,
                                      command = self.select,
                                      text = "Select",
                                      background = "Green",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Select.pack(side = LEFT, anchor = W)

        self.quadro_push = Frame(genitore)
        self.quadro_push.pack(side = TOP, expand = YES, fill = BOTH,pady = 10,
                                  ipadx = 5, ipady = 5)




      #-----------------------------      Browsefiles ---------------------------------------------
        self.filesel = ut.Browse_filename(genitore, "Experiment Filenames", 0)
        self.filesel.pulsanteA.configure(command= self.browse_command2)



    #def keymove(self,event):
        #self.entry_A.configure(bg="yellow")
        #self.entry_B.configure(bg="yellow")
        #self.entry_C.configure(bg="yellow")
    #    pass

    #def keyenter(self,event):
        #self.A.get()
        #self.B.get()
        #self.C.get()
        #self.entry_A.configure(bg="white")
        #self.entry_B.configure(bg="white")
        #self.entry_C.configure(bg="white")
    #    pass

    def radio_command(self):
        
        if self.v.get() ==1:
                              #use text
            self.Aslider.configure(variable= 0,  state = DISABLED, )   #command= None,
            self.Bslider.configure(variable= 1,  state = DISABLED, )   #command= None,
            self.Cslider.configure(variable= 0,  state = DISABLED, )   #command= None,
            self.entry_A.configure(state = NORMAL, )
            self.entry_B.configure(state = NORMAL, )
            self.entry_C.configure(state = NORMAL, )

        if self.v.get() ==2:   #use slider
            A=float(self.A.get())
            print A
            self.Aslider.configure(from_ = A*0.985,
                                   to =A*1.015)
            self.Aslider.configure(state = ACTIVE  ,variable=self.A)    #, command= self.setredraw_A
            self.Bslider.configure(state = ACTIVE , variable=self.B)    #,command= self.setredraw_B
            self.Cslider.configure(state = ACTIVE , variable=self.C)    #,command= self.setredraw_B
            self.entry_A.configure(state = 'readonly', )
            self.entry_B.configure(state = 'readonly', )
            self.entry_C.configure(state = 'readonly', )
        pass

    def plot(self):     
        if  self.A.get()+self.B.get()+self.C.get()=="010":
            self.pre_allig()                                         
        #if self.pulsante_dplot.configure()['relief'][-1]=='raised':
        #    self.pre_allig()
        self.graph= ut.Graph()
        self.graph.top.protocol("WM_DELETE_WINDOW", self.topcallback_plot)
        self.graph.plot([self.newE],[self.disp.Nor])  
        self.graph.plot([self.calib.E],[self.calib.Nor])             
        self.pulsante_plot.configure(relief="sunken", state=DISABLED) 


    def dplot(self):
        if  self.A.get()+self.B.get()+self.C.get()=="010":
            self.pre_allig()                                         
        #if self.pulsante_plot.configure()['relief'][-1]=='raised':
        #    self.pre_allig()
        self.graphd= ut.Graph()
        self.graphd.top.protocol("WM_DELETE_WINDOW", self.topcallback_dplot)
        self.graphd.plot([self.newE],[self.disp.E_MuFp/max(self.disp.E_MuFp)], comment=["Disp."])#self.disp.Ej])
        self.graphd.plot([self.calib.E],[self.calib.E_MuFp/max(self.calib.E_MuFp)], comment=["Calib."])#self.calib.Ej])
        self.pulsante_dplot.configure(relief="sunken", state=DISABLED)      
                                                                               
    def fitder(self):
        if  self.A.get()+self.B.get()+self.C.get()=="010":
            self.pre_allig()  
            print "get a new pre allignment"
        param=map(float,[self.A.get(),self.B.get(),self.C.get()])    
        print "param=",param
        param=ut.fitcalibration(self.calib.E, numpy.gradient(self.calib.Mu), \
                                self.disp.E, numpy.gradient(self.disp.Mu), param)
        self.A.set(param[0])
        self.B.set(param[1])
        self.C.set(param[2]) 
        
        print "fitted param=",param
        self.setredraw_A(param) 
        self.setredraw_B(param)    
        
        
        
    def pre_allig(self):
            self.calib= bm29.sfigati(self.Cal_sel.filenames[0])
            self.calib.bm29derE()
            self.calib.XANES_Norm()
            self.calib_maxi=self.calib.E_MuFp.argmax()
            print self.calib_maxi
            print self.calib.E[self.calib_maxi]

            self.disp= bm29.sfigati(self.Disp_sel.filenames[0])
            self.disp.bm29derE()
            self.disp.XANES_Norm()
            self.disp_maxi=self.disp.E_MuFp.argmax()
            print self.disp_maxi
            print self.disp.E[self.disp_maxi]
            
            
            first_calibration=self.calib.E[self.calib_maxi]- self.disp.E[self.disp_maxi]
            self.A.set(first_calibration)
            
            #self.Aslider.configure(from_ = self.calib.E[self.calib_maxi]*0.985,
            #                       to =self.calib.E[self.calib_maxi]*1.015)
            self.Aslider.configure(from_ = first_calibration*0.985,
                       to =first_calibration*1.015)
            
            self.newE= self.newf(numpy.arange(len(self.disp.E)))


    def setredraw_A(self,value):
        pippo = value
        if hasattr(self, "calib") and hasattr(self, "disp"):
            self.newE = self.newf(numpy.arange(len(self.disp.E)))
            try:
                self.graph.curves[0].set_xdata(self.newE)
                self.graph.canvas.draw()
            except: pass
            try:
                self.graphd.curves[0].set_xdata(self.newE)
                self.graphd.canvas.draw()
            except: pass
        pass           

    def setredraw_B(self,value):
        pippo = value
        shift = float(self.A.get())
        if hasattr(self, "calib") and hasattr(self, "disp"):
            Ealmax= self.newE[self.disp_maxi]
            diff_E   = self.newf(self.disp_maxi)-Ealmax
            self.A.set(shift - diff_E)
            self.newE = self.newf(numpy.arange(len(self.disp.E)))
            try:
                self.graph.curves[0].set_xdata(self.newE)
                self.graph.canvas.draw()
            except: pass
            try:
                self.graphd.curves[0].set_xdata(self.newE)
                self.graphd.canvas.draw()
            except: pass
        pass



    def newf(self, pippo):
           newE = (float(self.A.get())) \
                  +float(self.B.get())*pippo     \
                  +float(self.C.get())*pippo**2
           return newE


    def topcallback_plot(self):
        self.pulsante_plot.configure(relief="raised", state=NORMAL)
        self.graph.top.destroy()

    def topcallback_dplot(self):
        self.pulsante_dplot.configure(relief="raised", state=NORMAL)
        self.graphd.top.destroy()

    def select(self):
        global Dis_coeff
        Dis_coeff[0]=float(self.A.get())
        Dis_coeff[1]=float(self.B.get())
        Dis_coeff[2]=float(self.C.get())
                                                            
    def browse_command2(self):
        global filesel_spectra
        filesel_spectra=[]
        buffero = []
        self.filesel.browse_command()
        for i in self.filesel.filenames:
            buffero.append(bm29.disperati(i))
        try:
            for i in buffero:
                i.calibrate(*Dis_coeff)
                i.bm29ize()
                filesel_spectra.extend(i.spectra)
        except AttributeError:
            print "Error file not open" 
        del buffero
########################################################################################################    
####################################     QE cal      ####################################################
class QEcal():
    def __init__(self, genitore):
      #-----------------------------      Declare      --------------------------------------------------
        self.before = StringVar()
        self.after  = StringVar()
        #self.energy = StringVar()
        self._function= StringVar()
        self._function_p= StringVar()
        self._All_spectra= StringVar()
        self._c_range = IntVar()
      #-----------------------------      Define       --------------------------------------------------
        self._function.set("Ref.der.")
        self._function_p.set("Ref")        
        self._All_spectra.set("first spectra     ")        
        labelpack =  {"side" : LEFT,  "fill" :BOTH , "anchor" : N,"ipadx" : 0} #,"expand" : YES, "ipady" : 5
        entrypack = {"side" : LEFT, "padx" : 1 , "fill" : None}#"ipady" : 3
      #-----------------------------      Windows       --------------------------------------------------
        self.filesel = ut.Browse_filename(genitore, "Filenames", 0)
        self.filesel.pulsanteA.configure(command= self.browse_command2)
        self.dirsel = ut.Browse_Directory(genitore, "Files in a Directory if more than 350", 0)
      #--------------------------- Quadro correction ---------------------------------------------- 
        self.quadro_Define = LabelFrame(genitore,  text = "Allign spectra respect to")
        self.quadro_Define.pack(side = TOP, anchor=W, fill = X, pady= 3, ipadx = 5, ipady = 3, expand = N)   #, expand = YES
       #--------------------------- Quadro correction 1---------------------------------------------- 
        self.quadro_Define1 = Frame(self.quadro_Define)
        self.quadro_Define1.pack(side = TOP, anchor=W, fill = X, pady= 0, ipadx = 0, ipady = 0, expand = N)  
        self.combo_All= ttk.Combobox(self.quadro_Define1 , state ="readonly",
                                     textvariable=self._All_spectra,values=('first spectra     ', 'Calibration sample'))
        self.combo_All.pack(side=LEFT)
        self.combo_All.insert(0, 'first spectra     ')
        self.combo_All.insert(1, 'Calibration sample')
        
        Label(self.quadro_Define1, text=" using ").pack(side = LEFT)
        self.combo_Cal= ttk.Combobox(self.quadro_Define1 ,   textvariable=self._function,
                         values=( 'Ref.der.','Ref','-I0','Cal. Mu','Cal. der.'))
        self.combo_Cal.pack(side=LEFT)
        self.combo_Cal.insert(0, 'Ref.der.')
        self.combo_Cal.insert(1, 'Ref')
        self.combo_Cal.insert(2, '-I0')
        self.combo_Cal.insert(3, 'Cal. Mu')
        self.combo_Cal.insert(4, 'Cal. der.')        
        Frame(self.quadro_Define1).pack(side = LEFT, anchor=W, fill = X, pady= 2, ipadx = 10, padx=5, ipady = 3, expand = Y)
        Button(self.quadro_Define1,
              command = self.plot_set_Energy,
              text = "Plot  correction ",
              background = "violet",
              width = 15,
              padx = "1m",
              pady = "2m").pack(side = LEFT, anchor = W)
       #--------------------------- Quadro correction 2----------------------------------------------  
        self.quadro_Define2 = Frame(self.quadro_Define)
        self.quadro_Define2.pack(side = TOP, anchor=W, fill = X, pady= 3, ipadx = 0, ipady = 3, expand = N)  
        Label(self.quadro_Define2, text="In the range").pack(side = LEFT)    
        self.check_range=Checkbutton(self.quadro_Define2, variable=self._c_range )
        self.check_range.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1)
        Label(self.quadro_Define2, text=" between ").pack(side = LEFT)
        self.Define_before = Entry(self.quadro_Define2,   textvariable= self.before, width = 10 )#
        self.Define_before.pack(side = LEFT, padx = 5, ipadx =5  ,ipady = 3)
        Label(self.quadro_Define2, text=" and ").pack(side = LEFT)
        self.Define_after = Entry(self.quadro_Define2,   textvariable= self.after, width = 10 )
        self.Define_after.pack(side = LEFT, padx = 5,  ipadx = 5 ,ipady = 3)  
        Label(self.quadro_Define2, text=" eV ").pack(side = LEFT)
       #--------------------------- Quadro correction 3----------------------------------------------  
        self.quadro_Define3 = Frame(self.quadro_Define)
        self.quadro_Define3.pack(side = TOP, anchor=W, fill = X, pady= 0, ipadx = 0, ipady = 0, expand = N)         
        
        self.calibsel = ut.Browse_file(self.quadro_Define3, "Calibration Sample", 1)
    
      #--------------------------- Quadro plot cor ----------------------------------------------         
        self.quadro_plot = LabelFrame(genitore, text="Plot ")
        self.quadro_plot.pack(side = TOP, expand = YES, fill = X, pady = 10,
                                  ipadx = 5, ipady = 5)
        self.combo_Plot= ttk.Combobox(self.quadro_plot ,  state ="readonly",
                        textvariable=self._function_p,        values=('Ref.der.', 'Ref','-I0')  )
        self.combo_Plot.pack(side=LEFT)   
        self.pulsante_Plot_nc = Button(self.quadro_plot ,
                                      command = lambda x= "not": self.plot_all(x),
                                      text = "not corrected",
                                      background = "DeepPink2",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Plot_nc.pack(side = LEFT, anchor = W)
        self.pulsante_Plot_c = Button(self.quadro_plot ,
                                      command = lambda z= "cor": self.plot_all(z),
                                      text = "  corrected  ",
                                      background = "DeepPink2",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m",
                                      relief="ridge",#"solid",#"groove",#"flat",
                                      state=DISABLED)
        self.pulsante_Plot_c.pack(side = LEFT, anchor = W)
      #--------------------------- Quadro perform ----------------------------------------------
        self.quadro_buttonp3 = LabelFrame(genitore, text="Apply correction")
        self.quadro_buttonp3.pack(side = TOP, expand = YES, fill = X, pady = 10,
                                  ipadx = 5, ipady = 5)
        self.pulsante_Defcor = Button(self.quadro_buttonp3,
                                      command = self.correct,
                                      text = "Apply correction",
                                      background = "Violet",
                                      width = 10,
                                      padx = "5m",
                                      pady = "2m")
        self.pulsante_Defcor.pack(side = LEFT, anchor = W)
        self.pulsante_Remcor = Button(self.quadro_buttonp3, 
                                      command = self.rem_correct,
                                      text = "Remove correction",
                                      background = "Violet",
                                      width = 10,
                                      padx = "5m",
                                      pady = "2m")
        self.pulsante_Remcor.pack(side = LEFT, anchor = W)


    ##########################function################################################################
    def browse_command2(self,type_select):
        global filesel_spectra
        filesel_spectra=[]
        if type_select == "Fil":
            self.filesel.browse_command()
            list_filenames=self.filesel.filenames
        if type_select == "Dir":
            self.dirsel.browse_command() 
            list_filenames=self.dirsel.filenames          





        try:
            bm29.bm29file(list_filenames[0], All_Column="minimum")
            format="bm29"
        except bm29.FileFormatError:
            format="samba"
        if format=="bm29":
            print "opening ", len(list_filenames), "  files"
            for i in list_filenames:
                filesel_spectra.append(bm29.bm29file(i, All_Column="minimum"))
        elif  format=="samba":
            for i in list_filenames:
                filesel_spectra.append(bm29.sambafile(i, All_Column="minimum"))  
        self.pulsante_Defcor.configure(relief="raised")
        filesel_spectra[0].bm29derRef()
        Eo_test=bt.max_range(filesel_spectra[0].E, filesel_spectra[0].E_RefFp)
        self.before.set(round(Eo_test-50))
        self.after.set(round(Eo_test+50))  
        self._c_range.set(1)
        return
        


    def plot_all(self, ptype): 
        if ptype=="not":
            if hasattr(filesel_spectra[0], "oldE"):
                x_array=[item.oldE for item in filesel_spectra]
            else:
                x_array=[item.E for item in filesel_spectra]
        if ptype=="cor":
            if hasattr(filesel_spectra[0], "oldE"):
                x_array=[item.E for item in filesel_spectra]
            else: 
                print "\nCorrection still not applied\n\
                        press the button\n"
                return
        if self._function_p.get()=='Ref.der.':   
            try:
                for item in  filesel_spectra: item.bm29derRef()
                y_array=[item.E_RefFp for item in filesel_spectra]
                title="derivate reference"
            except:
                print "reference not measured"
                return            
            
        elif self._function_p.get()=='Ref':            
            try:
                y_array=[item.ref for item in filesel_spectra]
                title="reference"                
            except:
                print "reference not measured"
                return
        elif self._function_p.get()=='-I0':    
                y_array=[item.I0 for item in filesel_spectra]
                title= "I0"
        if ptype== "cor": title=title+" corrected"   
        self.graph = ut.Graph()
        self.graph.plot(x_array, y_array, title= title)
    



    def set_Energy(self):
        self.Energy_row=[]
        self._function.get()
        if self._c_range.get():
            before =float(self.before.get())
            after=float(self.after.get())
        else:
            before, after= None, None
        if self._function.get() == "-I0":
            Y= lambda x: -x.I0/abs(max(-x.I0))
        elif self._function.get() == 'Ref.':
            Y= lambda x: x.ref
        elif self._function.get() == 'Ref.der.':
            for item in filesel_spectra: item.bm29derRef()
            Y= lambda x: x.E_RefFp/max(x.E_RefFp)
        elif self._function.get() == 'Cal. Mu':
            Y= lambda x: x.Mu
        elif self._function.get() == 'Cal. der.':
            self.calibsel.spectra[0].bm29derRef()
            Y= lambda x: x.E_Fp/max(x.E_MuFp)            
            
        if  self._c_range.get():
            L = lambda objecto,x: x.compress((objecto.E>before)&(objecto.E<after))
        else:
            L = lambda objecto,x: x        
        if self._All_spectra.get() =='first spectra     ':
            if self._function.get() =='Cal. Mu' or self._function.get() =='Cal. der.':
                print "\nnot clear input\nasking to use first sample and calibration...."
            splinex1y1 = interpolate.splrep(filesel_spectra[0].E,Y(filesel_spectra[0]))
        elif self._All_spectra.get() =='Calibration sample':
            if self._function.get() =='Ref.' or self._function.get() =='Ref.der.':
                print "\nATTENTION you are using reference of calibration file\n"
                raise ValueError()
            try:
                splinex1y1 = interpolate.splrep(self.calibsel.spectra[0].E,Y(self.calibsel.spectra[0]))
            except:
                self.calibsel.spectra[0]=bm29.bm29file(self.calibsel.spectra[0].data)
            self.calibsel.spectra[0].bm29derE()
            if self._function.get() == 'Ref.':
                splinex1y1 = interpolate.splrep(self.calibsel.spectra[0].E, self.calibsel.spectra[0].Mu)
            elif self._function.get() == 'Ref.der.':    
                splinex1y1 = interpolate.splrep(self.calibsel.spectra[0].E, self.calibsel.spectra[0].E_MuFp)
        self.standard_Energy=bt.max_range(filesel_spectra[0].E, Y(filesel_spectra[0]),before,after) 
           
        for item in  filesel_spectra:
            self.Energy_row.append(float(ut.fitcalibration(x2=L(item,item.E), y2=L(item,Y(item)),
                                                     param=[0],splinex1y1=splinex1y1)))
           

        
    def plot_set_Energy(self):
        self.set_Energy()
        x_array= [range(len(filesel_spectra))]
        y_array= [self.Energy_row]
        self.graph = ut.Graph()
        self.graph.plot(x_array, y_array, title= "Energy shift")   

    def correct(self):
        self.set_Energy()
        if hasattr(filesel_spectra[0], "oldE"):            
            pass
        else:  
            for item in filesel_spectra: item.oldE=item.E
        for i,item in enumerate(filesel_spectra):
            item.E= bt.MvEAshift(item.E,item.dspac, self.standard_Energy-self.Energy_row[i],
                                 self.standard_Energy)
        print "\nCorrection applyed\n"            
        self.pulsante_Defcor.configure(relief="sunken")
        self.pulsante_Plot_c.configure(relief="raised",state=NORMAL)
        
    def rem_correct(self):
        for item in filesel_spectra:
            item.E=item.oldE
            del item.oldE    
        self.pulsante_Defcor.configure(relief="raised")
        self.pulsante_Plot_c.configure(relief="ridge",state=DISABLED)        
        print "\nCorrection removed\n"
            
       
#########################################################################################################
##################################       SAmbaQE   #####################################################     
class SambaQE():
    def __init__(self, genitore):
      #-----------------------------      Declare      --------------------------------------------------
        self.A = StringVar()
        self._r =StringVar()
        self.v = IntVar()
        self.v.set(2)


      #-----------------------------      Define      --------------------------------------------------
        self.A.set(0)

      #-----------------------------      geometry      --------------------------------------------------
      #-----------------------------      Browsefiles ---------------------------------------------
        self.filesel = ut.Browse_filename(genitore, "Experiment Filenames if less than 350", 0)
        #self.filesel.pulsanteA.configure(command= lambda i="Fil":  self.browse_command2(i))  the command changed in line 3496 
        self.dirsel = ut.Browse_Directory(genitore, "Files in a Directory if more than 250", 0)
        #self.dirsel.pulsanteA.configure(command= lambda i="Dir":  self.browse_command2(i))  the command changed in line 3496       
        self.Cal_sel = ut.Browse_filename(genitore, "Calibration sample", 1)
        self.quadro_Title = Frame(genitore)
        self.quadro_Title.pack(side = TOP, anchor= W, expand = Y, fill = BOTH)
        Label(self.quadro_Title, text= " Shift of Eo between different run   ").pack(side=LEFT, anchor=N)
        Radiobutton(self.quadro_Title, text="Write text",
                                        variable=self.v,
                                        value=1,
                                        command= self.radio_command
                                        ).pack(side=LEFT,   anchor=N)
        Radiobutton(self.quadro_Title, text="Use sliders",
                                        variable=self.v,
                                        value=2,
                                        command= self.radio_command
                                        ).pack(side=LEFT,  anchor=N)
      #-----------------------------      Calibration---------------------------------------------
        self.quadro_sliders = Frame(genitore)
        self.quadro_sliders.pack(side = TOP, anchor= W, expand = Y, fill = BOTH)
        self.quadro_A = Frame(self.quadro_sliders)
        self.quadro_A.pack(side =TOP, fill=BOTH)
        self.Aslider = Scale( self.quadro_A, from_=-2, to=2,
                                            command= self.setredraw_A,
                                            variable= self.A,
                                            resolution=0.001,
                                            orient=HORIZONTAL, # label= "A",
                                            showvalue=0
                                            )
        self.Aslider.pack(side = LEFT,fill = X, anchor = W,pady = 3, ipady = 0, expand = Y)
        #Label(self.quadro_A,text= " A ").pack(side=LEFT)#, anchor = SW
        self.entry_A= Entry(self.quadro_A, width = 9, textvariable = self.A, state='readonly')
        self.entry_A.pack(side = LEFT, ipadx = 5, ipady = 1, fill = None, pady= 2)
        Label(self.quadro_A, text= "Delta E").pack(side=LEFT)




        self.quadro_buttonp1 = Frame(genitore)
        self.quadro_buttonp1.pack(side = TOP, expand = N, fill = X, pady = 2,
                                  ipadx = 5, ipady = 5)
        self.pulsante_plot = Button(self.quadro_buttonp1,
                                      command = self.plot,
                                      text = "Plot Mu",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_plot.pack(side = LEFT, anchor = W)
        self.pulsante_dplot = Button(self.quadro_buttonp1,
                                      command = self.dplot,
                                      text = "Plo Derivative",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_dplot.pack(side = LEFT, anchor = W)
        self.pulsante_Fitder = Button(self.quadro_buttonp1, 
                                      command = self.fitder,
                                      text = "Fit Derivative",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Fitder.pack(side = LEFT, anchor = W)        
        
        

        self.quadro_buttonp3 = LabelFrame(genitore, text="Apply correction")
        self.quadro_buttonp3.pack(side = TOP, expand = YES, fill = X, pady = 10,
                                  ipadx = 5, ipady = 5)
        self.pulsante_Defcor = Button(self.quadro_buttonp3,
                                      command = self.correct,
                                      text = "Apply correction",
                                      background = "Violet",
                                      width = 10,
                                      padx = "5m",
                                      pady = "2m")
        self.pulsante_Defcor.pack(side = LEFT, anchor = W)
        self.pulsante_Remcor = Button(self.quadro_buttonp3, 
                                      command = self.rem_correct,
                                      text = "Remove correction",
                                      background = "Violet",
                                      width = 10,
                                      padx = "5m",
                                      pady = "2m")
        self.pulsante_Remcor.pack(side = LEFT, anchor = W)

        self.quadro_push = Frame(genitore)
        self.quadro_push.pack(side = TOP, expand = YES, fill = BOTH,pady = 10,
                                  ipadx = 5, ipady = 5)

    ##########################function################################################################
    def browse_command2(self,type_select):
        global filesel_spectra
        filesel_spectra=[]
        
        if type_select == "Fil":
            self.filesel.browse_command()
            list_filenames=self.filesel.filenames
        if type_select == "Dir":
            self.dirsel.browse_command() 
            list_filenames=self.dirsel.filenames            
            
            
        try:
            bm29.bm29file(list_filenames[0], All_Column="minimum")
            format="bm29"
        except bm29.FileFormatError:
            format="samba"
        
        if format=="bm29":
            for i in list_filenames:
                filesel_spectra.append(bm29.bm29file(i, All_Column="minimum"))
        elif  format=="samba":
            for i in list_filenames:
                try:
                    print i
                    filesel_spectra.append(bm29.sambafile(i, All_Column="minimum")) 
                except Exception as e:
                    name=str(type(e)).split("'")[-2]
                    print "\nproblem on file:\n%s" %(i)
                    print "{0:s} : {1:s}".format(name, e)
                    self.filesel.labelfiletext.set(name)
        self.pulsante_Defcor.configure(relief="raised", state=NORMAL)
        return

    def radio_command(self):
        if self.v.get() ==1:
            self.Aslider.configure(variable= 0,  state = DISABLED, )   #command= None,
            self.entry_A.configure(state = NORMAL, )

        if self.v.get() ==2:
            self.Aslider.configure(state = ACTIVE  ,variable=self.A)    #, command= self.setredraw_A
            self.entry_A.configure(state = 'readonly', )
        pass
    
    def setredraw_A(self,value):
        pippo = value
        try:
           self.graph.curves[0].set_xdata(self.firstfile.E+float(self.A.get()))
           self.graph.canvas.draw()
        except: pass
        try:
            self.graphd.curves[0].set_xdata(self.firstfile.E+float(self.A.get()))
            self.graphd.canvas.draw()
        except: pass
        pass
    
    def plot(self):     
        if self.pulsante_dplot.configure()['relief'][-1]=='raised':
            self.pre_allig()
        self.graph= ut.Graph()
        self.graph.top.protocol("WM_DELETE_WINDOW", self.topcallback_plot)
        self.graph.plot([self.firstfile.E+float(self.A.get())],[self.firstfile.Nor])
        self.graph.plot([ self.calib.E],[self.calib.Nor]) 
        #self.pulsante_plot.configure(relief="sunken", state=DISABLED) 


    def dplot(self):
        if self.pulsante_plot.configure()['relief'][-1]=='raised':
            self.pre_allig()
        self.graphd= ut.Graph()
        self.graphd.top.protocol("WM_DELETE_WINDOW", self.topcallback_dplot)
        self.graphd.plot([self.firstfile.E+float(self.A.get())],[self.firstfile.E_MuFp/max(
                                                              self.calib.E_MuFp)])#self.calib.Ej])
        self.graphd.plot([self.calib.E],[self.calib.E_MuFp/max(self.calib.E_MuFp)])#self.disp.Ej])                                                      
        self.pulsante_dplot.configure(relief="sunken", state=DISABLED)      
                                                                               

    def pre_allig(self):
        if hasattr(filesel_spectra[0], "oldE"):            
            pass
        else:  
            for item in filesel_spectra: item.oldE=item.E
        self.calib= bm29.sfigati(self.Cal_sel.filenames[0])
        self.calib.bm29derE()
        self.calib.XANES_Norm()
        self.calib_maxi=self.calib.E_MuFp.argmax()
        ref=numpy.zeros(len(filesel_spectra[0].ref))
        for i in filesel_spectra: 
           ref+=i.ref/len(filesel_spectra) 
        self.firstfile= bm29.bm29file([filesel_spectra[0].E, ref])
        del ref
        self.firstfile.bm29derE()
        self.firstfile.XANES_Norm()
        self.firstfile_maxi=self.firstfile.E_MuFp.argmax()      
            #self.Aslider.configure(from_ = self.calib.E[self.calib_maxi]*0.985,
            #                       to =self.calib.E[self.calib_maxi]*1.015)
            #self.A.set(self.calib.E[self.calib_maxi]- self.disp_maxi)
            #self.newE= self.newf(numpy.arange(len(self.disp.E)))
    def topcallback_plot(self):
        self.pulsante_plot.configure(relief="raised", state=NORMAL)
        self.graph.top.destroy()

    def topcallback_dplot(self):
        self.pulsante_dplot.configure(relief="raised", state=NORMAL)
        self.graphd.top.destroy()
        
    def fitder(self):
        if self.pulsante_dplot.configure()['relief'][-1]=='raised':
                    if self.pulsante_plot.configure()['relief'][-1]=='raised':
                        self.pre_allig()
        param=[float(self.A.get())]    
        param=ut.fitcalibration(self.calib.E, numpy.gradient(self.calib.Mu), \
                                self.firstfile.E, numpy.gradient(self.firstfile.Mu), param)
        self.A.set(round(param,3))
        self.setredraw_A(param) 
              
    
    def correct(self):
        if hasattr(filesel_spectra[0], "oldE"):            
            pass
        else:  
            for item in filesel_spectra: item.oldE = item.E
        for i,item in enumerate(filesel_spectra):
            # if correction has to be done in angle change with
            # bt.MvEAshift(item.E,item.dspac, self.Energy_row[i],standard_energy)
            item.E= item.oldE+float(self.A.get())
        print "\nCorrection applied\n"
        self.pulsante_Defcor.configure(relief="sunken", state=NORMAL)


            
    def rem_correct(self):
        for item in filesel_spectra:
            item.E=item.oldE
            del item.oldE    
        print "\nCorrection removed\n"
        self.pulsante_Defcor.configure(relief="raised", state=NORMAL)


#########################################################################################################
##################################       Avesel     #####################################################
class Avesel(Rebin.REBIN): 
    def __init__(self, genitore):
      #-----------------------------      Declare      --------------------------------------------------
        self._from_tof= StringVar()              #select
        self._c_aver = IntVar()            #aver
        self._aver = IntVar()              #aver
        self._c_Trun = IntVar()            #Truncate
        self.before = StringVar()          #Truncate
        self.after = StringVar()           #Truncate
        self._c_Rebin = IntVar()
        self.Edgep = StringVar()           #rebin
        self.Prep = StringVar()            #rebin
        self.Postp = StringVar()           #rebin
        self.Edges = StringVar()           #rebin
        self.Pres = StringVar()            #rebin
        self.Posts = StringVar()           #rebin
        self.labelfiletext = StringVar()   #rebin
      #-----------------------------      Define       --------------------------------------------------
        self._from_tof.set("1,2,5-15,23")
        self._aver.set(1)
        self.Edgep.set(24350)
        self.Prep.set(30)
        self.Postp.set(20)
        self.Edges.set(.5)
        self.Pres.set(5)
        self.Posts.set(.03)
      #-----------------------------     Browse file   ------------------------------------------------
        #self.filesel = ut.Browse_file(genitore, "Filenames", 0, All_Column=False)
        #self.filesel.pulsanteA.configure(command= self.browse_command2)
        # 'quadro_process'
      #-----------------------------     Select   and   Truncate      -----------------------------------
        self.SelTrunc = Frame(genitore)    #,text = "Correction"
        self.SelTrunc.pack(side =TOP, fill = BOTH, padx =3, pady =10)
        labelpack =  {"side" : LEFT,  "fill" : BOTH, "anchor" : N,"ipadx" : 5} #,"expand" : YES, "ipady" : 5
        entrypack = {"side" : LEFT, "padx" : 5, }#"ipady" : 3
      #-----------------------------     Select        --------------------------------------------------
        self.process = LabelFrame(self.SelTrunc, text = "Select")    #,text = "Correction"
        self.process.pack(side = LEFT, fill = BOTH, pady= 3, ipadx = 5, ipady = 3, expand = YES)   #
        # Si aggiungono alcuni sottoquadri a 'dspacing'
        self.from_tof = ut.LabelEntry(self.process,  Ltext = " Select spectra  ex. 1,2,5-15,23",
                                      EtextVar= self._from_tof, Ewith = 20 )#
        self.from_tof.LabFr.pack(**labelpack)
        self.from_tof._entry.pack(**entrypack)
      #-----------------------------     Truncate      -------------------------------------------------
        self.quadro_Trun = LabelFrame(self.SelTrunc,  text = "Truncate")
        self.quadro_Trun.pack(side = LEFT, fill = BOTH, pady= 3, ipadx = 5, ipady = 3, expand = YES)   #, expand = YES
        self.Trun_before = ut.LabelEntry(self.quadro_Trun,  Ltext = "before", EtextVar= self.before, Ewith = 10 )#
        self.Trun_before.LabFr.pack(**labelpack)
        self.Trun_before._entry.pack(**entrypack)
        self.Trun_after = ut.LabelEntry(self.quadro_Trun, Ltext = "after", EtextVar= self.after, Ewith = 10 )
        self.Trun_after.LabFr.pack(**labelpack)
        self.Trun_after._entry.pack(**entrypack)
      #-----------------------------      Rebin        --------------------------------------------------
        #labelpack =  {"side" : LEFT, "expand" : YES, "fill" : BOTH, "anchor" : N,"ipadx" : 5, "ipady" : 5}
        #entrypack = {"side" : LEFT, "padx" : 5, "ipady" : 3}
        self.quadro_Rebin = LabelFrame(genitore,  text = "Rebin")
        self.quadro_Rebin.pack(side = TOP, expand = YES, fill = X, ipadx = 5, ipady = 3)

        self.quadro_Rebinrange = Frame(self.quadro_Rebin)   # Label   , text = "Range"
        self.quadro_Rebinrange.pack(side = TOP, fill = X)#, expand = YES, ,ipadx = 5, ipady = 5
        self.Edgep_LB = ut.LabelEntry(self.quadro_Rebinrange,  Ltext = "Edge position",
                                   EtextVar= self.Edgep, Ewith = 8, SLtext ="eV" )#
        self.Edgep_LB.LabFr.pack(**labelpack)  ;   self.Trun_before._entry.pack(**entrypack)
        self.Prep_LB = ut.LabelEntry(self.quadro_Rebinrange,  Ltext = "Preedge ends  ",
                                  EtextVar= self.Prep, Ewith = 8, SLtext = "eV bef. Eo" )
        self.Postp_LB = ut.LabelEntry(self.quadro_Rebinrange,  Ltext = "EXAFS starts",
                                   EtextVar= self.Postp, Ewith = 8, SLtext = "eV after Eo")

        self.quadro_RebinStep = Frame(self.quadro_Rebin)  #Label    , text = "Step"
        self.quadro_RebinStep.pack(side = TOP, fill = X)#, expand = YES, fill = BOTH,ipadx = 5, ipady = 5
        self.Edgep_LB = ut.LabelEntry(self.quadro_RebinStep,  Ltext = "Edge step", EtextVar= self.Edges, Ewith = 8,SLtext ="eV" )#
        self.Edgep_LB.LabFr.pack(**labelpack)  ;   self.Trun_before._entry.pack(**entrypack)
        self.Prep_LB = ut.LabelEntry(self.quadro_RebinStep,  Ltext = "Preedge  step", EtextVar= self.Pres, Ewith = 8, SLtext ="eV            " )#
        self.Postp_LB = ut.LabelEntry(self.quadro_RebinStep,  Ltext = "EXAFS  step", EtextVar= self.Posts, Ewith = 8 , SLtext = u'\xc5-1             ')#
        self.pulsante_Rebin = Button(self.quadro_Rebin,
                                      command = self.RebinSparam,
                                      text = "Eval on Graph",
                                      background = "violet",
                                      width = 12,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Rebin.pack(side = TOP, anchor = W)
      #-----------------------------     Average       --------------------------------------------------
        self.process1 = Frame(genitore)    #,text = "Correction"
        self.process1.pack(side = TOP, expand = YES, fill = BOTH, ipadx = 5, ipady = 3)
        self.quadro_aver = LabelFrame(self.process1, text = "Perform:")
        Label(self.quadro_aver, text = "  Select,         ").pack(side = LEFT)
        self.check_aver=Checkbutton(self.quadro_aver, text="Average each" ,variable=self._c_aver )
        self.check_aver.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1)
        self.quadro_aver.pack(side = LEFT, expand = YES, fill = BOTH, anchor = W , ipady = 0)
        self._entry_aver= Entry(self.quadro_aver, width = 3, textvariable=self._aver)
        self._entry_aver.pack(side = LEFT, ipady = 3,anchor = W )
        Label(self.quadro_aver, text="files,  ").pack(side = LEFT, ipady = 3, anchor = W , fill = Y)
        self.check_Trun=Checkbutton(self.quadro_aver, text="Truncate,  " ,variable=self._c_Trun )
        self.check_Trun.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1)
        self.check_Rebin=Checkbutton(self.quadro_aver, text="Rebin " ,variable=self._c_Rebin )
        self.check_Rebin.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1)

      #-----------------------------     Perform       ---------------------------------------------------
        self.quadro_buttonp1 = Frame(genitore)
        self.quadro_buttonp1.pack(side = TOP, expand = YES, fill = BOTH,pady = 10,
                                  ipadx = 5, ipady = 5)
        self.pulsante_Aver = Button(self.quadro_buttonp1,
                                      command = self.Perform,
                                      text = "Perform",
                                      background = "green",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Aver.pack(side = LEFT, anchor = W)
        self.Avesel_PlSa_But=ut.PloteSaveB(self.quadro_buttonp1,ext="reb" , title="Rebin")
        #self.Avesel_PlSa_But.Button_plot.configure( command = self.plot2)


    def RebinSparam(self):
        global filesel_spectra
        self.num=0
        self.top = Toplevel()
        self.top.title("REBIN PARAMETER")        
       #--------------------------   Prepare group  --------------------------------------------------
        dif =lambda x: numpy.argmax(numpy.gradient(x.Mu)/numpy.gradient(x.E))
        Eo=filesel_spectra[0].E[dif(filesel_spectra[0])]
        self.Edgep.set(Eo)
        self.evaluatepar()
       #--------------------------   Graphic win  --------------------------------------------------
        self.graphframe = Frame(self.top)        
        self.graphframe.pack(side = TOP, fill=BOTH, expand=YES)
        self.grap_win=ut.ParamGraph(self.graphframe, filesel_spectra, "E", ["Mu",])
        self.grap_win.plot(self.num)        
        self.grap_win.paramplot(self.get_param(), ["b","g","k","r","b"], 
                                ["Min","XAN","Eo","EXAFS","Max"])
        if len(filesel_spectra)>1:
            self.grap_win.slider.configure(command= self.panor2)
        #self.grap_win.onmoving=self.onmoving
        self.grap_win.canvas.mpl_disconnect(self.grap_win.mov_link)
        self.grap_win.mov_link=self.grap_win.canvas.mpl_connect(
                                           'motion_notify_event', self.onmoving)

    def evaluatepar(self):
        Eo=float(eval(self.Edgep.get()))
        E=filesel_spectra[self.num].E
        # Evaluate the minimum step around the edge 
        E=E.compress(numpy.logical_and(E>Eo-2,E<Eo+2))
        step=numpy.average(numpy.gradient(E))+.05
        self.Edges.set(round(step,1))        
            

    def get_param(self):
        Lim1=float(eval(self.before.get()))
        Lim2=float(eval(self.after.get()))
        Eo = float(eval(self.Edgep.get()))
        predg= float(eval(self.Prep.get()))
        postedg = float(eval(self.Postp.get()))
        spec=  filesel_spectra[self.num]
        return      [Lim1, Eo-predg, Eo, Eo+postedg, Lim2]


    def panor2(self,event):
        self.num=int(event)-1
        self.grap_win.param=self.get_param()
        self.evaluatepar()
        self.grap_win.panor(self.num+1)


    def onmoving(self, event):
        if self.grap_win.press:
            string_params= [self.before,self.Prep,self.Edgep,self.Postp,self.after]
            if self.grap_win.param_num==2:
                string_params[2].set(round(event.xdata,3))
            elif self.grap_win.param_num==1 or self.grap_win.param_num==3: 
                if event.xdata==None:pass
                else:string_params[self.grap_win.param_num].set(abs(round(event.xdata- float(eval(self.Edgep.get())),3)))
            else:
                string_params[self.grap_win.param_num].set(abs(round(event.xdata)))
            self.panor2(self.grap_win.slider.get())
            return
        else: return    
    
    




    def plot2(self):
           #start = self._fromf.get()
           #end = self._tof.get()
           self.Avesel_PlSa_But.plot()
           self.Avesel_PlSa_But.graph.clear()
           #self.Avesel_PlSa_But.graph.plot( self.Avesel_PlSa_But.x_array,
           #             self.Avesel_PlSa_But.y_array)
           #if self._c_aver.get():
           #    E = [filesel_spectra[i].E for i in self.lista_iter]
           #    Mu= [filesel_spectra[i].Mu for i in self.lista_iter]
           #    self.Avesel_PlSa_But.graph.plot(E, Mu)
           #else:
           #    self.Avesel_PlSa_But.graph.plot([i.E   for i in filesel_spectra[start -1:end]] ,
           #                                    [i.Mu  for i in filesel_spectra[start -1:end]])



    def Perform(self):
        aver = self._aver.get()
        filesel = ut.string_range(self._from_tof.get())
        Eo = float(eval(self.Edgep.get()))
        predg= float(eval(self.Prep.get()))
        postedg = float(eval(self.Postp.get()))
        xstep = float(eval(self.Edges.get()))
        pstep = float(eval(self.Pres.get()))
        kstep = float(eval(self.Posts.get()))
        trunbef= float(eval(self.before.get()))
        trunaft= float(eval(self.after.get()))
        #print aver , start
        global spectra
        global x
        spectra =[]
        listcomment=[]
        comment="#"
        if self._c_aver.get() and (self._aver.get()>1):
            comment+= " averaged each {0:4d} spectra,".format(aver)
            self.lista_iter = range(0,len(filesel),aver)
            for item in self.lista_iter:
                list_ave=[filesel_spectra[ii] for ii in filesel[item:item+aver]]                
                E, Mu  = bt.spectra_average([[i.E,i.Mu]for i in list_ave])
                spectra.append(bm29.bm29file([E,Mu]))
                try:
                    spectra[-1].T1=bt.dat_average([i.T1 for i in filesel_spectra[item:item+aver]])
                    spectra[-1].T2=bt.dat_average([i.T2 for i in filesel_spectra[item:item+aver]])
                except: pass
                try:
                    spectra[-1].start_time_ep=bt.dat_average([i.start_time_ep for i in filesel_spectra[item:item+aver]])
                except: pass
                listcomment.append(filesel_spectra[item].comments)
        else:
            for item  in [filesel_spectra[i] for i in filesel]:
                data = numpy.transpose(numpy.vstack((item.E,item.Mu)))
                spectra.append(bm29.bm29file(data))
                try:    spectra[-1].T1=item.T1
                except: pass
                try:    spectra[-1].T2=item.T2
                except: pass
                try:    spectra[-1].start_time_ep=item.start_time_ep
                except: pass
                listcomment.append(item.comments)

        if self._c_Trun.get():
            comment+= " truncate between {0:5.9f} and{1:5.9f} ,".format(trunbef, trunaft)              
            for i,item in enumerate(spectra):
                    data = numpy.transpose(numpy.vstack((item.E,item.Mu)))
                    data = bt.dat_Truncate(data, trunbef, trunaft)
                    spectra[i].E, spectra[i].Mu = map(numpy.ravel, numpy.hsplit(data,2))
                    #spectra[i]=bm29.bm29file(data)
                    
        if self._c_Rebin.get():
            comment+= " rebin with param.{0:5.7f},{1:5.7f},{2:5.7f},{3:5.7f},{4:5.7f},{5:5.7f},".format(Eo, predg, postedg, pstep, xstep, kstep)  
            for i,item in enumerate(spectra):
                data = numpy.transpose(numpy.vstack((item.E,item.Mu)))
                try:
                   data=bt.rebin(data, 0, Eo, predg, postedg, pstep, xstep, kstep, file='', msgStream=None)
                   spectra[i]=(bm29.bm29file(data))
                except bt.RebinError, self.rebinerror:
                   top = Toplevel()
                   Label(top, text = "Rebin not performed      " + self.rebinerror.parameter).pack(expand = YES)
                   break
        
        
        if comment== "#": comment = "#L E  Mu  \n"
        else: comment = comment[:-1]+"\n" +"#L E  Mu  \n" 
        for i, item in enumerate(spectra) :
            listcomment[i][-1]= comment
            item.comments= listcomment[i]
        x=range(1,len(spectra)+1)
        self.Avesel_PlSa_But.x_array= [item.E for item in spectra]
        self.Avesel_PlSa_But.y_array= [item.Mu for item in spectra]
        self.Avesel_PlSa_But.comments= [item.comments for item in spectra]
        
        print "\n---module average done---\n"       
        pass


#########################################################################################################
####################################     XANES       ####################################################
from matplotlib.backends.backend_tkagg import  cursors
import types
class XANESparam:
    def __init__(self, genitore, ini):
        global spectra
        self.genitore=genitore
       #--------------------------   Declare--------------------------------------------------
        self._Eop= StringVar()
        self._pr_es= StringVar()
        self._pr_ee= StringVar()
        self._po_es= StringVar()
        self._po_ee= StringVar()
        self._n_poly= StringVar()
        self.n_poly=3
       #--------------------------   Define--------------------------------------------------
        self.Eop,self.pr_es,self.pr_ee,self.po_es,self.po_ee,self.n_poly =ini
        self.num=0
        if ini==[0,0,0,0,0,3]:
            self._Eop.set("Ifeffit default")
            self._pr_es.set("start of the spectra")
            self._pr_ee.set(-50)
            self._po_es.set(150)
            self._po_ee.set("end of the spectra")
            self._n_poly.set(3)
        else:
            self._Eop.set(round(ini[0],2))
            self._pr_es.set(round(ini[1],2))
            self._pr_ee.set(round(ini[2],2))
            self._po_es.set(round(ini[3],2))
            self._po_ee.set(round(ini[4],2))
            self._n_poly.set(ini[5])            
       #--------------------------   Params  Entries--------------------------------------------------
        self.param_win = Frame(genitore)
        self.param_win.pack(side=LEFT)
       
        self.quadro_Eop = LabelFrame(self.param_win, text = "Eo")
        self.quadro_Eop.pack(side = TOP,  fill = X)
        self._entry_Eop= Entry(self.quadro_Eop, width = 20, textvariable=self._Eop)
        self._entry_Eop.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_pr_es = LabelFrame(self.param_win, text = "pre1")
        self.quadro_pr_es.pack(side = TOP,  fill = X)
        self._entry_pr_es= Entry(self.quadro_pr_es, width = 20, textvariable=self._pr_es)
        self._entry_pr_es.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_pr_ee = LabelFrame(self.param_win, text = "pre2")
        self.quadro_pr_ee.pack(side = TOP,  fill = X)
        self._entry_pr_ee= Entry(self.quadro_pr_ee, width = 20, textvariable=self._pr_ee)
        self._entry_pr_ee.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_po_es = LabelFrame(self.param_win, text = "Norm1")
        self.quadro_po_es.pack(side = TOP,  fill = X)
        self._entry_po_es= Entry(self.quadro_po_es, width = 20, textvariable=self._po_es)
        self._entry_po_es.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_po_ee = LabelFrame(self.param_win, text = "Norm2")
        self.quadro_po_ee.pack(side = TOP,  fill = X)
        self._entry_po_ee= Entry(self.quadro_po_ee, width = 20, textvariable=self._po_ee)
        self._entry_po_ee.pack(side = LEFT, padx = 5, ipady = 3, fill = X)
        
        self.quadro_n_poly = LabelFrame(self.param_win, text = "n_poly")
        self.quadro_n_poly.pack(side = TOP,  fill = X)
        self._entry_n_poly= Entry(self.quadro_n_poly, width = 20, textvariable=self._n_poly)
        self._entry_n_poly.pack(side = LEFT, padx = 5, ipady = 3, fill = X)        

        self.rerefresh = Button(self.param_win,
                                     command = self.refresh,#lambda x= self.num: self.refresh(x),
                                      text = "refresh graph",
                                      background = "violet",
                                      width = 20,
                                      padx = "3m",
                                      pady = "2m")
        self.rerefresh.pack(side = TOP, anchor = W, padx = 5, pady = 5)

        self.resave = Button(self.param_win,
                                      command = self.saveparam,
                                      text = "Save new paramerter",
                                      background = "green",
                                      width = 20,
                                      padx = "3m",
                                      pady = "2m")
        self.resave.pack(side = TOP, anchor = W, padx = 5, pady = 5)
        
       #--------------------------   Graphic win  --------------------------------------------------
        self.graphframe = Frame(genitore)        
        self.graphframe.pack(side = LEFT, fill=BOTH, expand=YES)
        self.grap_win=ut.ParamGraph(self.graphframe, spectra, "E", ["Mu", "pre_edge", "post_edge"])
        self.refresh()
        #self.onmoving = types.MethodType(self.onmoving, self.grap_win, ut.ParamGraph)
        #setattr(self.grap_win, "onmoving", self.onmoving)
        self.grap_win.canvas.mpl_disconnect(self.grap_win.mov_link)                                        # new pick release link
        self.grap_win.mov_link=self.grap_win.canvas.mpl_connect('motion_notify_event', self.onmoving)      # new pick release link
        self.grap_win.canvas.mpl_disconnect(self.grap_win.pick)                                            # new pick release link
        self.grap_win.pick=self.grap_win.canvas.mpl_connect('pick_event', self.onpick)                     # new pick release link
        self.grap_win.canvas.mpl_disconnect(self.grap_win.release)                                         # new pick release link
        self.grap_win.release=self.grap_win.canvas.mpl_connect('button_release_event', self.onrelease)
        self.press=False        
        self.grap_win.slider.configure(command= self.panor2)                                               # new pick release link
        genitore.wait_window()    
    
    def onpick(self,event_p):
        #print "ppppppppppppppppppppppp"
        if not(event_p.artist in self.grap_win.parmlines): 
            return True
        else:
            cursors.POINTER=0
            self.grap_win.param_num= self.grap_win.parmlines.index(event_p.artist)
            self.grap_win.mov_link=self.grap_win.canvas.mpl_connect('motion_notify_event', self.onmoving)
            self.press=True
            return True
        
    def onrelease(self,event_r):
        cursors.POINTER=1
        self.press=False
        #try:
        #self.grap_win.canvas.mpl_disconnect(self.grap_win.mov_link)
        #print "disconnect"
        #except: pass 
        
       #--------------------------   Function  -----------------------------------------------------        


    def onmoving(self, event):
        "when a parameter is move graphically"
        if not(self.press): return
        string_params= [self._pr_es,self._pr_ee,self._Eop, self._po_es, self._po_ee]
        #print "pippo" , self.grap_win.param_num
        if self.grap_win.param_num==2:
            string_params[2].set(round(event.xdata,2))
        else:
            if event.xdata==None:pass
            else:string_params[self.grap_win.param_num].set(round(event.xdata- spectra[self.num].Eo,2))
        self.panor2(self.num)
        
    def preposted(self):
        """ take parameter and perform calc"""
        try: self.saveparam(destroy=False)
        except:
            print "self.saveparam(destroy=False) fails"
            raise ValueError()        
            
        if spectra!=[]:
            spectra[self.num].XANES_Norm(self.Eop, self.pr_es, self.pr_ee, 
                                  self.po_es , self.po_ee, n_postpoly= self.n_poly)
            spectra[self.num].pre_edge= spectra[self.num].preedge_poly(spectra[self.num].E) 
            spectra[self.num].post_edge= spectra[self.num].postedge_poly(spectra[self.num].E)       
            
    def refresh(self):
        #"refresh picture when parameter are change in the textbox"
        try:
            self.grap_win.figsub.clear()
            self.preposted()
            self.grap_win.plot(self.num)
            self.grap_win.paramplot(self.get_param(), ["g"]*2+["k"]+["r"]*2,["pre1","pre2", "Eo", "norm1","norm2" ])
            self.panor2(self.num)
        except :
            self.grap_win.figsub.clear()
            dif =lambda x: numpy.argmax(numpy.gradient(x.Mu)/numpy.gradient(x.E))
            spectra[self.num].Eo=spectra[self.num].E[dif(spectra[self.num])]     # find the edge
            if min(spectra[self.num].E)> self.pr_ee+spectra[self.num].Eo:        # case in wich the two preedge are inverted
                self._pr_ee.set(-(spectra[self.num].Eo-min(spectra[self.num].E))/2)
                self.refresh()
                return
            if max(spectra[self.num].E)< self.po_es+spectra[self.num].Eo:        # case in wich the two post edge are inverted
                self._po_es.set((max(spectra[self.num].E)-spectra[self.num].Eo)/2)
                self.refresh()
                return    
            self.grap_win.plot(self.num)
            pippo=[min(spectra[self.num].E), self.pr_ee+spectra[self.num].Eo ,
                    spectra[self.num].Eo, spectra[self.num].Eo+self.po_es ,
                    max(spectra[self.num].E)]
            self.grap_win.paramplot(pippo, ["g"]*2+["k"]+["r"]*2, ["pre1","pre2", "Eo", "norm1","norm2"])    #
            print "\n---wrong initial parameter---\n"     
            
    def panor2(self,event):
        "when the slider is moved"
        self.num=int(event)
        try:
            self.preposted()
            self.grap_win.param=self.get_param()
            self.grap_win.panor(self.num)
        except: 
            print "still wrong"
            
            
    def get_param(self):
        spec= spectra[self.num]
        Eo= spec.Eo
        return      [spec.pr_es+Eo, spec.pr_ee+Eo , Eo, Eo+spec.po_es ,Eo+spec.po_ee]            
            
    
    def saveparam(self, destroy=True):
        ##########################################################################
        def error_message(Name,param,comp,string):
            if comp==string: param=0
            else: print "\nPlease write a numerical value for "+ Name +"\n" +  \
                             "for Ifeffit default write 0 or \""+string+"\" \n"
        ##########################################################################
        try:    self.Eop = float(eval(self._Eop.get()))
        except SyntaxError:error_message("E0", self.Eop ,                 \
                                         self._Eop.get(),"Ifeffit default")
        try:    self.pr_es = float(eval(self._pr_es.get()))
        except SyntaxError: error_message("pre edge start",self.pr_es,     \
                                          self._pr_es.get(),"start of the spectra")
        try:    self.pr_ee = float(eval(self._pr_ee.get()))
        except SyntaxError: error_message("pre edge end",self.pr_ee,      \
                                          self._pr_ee.get(),"0")
        try: self.po_es  = float(eval(self._po_es.get()))
        except SyntaxError: error_message("post edge start",self.po_es,   \
                                          self._po_es.get(),"0")
        try:  self.po_ee = float(eval(self._po_ee.get()))
        except SyntaxError: error_message("post edge end", self.po_ee,    \
                                          self._po_ee.get(),"end of the spectra")
        try:  self.n_poly = float(eval(self._n_poly.get()))
        except SyntaxError: error_message("polyn degree", self.n_poly,    \
                                          self._n_poly.get(),"3")
        if destroy:
            self.genitore.destroy()
            #self.param_win.destroy()
        













class DERIVparam_c:
    """
    class for calculation of numerical derivative
    """
    def __init__(self, genitore, ini):
        global spectra
      #--------------------------   Declare--------------------------------------------------
        self._smoot      = StringVar()
        self._interpolation = StringVar()
        self._smoot_repeat = StringVar()
      #--------------------------   Define--------------------------------------------------
        self.genitore=genitore
        self.num_der=1
        self.smoot,self.interpolation,self.smoot_repeat, self.lim1,self.lim2=ini
        self._smoot_repeat.set(self.smoot_repeat)
        self._smoot.set(self.smoot)
        if self.interpolation==0:self._interpolation.set("experimental sampling")             
        else:self._interpolation.set(self.interpolation)
      #--------------------------   Params  Entries--------------------------------------------------
        self.param_win_der = Frame(self.genitore)
        self.param_win_der.pack(side=LEFT)
        self.quadro_spin_smoot = LabelFrame(self.param_win_der, text = "smoot win int from 0 to ..")
        self.quadro_spin_smoot.pack(side = TOP,  fill = X)
        self.spin_smoot = Spinbox(self.quadro_spin_smoot, from_ = 0, to = 10,
                                 command= self.refresh_der, 
                                 textvariable= self._smoot,
                                 state= "readonly",
                                 width = 3)
        self.spin_smoot.pack(side = LEFT ,anchor = W, padx = 5, ipadx = 2, ipady = 3)
        
        self.quadro_spin_smootr = LabelFrame(self.param_win_der, text = "smoot rep. from 0 to ..")
        self.quadro_spin_smootr.pack(side = TOP,  fill = X)
        self.spin_smootr = Spinbox(self.quadro_spin_smootr, from_ = 0, to = 10,
                                 command= self.refresh_der, 
                                 textvariable= self._smoot_repeat,
                                 state= "readonly",
                                 width = 3)
        self.spin_smootr.pack(side = LEFT ,anchor = W, padx = 5, ipadx = 2, ipady = 3)        
        #self.spin_smoot = Entry(self.quadro_spin_smoot, 
        #                          textvariable= self._smoot,
        #                          width = 10)
        #self.spin_smoot.pack(side = LEFT ,anchor = W, padx = 5, ipadx = 2, ipady = 3)

        self.quadro_inter = LabelFrame(self.param_win_der, text = "interpolation")
        self.quadro_inter.pack(side = TOP,  fill = X)
        
        self._spin_inter= Spinbox(self.quadro_inter, from_ = 0.0, to = 1.0, increment=0.1,
                                command= self.refresh_der,
                                textvariable=self._interpolation,
                                state= "readonly",
                                width = 5)
        self._spin_inter.pack(side = LEFT, padx = 5, ipady = 3, fill = X, expand=Y)        
        
        
        #self._entry_inter= Entry(self.quadro_inter, width = 20, textvariable=self._interpolation)
        #self._entry_inter.pack(side = LEFT, padx = 5, ipady = 3, fill = X, expand=Y)
        Label(self.quadro_inter, text = "eV", justify = LEFT).pack(side = LEFT, anchor = W)

        self.topsave = Button(self.param_win_der,
                                      command = self.saveparam_deriv,
                                      text = "Save new paramerter",
                                      background = "green",
                                      width = 20,
                                      padx = "3m",
                                      pady = "2m")
        self.topsave.pack(side = TOP, anchor = W, padx = 5, pady = 5)
      #--------------------------   Graph --------------------------------------------------        
        self.graphframe_der = Frame(self.genitore)        
        self.graphframe_der.pack(side = LEFT, fill=BOTH)
        self.grap_win_der=ut.ParamGraph(self.graphframe_der, spectra, "x_int", ["deriv"])
        self.refresh_der()
        self.grap_win_der.slider.configure(command= self.panor2_der)
        
      #--------------------------   Graph -------------------------------------------------- 
        genitore.wait_window()   
      #--------------------------   functions --------------------------------------------------       
      
    def refresh_der(self):
        self.grap_win_der.figsub.clear()
        self.saveparam_deriv(destroy=False)
        self.calc()
        self.grap_win_der.plot(self.num_der)
        self.panor2_der(self.num_der)
      
    def calc(self):
        """calculate derivative and interpoolated x"""
        if spectra!=[]:
            spectra[self.num_der].bm29Num_der(window_len=self.smoot, step=self.interpolation,
                                              L1=self.lim1,L2=self.lim2, repeat=self.smoot_repeat)
            spectra[self.num_der].deriv=spectra[self.num_der].NumDer.deriv
            spectra[self.num_der].x_int=spectra[self.num_der].NumDer.x_int          
    
    def panor2_der(self,event):
        self.num_der=int(event)
        self.saveparam_deriv(destroy=False)
        self.calc()           
        self.grap_win_der.panor(self.num_der)

    def saveparam_deriv(self, destroy=True):
        ##########################################################################
        def error_message(Name,param,comp,string):
            if comp==string: param=0
            else: print "\nPlease write a numerical value for "+ Name +"\n" +  \
                             "for Ifeffit default write 0 or \""+string+"\" \n"
        ##########################################################################
        self.smoot = int(self._smoot.get())
        self.smoot_repeat=int(self._smoot_repeat.get())
        try:  self.interpolation = float(self._interpolation.get())          
        except ValueError: error_message("sampling", self._interpolation,     \
                              self._interpolation.get(),"experimental sampling")
        #else: raise SyntaxError("the value acepted are numerical or \"experimental sampling\"") 
        if destroy:
            self.genitore.destroy()





class DERIVparam_spline(DERIVparam_c):
    def __init__(self, genitore, ini):
        global spectra
      #--------------------------   Declare--------------------------------------------------
        self._smoot      = StringVar()
        self._interpolation = StringVar()
      #--------------------------   Define--------------------------------------------------
        self.genitore=genitore
        self.num_der=0
        self.smoot,self.interpolation, self.lim1,self.lim2=ini
        self._smoot.set(self.smoot)
        if self.interpolation==0:self._interpolation.set("experimental sampling")             
        else:self._interpolation.set(self.interpolation)
      #--------------------------   Params  Entries--------------------------------------------------
        self.param_win_der = Frame(self.genitore)
        self.param_win_der.pack(side=LEFT)
        self.quadro_spin_smoot = LabelFrame(self.param_win_der, text = "smoot float from 0 to 1%")
        self.quadro_spin_smoot.pack(side = TOP,  fill = X)
        self.spin_smoot = Entry(self.quadro_spin_smoot, 
                                  textvariable= self._smoot,
                                  width = 10)
        self.spin_smoot.pack(side = LEFT ,anchor = W, padx = 5, ipadx = 2, ipady = 3)

        self.quadro_inter = LabelFrame(self.param_win_der, text = "interpolation")
        self.quadro_inter.pack(side = TOP,  fill = X)
        
        self._spin_inter= Spinbox(self.quadro_inter, from_ = 0.0, to = 1.0, increment=0.1,
                                command= lambda x=self.num_der:  self.panor2_der(x),
                                textvariable=self._interpolation,
                                state= "readonly",
                                width = 5)
        self._spin_inter.pack(side = LEFT, padx = 5, ipady = 3, fill = X, expand=Y)        
        
        

        Label(self.quadro_inter, text = "eV", justify = LEFT).pack(side = LEFT, anchor = W)
        self.toprefr = Button(self.param_win_der,
                                      command = self.refresh_der,
                                      text = "refresh",
                                      background = "violet",
                                      width = 20,
                                      padx = "3m",
                                      pady = "2m")
        self.toprefr.pack(side = TOP, anchor = W, padx = 5, pady = 5)
        self.topsave = Button(self.param_win_der,
                                      command = self.saveparam_deriv,
                                      text = "Save new paramerter",
                                      background = "green",
                                      width = 20,
                                      padx = "3m",
                                      pady = "2m")
        self.topsave.pack(side = TOP, anchor = W, padx = 5, pady = 5)
      #--------------------------   Graph --------------------------------------------------        
        self.graphframe_der = Frame(self.genitore)        
        self.graphframe_der.pack(side = LEFT, fill=BOTH)
        self.grap_win_der=ut.ParamGraph(self.graphframe_der, spectra, "x_int", ["deriv"])
        self.refresh_der()
        self.grap_win_der.slider.configure(command= self.panor2_der)
        
      #--------------------------   Graph -------------------------------------------------- 
        genitore.wait_window()   
      #--------------------------   functions --------------------------------------------------       
      
      
    def calc(self):
        """calculate derivative and interpoolated x"""
        if self.interpolation !=0:
            self.x_deriv=numpy.arange(self.lim1,self.lim2,self.interpolation)
        else:    
            self.x_deriv=bt.dat_Truncate(spectra[0].E, self.lim1, self.lim2)            
        if spectra!=[]:
            spectra[self.num_der].bm29derE(sampling=self.x_deriv, L1=self.lim1,L2=self.lim2, s=self.smoot/100) 
            spectra[self.num_der].deriv=spectra[self.num_der].E_MuFp
            spectra[self.num_der].x_int=self.x_deriv          
    

    def saveparam_deriv(self, destroy=True):
        ##########################################################################
        def error_message(Name,param,comp,string):
            if comp==string: param=0
            else: print "\nPlease write a numerical value for "+ Name +"\n" +  \
                             "for Ifeffit default write 0 or \""+string+"\" \n"
        ##########################################################################
        self.smoot = float(self._smoot.get())
        try:  self.interpolation = float(self._interpolation.get())          
        except ValueError: error_message("sampling", self._interpolation,     \
                              self._interpolation.get(),"experimental sampling")
        #else: raise SyntaxError("the value acepted are numerical or \"experimental sampling\"") 
        if destroy:
            self.genitore.destroy()









#    
class XANES():
    def __init__(self, genitore):
      #--------------declare----------------------
        self._deriv_end   = StringVar()
        self._deriv_start = StringVar()
        self.smoot=0
        self.interpolation =0
        if num_deriv: 
            self.smoot_repeat=0
            self.smoot=1
        self._TCW_start = StringVar()
        self._TCW_end   = StringVar()
        self._INTxan_start = StringVar()
        self._INTxan_end   = StringVar()
        self._check_deriv=IntVar()
        self._check_xan = IntVar()
        self._check_TCW = IntVar()
        self._check_INT = IntVar()
        self._xflatten= IntVar()
        self._xpreedge= IntVar()
        self._xnormalization= IntVar()        
        self.Eop  =    0
        self.pr_es=    0
        self.pr_ee=    0
        self.po_es=    0
        self.po_ee=    0
        self.n_poly =  3
        #--------------set---------------------------------
        self._xflatten.set(1)
        self._xpreedge.set(1)
        self._xnormalization.set(1)       
        self._check_xan.set(1)   
        self._check_deriv.set(1)         


        #------------------------------------------------------
      #----------------Quadro Derivative-------------------------------------
        self.quadro_derivative = LabelFrame(genitore, text = "XANES Derivative")    #,text = "Correction"
        self.quadro_derivative.pack(side = TOP,  fill = X, pady= 3, ipadx = 5, ipady = 3)

        self.derivfrom = LabelFrame(self.quadro_derivative, text = "from")
        self.derivfrom.pack(side = LEFT,  fill = X, ipady=2, anchor = W, padx=2, expand =Y)
        self._entry_derivfrom= Entry(self.derivfrom, width = 7, textvariable=self._deriv_start)
        self._entry_derivfrom.pack(side = LEFT, padx = 5, ipady = 3, fill = X, expand = YES)
        Label(self.derivfrom, text = "eV", justify = LEFT).pack(side = LEFT, anchor = W)
        self.derivto = LabelFrame(self.quadro_derivative, text = "to ")
        self.derivto.pack(side = LEFT,  fill = X, ipady=2, anchor = W, padx=2, expand =Y) #, expand = YES
        self._entry_derivto= Entry(self.derivto, width = 7, textvariable=self._deriv_end)
        self._entry_derivto.pack(side = LEFT, padx = 5, ipady = 3, fill = X, expand = YES)
        Label(self.derivto, text = "eV", justify = LEFT).pack(side = LEFT, anchor = W)
        #Frame(self.quadro_derivative).pack(side = LEFT,expand =Y)
        self.button_derivative_default = Button(self.quadro_derivative,
                                      command = self.DERIVparam,
                                      text = "smoot&interp",
                                      background = "violet",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m")
        self.button_derivative_default.pack(side = LEFT, anchor = W, padx = 5, pady = 5)
        self.derivate_PlSa_But=ut.PloteSaveB(self.quadro_derivative, [],
                                                             [],
                                                             ext="Der" ,comment= None, title="DERIVATIVE")

      #----------------Quadro Max Derivative-------------------------------------
        self.quadro_Max_Derivative = Frame(genitore)    #,text = "Correction"
        self.quadro_Max_Derivative.pack(side = TOP,  fill = X)
        self.quadro_Max_Derivative1 = LabelFrame(self.quadro_Max_Derivative, text = "Derivate Max")    #,text = "Correctio
        self.quadro_Max_Derivative1.pack(side = LEFT,  fill = X, expand =Y)
        self.quadro_Max_Derivative2 = Frame(self.quadro_Max_Derivative1)
        self.quadro_Max_Derivative2.pack(side = LEFT, anchor = W, fill=X, expand =Y)
        self.Max_PlSa_But=ut.PloteSaveB(self.quadro_Max_Derivative2, [x], [],
                                                        ext=None ,comment= None, title="Iff Eo")
      #----------------QuadroXan-------------------------------------
        self.quadro_xanes = LabelFrame(genitore, text = "XANES Normalization")    #,text = "Correction"
        self.quadro_xanes.pack(side = TOP,  fill = X, pady= 3, ipadx = 5, ipady = 3)
        Checkbutton(self.quadro_xanes, text="Pre_edge" ,variable=self._xpreedge ).pack(
                  side = LEFT, expand = YES,  fill = BOTH ,anchor = N,ipadx = 1, ipady = 1)
        Checkbutton(self.quadro_xanes, text="Norm." ,variable=self._xnormalization ).pack(
                      side = LEFT, expand = YES,  fill = BOTH ,anchor = N,ipadx = 1, ipady = 1)   
        self.check_flat=Checkbutton(self.quadro_xanes, text="Flatten" ,variable=self._xflatten )
        self.check_flat.pack(side = LEFT, expand = YES,  fill = BOTH ,anchor = N,ipadx = 1, ipady = 1)
     
        self.button_xanes_default = Button(self.quadro_xanes,
                                      command = self.XANESparam,
                                      text = "XANES param.",
                                      background = "violet",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m")
        self.button_xanes_default.pack(side = LEFT, anchor = W, padx = 5, pady = 5)
        #ATTENZIONE
        self.Xanes_PlSa_But=ut.PloteSaveB(self.quadro_xanes, [],
                                                             [],
                                                             ext="Nor" ,comment= None, title="XANES")
      #--------------------------------------iffeffit---------------------------------------------------
        self.quadro_Iffefit = Frame(genitore)    #,text = "Correction"
        self.quadro_Iffefit.pack(side = TOP,  fill = X)
        self.quadro_Eo = LabelFrame(self.quadro_Iffefit, text = "Ifeffit() Eo")    #,text = "Correction"
        self.quadro_Eo.pack(side = LEFT,  fill = X, expand =Y)
        self.quadro_Eo1 = Frame(self.quadro_Eo)
        self.quadro_Eo1.pack(side = LEFT, anchor = W, fill=X, expand =Y)
        #ATTENZIONE
        self.Eo_PlSa_But=ut.PloteSaveB(self.quadro_Eo1, [], [],
                                                        ext=None ,comment= None, title="Iff Eo")
        self.quadro_Ej = LabelFrame(self.quadro_Iffefit, text = "Ifeffit() Ej")    #,text = "Correction"
        self.quadro_Ej.pack(side = LEFT,  fill = X, expand =Y)
        self.quadro_Ej1 = Frame(self.quadro_Ej)
        self.quadro_Ej1.pack(side = LEFT, anchor = W, fill=X, expand =Y)
        self.Ej_PlSa_But=ut.PloteSaveB(self.quadro_Ej, [], [],
                                                       ext=None ,comment= None, title="Iff Ej")
      #----------------------------------------TC Weng Eo---------------------------------------------
        self.quadro_TCWxan = LabelFrame(genitore, text = "TC Weng Eo")    #,text = "Correction"
        self.quadro_TCWxan.pack(side = TOP,  fill = X, pady= 3, ipadx = 6, ipady = 3)
        self.TCWfrom = LabelFrame(self.quadro_TCWxan, text = "from")
        self.TCWfrom.pack(side = LEFT, expand = YES, fill = BOTH, anchor = W, ipady = 5)
        self._entry_TCWfrom= Entry(self.TCWfrom, width = 7, textvariable=self._TCW_start)
        self._entry_TCWfrom.pack(side = LEFT, padx = 5, ipady = 3, fill = X, expand = YES)
        Label(self.TCWfrom, text = "eV    ", justify = LEFT).pack(side = LEFT, anchor = W)
        self.TCWto = LabelFrame(self.quadro_TCWxan, text = "to ")
        self.TCWto.pack(side = LEFT, expand = YES, fill = BOTH, anchor = W, ipady = 5) #, expand = YES
        self._entry_TCWto= Entry(self.TCWto, width = 7, textvariable=self._TCW_end)
        self._entry_TCWto.pack(side = LEFT, padx = 5, ipady = 3, fill = X, expand = YES)
        Label(self.TCWto, text = "eV    ", justify = LEFT).pack(side = LEFT, anchor = W)
        self.TCWxan_PlSa_But=ut.PloteSaveB(self.quadro_TCWxan, [x], [],
                                                                ext=None ,comment= None, title="TCW")
      #------------------------------------Integralof Nor. XANES
        self.quadro_INTxan = LabelFrame(genitore, text = "Integralof Nor. XANES")    #,text = "Correction"
        self.quadro_INTxan.pack(side = TOP,  fill = X, pady= 3, ipadx = 5, ipady = 3)
        self.INTfrom = LabelFrame(self.quadro_INTxan, text = "from")
        self.INTfrom.pack(side = LEFT, expand = YES, fill = BOTH, anchor = W, ipady = 5)
        self._entry_INTfrom= Entry(self.INTfrom, width = 7, textvariable=self._INTxan_start)
        self._entry_INTfrom.pack(side = LEFT, padx = 5, ipady = 3, fill = X, expand = YES)
        Label(self.INTfrom, text = "eV    ", justify = LEFT).pack(side = LEFT, anchor = W)
        self.INTto = LabelFrame(self.quadro_INTxan, text = "to ")
        self.INTto.pack(side = LEFT, expand = YES, fill = BOTH, anchor = W, ipady = 5) #, expand = YES
        self._entry_INTto= Entry(self.INTto, width = 7, textvariable=self._INTxan_end)
        self._entry_INTto.pack(side = LEFT, padx = 5, ipady = 3, fill = X, expand = YES)
        Label(self.INTto, text = "eV    ", justify = LEFT).pack(side = LEFT, anchor = W)
        self.quadro_INTxan2 = Frame(self.quadro_INTxan)
        self.quadro_INTxan2.pack(side = TOP, fill = X)
        self.INTxan_PlSa_But=ut.PloteSaveB(self.quadro_INTxan, [x], [],
                                            ext=None ,comment= None, title="Integral")
      #--------------------------------------Perform---------------------------------------------------
        self.quadro_perform = LabelFrame(genitore)    #,text = "Correction"
        self.quadro_perform.pack(side = BOTTOM,  fill = X, expand =YES)
        self.button_xan_per = Button(self.quadro_perform,
                                      command = self.Perform,
                                      text = "Perform" ,
                                      background = "green",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m")
        self.button_xan_per.pack(side = LEFT, anchor = W, padx = 5, pady = 5)
        self.check_deriv=Checkbutton(self.quadro_perform, text="Derivative" ,variable=self._check_deriv )
        self.check_deriv.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 5)
        self.check_xan=Checkbutton(self.quadro_perform, text="XanNorm" ,variable=self._check_xan )
        self.check_xan.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 5)
        self.check_TCW=Checkbutton(self.quadro_perform, text="TCW_Eo"    ,variable=self._check_TCW)#, state= DISABLED)
        self.check_TCW.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 5)
        self.check_INT=Checkbutton(self.quadro_perform, text="Xan_Int" ,variable=self._check_INT )
        self.check_INT.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 5)
      #---------------------------------Function----------------------------------------
    def XANESparam(self):
        if hasattr(self, "topX"): return
        ini=[self.Eop,self.pr_es,self.pr_ee,self.po_es,self.po_ee,self.n_poly]
        self.topX = Toplevel()
        self.topX.title("XANES PARAMETER") 
        self.XAN_par=XANESparam(self.topX,ini)
        self.pr_es, self.pr_ee, self.Eop, self.po_es, self.po_ee = self.XAN_par.get_param()
        self.pr_es, self.pr_ee= self.pr_es-self.Eop, self.pr_ee-self.Eop
        self.po_es, self.po_ee=self.po_es-self.Eop, self.po_ee-self.Eop
        self.n_poly =self.XAN_par.n_poly
        del self.XAN_par
        del self.topX


    def DERIVparam(self):
        if hasattr(self, "top_der"): 
            print hasattr(self, "top_der"),"\n"
            return
        self.top_der = Toplevel()
        self.top_der.title("smoot and interpolation parameter") 
        if num_deriv:
            ini=[self.smoot,self.interpolation ,self.smoot_repeat ,float(self._deriv_start.get()),float(self._deriv_end.get())]
            self.Der_param=DERIVparam_c(self.top_der,ini)
            self.smoot,self.interpolation,self.smoot_repeat=self.Der_param.smoot ,self.Der_param.interpolation,self.Der_param.smoot_repeat
        else:
            ini=[self.smoot,self.interpolation ,float(self._deriv_start.get()),float(self._deriv_end.get())]
            self.Der_param=DERIVparam_spline(self.top_der,ini)
            self.smoot,self.interpolation=self.Der_param.smoot ,self.Der_param.interpolation            
        del self.Der_param
        del self.top_der
        
        
    def Perform(self):                     
        if self._check_deriv.get():  
            print "\n ---Derivative Calculation---" , num_deriv
            if num_deriv:    
                for item in spectra:
                    if __verbose__: print "Xanes derivative"
                    item.bm29Num_der(window_len=self.smoot, step=self.interpolation,
                                     L1=float(self._deriv_start.get()),L2=float(self._deriv_end.get()),repeat=self.smoot_repeat)
                self.derivate_PlSa_But.x_array= [item.NumDer.x_int for item in spectra]
                self.derivate_PlSa_But.y_array= [item.NumDer.deriv for item in spectra]
                self.derivate_PlSa_But.comments= [item.comments[:-1] for item in spectra]
            else:    
                if self.interpolation !=0:
                    self.x_deriv=numpy.arange(float(self._deriv_start.get()), \
                                           float(self._deriv_end.get()),  \
                                           self.interpolation)
                else:
                    self.x_deriv=bt.dat_Truncate(spectra[0].E, \
                                                   float(self._deriv_start.get()), \
                                                   float(self._deriv_end.get()))
                for item in spectra:
                    if __verbose__: print "Xanes derivative"
                    item.bm29derE(sampling=self.x_deriv, L1=float(self._deriv_start.get()),\
                                  L2=float(self._deriv_end.get()), s=self.smoot/100) 
                self.derivate_PlSa_But.x_array= [self.x_deriv for item in spectra]
                self.derivate_PlSa_But.y_array= [item.E_MuFp for item in spectra]
                self.derivate_PlSa_But.comments= [item.comments[:-1] for item in spectra]                    
                    
            for item in self.Xanes_PlSa_But.comments: 
                c1 ="# Derivative calc. between "+ self._deriv_start.get()+" and "+ self._deriv_end.get()+"\n"
                item.append(c1)
                if num_deriv:
                    c1 = "# Num. derivative calc.  with smoot= %1.8f ,interpolation= %1.4f, repeated444= %2d\n" %(
                                                self.smoot, self.interpolation ,self.smoot_repeat)
                else:
                    c1 = "# Spl derivative  calc.  with smoot= %1.8f ,interpolation= %1.4f\n" %(
                                                self.smoot, self.interpolation)
                item.append(c1)
                item.append("#L E  Derivate_smot"+str(self.smoot)+"\n")    
            #-----------------Max derivate  ---------------------             
            self.Max_PlSa_But.x_array= [x]
            self.Max_PlSa_But.comments=[]                                 
            self.Max_PlSa_But.comments.append(spectra[0].comments[:-3])
            c1 ="# Max derivative calc. between "+ self._deriv_start.get()+" and "+ self._deriv_end.get()+"\n"
            self.Max_PlSa_But.comments[0].append(c1)
            if num_deriv: 
                c1 = "# Max derivative calc.  with smoot= %1.8f ,interpolation= %1.4f, repeated= %1.4f\n" %(
                                                self.smoot, self.interpolation,self.smoot_repeat)
            self.Max_PlSa_But.comments[0].append(c1)
            self.Max_PlSa_But.comments[0].append(spectra[0].comments[-3])
            self.Max_PlSa_But.comments[0].append(spectra[0].comments[-2])
            self.Max_PlSa_But.comments[0].append( "#L  "+ xlabel+ "   Derivate_Max\n")
            for item in spectra:
                self.Max_PlSa_But.y_array= [[item.NumDer.x_int[numpy.argmax(item.NumDer.deriv)] for item in spectra]]        
        if self._check_xan.get():
            print "\n ---XANES Normalization---"            
            for item in spectra:
                if __verbose__: print "Xanes norm"
                item.XANES_Norm(self.Eop, self.pr_es, self.pr_ee, self.po_es , self.po_ee,
                                self._xflatten.get(), n_postpoly= self.n_poly,
                                operation={"p":self._xpreedge.get(),"n":self._xnormalization.get()})
                if __verbose__: print "Xanes norm done"
            #self._check_xan.set(0)
            self._deriv_start.set(round(spectra[0].Eo -50, 2))
            self._deriv_end.set(round(spectra[0].Eo +80, 2))            
            self._TCW_start.set(round(spectra[0].Eo -50, 2))
            self._TCW_end.set(round(spectra[0].Eo +80, 2))
            self._INTxan_start.set(round(spectra[0].Eo -50, 2))
            self._INTxan_end.set(round(spectra[0].Eo +80, 2))
            #self.check_INT.configure(state = ACTIVE)
            #self.check_TCW.configure(state = ACTIVE)
            self.Xanes_PlSa_But.x_array= [item.E for item in spectra]
            self.Xanes_PlSa_But.y_array= [item.Nor for item in spectra]
            self.Xanes_PlSa_But.comments= [item.comments[:-1] for item in spectra]
            for item in self.Xanes_PlSa_But.comments: item.append("#L E  Nor\n")
            #-----------------iff e0---------------------
            self.Eo_PlSa_But.x_array= [x]
            self.Eo_PlSa_But.comments=[]
            self.Eo_PlSa_But.comments.append(spectra[0].comments[:-3])
            c1 ="# Eo Ifeffit calc. with E0= "+ str(self.Eop)+",pre1= "+ str(self.pr_es) +", pre2= "+str(self.pr_ee)+"\n"
            self.Eo_PlSa_But.comments[0].append(c1)
            c1 = "# Eo Ifeffit calc. with norm1= "+str(self.po_es)+",norm2= "+str(self.po_ee)+", flatted= "+str(self._xflatten.get() and True or False)
            self.Eo_PlSa_But.comments[0].append(c1)
            self.Eo_PlSa_But.comments[0].append(spectra[0].comments[-3])
            self.Eo_PlSa_But.comments[0].append(spectra[0].comments[-2])
            self.Eo_PlSa_But.comments[0].append( "#L  "+ xlabel+ "  iff_Eo\n")
            self.Eo_PlSa_But.y_array= [[item.Eo for item in spectra]]        
            #-----------------iff ej---------------------
            self.Ej_PlSa_But.x_array= [x]
            self.Ej_PlSa_But.comments=[]
            self.Ej_PlSa_But.comments.append(spectra[0].comments[:-3])
            c1 ="# Eo Ifeffit calc. with E0= "+ str(self.Eop)+",pre1= "+ str(self.pr_es) +", pre2= "+str(self.pr_ee)+"\n"
            self.Ej_PlSa_But.comments[0].append(c1)
            c1 = "# Eo Ifeffit calc. with norm1= "+str(self.po_es)+",norm2= "+str(self.po_ee)+", flatted= "+str(self._xflatten.get() and True or False)
            self.Ej_PlSa_But.comments[0].append(c1)              
            self.Eo_PlSa_But.comments[0].append(spectra[0].comments[-3])
            self.Eo_PlSa_But.comments[0].append(spectra[0].comments[-2])
            self.Eo_PlSa_But.comments[0].append( "#L  "+ xlabel+ "  iff_Ej\n")
            self.Ej_PlSa_But.y_array= [[item.Ej for item in spectra]]
            #-----------------Eo TCW---------------------
        if self._check_TCW.get():
            self.TCWxan_PlSa_But.x_array= [x]
            self.TCWxan_PlSa_But.comments=[]
            self.TCWxan_PlSa_But.comments.append(spectra[0].comments[:-3])
            self.TCWxan_PlSa_But.comments[0].append( "# TCW Eo clculated with parameter %s , %s%s"
                                                      %(str(self._TCW_start.get()), str(self._TCW_end.get()),"\n"))
            self.TCWxan_PlSa_But.comments[0].append(spectra[0].comments[-3])
            self.TCWxan_PlSa_But.comments[0].append(spectra[0].comments[-2])
            self.TCWxan_PlSa_But.comments[0].append( "#L  "+ xlabel+ "  TCW_Eo\n")
            for item in spectra:
                item.TCW_Eo= float(self._TCW_end.get()) -item.bm29int_Nor(float(eval(self._TCW_start.get())), float(eval(self._TCW_end.get())))
            self.TCWxan_PlSa_But.y_array= [[item.TCW_Eo for item in spectra]]
        if self._check_INT.get():
            self.INTxan_PlSa_But.x_array= [x]
            self.INTxan_PlSa_But.comments=[]
            self.INTxan_PlSa_But.comments.append(spectra[0].comments[:-3])
            self.INTxan_PlSa_But.comments[0].append( "# Int Eo clculated with parameter %s , %s%s"
                                                   %(str(self._INTxan_start.get()), str(self._INTxan_end.get()),"\n"))
            self.INTxan_PlSa_But.comments[0].append(spectra[0].comments[-3])
            self.INTxan_PlSa_But.comments[0].append(spectra[0].comments[-2])
            self.INTxan_PlSa_But.comments[0].append( "#L  "+ xlabel+ "  Int\n")
            for item in spectra:
                item.INTxan= item.bm29int_Nor(float(eval(self._INTxan_start.get())), float(eval(self._INTxan_end.get())))
            self.INTxan_PlSa_But.y_array= [[item.INTxan for item in spectra]]
        print "\n---module XANES done\n"    






####################################   EXAFS/FT #########################################################
class EXAFT():
    def __init__(self, genitore):
      #-------------------------------    declare    ----------------------------------------------

        self._Eop  = StringVar()
        self._rbkg = StringVar()
        self._skmin = StringVar()
        self._skmax = StringVar()
        self._pr_es= StringVar()
        self._pr_ee= StringVar()
        self._po_es= StringVar()
        self._po_ee= StringVar()
        self._check_FT    = IntVar()
        self._check_exa   = IntVar()
        self.kweigth      = IntVar()
        self.kweigthplot  = IntVar()
        self._rstart      = StringVar()
        self._kstart      = StringVar()
        self._kend        = StringVar()
        self.FTweigth     = IntVar()
        self._FTWind      = StringVar()
        self._dk          = StringVar()
        packLabelFrame = {"side" : LEFT,  "expand" : YES, "anchor" : W, "pady" : 3}
        packEntry      = {"side" : LEFT,   "anchor" : W, "pady" : 6, "padx" : 3, "fill" : X }   # "expand" : YES,
      #---------------------------------  set      ------------------------------------------

        self._check_exa.set(1)
        self._Eop.set("Ifeffit default")
        self._rbkg.set(1)
        self._skmin.set("Ifeffit default")
        self._skmax.set("Ifeffit default")
        self._dk.set(.2)
        self._kstart.set(3)
        self._kend.set(16)
        self._pr_es.set("start of the spectra")
        self._pr_ee.set(-50)
        self._po_es.set(150)
        self._po_ee.set("end of the spectra")
        self.kweigth.set(2)
        self.kweigthplot.set(1)
        self.FTweigth.set(3)
        self._FTWind.set('kaiser-bessel')
        #---------------------------------  set      ------------------------------------------

        self.Eop  =    0
        self.rbkg =    0
        self.pr_es=    0
        self.pr_ee=    0
        self.po_es=    0
        self.po_ee=    0
        self.skmax=    0
        self.skmin=    0
      #--------------------------------EXAFS--------------------------------------------------------
        self.quadro_exafs = LabelFrame(genitore, text = "EXAFS extraction")    #,text = "Correction"
        self.quadro_exafs.pack(side = TOP,  fill = X, pady= 3, ipadx = 5, ipady = 3)
        self.quadro_exafs1 = Frame(self.quadro_exafs)    #,text = "Correction"
        self.quadro_exafs1.pack(side = TOP,  fill = X, pady=5)
        self.quadro_rbkg = LabelFrame(self.quadro_exafs1, text = "rbkg")
        self.quadro_rbkg.pack(side = LEFT,  fill = X, ipady=2, anchor = W, padx=2)
        self._entry_rbkg= Entry(self.quadro_rbkg, width = 5, textvariable=self._rbkg)
        self._entry_rbkg.pack(side = LEFT, padx = 5, ipady = 3, fill = X)
        self.quadro_spin_kweigth = LabelFrame(self.quadro_exafs1, text = "k_weight extraction")
        self.quadro_spin_kweigth.pack(side = LEFT,  fill = X, ipady=2, anchor = W, padx=2)
        self.spin_kweigth = Spinbox(self.quadro_spin_kweigth, from_ = 0, to = 3, textvariable= self.kweigth, width = 5)
        self.spin_kweigth.pack(side = LEFT ,anchor = W, padx = 5, ipadx = 1, ipady = 3) #, expand = YES,  fill = BOTH
        #Label(self.quadro_exafs1, text = "k_weigth", justify = LEFT).pack(side = LEFT, anchor = W, expand =Y)
        self.button_exafs_default = Button(self.quadro_exafs1,
                                        command = self.EXAFSparam,
                                        text = "EXAFS param.",
                                        background = "violet",
                                        width = 10,
                                        padx = "3m",
                                        pady = "2m")
        self.button_exafs_default.pack(side = LEFT, anchor = W, padx = 5, pady = 2)
        self.quadro_exafs2 = Frame(self.quadro_exafs)    #,text = "Correction"
        self.quadro_exafs2.pack(side = TOP,  fill = BOTH, pady=2,expand= YES,)
        self.quadro_EXA_bkg = LabelFrame(self.quadro_exafs2, text = "EXA_bkg")
        self.quadro_EXA_bkg.pack(fill= X, **packLabelFrame)
        self.quadro_EXA_chi= LabelFrame(self.quadro_exafs2, text = "EXAFS signal k")
        self.quadro_EXA_chi.pack(fill= X, **packLabelFrame)
        self.spin_kweigthplot = Spinbox(self.quadro_EXA_chi, from_ = 0, to = 3,
            textvariable= self.kweigthplot, width = 1, command= self.kwrefresh)
        self.spin_kweigthplot.pack(side =LEFT, ipady =3)
        self.bkg_PlSa_But=ut.PloteSaveB(self.quadro_EXA_bkg, ext=".chi" ,comment= None, title="background")
        self.bkg_PlSa_But.Button_plot.configure(command = self.plot2)
        self.exa_PlSa_But=ut.PloteSaveB(self.quadro_EXA_chi, ext=".bkg" ,comment= None, title="Exafs")

      #-------------------------------------FT------------------------------------------------------------------------
        self.quadro_FT = LabelFrame(genitore, text = "Foward FT")    #,text = "Correction"
        self.quadro_FT.pack(side = TOP,  fill = X, pady= 3, ipadx = 5, ipady = 3)
        self.quadro_FT1 = Frame(self.quadro_FT)
        self.quadro_FT1.pack(side = TOP,  fill = X)
        self.quadro_FTweigth = LabelFrame(self.quadro_FT1, text = "FT_weight")
        self.quadro_FTweigth.pack(**packLabelFrame)
        self.spin_FTweigth = Spinbox(self.quadro_FTweigth, from_ = 0, to = 3, textvariable= self.FTweigth, width = 3)
        self.spin_FTweigth.pack(side = LEFT ,anchor = S, pady=5, padx = 5, ipadx = 1) #,  fill = BOTH
        #Label(self.quadro_FT1, text = "FT_weigth", justify = LEFT).pack(side = LEFT, anchor = S, pady=10)
        self.quadro_FTwin = LabelFrame(self.quadro_FT1, text = "FT_win")
        self.quadro_FTwin.pack(**packLabelFrame)
        self.combo_FTw= ttk.Combobox(self.quadro_FTwin , state="readonly",   textvariable=self._FTWind,
                     values=('kaiser-bessel', 'hanning', 'welch', 'sine'))
        self.combo_FTw.pack(side = LEFT ,anchor = S, pady=5, padx = 5, ipadx = 1)
        self.quadro_FT_lim = LabelFrame(self.quadro_FT1, text = "k Range Limits")
        self.quadro_FT_lim.pack(**packLabelFrame)
        self._entry_FT_kstart= Entry(self.quadro_FT_lim, width = 7, textvariable=self._kstart)
        self._entry_FT_kstart.pack(**packEntry)
        self._entry_FT_kend= Entry(self.quadro_FT_lim, width = 7, textvariable=self._kend)
        self._entry_FT_kend.pack(**packEntry)
        self.quadro_FT_dk = LabelFrame(self.quadro_FT1, text = "dk")
        self.quadro_FT_dk.pack(**packLabelFrame)
        self._entry_FT_dk= Entry(self.quadro_FT_dk, width = 7, textvariable=self._dk)
        self._entry_FT_dk.pack(**packEntry)
        self.quadro_FT2 = Frame(self.quadro_FT)
        self.quadro_FT2.pack(side = TOP,  fill = BOTH, expand= YES,)
        self.quadro_FTMg = LabelFrame(self.quadro_FT2, text = "FT Mag.")
        self.quadro_FTMg.pack(fill= X, **packLabelFrame)
        self.quadro_FTIm = LabelFrame(self.quadro_FT2, text = "FT Im.")
        self.quadro_FTIm.pack(fill= X, **packLabelFrame)
        self.FTMg_PlSa_But=ut.PloteSaveB(self.quadro_FTMg, ext=".ftmg" ,comment= None, title="FT Mag")
        self.FTIm_PlSa_But=ut.PloteSaveB(self.quadro_FTIm, ext=".ftim" ,comment= None, title="FT Im")
      #--------------------------------------Perform----------------------------------------------------
        self.quadro_perform = LabelFrame(genitore)    #,text = "Correction"
        self.quadro_perform.pack(side = BOTTOM,  fill = X, expand =YES)
        self.button_exa_per = Button(self.quadro_perform, #
                                      command = self.Perform,
                                      text = "Perform" ,
                                      background = "green",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m")
        self.button_exa_per.pack(side = LEFT, anchor = W, padx = 5, pady = 5)
        self.check_exa=Checkbutton(self.quadro_perform, text="EXAFS" ,variable=self._check_exa )
        self.check_exa.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 5)
        self.check_FT=Checkbutton(self.quadro_perform, text="FT"    ,variable=self._check_FT)
        self.check_FT.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 5)
      #---------------------------------Function--------------------------------------------------------
    def kwrefresh(self):
        w = self.kweigthplot.get()
        c1="#L k  chik**"+ str(w)+"\n"
        for item in self.exa_PlSa_But.comments: item.pop(); item.append(c1)
        self.exa_PlSa_But.title = "EXAFS chi*k**"+str(w)
        self.exa_PlSa_But.y_array= [item.chi*item.k**w for item in spectra]

    def plot2(self):
        self.bkg_PlSa_But.plot()
        self.bkg_PlSa_But.graph.clear()
        self.bkg_PlSa_But.graph.plot([i.E   for i in spectra],
                                           [i.Mu  for i in spectra])
        self.bkg_PlSa_But.graph.plot( self.bkg_PlSa_But.x_array,
                                        self.bkg_PlSa_But.y_array)

    def Perform(self):
        self._check_exa.get()
        self._check_FT.get()
        #-----------------         EXAFS      ---------------------
        if self._check_exa.get():
            w = self.kweigthplot.get()
            for item in spectra:
                ceck=item.EXAFS_EX( self.Eop, self.rbkg, self.skmin, self.skmax, self.kweigth.get(),
                               0.2,  self._FTWind.get(), self.pr_es, self.pr_ee,
                               self.po_es , self.po_ee)
            self.exa_PlSa_But.x_array= [item.k for item in spectra]
            self.exa_PlSa_But.y_array= [item.chi*item.k**w for item in spectra]
            self.exa_PlSa_But.comments= [item.comments[:-1] for item in spectra]
            self.exa_PlSa_But.title = "EXAFS chi*k**"+str(w)
            c1="#L k  chik**"+ str(self.kweigthplot.get())+"\n"
            for item in self.exa_PlSa_But.comments: item.append(c1)
            self.bkg_PlSa_But.x_array= [item.E for item in spectra]
            self.bkg_PlSa_But.y_array= [item.bkg for item in spectra]
            self.bkg_PlSa_But.comments= [item.comments[:-1] for item in spectra]
            for item in self.bkg_PlSa_But.comments: item.append("#L E  bkg\n")
        #-----------------         FT      ---------------------
        if self._check_FT.get():
            w = self.FTweigth.get()
            k_min=float(eval(self._kstart.get()))
            k_max=float(eval(self._kend.get()))
            _dk  =float(eval(self._dk.get()))
            for item in spectra:
                item.FT_F( k_min , 0 ,k_max, _dk, self.FTweigth.get(), self._FTWind.get())
            self.FTMg_PlSa_But.x_array= [item.r for item in spectra]
            self.FTMg_PlSa_But.y_array= [item.mag for item in spectra]
            self.FTMg_PlSa_But.comments= [item.comments[:-1] for item in spectra]
            self.FTMg_PlSa_But.title = "FT chi*k**"+str(w)
            c1="#L R  FT_Mg"+str(self.FTweigth.get())+"\n"
            for item in self.exa_PlSa_But.comments: item.append(c1)
            self.FTMg_PlSa_But.title = "FT chi*k**"+str(w)
            c1= "#L R  FT_Im*k**"+str(self.FTweigth.get())+"\n"
            for item in self.FTMg_PlSa_But.comments: item.append(c1)
            self.FTIm_PlSa_But.x_array= [item.r for item in spectra]
            self.FTIm_PlSa_But.y_array= [item.imag for item in spectra]
            self.FTIm_PlSa_But.comments= [item.comments[:-1] for item in spectra]
            c1="#L R  FT_Im"+str(self.FTweigth.get())+"\n"
            for item in self.FTIm_PlSa_But.comments: item.append(c1)
        return

    def EXAFSparam(self):
        self.param_win = Toplevel()
        self.param_win.title("EXAFS PARAMETER")

        self.quadro_Eop = LabelFrame(self.param_win, text = "Eo")
        self.quadro_Eop.pack(side = TOP,  fill = X)
        self._entry_Eop= Entry(self.quadro_Eop, width = 20, textvariable=self._Eop)
        self._entry_Eop.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_skmin = LabelFrame(self.param_win, text = "skmin")
        self.quadro_skmin.pack(side = TOP,  fill = X)
        self._entry_skmin= Entry(self.quadro_skmin, width = 20, textvariable=self._skmin)
        self._entry_skmin.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_skmax = LabelFrame(self.param_win, text = "skmax")
        self.quadro_skmax.pack(side = TOP,  fill = X)
        self._entry_skmax= Entry(self.quadro_skmax, width = 20, textvariable=self._skmax)
        self._entry_skmax.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_pr_es = LabelFrame(self.param_win, text = "pre1")
        self.quadro_pr_es.pack(side = TOP,  fill = X)
        self._entry_pr_es= Entry(self.quadro_pr_es, width = 20, textvariable=self._pr_es)
        self._entry_pr_es.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_pr_ee = LabelFrame(self.param_win, text = "pre2")
        self.quadro_pr_ee.pack(side = TOP,  fill = X)
        self._entry_pr_ee= Entry(self.quadro_pr_ee, width = 20, textvariable=self._pr_ee)
        self._entry_pr_ee.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_po_es = LabelFrame(self.param_win, text = "Norm1")
        self.quadro_po_es.pack(side = TOP,  fill = X)
        self._entry_po_es= Entry(self.quadro_po_es, width = 20, textvariable=self._po_es)
        self._entry_po_es.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_po_ee = LabelFrame(self.param_win, text = "Norm1")
        self.quadro_po_ee.pack(side = TOP,  fill = X)
        self._entry_po_ee= Entry(self.quadro_po_ee, width = 20, textvariable=self._po_ee)
        self._entry_po_ee.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.topsave = Button(self.param_win,
                                      command = self.saveparam,
                                      text = "Save new paramerter",
                                      background = "green",
                                      width = 20,
                                      padx = "3m",
                                      pady = "2m")
        self.topsave.pack(side = TOP, anchor = W, padx = 5, pady = 5)

        #root.protocol("WM_DELETE_WINDOW", callback)

    def saveparam(self):
        try:     self.Eop = float(eval(self._Eop.get()))
        except:  pass
        self.rbkg = float(eval(self._rbkg.get()))
        try:     self.skmax = float(eval(self._skmax.get()))
        except:  pass
        try:     self.skmin = float(eval(self._skmin.get()))
        except:  pass
        try:     self.pr_es = float(eval(self._pr_es.get()))
        except:  pass
        self._pr_ee.set  = float(eval(self._pr_ee.get()))
        self._po_es.set  = float(eval(self._po_es.get()))
        try:  self._po_ee.set  = float(eval(self._po_ee.get()))
        except:  pass
        self.param_win.destroy()


########################################################################################################
class QFeffGenerate():
    def __init__(self, genitore):
        self.genitore=genitore
        self._geometry= StringVar()
        self._Absorber= StringVar()
        self._Scatter=  StringVar()
        self._bond = StringVar()
        self._edge = StringVar()
        self._edge.set("K")
        self._geometry.set("Tetrahedral")
        self._Absorber.set("Ti")
        self._Scatter.set("O")
        self._bond.set("1.81")
        LElfpack = {"side" : LEFT, "padx" :3, "ipadx" :0 }; LEepack ={"side" : LEFT, "expand" : NO, "padx" :0}

        self.quadro_genpath = LabelFrame(genitore, text = "Generate a sigle scattering path")
        self.quadro_genpath.pack(side = TOP, expand = YES, fill = X , anchor = W, ipadx = 5, ipady = 5)
        self.quadro_genpath1 = Frame(self.quadro_genpath)
        self.quadro_genpath1.pack(side = TOP, expand = YES, fill = X , anchor = W)
        self.quadro_geometry = LabelFrame(self.quadro_genpath1, text = "Geometry")
        self.quadro_geometry.pack(side = LEFT, expand = YES, anchor = W, ipadx = 5, ipady = 5)
        self.combo_geometry= ttk.Combobox(self.quadro_geometry, state="readonly",
                    textvariable=self._geometry,values=('Tetrahedral','Sq Planar','Octahedral','Icosahedral'))

        self.combo_geometry.pack(side=LEFT)
        self.quadro_edge = LabelFrame(self.quadro_genpath1, text = "Edge")
        self.quadro_edge.pack(side = LEFT, expand = YES,  anchor = W, ipadx = 5, ipady = 5)
        self.combo_edge= ttk.Combobox (self.quadro_edge, state="readonly",
                                textvariable=self._edge,values=('K', 'L1', 'L2', 'L3'))
        
        self.combo_edge.pack(side=LEFT)

        self.quadro_genpath2 = Frame(self.quadro_genpath)
        self.quadro_genpath2.pack(side = TOP, expand = YES, fill = X , anchor = W)
        self.Absorber_LE = ut.LabelEntry(self.quadro_genpath2, Ltext = "Absober",       EtextVar= self._Absorber, Ewith = 5, SLtext ="",
                                                                            labelframepack =LElfpack,entrypack=LEepack)
        self.Scatterer =   ut.LabelEntry(self.quadro_genpath2, Ltext = "Scatterer",     EtextVar= self._Scatter,  Ewith = 5, SLtext ="",
                                                                            labelframepack =LElfpack,entrypack=LEepack)
        self.Bond_LE =     ut.LabelEntry(self.quadro_genpath2, Ltext = "Bond Distance", EtextVar= self._bond,     Ewith = 7, SLtext ="",
                                                                            labelframepack =LElfpack,entrypack=LEepack)
        self.quadro_genpath3 = Frame(self.quadro_genpath)
        self.quadro_genpath3.pack(side = TOP, expand = YES, fill = X , anchor = W, ipady=2)
        self.pulsanteA = Button(self.quadro_genpath3, command = self.feffgenerate,  text = "Generate....", background ="pale goldenrod")
        self.pulsanteA.pack(side = LEFT, expand = NO, ipadx = 5, ipady = 3)
        Frame(genitore).pack(side = TOP, expand = YES, fill = X , anchor = W, ipady=2, pady=5)
        self.genpath=ut.Browse_filename(genitore, "Or select one", singlefile=1)
        self.genpath.pulsanteA.configure(background ="pale goldenrod")
        self.genpath.filenames=[]
        Frame(genitore).pack(side = TOP, expand = YES, fill = X , anchor = W, ipady=2, pady=10)
        Define = Button(genitore, command = self.quit,  text = "Define and Quit", background ="green")
        Define.pack(side =TOP, anchor = W, ipady=5)


    def quit(self):
        self.active=False
        self.genitore.destroy()



    def feffgenerate(self):              
        geometry = self._geometry.get()
        edge = self._edge.get()
        bond = float(self._bond.get())
        Absorber = self._Absorber.get()
        Scatter = self._Scatter.get()
        feffinput=Exapy.QSFEFF(Absorber, Scatter, bond , edge, geometry)
        fefffile=tkFileDialog.asksaveasfile(title= "directory for save feff input end output",
                                                initialfile ="feff",
                                                defaultextension = "inp")
        Start_Dir=os.getcwd()
        directory= os.path.dirname(fefffile.name)
        fefffile.write(feffinput)
        fefffile.close()
        print "*************************************************"
        print "feff6l \"%s\"" %fefffile.name
        os.chdir(directory)
        if os.name =="nt":
            os.system(os.path.join(inivar.get("PrestoPronto", "PrestoPronto_Dir"),"feff6l.exe").join("\"\""))
        elif os.name =="posix":
            os.system(feff6)
        os.chdir(Start_Dir)
        print "*************************************************"
        self.genpath.filenames.append(fefffile.name[:-4] + "0001.dat")
        self.genitore.focus()

        #print self.genpath.filenames[0]
########################################################################################################
class FIT:
    def __init__(self, genitore):
      #-------------------------------    declare    ----------------------------------------------
        self.plotfit    = StringVar()
        self.label_path1 =StringVar()         #define the label of path1
        self.label_path2 =StringVar()         #define the label of path2
        self._check_n1  = IntVar()            #define if the corresponding parameter is refined
        self._check_s1  = IntVar()            #define if the corresponding parameter is refined
        self._check_r1  = IntVar()            #define if the corresponding parameter is refined
        self._check_e1  = IntVar()            #define if the corresponding parameter is refined
        self._check_n2  = IntVar()            #define if the corresponding parameter is refined
        self._check_s2  = IntVar()            #define if the corresponding parameter is refined
        self._check_r2  = IntVar()            #define if the corresponding parameter is refined
        self._check_e2  = IntVar()            #define if the corresponding parameter is refined
        self._check_path1 = IntVar()          #def. if corresponding path is used
        self._check_path2 = IntVar()          #def. if corresponding path is used
        self._s1     = StringVar()            #entry for parameters
        self._r1     = StringVar()            #entry for parameters
        self._e1     = StringVar()            #entry for parameters
        self._n1     = StringVar()            #entry for parameters
        self._s2     = StringVar()            #entry for parameters
        self._r2     = StringVar()            #entry for parameters
        self._e2     = StringVar()            #entry for parameters
        self._n2     = StringVar()            #entry for parameters
        self._kstart = StringVar()            #entry for fit parameters
        self._kend   = StringVar()            #entry for fit parameters
        self._Rstart = StringVar()            #entry for fit parameters
        self._Rend   = StringVar()            #entry for fit parameters
        self._kweigth= IntVar()               #entry for fit parameters
        self._Fspace = StringVar()            #entry for fit parameters



        packLabelFrame = {"side" : LEFT,  "expand" : YES, "anchor" : W, "pady" : 3, "ipadx" :3}
        packEntry      = {"side" : LEFT,   "anchor" : W, "pady" : 3, "padx" : 0, "fill" : X }   # "expand" :
        LElfpack = {"side" : LEFT, "padx" :3, "ipadx" :0 }; LEepack ={"side" : LEFT, "expand" : NO, "padx" :0}
      #---------------------------------  set      ------------------------------------------
        self._kstart.set(0)
        self._kend.set(0)
        self._Rstart.set(0)
        self._Rend.set(6)
        self._kweigth.set(2)
        self._kend.set("k max")
        self._Fspace.set("R")
        self.plotfit.set("R")
        self.kstart =  0
        self.kend   =  0
        self.Rstart =  0
        self.Rend   =  6


      #############------------------------------Page 1----------------------------------------------------
        self.nb = ttk.Notebook(genitore)
        self.nb.pack(fill=BOTH)
        self.p1 = Frame(self.nb)
        self.nb.add(self.p1 , text="Param.")
 
        
        
      #------------------------------  Param  -----------------------------------------------------
        self.quadro_Parameter = LabelFrame(self.p1, text = "Fit parameter")    #,text = "Correction"
        self.quadro_Parameter.pack(side = TOP,  fill = X, pady= 3, ipadx = 5, ipady = 3)
        self.quadro_k_lim = LabelFrame(self.quadro_Parameter, text = "k Range Limits")
        self.quadro_k_lim.pack(**packLabelFrame)
        self._entry_kstart= Entry(self.quadro_k_lim, width = 6, textvariable=self._kstart)
        self._entry_kstart.pack(**packEntry)
        self._entry_kend= Entry(self.quadro_k_lim, width = 6, textvariable  =self._kend  )
        self._entry_kend.pack(**packEntry)
        self.quadro_R_lim = LabelFrame(self.quadro_Parameter, text = "R Range Limits")
        self.quadro_R_lim.pack(**packLabelFrame)
        self._entry_Rstart= Entry(self.quadro_R_lim, width = 6, textvariable=self._Rstart)
        self._entry_Rstart.pack(**packEntry)
        self._entry_Rend= Entry(self.quadro_R_lim, width = 6, textvariable=  self._Rend)
        self._entry_Rend.pack(**packEntry)
        self.quadro_spin_kweigth = LabelFrame(self.quadro_Parameter, text = "k_weigth")
        self.quadro_spin_kweigth.pack(**packLabelFrame)
        self.spin_kweigth = Spinbox(self.quadro_spin_kweigth, from_ = 0, to = 3, textvariable= self._kweigth, width = 5)
        self.spin_kweigth.pack(**packEntry)
        self.quadro_fit_space = LabelFrame(self.quadro_Parameter, text = "Fit space")
        self.quadro_fit_space.pack(**packLabelFrame)
        self.combo_fit_space= ttk.Combobox(self.quadro_fit_space, state="readonly", textvariable=self._Fspace,values=('k','R','q'))
        self.combo_fit_space.pack(**packEntry)

      #--------------------------------------Path 1----------------------------------------------------
        self.quadro_Path1 = LabelFrame(self.p1, text = "Fit parameter")    #,text = "Correction"
        self.quadro_Path1.pack(side = TOP,  fill = X, pady= 1, ipadx = 0, ipady = 0)
        self.pathselect_1=ut.Browse_filename(self.quadro_Path1, "Path 1", singlefile=1)
        self.pathselect_1.quadro_selezione.pack(side = TOP,  ipadx = 0, ipady = 3 )
        self.pathselect_1.pulsanteA.configure(command = self.browse_command2_1, text="Path1", width=8, background ="pale goldenrod" )
        self.quadro_Path1_var = Frame(self.quadro_Path1)
        self.quadro_Path1_var.pack(side = TOP,  fill = X, pady= 0, ipadx = 0, ipady = 0)
        self.path1_Buttoncheck = Checkbutton(self.quadro_Path1_var, text="Use   " ,variable=self._check_path1 )
        self.path1_Buttoncheck.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.n1_LE = ut.LabelEntry(self.quadro_Path1_var, Ltext = "n1", EtextVar= self._n1, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.n1_check = Checkbutton(self.n1_LE.LabFr, text="",variable=self._check_n1)
        self.n1_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.r1_LE = ut.LabelEntry(self.quadro_Path1_var, Ltext = "r1", EtextVar= self._r1, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.r1_check = Checkbutton(self.r1_LE.LabFr, text="",variable=self._check_r1)
        self.r1_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.s1_LE = ut.LabelEntry(self.quadro_Path1_var, Ltext = "s1", EtextVar= self._s1, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.s1_check = Checkbutton(self.s1_LE.LabFr, text="" ,variable=self._check_s1 )
        self.s1_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.e1_LE = ut.LabelEntry(self.quadro_Path1_var, Ltext = "e1", EtextVar= self._e1, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.e1_check = Checkbutton(self.e1_LE.LabFr ,variable=self._check_e1 )
        self.e1_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 1)

      #--------------------------------------Path 2----------------------------------------------------
        self.quadro_Path2 = LabelFrame(self.p1, text = "Fit parameter")    #,text = "Correction"
        self.quadro_Path2.pack(side = TOP,  fill = X, pady= 1, ipadx = 0, ipady = 0)
        self.pathselect_2=ut.Browse_filename(self.quadro_Path2, "Path 2", singlefile=1)
        self.pathselect_2.quadro_selezione.pack(side = TOP,ipady = 2)
        self.pathselect_2.pulsanteA.configure(command = self.browse_command2_2, text="Path2", width=8, background ="pale goldenrod" )
        self.quadro_Path2_var = Frame(self.quadro_Path2)
        self.quadro_Path2_var.pack(side = TOP,  fill = X, pady= 0, ipadx = 0, ipady = 0)
        self.path1_Buttoncheck = Checkbutton(self.quadro_Path2_var, text="Use   " ,variable=self._check_path2 )
        self.path1_Buttoncheck.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.n2_LE = ut.LabelEntry(self.quadro_Path2_var, Ltext = "n2", EtextVar= self._n2, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.n2_check = Checkbutton(self.n2_LE.LabFr, text="" ,variable=self._check_n2 )
        self.n2_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.r2_LE = ut.LabelEntry(self.quadro_Path2_var, Ltext = "r2", EtextVar= self._r2, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.r2_check = Checkbutton(self.r2_LE.LabFr, text="" ,variable=self._check_r2 )
        self.r2_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.s2_LE = ut.LabelEntry(self.quadro_Path2_var, Ltext = "s2", EtextVar= self._s2, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.s2_check = Checkbutton(self.s2_LE.LabFr, text="" ,variable=self._check_s2 )
        self.s2_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.e2_LE = ut.LabelEntry(self.quadro_Path2_var, Ltext = "e2", EtextVar= self._e2, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.e2_check = Checkbutton(self.e2_LE.LabFr ,variable=self._check_e2 )
        self.e2_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 1)

      #--------------------------------------Perform----------------------------------------------------
        self.quadro_perform = LabelFrame(self.p1)    #,text = "Correction"
        self.quadro_perform.pack(side = BOTTOM,  fill = X, expand =YES)
        self.button_fit_per = Button(self.quadro_perform,
                                      command = self.perform,
                                      text = "Perform" ,
                                      background = "green",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m")
        self.button_fit_per.pack(side = LEFT, anchor = W, padx = 5, pady = 5)
        Frame(self.quadro_perform).pack(side = LEFT, expand =Y)
        self.radioframe = Frame(self.quadro_perform)
        self.radioframe.pack(side = LEFT)
        self.radio_plot_q= Radiobutton(self.radioframe, text="k", variable=self.plotfit, value="k",command = self.changeplot)
        self.radio_plot_q.pack(side= TOP,  anchor=E)
        self.radio_plot_r= Radiobutton(self.radioframe, text="R", variable=self.plotfit, value="R",command = self.changeplot)
        self.radio_plot_r.pack(side= TOP,  anchor=E)
        self.Fit_PlSa_But=ut.PloteSaveB(self.quadro_perform, ext="" ,comment= None, title="FIT Plot")

      ############---------------------------Page 2----------------------------------------------------
        self.p2 = Frame(self.nb)
        self.nb.add(self.p2, text="Plot FitVar")
        self.nb.pack(fill=BOTH)

        self.quadro_PlotP1 = LabelFrame(self.p2, text =self.label_path1)
        self.quadro_PlotP1.pack(side = TOP, expand = YES, anchor=N, fill =X)
        self.quadro_PlotP1_1 = Frame(self.quadro_PlotP1)
        self.quadro_PlotP1_1.pack(side = TOP, expand = YES, anchor=N, fill=X)
        self.quadro_n1Bu= LabelFrame(self.quadro_PlotP1_1, text="n1")
        self.quadro_n1Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.n1_PlSa_But=ut.PloteSaveB(self.quadro_n1Bu, ext="" ,comment= None, title="n 1")
        self.quadro_r1Bu= LabelFrame(self.quadro_PlotP1_1, text="r1")
        self.quadro_r1Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.r1_PlSa_But=ut.PloteSaveB(self.quadro_r1Bu, ext="" ,comment= None, title="r 1")
        self.quadro_PlotP1_2 = Frame(self.quadro_PlotP1)
        self.quadro_PlotP1_2.pack(side = TOP, fill=X)
        self.quadro_s1Bu= LabelFrame(self.quadro_PlotP1_2, text="s1")
        self.quadro_s1Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.s1_PlSa_But=ut.PloteSaveB(self.quadro_s1Bu, ext="" ,comment= None, title="s 1")
        self.quadro_e1Bu= LabelFrame(self.quadro_PlotP1_2, text="e1")
        self.quadro_e1Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.e1_PlSa_But=ut.PloteSaveB(self.quadro_e1Bu, ext="" ,comment= None, title="e 1")

        self.quadro_PlotP2 = LabelFrame(self.p2, text =self.label_path2)
        self.quadro_PlotP2.pack(side = TOP, expand = YES, anchor=N, fill =X)
        self.quadro_PlotP2_1 = Frame(self.quadro_PlotP2)
        self.quadro_PlotP2_1.pack(side = TOP, expand = YES, anchor=N, fill=X)
        self.quadro_n2Bu= LabelFrame(self.quadro_PlotP2_1, text="n1")
        self.quadro_n2Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.n2_PlSa_But=ut.PloteSaveB(self.quadro_n2Bu, ext="" ,comment= None, title="n 1")
        self.quadro_r2Bu= LabelFrame(self.quadro_PlotP2_1, text="r1")
        self.quadro_r2Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.r2_PlSa_But=ut.PloteSaveB(self.quadro_r2Bu, ext="" ,comment= None, title="r 1")
        self.quadro_PlotP2_2 = Frame(self.quadro_PlotP2)
        self.quadro_PlotP2_2.pack(side = TOP, fill=X)
        self.quadro_s2Bu= LabelFrame(self.quadro_PlotP2_2, text="s1")
        self.quadro_s2Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.s2_PlSa_But=ut.PloteSaveB(self.quadro_s2Bu, ext="" ,comment= None, title="s 1")
        self.quadro_e2Bu= LabelFrame(self.quadro_PlotP2_2, text="e1")
        self.quadro_e2Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.e2_PlSa_But=ut.PloteSaveB(self.quadro_e2Bu, ext="" ,comment= None, title="e 1")



    def browse_command2_1(self):
        Path_Quadro=Toplevel()
        path1=QFeffGenerate(Path_Quadro)
        Path_Quadro.wait_window()
        self.pathselect_1.filenames=path1.genpath.filenames
        self.pathselect_1.name=os.path.basename(path1.genpath.filenames[0])
        self.path1 = (Exapy.path(self.pathselect_1.filenames[0]))
        self.label_path1 = self.pathselect_1.name + "      reff =" + str(self.path1.reff)+"  "
        self.label_path1+= self.path1.geom+"  nleg="+str(self.path1.nlegs)
        self.pathselect_1.labelfiletext.set(self.label_path1)
        self._n1.set(self.path1.degen_start)
        self._r1.set(self.path1.reff)
        self._e1.set(self.path1.e0_start)
        self._s1.set(self.path1.ss2_start)
        self._check_n1.set(1)
        self._check_s1.set(1)
        self._check_r1.set(1)
        self._check_e1.set(1)
        self._check_path1.set(1)
        self.quadro_PlotP1.configure(text=self.label_path1)


    def browse_command2_2(self):
        Path_Quadro=Toplevel()
        path1=QFeffGenerate(Path_Quadro)
        Path_Quadro.wait_window()
        self.pathselect_1.filenames=path1.genpath.filenames
        self.pathselect_1.name=os.path.basename(path1.genpath.filenames[0])
        self.path2 = (Exapy.path(self.pathselect_1.filenames[0]))
        self.label_path2 = self.pathselect_1.name + "      reff =" + str(self.path1.reff)+"  "
        self.label_path2+= self.path1.geom+"  nleg="+str(self.path1.nlegs)
        self.pathselect_2.labelfiletext.set(self.label_path2)
        self._n2.set(self.path2.degen_start)
        self._r2.set(self.path2.reff)
        self._e2.set(self.path2.e0_start)
        self._s2.set(self.path2.ss2_start)
        self._check_n2.set(1)
        self._check_s2.set(1)
        self._check_r2.set(1)
        self._check_e2.set(1)
        self._check_path2.set(1)




    def perform(self):
        path=list()
        kmin      =  float(self._kstart.get())
        try:
            kmax =  float(self._kend.get())
        except ValueError:
            kmax=max(spectra[0].k)
        rmin      =  float(self._Rstart.get())
        rmax      =  float(self._Rend.get())
        kweight   =  self._kweigth.get()
        fit_space =  self._Fspace.get()
        if self._check_path1:
            if self._check_n1.get(): self.path1.degen_minimize=  "guess"
            else:              self.path1.degen_minimize=  "def"
            if self._check_r1.get(): self.path1.delr_minimize=  "guess"
            else:              self.path1.r_minimize=  "def"
            if self._check_e1.get(): self.path1.e0_minimize=  "guess"
            else:              self.path1.e0_minimize=  "def"
            if self._check_s1.get(): self.path1.ss2_minimize=  "guess"
            else:              self.path1.ss2_minimize=  "def"
            path.append(self.path1)
            self.path1.degen_start=   float(self._n1.get())
            self.path1.e0_start=      float(self._e1.get())
            self.path1.ss2_start =    float(self._s1.get())
            self.path1.r_start=       float(self._r1.get())
        if self._check_path2.get():
            path.append(self.path2)
            if self._check_n2.get(): self.path2.degen_minimize=  "guess"
            else:              self.path2.degen_minimize=  "def"
            if self._check_r2.get(): self.path2.delr_minimize=  "guess"
            else:              self.path2.r_minimize=  "def"
            if self._check_e2.get(): self.path2.e0_minimize=  "guess"
            else:              self.path2.e0_minimize=  "def"
            if self._check_s2.get(): self.path2.ss2_minimize=  "guess"
            else:              self.path2.ss2_minimize=  "def"
            self.path2.degen_start=   float(self._n2.get())
            self.path2.e0_start=      float(self._e2.get( ))
            self.path2.ss2_start =    float(self._s2.get())
            self.path2.r_start=       float(self._r2.get())
      #---------------------------Fit --------------------------------
        print kmin
        for item in spectra:
            item.FT_F(kmin , 0 ,kmax, .3, kweight,
                           "hanning")
            item.FIT(kmin, kmax, rmin, rmax, .3, kweight,
                        "hanning", fit_space, path)
      #---------------------------Post Fit --------------------------------
        self.Fit_PlSa_But.x_array = [item.r for item in spectra]
        self.Fit_PlSa_But.y_array = [item.fit_mag for item in spectra]
        self.Fit_PlSa_But.z_array = [item.mag for item in spectra]
        self.Fit_PlSa_But.comments = [item.comments[:-1] for item in spectra]
        c1="#L k  chi*k**"+ str(self._kweigth.get())+" exp\n"
        for item in self.Fit_PlSa_But.comments: item.append(c1)
        self.Fit_PlSa_But.ext ="FTMag"


        if self._check_path1.get():
            self.Fitpage2(1)
            #print "yyyyyyyyyyyyyyyyyyyyyyy"
        if self._check_path2.get():
            self.Fitpage2(2)



    def Fitpage2(self,it):
        x_att, y_att, z_att ="x_array","y_array","z_array"
        for n in "ners":
            pa= n+str(it)
            st_attrib = pa +"_PlSa_But"
            #print st_attrib
            bu_attrib= getattr(self, st_attrib)
            #print bu_attrib
            setattr(bu_attrib, x_att, [x])
            yarray = [[item.fit_res[pa]  for item in spectra]]
            setattr(bu_attrib, y_att, yarray)
            delta_pa="delta_"+pa
            zarray = [[item.fit_res[delta_pa]  for item in spectra]]
            setattr(bu_attrib, z_att, zarray)
            commentarray = ["# "+pa +delta_pa  for item in spectra]
            setattr(bu_attrib, "comments", commentarray)
            setattr(bu_attrib, "error", True)
        return




    def changeplot(self):
        w =self._kweigth.get()
        if self.plotfit.get()=="R":
            self.Fit_PlSa_But.x_array = [item.r for item in spectra]
            self.Fit_PlSa_But.y_array = [item.fit_mag for item in spectra]
            self.Fit_PlSa_But.z_array = [item.mag for item in spectra]
            self.Fit_PlSa_But.comments = [item.comments[:-1] for item in spectra]
            c1="#L k  chik**"+ str(self._kweigth.get())+"  exp\n"
            for item in self.Fit_PlSa_But.comments: item.append(c1)
            self.Fit_PlSa_But.title = "FT(chi(k)*k**%s)" %w
            self.Fit_PlSa_But.ext =".FitFTMag"
        if self.plotfit.get()=="k":
            self.Fit_PlSa_But.x_array = [item.k for item in spectra]
            self.Fit_PlSa_But.y_array = [item.fit_chi*item.k**w for item in spectra]
            self.Fit_PlSa_But.z_array = [item.chi*item.k**w for item in spectra]
            self.Fit_PlSa_But.comments = [item.comments[:-1] for item in spectra]
            c1="#L k  chik**"+ str(w)+"  exp\n"
            for item in self.Fit_PlSa_But.comments: item.append(c1)
            self.Fit_PlSa_But.title = "chi(k)*k**%s" %w
            self.Fit_PlSa_But.ext ="Fitk"





#######################################################################################################
class XDEF:
    def __init__(self, genitore):
              #-------------------------------    declare    ----------------------------------------------
        self._x    = StringVar()
        self.synch_title =StringVar()          #define the label of plot
        self._plot =StringVar()                #define the type of plot
        #self._check_n1  = IntVar()            #define if the corresponding parameter is refined
        #self._check_s1  = IntVar()            #define if the corresponding parameter is refined
        #self._Rend   = StringVar()            #entry for fit parameters
      #---------------------------------  set      ------------------------------------------
        self._x.set("index")
        self.synch_title.set("")
        self._plot.set("index")
      #---------------------------------  define x      ------------------------------------------
        self.quadro_x = LabelFrame(genitore, text = "Define abscissa")    #,text = "Correction"
        self.quadro_x.pack(side = TOP,  fill = X, pady= 3, ipadx = 5, ipady = 3)
        self.combo_x= ttk.Combobox(self.quadro_x , state="readonly",   textvariable=self._x,
                     values=('index','elapsed time: min','elapsed time: sec'))
        self.combo_x.pack(side = LEFT ,anchor = E, pady=5, padx = 5, ipadx = 1)
        self.button_defx = Button(self.quadro_x,
                                      command = self.Define,
                                      text = "Define" ,
                                      background = "green",
                                      width = 10,
                                      padx = "3m",
                                      pady = "1m")
        self.button_defx.pack(side = LEFT, anchor = W, padx = 5, pady = 5)
      #---------------------------------  plot T1      ------------------------------------------
        self.quadro_plot = LabelFrame(genitore, text = "synch. plot")    #,text = "Correction"
        self.quadro_plot.pack(side = TOP,  fill = X, pady= 3, ipadx = 5, ipady = 3)
        self.combo_plot= ttk.Combobox(self.quadro_plot , state="readonly",   textvariable=self._plot, 
                     values=('index','elapsed time: min','elapsed time: sec','Temperature 1    ','Temperature 2    '))    
        self.combo_plot.bind('<<ComboboxSelected>>',self.Synchplot)

        self.combo_plot.pack(side = LEFT ,anchor = E, pady=5, padx = 5, ipadx = 1)
        self.Plot_PlSa_But=ut.PloteSaveB(self.quadro_plot, ext="" ,comment= None, title= "pippo ") #str(self.synch_title))
      #---------------------------------  perform        ------------------------------------------

    def Define(self):
        global x, xlabel
        xset= self._x.get()
        if   xset=="elapsed time: min":
            x = numpy.array([item.start_time_ep for item in spectra])
            x-= x[0]
            x/= 60
            xlabel= "min"
        elif xset=='elapsed time: sec':
            x = numpy.array([item.start_time_ep for item in spectra])
            x-= x[0]
            xlabel= "sec"
        elif xset=="index":
            x=range(1,len(spectra)+1)
            xlabel= "index"
        else: print "ERROR", xset    
        self.Synchplot(self._plot.get())



    def Synchplot(self, evt):
        xset= evt
        if isinstance(xset, Event): 
                   xset=self._plot.get()
        print "defined x " ,self._x.get()        
        print "defined y " ,xset, "\n"
        self.Plot_PlSa_But.x_array= [x]
        self.Plot_PlSa_But.comments=[]
        self.Plot_PlSa_But.comments.append(spectra[0].comments[:-1])
        
        if xset=='elapsed time: min':
            y = numpy.array([item.start_time_ep for item in spectra])
            y -= y[0]
            y /= 60
            self.Plot_PlSa_But.y_array= [y]
            xset="min"
            self.Plot_PlSa_But.title= xset+"  vs  "+xlabel
        elif xset== 'elapsed time: sec':
            y = numpy.array([item.start_time_ep for item in spectra])
            y-= y[0]
            self.Plot_PlSa_But.y_array= [y]
            self.Plot_PlSa_But.title= xset+"vs  "+xlabel
            xset="sec"
        elif xset=='Temperature 1    ':
            y = [item.T1 for item in spectra]
            self.Plot_PlSa_But.y_array= [y]
            self.Plot_PlSa_But.title= xset+"vs  "+xlabel
            xset="T1"
        elif xset=='Temperature 2    ':
            y = [item.T1 for item in spectra]
            self.Plot_PlSa_But.y_array= [y]
            self.Plot_PlSa_But.title= xset+" vs  "+xlabel
            xset="T2"
        elif xset=="index":
            y=range(1,len(spectra)+1)
            self.Plot_PlSa_But.y_array= [y]
            self.Plot_PlSa_But.title= xset+" vs  "+xlabel

        self.Plot_PlSa_But.comments[0].append( "#L  "+ xlabel+ "  "+xset+"\n")#

#######################################################################################################
class Tscan:
    def __init__(self, genitore):
        global filesel_spectra
        global spectra
        global x
        global xlabel
        global path
        global Dis_coeff
        global inivar
        
        
        
        
        readini()
             

        Dis_coeff=[None,None,None]
        path=list()
        xlabel = "Index"
        spectra=[]
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
        self.QE_gen= Gen_QE(self.p_QE_generic)
        self.QE_gen.filesel.pulsanteA.configure(command= lambda i="QE_GEN": self.Setlimit(i))
        #----------------------------------------------------------------------
        self.p_QE_spec =Frame(self.nb_beamline)  
        self.nb_beamline.add(self.p_QE_spec, text="SPEC single")
        self.QE_spec= Spec_QE(self.p_QE_spec)
        self.QE_spec.filesel.pulsanteA.configure(command= lambda i="SPEC": self.Setlimit(i))
        #----------------------------------------------------------------------
        self.p_bm29 =Frame(self.nb_beamline) 
        self.nb_beamline.add(self.p_bm29, text="BM29")
        self.QEcal= QEcal(self.p_bm29)
        self.QEcal.filesel.pulsanteA.configure(command= lambda i="BM29f": self.Setlimit(i))   
        self.QEcal.dirsel.pulsanteA.configure(command= lambda i="BM29d": self.Setlimit(i))   
        #----------------------------------------------------------------------
        self.p_samba =Frame(self.nb_beamline)  
        self.nb_beamline.add(self.p_samba, text="SAMBA")
  
        self.Samba= SambaQE(self.p_samba)
        self.Samba.filesel.pulsanteA.configure(command= lambda i="SAMBAf": self.Setlimit(i))   
        self.Samba.dirsel.pulsanteA.configure(command= lambda i="SAMBAd": self.Setlimit(i))   
        #----------------------------------------------------------------------
        self.p_id24 =Frame(self.nb_beamline) 
        self.nb_beamline.add(self.p_id24, text="ID24")

        self.Disp_calibration = DispCal(self.p_id24)
        self.Disp_calibration.filesel.pulsanteA.configure(command= lambda i="ID24": self.Setlimit(i))
        
       #  Averages
        self.p2 = Frame(self.nb)
        self.nb.add(self.p2, text="Averages")
        self.Avesel= Avesel(self.p2)
        self.Avesel.pulsante_Aver.configure(command = self.SelAver2)
       #  XANES
        self.p3 = Frame(self.nb)
        self.nb.add(self.p3, text="XANES")
        self.XAN= XANES(self.p3)
        self.nb.pack()
        self._fromf= StringVar()
        self._tof= StringVar()#
       #EXAFS-FT
        self.p4=Frame(self.nb)
        self.nb.add(self.p4, text="EXAFS-FT")
        self.EXAFT= EXAFT(self.p4)
       # FIT
        self.p5=Frame(self.nb)
        self.nb.add(self.p5, text="FIT")       
        self.EXAFT= FIT(self.p5)
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
        self.Avesel._from_tof.set("1-"+str(len(filesel_spectra)))
        self.Avesel.before.set((min(filesel_spectra[0].E)))
        self.Avesel.after.set((max(filesel_spectra[0].E)))
        pass

    def SelAver2(self):
        self.Avesel.Perform()
        if spectra != []:
            self.XAN._deriv_start.set(round(min(spectra[0].E),3))
            self.XAN._deriv_end.set(round(max(spectra[0].E),3))
            self.XAN._TCW_start.set(round(min(spectra[0].E),3))
            self.XAN._TCW_end.set(round(max(spectra[0].E),3))
            self.XAN._INTxan_start.set(round(min(spectra[0].E),3))
            self.XAN._INTxan_end.set(round(max(spectra[0].E),3))
        pass
    
    def num_deriv(self,x):
        self.menu.num_deriv(x)
        for wgt in self.p3.pack_slaves():
            wgt.destroy()
        del self.XAN
        self.XAN= XANES(self.p3)
        self.nb.pack()
        self._fromf= StringVar()
        self._tof= StringVar()
        if spectra != []:
            self.XAN._deriv_start.set(round(min(spectra[0].E),3))
            self.XAN._deriv_end.set(round(max(spectra[0].E),3))
            self.XAN._TCW_start.set(round(min(spectra[0].E),3))
            self.XAN._TCW_end.set(round(max(spectra[0].E),3))
            self.XAN._INTxan_start.set(round(min(spectra[0].E),3))
            self.XAN._INTxan_end.set(round(max(spectra[0].E),3))        
        
    

        
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
   


   
   