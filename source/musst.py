#Name: rebin-algbm29.py
# Purpose: An algorithm to perform XAFS data reduction.
# Author: C. Prestipino base
# at ESRF and CNRS
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
#  shall not be used in advertising or otherwise to promote
# the sale, use or other dealings in this Software without prior written
# authorization from Illinois Institute of Technology.





import matplotlib
matplotlib.use('TkAgg')
from  utility import Browse_file 
matplotlib.interactive(False)
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from Tkinter import *
import tkFileDialog
import bm29_tools as bt
import numpy                                                                                                  
import Tix
import tables
steptime= 2.5e-6
stepfordegree=36000.0
minstep =.1
maxstep =5
MUSSTminAcq = 1e-6 
MUSSTfiltMax = 16


class MUSST:
    def __init__(self, genitore):
        #--- costanti per il controllo della disposizione
        #--- dei pulsanti
        # impostazione delle variabili di controllo Tkinter,
        # controllate dai pulsanti radio
        self._Element = StringVar()        
        self._Edgecombo = Tix.StringVar()
        self._Energy= StringVar()
        self._Gamma = StringVar()
        self._afterE = StringVar()
        self._kafterE = StringVar()
        self._beforeE = StringVar()
        self._mEs  = StringVar()
        self._mono_velocity = StringVar()    
        self._Crystal = StringVar()         
        self._time = StringVar()
        self._filt = StringVar()
        self._Deff = StringVar()
        self._Npoint= StringVar()
    
        self._Element.set("Cu")
        self._Edgecombo.set("K")
        self._Crystal.set("Si 111")
        self._Energy.set(tables.Edge_energy[self._Element.get()]
               [tables.QN_Transition.index(self._Edgecombo.get())])
        self._Gamma.set(round(tables.getGamach(
               tables.elements.index(self._Element.get()),
               self._Edgecombo.get()),2))        
        self._afterE.set(1600)
        self._kafterE.set(str(bt.Etok(float(self._afterE.get()),0)))
        self._beforeE.set(150)
        self._mEs.set(.5)
        self._mono_velocity.set(10000)
        self._Npoint.set( (eval(self._afterE.get())+eval(self._beforeE.get())) /eval(self._mEs.get()) )
        
        

        #---------------
        self.mioGenitore = genitore
        #self.mioGenitore.geometry("640x400")
        ### Il quadro principale si chiama 'quadro_grande'
        self.quadro_grande = Frame(genitore) ###
        self.quadro_grande.pack(expand = YES, fill = BOTH)
        self.quadro_controllo = Frame(self.quadro_grande) ###
        self.quadro_controllo.pack(side = TOP, fill = BOTH, padx = 10,
                                   pady = 5, ipadx = 5, ipady = 5)
        
        # All'interno di 'quadro_controllo' si creano un'etichetta
        # per il titolo e un 'quadro_pulsanti'
        mioMessaggio = "POSSIBLE CORRECTION FOR EXAFS SCAN"
        Label(self.quadro_controllo,
          text = mioMessaggio,
          justify = LEFT).pack(side = TOP, anchor = W)
                                                                                             
        
        
        
        ################################################################################################
        # 'SCAN PARAMETER'
        self.scan_parameter = LabelFrame(self.quadro_controllo,text = "SCAN PARAMETER")    #,text = "Correction"
        self.scan_parameter.pack(side = TOP, expand = YES, fill = X, ipadx = 3, ipady = 10)
        # Si aggiungono alcuni sottoquadri a 'dspacing'
        
        self.scan_parameter1 = Frame(self.scan_parameter)    #,text = "Correction"
        self.scan_parameter1.pack(side = TOP, fill = X) #expand = YES, , ipadx = 3, ipady = 10
        # Si aggiungono alcuni sottoquadri a 'dspacing'        

        self.Element = LabelFrame(self.scan_parameter1, text = "Element")
        self.Element.pack(side = LEFT, expand = YES, fill = None, anchor = W, pady = 10, ipadx = 5, ipady = 3, padx = 5)
        self._entry_Element= Entry(self.Element, width = 6, textvariable=self._Element)
        self._entry_Element.pack(side = LEFT, padx = 10)
        self._entry_Element.bind("<Return>", self.Affiche)
        
        self.Edge = LabelFrame(self.scan_parameter1, text = "Edge")
        self.Edge.pack(side = LEFT, expand = YES, fill = None, anchor = W, pady = 10, ipadx = 5, ipady = 3, padx = 5)
        self.combo_Edge= Tix.ComboBox(self.Edge , editable=1, dropdown=1,   variable=self._Edgecombo, 
                     options='listbox.height 5 listbox.width 3 entry.width 3 ', command = self.Affiche)
        
        #combo.subwidget_list['slistbox']
        #self.combo_Edge.config(state='readonly')  ## met la zone de texte en lecture seule
        self.combo_Edge.insert(0, 'K') 
        self.combo_Edge.insert(1, 'L1')
        self.combo_Edge.insert(2, 'L2') 
        self.combo_Edge.insert(3, 'L3') 
        self.combo_Edge.pack(side = LEFT, padx = 10)
        
        self.Crystal = LabelFrame(self.scan_parameter1, text = "Mono Crystal")
        self.Crystal.pack(side = LEFT, expand = YES, fill = None, anchor = W, pady = 10, ipadx = 5, ipady = 3, padx = 5)
        self.combo_Crystal= Tix.ComboBox(self.Crystal , editable=1, dropdown=1, variable=self._Crystal, command = self.Affiche)
        #self.combo_Edge.config(state='readonly')  ## met la zone de texte en lecture seule
        self.combo_Crystal.insert(0, 'Si 111') 
        self.combo_Crystal.insert(1, 'Si 311')
        self.combo_Crystal.insert(2, 'Si 511') 
        self.combo_Crystal.pack(side = LEFT, padx = 10)        
        
        self.s2 = Frame(self.scan_parameter1, width = 20).pack(side = LEFT, expand = YES, fill = X, anchor = W, )
        ###################################################################################################
        
        self.scan_parameter2 = Frame(self.scan_parameter)    #,text = "Correction"
        self.scan_parameter2.pack(side = TOP, anchor = W)#, expand = YES, ipadx = 3, ipady = 10
        
        self.Energy = LabelFrame(self.scan_parameter2, text = "Energy")
        self.Energy.pack(side = LEFT, fill = None, anchor = W, pady = 10, ipadx = 5, ipady = 3, padx = 5)
        self._entry_Energy= Entry(self.Energy, width = 6, textvariable=self._Energy)
        self._entry_Energy.pack(side = LEFT, padx = 10)
        
        self.Gamma = LabelFrame(self.scan_parameter2, text = "Gamma")
        self.Gamma.pack(side = LEFT,  fill = None, anchor = W, pady = 10, ipadx = 5, ipady = 3, padx = 5)
        self._entry_Gamma= Entry(self.Gamma, width = 6, textvariable=self._Gamma)
        self._entry_Gamma.pack(side = LEFT, padx = 10)  
        
        self.beforeE = LabelFrame(self.scan_parameter2, text = "eV pre edge")
        self.beforeE.pack(side = LEFT, expand = YES, fill = None, anchor = W,  ipadx = 5, ipady = 3, padx = 5)
        self._entry_beforeE= Entry(self.beforeE, width = 6, textvariable=self._beforeE)
        self._entry_beforeE.pack(side = LEFT, padx = 10)
        self._entry_beforeE.bind("<Return>", self.setparam)
        
        self.afterE = LabelFrame(self.scan_parameter2, text = "eV after the edge")
        self.afterE.pack(side = LEFT, expand = YES,fill = None, anchor = W, pady = 10, ipadx = 5, ipady = 3, padx = 5) #
        spacer= Frame(self.afterE).pack(side = LEFT, anchor = W, padx = 3)
        self._entry_afterE= Entry(self.afterE, width = 6, textvariable=self._afterE)
        self._entry_afterE.pack(side = LEFT)        
        self.l_entry_afterE = Label(self.afterE, text = "eV", justify = LEFT)
        self.l_entry_afterE.pack(side = LEFT, expand = NO, fill = None, anchor = W, padx = 0)
        spacer= Frame(self.afterE).pack(side = LEFT, anchor = W, padx = 10)
        self._entry_kafterE= Entry(self.afterE, width = 6, textvariable= self._kafterE)
        self._entry_kafterE.pack(side = LEFT, padx = 1)         
        self.l_entry_kafterE = Label(self.afterE, text = "A-1", justify = LEFT)
        self.l_entry_kafterE.pack(side = LEFT, expand = NO, fill = None, anchor = W, padx = 0)
        self._entry_afterE.bind("<Return>", self.E2A)
        self._entry_kafterE.bind("<Return>", self.A2E)
        #self.s = Frame(self.scan_parameter2).pack(side = LEFT, expand = YES, fill = X)
        ###################################################################################################
        self.scan_parameter3 = LabelFrame(self.scan_parameter, text= "minimum energy step")
        self.scan_parameter3.pack(side = TOP, fill = X)
        self.Eslider = Scale(self.scan_parameter3, from_=.1, to=3, length= 420,
                                                     command= self.setparam,
                                                     variable= self._mEs, 
                                                     resolution=.1,
                                                     orient=HORIZONTAL)
        self.Eslider.pack(side = LEFT,fill = X, anchor = W, ipady = 0)
        self.mEs = Frame(self.scan_parameter3)
        self.mEs.pack(side = LEFT, expand = YES, fill = BOTH, anchor =W, pady = 0, ipadx = 5, ipady = 2, padx = 5)
        self._entry_mEs= Entry(self.mEs, width = 6, textvariable=self._mEs)
        self._entry_mEs.pack(side = LEFT,fill = X, anchor = S, pady=2,padx = 10)
        self._entry_mEs.bind("<Return>", self.setparam)
        ##################################################################################################
        self.scan_parameter4 = LabelFrame(self.scan_parameter, text= "mono_velocity")
        self.scan_parameter4.pack(side = TOP, fill = X)
        self.Aslider = Scale(self.scan_parameter4, from_=1, to=15000, length= 420,
                                                     command= self.setparam,
                                                     variable= self._mono_velocity, 
                                                     resolution=1,
                                                     orient=HORIZONTAL)
        self.Aslider.pack(side = LEFT,fill = X, anchor = W, ipady = 0)
        self.monovelocity = Frame(self.scan_parameter4)
        self.monovelocity.pack(side = LEFT, expand = YES, fill = BOTH, anchor =W, pady = 0, ipadx = 5, ipady = 2, padx = 5)
        self._entry_monovelocity= Entry(self.monovelocity, width = 6, textvariable= self._mono_velocity)
        self._entry_monovelocity.pack(side = LEFT,fill = X, anchor = S, pady=2,padx = 10)      
        self._entry_mEs.bind("<Return>", self.setparam)
        ##################################################################################################
        # 'Suggested PARAMETER'
        self.sugg_parameter = LabelFrame(self.quadro_controllo,text = "OBTAINED PARAMETER")    #,text = "Correction"
        self.sugg_parameter.pack(side = TOP, fill = X, ipadx = 3, ipady = 10) #, expand = YES
        # Si aggiungono alcuni sottoquadri a 'dspacing'
        self.time = LabelFrame(self.sugg_parameter, text = "Scan Time")
        self.time.pack(side = LEFT, fill = None, anchor = W, pady = 10, ipadx = 3, ipady = 3, padx = 5) #, expand = YES
        self._entry_time= Entry(self.time, width = 6, textvariable=self._time)
        self._entry_time.pack(side = LEFT, padx = 10) 
        self.time_s = Label(self.time, text = "s",justify = LEFT).pack(side = LEFT, anchor = W)#, expand = YES
        
        self.filt = LabelFrame(self.sugg_parameter, text = "MUSST filter")
        self.filt.pack(side = LEFT, fill = None, anchor = E, pady = 10, ipadx = 5, ipady = 3, padx = 5)#, expand = YES
        self._entry_filt= Entry(self.filt, width = 6, textvariable=self._filt)
        self._entry_filt.pack(side = LEFT, padx = 1, expand = YES) 
        
        self.Deff = LabelFrame(self.sugg_parameter, text = "Det efficencency")
        self.Deff.pack(side = LEFT, fill = None, anchor = E, pady = 10, ipadx = 5, ipady = 3, padx = 5)#, expand = YES
        self._entry_Deff= Entry(self.Deff, width = 6, textvariable=self._Deff)
        self._entry_Deff.pack(side = LEFT, padx = 1, expand = YES)         
        
        self.Npoint = LabelFrame(self.sugg_parameter, text = "Number of points")
        self.Npoint.pack(side = LEFT, fill = None, anchor = E, pady = 10, ipadx = 5, ipady = 3, padx = 5)#, expand = YES
        self._entry_Npoint= Entry(self.Npoint, width = 6, textvariable=self._Npoint)
        self._entry_Npoint.pack(side = LEFT, padx = 1, expand = YES)          
        ##################################################################################################
        ##################################################################################################        
        ################################################################################################## 
        ##################################################################################################        



    ########################################################################################### 
    ###########################################################################################
    def setparam(self,value):
        monovelocity = float(eval(self._mono_velocity.get()))
        start=   float(eval(self._Energy.get()))- float(eval(self._beforeE.get()))
        end =  float(eval(self._Energy.get()))+float(eval(self._afterE.get()))
        dspacing = tables.dspacing[self._Crystal.get()]
        self._time.set(round(bt.time_scan(start,end,monovelocity,dspacing,stepfordegree=36000.0),1))
        start=   float(eval(self._Energy.get()))
        end =  float(eval(self._Energy.get())) + float(eval(self._mEs.get()))
        time =bt.time_scan(start,end,monovelocity,dspacing,stepfordegree=36000.0)
        nstep=time/steptime
        for item in range(17):
            if nstep < 2**item: filt= item-1 ; break
        else: filt= 16   
        self._filt.set(filt)
        self._Deff.set(100-round(((nstep-2**filt)/nstep)*100))
        pass                         


    def setparam(self,value):
        monovelocity = float(eval(self._mono_velocity.get()))
        start=   float(eval(self._Energy.get()))- float(eval(self._beforeE.get()))
        end =  float(eval(self._Energy.get()))+float(eval(self._afterE.get()))
        dspacing = tables.dspacing[self._Crystal.get()]
        self._time.set(round(bt.time_scan(start,end,monovelocity,dspacing,stepfordegree=36000.0),1))
        start=   float(eval(self._Energy.get()))
        end =  float(eval(self._Energy.get())) + float(eval(self._mEs.get()))
        time =bt.time_scan(start,end,monovelocity,dspacing,stepfordegree=36000.0)
        nstep=time/steptime
        for item in range(17):
            if nstep < 2**item: filt= item-1 ; break
        else: filt= 16   
        self._filt.set(filt)
        self._Deff.set(100-round(((nstep-2**filt)/nstep)*100))
        pass                         
    
    
    def Affiche(self,evt):
           #print self._Edgecombo.get() ## On affiche a l'ecran la valeur selectionnee
           self._Energy.set(tables.Edge_energy[self._entry_Element.get()]
               [tables.QN_Transition.index(self._Edgecombo.get())])
           pippo=tables.getGamach(tables.elements.index(self._Element.get()),self._Edgecombo.get())
           self._Gamma.set(round(pippo,2))
           self.setparam(evt)
           
    def A2E(self, evt): 
        self._afterE.set(bt.ktoE(eval(self._kafterE.get()), 0.0))
        setparam(evt)
    
    def E2A(self, evt): 
        self._kafterE.set(bt.Etok(eval(self._afterE.get()), 0.0))
        self.setparam(evt)
######################################################################################################################
                                          
if __name__ == "__main__":
  radice = Tix.Tk()
  pippo = MUSST(radice)
  #pippo.Show()
  radice.mainloop()





