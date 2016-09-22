# Name: PCA_GUI.py
# Purpose: Gui to perform Principal Component Analysis in a set of normalized XAFS spectra.
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
import numpy
import utility as ut
import bm29_tools as bt
import os
import zipfile
import PCA
from matplotlib.colors import cnames 
import bm29
      
global __verbose__                                                                    
__verbose__=False#True
global __version__
__version__= "b.0.0.8"
global inivar
inivar={}
global component_show
component_show =10
#import copy
global spectra
global spectra_tot
global x_array 
global x_array_t


######################################################################################################
##################################       Menu    #####################################################
class mymenu():
    def __init__(self,genitore):
        self.genitore=genitore
        self.menubar = Menu(genitore)
        # create a pulldown menu, and add it to the menu bar
        self.filemenu = Menu(self.menubar, tearoff=0)


        #self.filemenu.add_command(label="Open singlefile", command=self.opensfile)
        self.filemenu.add_command(label="Exit", command=self.quit1)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        
    
        
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About", command=self.version)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        
        # display the menu
        genitore.config(menu=self.menubar)

        
    def version(self):
        print "\n version %s \n" %__version__
        
    def quit1(self):
            print "\n\nfinally Santiago read the menu ; )\nthank you again Carmelo\n"
            self.genitore.quit()
            
 


#########################################################################################################
##################################       SETUP    #######################################################
class SETUP():
    def __init__(self, genitore):
      #-----------------------------      Declare      --------------------------------------------------
        self.A = StringVar()
        self._sel = StringVar()
        self._fromf = StringVar()
        self._tof = StringVar()
          #-----------------------------      Define      --------------------------------------------------
        self.A.set(0)


        labelpack =  {"side" : LEFT,  "fill" : BOTH, "anchor" : N,"ipadx" : 5} #,"expand" : YES, "ipady" : 5
        entrypack = {"side" : LEFT, "padx" : 5, }#"ipady" : 3     
      #-----------------------------      Browsefiles ---------------------------------------------
        self.file_sel = ut.Browsefile_plot(genitore, "Sample singlefile", 1)
        self.file_sel.fse.pulsanteA.configure(command= self.browse_command3)
        


      #-----------------------------      Range setup ---------------------------------------------  
        self.quadro_Define = LabelFrame(genitore,  text = "Setup")
        self.quadro_Define.pack(side = TOP, anchor=W, fill = X, pady= 3, ipadx = 5, ipady = 3, expand = N)  
      #-----------------------------     Select   files     --------------------------------------------------
        self.Sel_range = ut.LabelEntry(self.quadro_Define,  Ltext = "Select spectra       ex. 2,5-15,23"
                                       , EtextVar= self._sel, Ewith = 25)#
        self.Sel_range.LabFr.pack(side= TOP,  fill= X, anchor= N, ipadx= 5)
      #-----------------------------      Range  ------------------------------------------------------------          
        self.fromf = ut.LabelEntry(self.quadro_Define,  Ltext = " from ", EtextVar= self._fromf, Ewith = 12 )#
        self.fromf.LabFr.pack(**labelpack)
        self.tof = ut.LabelEntry(self.quadro_Define,  Ltext = " to ", EtextVar= self._tof, Ewith = 12 )#
        self.tof.LabFr.pack(**labelpack)
        self.quadro_Gr_ra =Frame(self.quadro_Define)
        self.quadro_Gr_ra.pack(**labelpack) 
        self.pulsante_range = Button(self.quadro_Gr_ra,
                                      command = self.ranges,
                                      text = "select Range",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_range.pack(side = LEFT, anchor = W)

        
      #-----------------------------      Perform  ---------------------------------------------
      
        self.quadro_buttonp1 = Frame(genitore)
        self.quadro_buttonp1.pack(side = TOP, expand = YES, fill = BOTH,pady = 10,
                                  ipadx = 5, ipady = 5)
        self.pulsante_Perform = Button(self.quadro_buttonp1,
                                      command = self.Perform,
                                      text = "Perform PCA",
                                      background = "green",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Perform.pack(side = LEFT, anchor = W)






    #-----------------------------      Functions Browse --------------------------------------------
    def browse_command3(self):
        self.file_sel.browse_command2()        
        self._fromf.set(min(self.file_sel.spectra[0].x))
        self._tof.set(max(self.file_sel.spectra[0].x))   
        self._sel.set("1-"+ str(len(self.file_sel.spectra)))
    #-----------------------------      Functions  Param---------------------------------------------
    def ranges(self):
        num=0
        self.top = Toplevel()
        self.top.title("RANGES PARAMETER")        
      #--------------------------   Graphic win  --------------------------------------------------
        self.graphframe = Frame(self.top)        
        self.graphframe.pack(side = LEFT, fill=BOTH, expand=YES)
        self.grap_win=ut.ParamGraph(self.graphframe, self.file_sel.spectra, "x", ["y"])
        self.grap_win.plot(num)        
        self.grap_win.paramplot(self.retr_ranges(),
                                ["g"]+["k"], ["lim1","lim2"])
        if len(self.file_sel.spectra)>1:
            self.grap_win.slider.configure(command= self.panor2)
        self.grap_win.canvas.mpl_disconnect(self.grap_win.mov_link)                                        # new pick release link
        self.grap_win.mov_link=self.grap_win.canvas.mpl_connect('motion_notify_event', self.onmoving)      # new pick release link

        
      
    def retr_ranges(self):
        lim1=float(eval(self._fromf.get()))
        lim2=float(eval(self._tof.get()))
        return  lim1, lim2
       
    def panor2(self,event):
        """
        """
        num=int(event)
        self.grap_win.param=self.retr_ranges()
        self.grap_win.panor(num)
        
    def onmoving(self, event):
        if not(self.grap_win.press):return
        string_params= [self._fromf, self._tof]
        if event.xdata==None:pass
        else:
            string_params[self.grap_win.param_num].set(round(event.xdata,4))
        self.panor2(self.grap_win.num)  
        
    #-----------------------------      Perform  ---------------------------------------------        
    def Perform(self):
        global spectra
        global spectra_tot
        global x_array 
        global x_array_t
        sel=ut.string_range(self._sel.get())
        x_array=self.file_sel.spectra[0].x
        start, end =  self.retr_ranges()    
        spectra_tot=ut.datalize(self.file_sel.spectra[0].y)
        for i in sel[1:]:
            spectra_tot =ut.datalize(spectra_tot,self.file_sel.spectra[i].y)
        spectra=ut.datalize(x_array, spectra_tot)
        spectra = bt.dat_Truncate(spectra, start, end)
        x_array_t=spectra[:,0]
        spectra =spectra[:,1:]
        spectra=spectra.astype("double")

        
        


#########################################################################################################
##################################       PCA     ########################################################
class line:
    def __init__(self, genitore, row): 
        self.DefClr = genitore.cget("bg") 
      #-----------------------------      Declare      --------------------------------------------------
        self.row=row
        self._check= IntVar()
        self._n= IntVar()
        self._eig = StringVar()
        self._RE  = StringVar()
        self._REV = StringVar()
        self._IND = StringVar()
        self._VAR = StringVar()
        self._pSL = StringVar()      
        self._RSD = StringVar()
        self._MAD = StringVar()              
      #-----------------------------      Define       --------------------------------------------------        
        confprop= { "state" :'readonly', "width":10, "relief":"flat","justify":"center"}#
        self._n.set(row)
        
        stringVar=[self._n, self._eig, self._RE, self._REV, self._IND, self._VAR,self._pSL,self._RSD,self._MAD]
        self.entrys=[]
      #-----------------------------      Structure    -------------------------------------------------- 
        self.check = Checkbutton(genitore, text="" ,variable=self._check, width=2, command=self.underline )
        self.check.grid(row= row, column=0)
        for i,item in enumerate(stringVar):
            self.entrys.append(Entry(genitore, textvariable = item, **confprop ))            
            self.entrys[-1].grid(row= row, column=i+1)
            
            
    def underline(self):
        if self._check.get():
            for i,item in enumerate(self.entrys):
                item.configure(readonlybackground='green')
        else:
            for i,item in enumerate(self.entrys):
                item.configure(readonlybackground=self.DefClr)

                
            

   

                 
class PCA_G():
    def __init__(self, genitore):
        global x_array 
        global component_show
        self.graph=[]
      #-----------------------------      Declare      --------------------------------------------------
        self.A = StringVar()
        self._select = StringVar()
        self.comp=IntVar()
      #-----------------------------      Define      --------------------------------------------------
        self.A.set(0)
        buttonconf= { "width" : 8, "padx" : 0, "pady" : "1m", "state":ACTIVE}#, "relief":"raised"}   
      #-----------------------------      Table  square---------------------------------------------
        self.table = LabelFrame(genitore)
        self.table.pack(side = TOP, expand = NO, fill = X ,pady = 3,      
                                  ipadx = 0, ipady = 3)      
      #-----------------------------      Table  heather---------------------------------------------      
        self.pulsante_n = Label(self.table, text="n") 
        self.pulsante_n.grid(row=0, column=1)
        
        self.pulsante_n1 = Button(self.table, text="eig. val.",
                                  command= lambda x="V": self.button_plot(x),
                                  **buttonconf) 
        self.pulsante_n1.grid(row=0, column=2) 
        
        self.pulsante_n2 = Button(self.table, text="RE",
                                  command= lambda x="RE": self.button_plot(x),
                                  **buttonconf) 
        self.pulsante_n2.grid(row=0, column=3) 

        self.pulsante_n3 = Button(self.table, text="REV",
                                  command= lambda x="REV": self.button_plot(x),
                                  **buttonconf) 
        self.pulsante_n3.grid(row=0, column=4) 
        
        self.pulsante_n4 = Button(self.table, text="IND",
                                  command= lambda x="IND": self.button_plot(x),
                                  **buttonconf) 
        self.pulsante_n4.grid(row=0, column=5) 
        
        self.pulsante_n5 = Button(self.table, text="VAR",
                                  command= lambda x="cumVp": self.button_plot(x),
                                  **buttonconf) 
        self.pulsante_n5.grid(row=0, column=6) 
        
        self.pulsante_n6 = Button(self.table, text="%SL",
                                  command= lambda x="SS": self.button_plot(x),
                                  **buttonconf) 
        self.pulsante_n6.grid(row=0, column=7)         

        self.pulsante_n6 = Button(self.table, text="RSD",
                                  command= lambda x="RSD": self.button_plot(x),
                                  **buttonconf) 
        self.pulsante_n6.grid(row=0, column=8)  
        
        self.pulsante_n6 = Button(self.table, text="MAD",
                                  command= lambda x="MAD": self.button_plot(x),
                                  **buttonconf) 
        self.pulsante_n6.grid(row=0, column=9)  
      #-----------------------------      Table  lines---------------------------------------------
        self.lines=[]
        for i in range(component_show):
            self.lines.append(line(self.table, row=i+1))
      
      #-----------------------------      saves  lines-----------------------------------------
        self.saves = Frame(genitore)
        self.saves.pack(side = TOP, expand = NO, fill = X ,pady = 3,      
                                  ipadx = 0, ipady = 0)
        
        self.pul_table = Button(self.saves, text="save table", background = "green", command=self.savestable) 
        self.pul_table.pack(side = LEFT, expand = NO, fill = X ,pady = 5,  padx = 3,     
                                  ipadx = 0, ipady = 3)   
        
        self.pul_compo = Button(self.saves, text="save all components", background = "green",
                                command=lambda x="co" :self.saveco_lo(x)) 
        self.pul_compo.pack(side = LEFT, expand = NO, fill = X ,pady = 5,   padx = 3,    
                                  ipadx = 0, ipady = 3)   
        
        self.pul_loads = Button(self.saves, text="save all loading", background = "green", 
                                 command=lambda x="lo" :self.saveco_lo(x))
        self.pul_loads.pack(side = LEFT, expand = NO, fill = X ,pady = 5, padx = 3,      
                                  ipadx = 0, ipady = 3)   
      #-----------------------------      saveplot  lines----------------------------------------- 
        self.selplotsaves = LabelFrame(genitore)
        self.selplotsaves.pack(side = TOP, expand = NO, fill = X ,pady = 3,      
                                  ipadx = 0, ipady = 3)        
        
        
        Label(self.selplotsaves, text="selected ").pack(side=LEFT)
        self._select.set('component')
        self.combo_All= ttk.Combobox(self.selplotsaves ,    textvariable=self._select, values=('component','loading','autovect'))
        self.combo_All.pack(side=LEFT)
        #self.combo_All.subwidget("entry").config(readonlybackground="white")
        Frame(self.selplotsaves).pack(side = LEFT,expand =YES, fill = X) 
        self.sel_PS=ut.PloteSaveB(self.selplotsaves, ext="spe" , title="save select")
        self.sel_PS.Button_plot.configure(command=lambda x="plot": self.con_sp(x))
        self.sel_PS.Button_save.configure(command=lambda x="save": self.con_sp(x))
        
      #-----------------------------      reduce set ----------------------------------------- 
        self.quadro_com = Frame(genitore)
        self.quadro_com.pack(side = TOP, expand = NO, fill = X ,pady = 3,      
                                  ipadx = 0, ipady = 3)     
        self.spinquadro=LabelFrame(self.quadro_com, text="n. of comp.")
        self.spinquadro.pack(side = LEFT ,anchor = W,pady = 1,   padx = 3,    
                                  ipadx = 0, ipady = 6)                           

        self.spin_comp = Spinbox(self.spinquadro, from_ = 1, to = component_show, textvariable= self.comp, width = 5)      
        self.spin_comp.pack(side = LEFT ,anchor = W, padx = 5, ipadx = 1, ipady = 3) #, expand = YES,  fill = BOTH
        
        self.quadro_Compare = LabelFrame(self.quadro_com,  text = "Compare")
        self.quadro_Compare.pack(side = LEFT, anchor = W, expand = NO, fill = X ,pady = 1,   padx = 3,    
                                  ipadx = 0, ipady = 1)  
        self.pulsante_com = Button(self.quadro_Compare,
                                      command = self.Compare,
                                      text = " Plot " ,
                                      background = "violet")
        self.pulsante_com.pack(side = LEFT, anchor = W, expand = NO, fill = X ,pady = 2,   padx = 3,    
                                  ipadx = 0, ipady = 3) 
        self.pulsante_comsave = Button(self.quadro_Compare,
                                      command = self.Comparesave,
                                      text = " Save " ,
                                      background = "violet")
        self.pulsante_comsave.pack(side = LEFT, anchor = W, expand = NO, fill = X ,pady = 2,   padx = 3,    
                                  ipadx = 0, ipady = 3) 
        
        
        
        self.quadro_Residuals = LabelFrame(self.quadro_com,  text = "Residuals")
        self.quadro_Residuals.pack(side = LEFT, anchor = W, expand = NO, fill = X ,pady = 1,   padx = 3,    
                                  ipadx = 0, ipady = 1)         
        self.pulsante_res = Button(self.quadro_Residuals,
                                      command = self.Residual,
                                      text = " Plot " ,
                                      background = "violet")
        self.pulsante_res.pack(side = LEFT, anchor = W, expand = NO, fill = X ,pady = 2,   padx = 3,    
                                  ipadx = 0, ipady = 3)  
        self.pulsante_ressave = Button(self.quadro_Residuals,
                                      command = self.Residualsave,
                                      text = " Save " ,
                                      background = "violet")
        self.pulsante_ressave.pack(side = LEFT, anchor = W, expand = NO, fill = X ,pady = 2,   padx = 3,    
                                  ipadx = 0, ipady = 3) 



        self.pul_compo = Button(self.quadro_com, text="reduce component", background = "green", command=self.reduce_c) 
        self.pul_compo.pack(side = LEFT, expand = NO, fill = X ,pady = 2,   padx = 3,    
                                  ipadx = 0, ipady = 3)         
    #-----------------------------      Perform  ---------------------------------------------   
    def Comn_res(self):
        global pca_sa
        global x_array_t
        self.reduce_c()
        spectro=[]
        for item  in zip(pca_sa.D.T, pca_sa.Dr.T) :
            spectro.append(Cspectro(x_array_t,*item))
        self.num=0        
        return spectro
    
    def Compare(self):
        spectro =self.Comn_res()
        self.top = Toplevel()
        self.top.title("COMPARES  "+ str(self.comp.get())+ " component")        
      #--------------------------   Graphic win  --------------------------------------------------
        self.graphframe = Frame(self.top)        
        self.graphframe.pack(side = LEFT, fill=BOTH, expand =YES)
        self.grap_win=ut.ParamGraph(self.graphframe, spectro, "x", ["y","z","r"])
        self.grap_win.plot(self.num)
        
    def Residual(self):
        spectro =self.Comn_res()
        title=("Residual "+ str(self.comp.get())+ " component")        
      #--------------------------   Graphic win  --------------------------------------------------
        self.grap_res=ut.Graph(title)
        self.grap_res.plot([range(1,len(spectro)+1)],
                           [[sum(abs(item.r)) for item in spectro]],
                           xlabel='# spectrum')    
        
        
    def Comparesave(self):
        spectro =self.Comn_res()
        ut.save_singlefile([spectro[0].x], [item.z for item in spectro], 
                           comment= ["#reconstruction %s \n"%str(self.comp.get()),
                           "# x  rec_y\n"],
                           tit="Save  reconstructed spectra")
        ut.save_singlefile([spectro[0].x], [item.r for item in spectro], 
                           comment= ["#reconstruction %s \n"%str(self.comp.get()),
                           "# x  res\n"],
                           tit="Save  residuals for each spectra")

      
    def Residualsave(self):
        spectro =self.Comn_res()
        ut.save_singlefile([range(1,len(spectro)+1)], [[sum(abs(item.r)) for item in spectro]], 
                           comment= ["#reconstruction %s \n"%str(self.comp.get()),
                           "# x  residual\n"],
                           tit="Save  residuals")




        
    def Perform(self):
        global spectra
        global pca_sa
        global component_show
        #print spectra[0][:6]
        #print spectra.dtype
        pca_sa= PCA.PCA(spectra)
        self.limit= component_show if  spectra.shape[1]>component_show  else spectra.shape[1]  
        for i in range(self.limit):
            self.lines[i]._eig.set("{0:.3g}".format(pca_sa.V[i]))               #eigen values
            self.lines[i]._RE.set("{0:.3g}".format(pca_sa.EVAL_IND.RE[i]))      #Re function
            self.lines[i]._REV.set("{0:.3g}".format(pca_sa.EVAL_IND.REV[i]))    #Ref function
            self.lines[i]._IND.set("{0:.3g}".format(pca_sa.EVAL_IND.IND[i]))    #ind funtion
            self.lines[i]._VAR.set("{0:.4g}".format(pca_sa.EVAL_IND.cumVp[i]))  #cumulative variance
            self.lines[i]._pSL.set("{0:.3f}".format(pca_sa.EVAL_IND.SS[i]))
            self.lines[i]._RSD.set("{0:.3g}".format(pca_sa.EVAL_IND.RSD[i])) 
            self.lines[i]._MAD.set(str(pca_sa.EVAL_IND.MAD[i]))

        if spectra.shape[1]<component_show:    
            for i in range(spectra.shape[1],component_show):
                self.lines[i]._eig.set("")
                self.lines[i]._RE.set("")
                self.lines[i]._REV.set("")
                self.lines[i]._IND.set("")
                self.lines[i]._VAR.set("")            
                self.lines[i]._pSL.set("")
                self.lines[i]._RSD.set("") 
                self.lines[i]._MAD.set("")
        #print pca_sa.V[2]
        #print pca_sa.EVAL_IND.REV[2]
        #print "toto",pca_sa.EVAL_IND.tototest[2]   
        #print "tota",pca_sa.EVAL_IND.totatest[2]           
        #print "RE",pca_sa.EVAL_IND.RE[2]
        #print pca_sa.EVAL_IND.IND[2]
        #print pca_sa.EVAL_IND.MAD[2],"\n"                               
                                       
    def button_plot(self, types):
        array=numpy.zeros(self.limit)
        for i in range(self.limit):
            array[i]=getattr(pca_sa.EVAL_IND, types)[i]
        if types=="V": title="Eigen Values"
        elif types=="SS": title="Significance  Level"
        elif types=="IND": title="Malinowsky IND factor"
        elif types=="cumVp": title="Cumulative Variance"        
        else: title=types        
        self.graph.append(ut.Graph(title=title))
        self.graph[-1].plot([numpy.arange(self.limit)+1],[array],
                                                    title=title)
        
    def con_sp(self,x):
        """
        component plot plot or save the checked component
        x= string equal to save or plot to decide to save or plot
        """
        global pca_sa
        global x_array
        self.sel_PS.x_array=[]
        self.sel_PS.y_array=[] 
        self.sel_PS.legend=[]
        self.sel_PS.comments= []
        for i in range(self.limit):
            if self.lines[i]._check.get():
                if self._select.get()=='component':
                    self.sel_PS.comments.append("#components \n")
                    self.sel_PS.y_array.append(pca_sa.R[:,i])
                    self.sel_PS.x_array.append(x_array_t)
                    self.sel_PS.legend.append("component " +str(i+1))
                elif self._select.get()=='autovect':    
                    self.sel_PS.comments.append("#nor weighted autovector  \n")
                    self.sel_PS.y_array.append(pca_sa.U[:,i])
                    self.sel_PS.x_array.append(x_array_t)
                    self.sel_PS.legend.append("component " +str(i+1))
                elif self._select.get()=='loading':
                    self.sel_PS.comments.append("#loadings  \n")
                    self.sel_PS.y_array.append(pca_sa.C[i,:])
                    self.sel_PS.x_array.append(numpy.arange(pca_sa.C.shape[1])+1)
                    self.sel_PS.legend.append("loading " +str(i+1))
        if self.sel_PS.x_array==[]:
            print "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            print      "No line selected"
            print      "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" 
            return
        if x=="save": self.sel_PS.save()
        elif x=="plot": self.sel_PS.plot(title=self._select.get())
        pass 
    
    def reduce_c(self):
        global pca_sa
        pca_sa.red(int(self.comp.get()))
        pca_sa.varimax()
    
    def savestable(self):
        global pca_sa
        table=ut.datalize(numpy.arange(self.limit)+1,
                        pca_sa.V[:self.limit],
                        pca_sa.EVAL_IND.RE[:self.limit],
                        pca_sa.EVAL_IND.REV[:self.limit],
                        pca_sa.EVAL_IND.IND[:self.limit],
                        pca_sa.EVAL_IND.cumVp[:self.limit],
                        pca_sa.EVAL_IND.SS[:self.limit],  
                        pca_sa.EVAL_IND.RSD[:self.limit], 
                        pca_sa.EVAL_IND.MAD[:self.limit])
        
        
        comment= ["####################################################################################################################\n",
                  "# Comp.      autovectors      REV          RE           IND       Variance   Signif. Level     RSD         MAD     #\n"]
        radix=tkFileDialog.asksaveasfilename()
        ut.filewrite(radix,  table, comment=comment, footers=None, fmt=table.shape[1]*'%1.5e ')       
                   
           
 
    def saveco_lo(self,x):
        global pca_sa
        table = pca_sa.R[:,:self.limit]   if x=="co" else pca_sa.C[:self.limit,:]
        comment= "# first "+str(self.limit)+ " component"
        comment = comment +"\n" if x=="lo" else comment +"loading along the set\n"
        radix=tkFileDialog.asksaveasfilename()
        ut.filewrite(radix,  table, comment=comment, footers=None)               
        
        
        
        









#########################################################################################################
##################################       ITFA     #######################################################
class Constr_Line:
    def __init__(self, genitore, ncom, row, Constrain=None): 
      #-----------------------------      Declare      --------------------------------------------------
        self.ncom=ncom        
        self._check= IntVar()
        self._compo=IntVar()
        self._position= IntVar()
        self._value = StringVar()
        self._c_type  = StringVar()
        self.Constrain = Constrain
      #-----------------------------      Define       --------------------------------------------------  
        if Constrain:                  
            self._compo.set(Constrain.compo+1)         
            self._c_type.set(Constrain.c_type)
            self._value.set(Constrain.value)
            self._position.set(Constrain.position)
            self._check.set(Constrain.use)
        else:            
            self._check.set(False)
            self._compo.set(1)         
            self._c_type.set("=")
            self._value.set(1)
            self._position.set(0)            
            
        
      #-----------------------------      Structure    --------------------------------------------------
        self.check = Checkbutton(genitore, variable=self._check, width=2)#, command=self.underline )
        self.check.grid(row= row, column=0)
        
        self.spin_comp= Spinbox(genitore, from_ = 1, to = self.ncom, textvariable= self._compo, width = 2)      
        self.spin_comp.grid(row= row, column=1)

        self.combo_type= ttk.Combobox(genitore ,   textvariable=self._c_type, 
                    values=('=','>','<'))

        self.combo_type.grid(row= row, column=2) 

        self.Entry_Value =Entry(genitore, textvariable =  self._value, width=8, justify=CENTER )
        self.Entry_Value.grid(row= row, column=3) 
        
        self.spin_pos= Spinbox(genitore, from_ = 0, to = pca_sa.D.shape[1]-1, textvariable= self._position, width = 7)      
        self.spin_pos.grid(row= row, column=4)
        
        
      #-----------------------------      Functios    --------------------------------------------------
    def destroy(self):
       self.check.destroy(); self.combo_type.destroy()
       self.spin_comp.destroy(); self.spin_pos.destroy()
       self.Entry_Value.destroy()
       
    def return_value(self):
      return self._check.get(), self._compo.get()-1, self._c_type.get(), float(self._value.get()),self._position.get()
        
        

        
        #for i,item in enumerate(stringVar):
        #    self.entrys.append(Entry(genitore, textvariable = item, **confprop ))            
        #    self.entrys[-1].grid(row= row, column=i+1)
            
            
    

class Constr_Window:
    def __init__(self,constrains_list):
        global pca_sa
      #--------------------------   Declare-------------------------------------------------
        self._ncons=IntVar()
        self.Constr_Lines=[]
        self._check=IntVar()
        self._mono_check= IntVar()
      #--------------------------   Define--------------------------------------------------  
        self.constrains_list=constrains_list
        self._ncons.set(len(constrains_list ))
        self._check.set(True)
        self._mono_check.set(pca_sa.use_monotonicity)
      #--------------------------   Params  Entries--------------------------------------------------        
        self.top_con = Toplevel()
        self.top_con.title("define constrain for ITFFA rotation")        
      #--------------------------   Params  Entries--------------------------------------------------
        self.param_win_con = Frame(self.top_con)
        self.param_win_con.pack(side=TOP,expand=YES)

        self.quadro_mono_check  = LabelFrame(self.param_win_con, text = "n_cons from 0 to ....")
        self.quadro_mono_check.pack(side = TOP,  fill = X,expand=YES)
        
        self.mono_check = Checkbutton(self.quadro_mono_check, text="use monotonicity" ,
                                 variable=self._mono_check, width=12)
        self.mono_check.pack(side = LEFT ,anchor = W, padx = 15, ipadx = 2, ipady = 3)
        
        self.quadro_spin_n_cons = LabelFrame(self.param_win_con, text = "n_cons from 0 to ....")
        self.quadro_spin_n_cons.pack(side = TOP,  fill = X,expand=YES)
        
        self.spin_cons = Spinbox(self.quadro_spin_n_cons, from_ = 0, to_=20,
                                 command= self.def_ncons, 
                                 textvariable= self._ncons,
                                 state= "readonly",
                                 width = 3)
        self.spin_cons.pack(side = LEFT ,anchor = W, padx = 5, ipadx = 2, ipady = 3)

        self.check = Checkbutton(self.quadro_spin_n_cons, text="use constrain" ,
                                 variable=self._check, width=8)#,command=self.underline)
        self.check.pack(side = LEFT ,anchor = W, padx = 15, ipadx = 2, ipady = 3)
        
        
        self.quadro_constrain = Frame(self.param_win_con)
        self.quadro_constrain.pack(side = TOP,  fill = X)
        
      #--------------------------   Header--------------------------------------------------        
        self.H_1 = Label(self.quadro_constrain, text="Use       ") 
        self.H_1.grid(row=0, column=0)
        self.H_2 = Label(self.quadro_constrain, text="Comp.     ") 
        self.H_2.grid(row=0, column=1)        
        self.H_3 = Label(self.quadro_constrain, text="C. Type   ") 
        self.H_3.grid(row=0, column=2)
        self.H_4 = Label(self.quadro_constrain, text="Value     ") 
        self.H_4.grid(row=0, column=3)  
        self.H_5 = Label(self.quadro_constrain, text="Position  ") 
        self.H_5.grid(row=0, column=4)          
      #--------------------------   Button --------------------------------------------------

        self.quadro_button = Frame(self.param_win_con)      
        self.quadro_button.pack(side = TOP,  fill = X) 
        self.save_cons = Button(self.quadro_button,
                                      command = self.save_cons,
                                      text = "SAVE constrain",
                                      background = "Green",
                                      width = 13,
                                      padx = "3m",
                                      pady = "3m")
        self.save_cons.pack(side = LEFT, anchor = W,pady = 10, padx=5) 
      #--------------------------   Set constrain already saved --------------------------------------------------        
        for i,item in enumerate(self.constrains_list):
            self.Constr_Lines.append(Constr_Line(self.quadro_constrain,ncom=pca_sa.n_comp,
                                     row=i+1, Constrain=item))           
      #--------------------------   Function --------------------------------------------------
    def def_ncons(self):
        self.ncons=int(self._ncons.get())
        if self.ncons>len(self.Constr_Lines):
            self.Constr_Lines.append(Constr_Line(self.quadro_constrain,ncom=pca_sa.n_comp,
                     row=1+len(self.Constr_Lines)))
        else:
            self.Constr_Lines[-1].destroy()  
            del self.Constr_Lines[-1]
            
            
                
                
    def save_cons(self):
        pca_sa.constrains_list=[]
        for item in self.Constr_Lines:
            pca_sa.constrains_list.append(PCA.CONSTRAIN(*item.return_value()))
            #print item.return_value()
        self.constrains_list=pca_sa.constrains_list    
        print  "\n",len(pca_sa.constrains_list), "constrains defined" 
        if len(pca_sa.constrains_list) and self._check.get():
              pca_sa.use_constrain=True
        else: pca_sa.use_constrain=False
        if self._mono_check.get():pca_sa.use_monotonicity=True
        else:pca_sa.use_monotonicity= False
        print  "monotonicity of loading ", str(pca_sa.use_monotonicity),"\n"
        for item in pca_sa.constrains_list:
          if item.c_type=="=" and item.value==1 and item.use:
            for i in range(pca_sa.n_comp):
              if i!= item.compo:
                 pca_sa.constrains_list.append(PCA.CONSTRAIN(True, i, "=",
                                                             0, item.position))
        return                      
      
      
      
class Cspectro:
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        self.r= y-z

        
class ITTFA_G():
    def __init__(self, genitore):
        global x_array 
        global component_show
      #___________________________________________________________________________________
        if os.name == 'nt':
                os.chdir(os.path.join(os.environ['HOMEDRIVE'],os.environ['HOMEPATH']))
        else:
                os.chdir(os.environ['HOME'])
      #-----------------------------      Declare      --------------------------------------------------
        self.A = StringVar()
        self._select = StringVar()
        self.comp=IntVar()
      #-----------------------------      Define      --------------------------------------------------
        self.A.set(0)
        buttonconf= { "width" : 8, "padx" : 0, "pady" : "1m", "state":ACTIVE, "relief":"groove"}   
      #-----------------------------      Buttons Performs  ---------------------------------------------
        self.quadro_buttonp1 = Frame(genitore)
        self.quadro_buttonp1.pack(side = TOP, expand = NO, fill = X ,pady = 0,
                                  ipadx = 5, ipady = 0)
        self.pulsante_NeedM = Button(self.quadro_buttonp1,
                                      command = self.P_Need,
                                      text = "Manual selection\nneedle matrix",
                                      background = "violet",
                                      width = 12,
                                      padx = "3m",
                                      pady = "1m")
        self.pulsante_NeedM.pack(side = LEFT, anchor = W,pady = 10, padx=5)
        
        self.quadro_buttonp1.pack(side = TOP, expand = NO, fill = X ,pady = 0,
                                  ipadx = 5, ipady = 0)
        self.pulsante_NPRcomp = Button(self.quadro_buttonp1,
                                      command = self.P_CompR,
                                      text = "plot rot. comp.",
                                      background = "violet",
                                      width = 11,
                                      padx = "3m",
                                      pady = "3m")
        self.pulsante_NPRcomp.pack(side = LEFT, anchor = W,pady = 10, padx=5)
        
        self.pulsante_Const = Button(self.quadro_buttonp1,
                                      command = self.Def_constr,
                                      text = "Define constrains",
                                      background = "violet",
                                      width = 11,
                                      padx = "3m",
                                      pady = "3m")
        self.pulsante_Const.pack(side = LEFT, anchor = W, pady = 10, padx=5)  
        
        self.pulsante_PerITFA = Button(self.quadro_buttonp1,
                                       command = self.Perform,
                                      text = "Perform ITTFA",
                                      background = "Green",
                                      width = 11,
                                      padx = "3m",
                                      pady = "3m")
        self.pulsante_PerITFA.pack(side = LEFT, anchor = W,pady = 10, padx=5)         
        
        
      #-----------------------------      Results  ---------------------------------------------
        self.quadro_Results = Frame(genitore)
        self.quadro_Results.pack(side = TOP, expand = NO, fill = X ,pady = 0,
                                  ipadx = 0, ipady = 0)
        self.Frame_loading =LabelFrame(self.quadro_Results,  text = "Loading")
        self.Frame_loading.pack(side = LEFT, anchor=N, expand = YES, fill = X ,pady = 0,
                                  ipadx = 0, ipady = 0)
        self.SP_loading=ut.PloteSaveB(self.Frame_loading, ext=".dat", comment= None,  title="True Loadings",error=False)

        self.Frame_component =LabelFrame(self.quadro_Results,  text = "Component")
        self.Frame_component.pack(side = LEFT, anchor=N, expand = YES, fill = X ,pady = 0,
                                  ipadx = 0, ipady = 0)        
        self.SP_component=ut.PloteSaveB(self.Frame_component, ext=".dat", comment= None,  title="True Components",error=False)
        
    
      #-----------------------------      Perform  ---------------------------------------------        
      
    
  
      
      
    def Man_needle(self):
        global spectra
        global spectra_tot
        global pca_sa
        global component_show
        pca_sa= PCA.PCA(spectra)
        if spectra.shape[1]>component_show:
            for i in range(component_show):
                self.lines[i]._eig.set("{0:.3g}".format(pca_sa.V[i]))
                self.lines[i]._RE.set("{0:.3g}".format(pca_sa.EVAL_IND.RE[i]))
                self.lines[i]._REV.set("{0:.3g}".format(pca_sa.EVAL_IND.REV[i]))
                self.lines[i]._IND.set("{0:.3g}".format(pca_sa.EVAL_IND.IND[i]))
                self.lines[i]._VAR.set("{0:.4g}".format(pca_sa.EVAL_IND.cumVp[i]))
                self.lines[i]._pSL.set("{0:.3f}".format(pca_sa.EVAL_IND.SS[i]))                
        else:
            for i in range(component_show):
                lines[i]._eig.set(0)
                lines[i]._RE.set(0)
                lines[i]._REV.set(0)
                lines[i]._IND.set(0)
                lines[i]._VAR.set(0)  
                
    def P_Need(self):
        """plot results of varimax rotation and the needle matrix
           TODO manual selection of the needle matrix
        """
        global pca_sa
        self.top = Toplevel()
        self.top.title("ROTATED LOADING and Needle matrix")
        self.graphframe = Frame(self.top)        
        self.graphframe.pack(side = LEFT, fill=BOTH, expand=YES) 
        row, col =pca_sa.Cr_rot.shape
        self.grap_win=ut.ParamGraph_multi(self.graphframe)
        self.grap_win.plot(x_array=[numpy.arange(col) for item in range(row)], 
                           y_array=[pca_sa.Cr_rot[i] for i in range(row)], 
                           comment=["com "+str(i) for i in range(1,row+1)])
        #print [pca_sa.Cr_rot[i].argmax() for i in range(row)]
        self.param=[pca_sa.Needle[i].argmax() for i in range(row)]
        self.grap_win.paramplot(param=self.param,
                                color=["bgrcmyk"[i] for i in range(row)],
                                keys=["com "+str(i) for i in range(1,row+1)])
        self.grap_win.onmoving=self.onmoving
        
        
    def P_CompR(self):
        """plot results of varimax rotation 
           TODO manual selection of the needle matrix
        """
        global pca_sa
        global x_array_t
        self.top = Toplevel()
        self.top.title("ROTATED COMPONENTS")
        self.graphframe = Frame(self.top)        
        self.graphframe.pack(side = LEFT, fill=BOTH, expand=YES) 
        row, col =pca_sa.Rr_rot.shape
        print row, col, x_array_t.shape
        self.grap_winCR=ut.ParamGraph_multi(self.graphframe)
        self.grap_winCR.plot(x_array=[x_array_t for item in range(col)], 
                             y_array=[pca_sa.Rr_rot[:,i] for i in range(col)], 
                            comment=["comp. "+str(i) for i in range(1,col+1)])
        #print [pca_sa.Cr_rot[i].argmax() for i in range(row)]
    
        
        
        

            
    def onmoving(self, event):
        global pca_sa
        self.grap_win.param[self.grap_win.param_num]=event.xdata
        self.grap_win.panor(self.grap_win.num)
        self.param=self.grap_win.param
        pca_sa.Needle=numpy.zeros(pca_sa.Cr_rot.shape)
        for i,item in enumerate(self.grap_win.param):
            pca_sa.Needle[i,:]=0            
            if item<0: item=0
            elif item>pca_sa.Needle.shape[1]-1:item=pca_sa.Needle.shape[1]-1
            pca_sa.Needle[i,round(item)]=1
        print [round(item) for item in self.grap_win.param]  
        #print pca_sa.Needle
        
    def Def_constr(self):
        self.Constrain_Window=Constr_Window(pca_sa.constrains_list)

                
    def Perform(self):
        global pca_sa
        global x_array_t
        pca_sa.EMiteraction()
        pca_sa.ITTFA()
        
        row, col= pca_sa.Cr_t.shape
        self.SP_loading.x_array=[numpy.arange(col) for item in range(row)]
        self.SP_loading.y_array=[pca_sa.Cr_t[i] for i in range(row)]
        #print pca_sa.Cr_t[1], pca_sa.Cr_t[1].shape
        self.SP_loading.comments=["# Evolution of each component along the set\n# "+ 
                                  "   ".join(["comp."+str(i+1) for i in range(row)])+"\n"]     
        self.SP_loading.legend=["comp."+str(i) for i in range(row)]  ### change i+1 to i Santiago
        
        row, col= pca_sa.Rr_t.shape        
        self.SP_component.x_array=[x_array_t for item in range(col)]
        self.SP_component.y_array=[pca_sa.Rr_t[:,i] for i in range(col)]  
        self.SP_component.comments=["# Components present in the set\n# "+ 
                                  "   ".join(["comp."+str(i) for i in range(col)])+"\n"]     
        self.SP_component.legend=["comp."+str(i+1) for i in range(col)] ### change i+1 to i Santiago
        
        
                
                
         
#########################################################################################################
#########################################################################################################



class PCA_GUI:
    def __init__(self, genitore):
        global filesel_spectra
        global spectra
        global x
        global xlabel
        global path
        global Dis_coeff
        global inivar
        
        inivar={}
        

        Dis_coeff=[None,None,None]
        path=list()
        xlabel = "Index"
        spectra=[]
        x=[]

        #menu
        self.menu=mymenu(genitore)
        self.menu.filemenu.entryconfig(index=0, command= lambda : self.Setlimit("opensf"))    


        self.nb = ttk.Notebook(genitore)
        self.nb.pack()
  
        #----------------------------------------------------------------------
        self.p1 = Frame(self.nb)
        self.nb.add(self.p1, text="Open,Ranges")

        self.SETUP= SETUP(self.p1)
        self.SETUP.pulsante_Perform.configure(command= self.performPCA)
        #-----------------------------------------------------------------------
        self.p2 = Frame(self.nb)        
        self.nb.add(self.p2, text="PCA")
        self.PCA= PCA_G(self.p2)
        self.PCA.pul_compo.configure(command= self.reduce_c)        
        #-----------------------------------------------------------------------
        self.p3 = Frame(self.nb)        
        self.nb.add(self.p3, text="ITTFA_G")
        self.ITTFA_G= ITTFA_G(self.p3)

    #--------------------Perform PCA--------------------------------------------
    def performPCA(self):
        self.SETUP.Perform()
        self.PCA.Perform()
        self.nb.select(1)
        
        
    def reduce_c(self):
        self.PCA.reduce_c()
        self.nb.select(2)   
        



if __name__ == "__main__":
   radice = Tk()
   radice.title("PCA GUI")
   pippo = PCA_GUI(radice)
   #radice.protocol("WM_DELETE_WINDOW", destroy)
   radice.mainloop()








