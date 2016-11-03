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

from   Tkinter import *
import ttk
import numpy
import utility as ut
import bm29_tools as bt

import PPset


      
global __verbose__                                                                    
__verbose__=False#True#
global num_deriv
num_deriv=True



from matplotlib.backends.backend_tkagg import  cursors
class XANESparam:
    def __init__(self, genitore):
        self.genitore=genitore
       #--------------------------   Declare--------------------------------------------------
        self._Eop= StringVar()
        self._pr_es= StringVar()
        self._pr_ee= StringVar()
        self._po_es= StringVar()
        self._po_ee= StringVar()
        self._n_poly= StringVar()
        self.n_poly=3
        self.parN= [ "pre1", "pre2", "e0" , "norm1", "norm2", "nnorm"]
        
       #--------------------------   Define--------------------------------------------------
        self.num=0
        
        if PPset.spectra.call_pe["e0"]: self._Eop.set(PPset.spectra.call_pe["e0"]) 
        else:      self._Eop.set("Ifeffit default")   
        
        if PPset.spectra.call_pe["pre1"]: self._pr_es.set(PPset.spectra.call_pe["pre1"])
        else:      self._pr_es.set("Ifeffit default")
        
        if PPset.spectra.call_pe["pre2"]: self._pr_ee.set(PPset.spectra.call_pe["pre2"]) 
        else:      self._pr_ee.set(-50) 
        
        if PPset.spectra.call_pe["norm1"]: self._po_es.set(PPset.spectra.call_pe["norm1"])
        else:      self._po_es.set(150)  
        
        if PPset.spectra.call_pe["norm2"]: self._po_ee.set(PPset.spectra.call_pe["norm2"])
        else:      self._po_ee.set("Ifeffit default") 
        
        self._n_poly.set(PPset.spectra.call_pe["nnorm"]) 
        
                       
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
        self.grap_win=ut.ParamGraph(self.graphframe, PPset.spectra, "energy", 
                                    ["mu", "pre_edge", "post_edge"],
                                    xlabel='energy (eV)', ylabel='mu (abs. unit)')
        self.refresh()
        self.grap_win.pick=self.grap_win.canvas.mpl_connect('pick_event', self.onpick)                     # new pick release link
        self.grap_win.release=self.grap_win.canvas.mpl_connect('button_release_event', self.onrelease)
        self.press=False        
        self.grap_win.slider.configure(command= self.panor2)                                               # new pick release link
        genitore.wait_window()    
    

        
   #--------------------------  mouse Function  -----------------------------------------------------        
    def onpick(self,event_p):
        if not(event_p.artist in self.grap_win.parmlines): 
            print 'wrong click'
            return True

        else:
            self.grap_win.param_num= self.grap_win.parmlines.index(event_p.artist)            
            self.grap_win.mov_link=self.grap_win.canvas.mpl_connect(
                                           'motion_notify_event', self.onmoving)
            return True
        
    def onrelease(self,event_r):
        #print "release"
        if hasattr(self.grap_win, "mov_link"):
            self.grap_win.canvas.mpl_disconnect(self.grap_win.mov_link)
            
        string_params= [self._pr_es,self._pr_ee,self._Eop, self._po_es, self._po_ee]
        for item in zip(self.parN[:-1],string_params):
            value=PPset.spectra[self.num].pre_edge_details.call_args[item[0]]
            if value is None:
                item[1].set('default')
            else: 
              item[1].set(round(
                         PPset.spectra[self.num].pre_edge_details.call_args[item[0]],2))
        self.refresh()    


    def onmoving(self, event):
        param_n=self.grap_win.param_num
        if param_n==2:                                          #nel caso di eo
            PPset.spectra.call_pe["e0"] = round(event.xdata,2)
        else:
            PPset.spectra.call_pe[self.parN[param_n]]=round(
                                       event.xdata- PPset.spectra[self.num].e0,2)
        self.panor2(self.num)
        
   #--------------------------  Function  -----------------------------------------------------         
    def preposted(self):
        """ perform XANES calc"""
        if len(PPset.spectra)>0:
            #try:
            PPset.spectra[self.num].XANES_Norm(**PPset.spectra.call_pe)
            #except:    print "proposted bad", PPset.spectra.call_pe
        #PPset.spectra.call_pe=PPset.spectra[self.num].pre_edge_details.call_args
            
    def refresh(self):
        "refresh picture when parameter are change in the textbox"
        self.grap_win.figsub.clear()
        self.saveparam(destroy=False)
        self.preposted()              #perform calc#
        self.grap_win.plot(self.num)
        e0=PPset.spectra[self.num].e0
        p1=PPset.spectra[self.num].pre_edge_details.pre1
        p2=PPset.spectra[self.num].pre_edge_details.pre2
        n1=PPset.spectra[self.num].pre_edge_details.norm1
        n2=PPset.spectra[self.num].pre_edge_details.norm2
        values = numpy.array((e0+p1, e0+p2, e0, e0+n1, e0+n2))
        self.grap_win.paramplot(values, ["g"]*2+["k"]+["r"]*2, self.parN[:-1])
        self.grap_win.panor(self.num)


            
    def panor2(self,event):
        """when the params are moved slider is moved"""
        self.num=int(event)
        self.preposted()
        self.grap_win.panor(self.num)

            
            
           
            
    
    def saveparam(self, destroy=True):
        ##########################################################################
        def error_message(Name):
            print "\nPlease write a numerical value for "+ Name +"\n" +  \
                     "for Larch default, write \"None\" or \"default\" \n"
        ##########################################################################
        def check_input(Name, variable, default):
            xxx=variable.get()
            if "default" in xxx:PPset.spectra.call_pe[Name]=default
            elif xxx=='None':PPset.spectra.call_pe[Name]=default  
            else:
                try:   PPset.spectra.call_pe[Name] = round(float(variable.get()),2)
                except SyntaxError:error_message(Name)
        ##########################################################################        
        check_input("e0",self._Eop,None)
        check_input("pre1",self._pr_es,None)
        check_input("pre2",self._pr_ee,-50)
        check_input("norm1",  self._po_es, 50)       
        check_input("norm2",  self._po_ee, None)        
        PPset.spectra.call_pe["nnorm"] = float(eval(self._n_poly.get()))
        if destroy:
            self.genitore.destroy()
            #self.param_win.destroy()
   #--------------------------  Function  -----------------------------------------------------         
      













class DERIVparam_c:
    """
    class for calculation of numerical derivative
    """
    def __init__(self, genitore, ini):
        global x
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
        self.grap_win_der=ut.ParamGraph(self.graphframe_der, PPset.spectra, "x_int", ["deriv"])
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
        if len(PPset.spectra)!=0:
            PPset.spectra[self.num_der].bm29Num_der(window_len=self.smoot, step=self.interpolation,
                                              L1=self.lim1,L2=self.lim2, repeat=self.smoot_repeat)
            PPset.spectra[self.num_der].deriv=PPset.spectra[self.num_der].NumDer.deriv
            PPset.spectra[self.num_der].x_int=PPset.spectra[self.num_der].NumDer.x_int          
    
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
        global x
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
        
        self._spin_inter= Spinbox(self.quadro_inter, from_ = 0.0, to = 1.0, increment=0.02,
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
        self.grap_win_der=ut.ParamGraph(self.graphframe_der, PPset.spectra, "x_int", ["deriv"])
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
            self.x_deriv=bt.dat_Truncate(PPset.spectra[0].energy, self.lim1, self.lim2)            
        if len(PPset.spectra)!=0:
            PPset.spectra[self.num_der].bm29derE(sampling=self.x_deriv, L1=self.lim1,
                                                       L2=self.lim2, s=self.smoot/100) 
            PPset.spectra[self.num_der].deriv=PPset.spectra[self.num_der].E_MuFp
            PPset.spectra[self.num_der].x_int=self.x_deriv          
    

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
        #self.smoot=0
        #self.interpolation =0
        #if num_deriv: 
        #    self.smoot_repeat=0
        #    self.smoot=1
        self._INTxan_start = StringVar()
        self._INTxan_end   = StringVar()
        self._check_deriv=IntVar()
        self._check_xan = IntVar()
        self._check_INT = IntVar()
        self._xflatten= IntVar()
        #--------------set---------------------------------
        self._xflatten.set(1)
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
        self.derivate_PlSa_But=ut.PloteSaveB(self.quadro_derivative, [],[],
                                             ext="Der" ,comment= None,
                                             xlabel='energy (eV)',
                                             ylabel='f\'(mu) (abs. unit)',
                                             title="DERIVATIVE")

      #----------------Quadro Max Derivative-------------------------------------
        self.quadro_Max_Derivative = Frame(genitore)    #,text = "Correction"
        self.quadro_Max_Derivative.pack(side = TOP,  fill = X)
        self.quadro_Max_Derivative1 = LabelFrame(self.quadro_Max_Derivative, text = "Derivate Max")    #,text = "Correctio
        self.quadro_Max_Derivative1.pack(side = LEFT,  fill = X, expand =Y)
        self.quadro_Max_Derivative2 = Frame(self.quadro_Max_Derivative1)
        self.quadro_Max_Derivative2.pack(side = LEFT, anchor = W, fill=X, expand =Y)
        self.Max_PlSa_But=ut.PloteSaveB(self.quadro_Max_Derivative2, [PPset.x], [],
                                             ext=None , comment= None,
                                             xlabel='spectra',ylabel='position (eV)',                                                        
                                             title="max derivative position")
      #----------------QuadroXan-------------------------------------
        self.quadro_xanes = LabelFrame(genitore, text = "XANES Normalization")    #,text = "Correction"
        self.quadro_xanes.pack(side = TOP,  fill = X, pady= 3, ipadx = 5, ipady = 3)
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
        self.Xanes_PlSa_But=ut.PloteSaveB(self.quadro_xanes, [],[],
                                   xlabel='energy (eV)',ylabel='normalized mu',    
                                   ext="Nor" ,comment= None, title="XANES")
      #--------------------------------------iffeffit---------------------------------------------------
        self.quadro_Iffefit = Frame(genitore)    #,text = "Correction"
        self.quadro_Iffefit.pack(side = TOP,  fill = X)
        self.quadro_Eo = LabelFrame(self.quadro_Iffefit, text = "Ifeffit E0")    #,text = "Correction"
        self.quadro_Eo.pack(side = LEFT,  fill = X, expand =Y)
        self.quadro_Eo1 = Frame(self.quadro_Eo)
        self.quadro_Eo1.pack(side = LEFT, anchor = W, fill=X, expand =Y)
        #ATTENZIONE
        self.Eo_PlSa_But=ut.PloteSaveB(self.quadro_Eo1, [], [],ext=None ,
                                       xlabel='spectra',
                                       ylabel='position (eV)',    
                                       comment= None, title="Iff Eo")
        self.quadro_Ej = LabelFrame(self.quadro_Iffefit, text = "Ifeffit edge jump")    #,text = "Correction"
        self.quadro_Ej.pack(side = LEFT,  fill = X, expand =Y)
        self.quadro_Ej1 = Frame(self.quadro_Ej)
        self.quadro_Ej1.pack(side = LEFT, anchor = W, fill=X, expand =Y)
        self.Ej_PlSa_But=ut.PloteSaveB(self.quadro_Ej, [], [],
                                       xlabel='spectra',
                                       ylabel='Edge jump (abs. unit)' ,   
                                       ext=None ,comment= None, title="Edge jump")
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
        self.INTxan_PlSa_But=ut.PloteSaveB(self.quadro_INTxan, [PPset.x], [],
                                       xlabel='spectra',
                                       ylabel='Integral values (abs. unit)',    
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
        #self.check_TCW=Checkbutton(self.quadro_perform, text="TCW_Eo"    ,variable=self._check_TCW)#, state= DISABLED)
        #self.check_TCW.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 5)
        self.check_INT=Checkbutton(self.quadro_perform, text="Xan_Int" ,variable=self._check_INT )
        self.check_INT.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 5)
      #---------------------------------Function----------------------------------------
    def XANESparam(self):
        if hasattr(self, "topX"): return
        self.topX = Toplevel()
        self.topX.title("XANES PARAMETER") 
        self.XAN_par=XANESparam(self.topX)
        del self.XAN_par
        del self.topX


    def DERIVparam(self):
        if hasattr(self, "top_der"): 
            print hasattr(self, "top_der"),"\n"
            return
        c_p=PPset.spectra.call_di
        c_p['L1']=float(self._deriv_start.get())
        c_p['L2']=float(self._deriv_end.get())
        self.top_der = Toplevel()
        self.top_der.title("smoot and interpolation parameter") 
        if num_deriv:
            ini=[c_p[i] for i in ['smoot_num', 'smoot_repeat',
                                    'interpolation','L1', 'L2']]
            self.Der_param=DERIVparam_c(self.top_der,ini)
            c_p['smoot_num']=self.Der_param.smoot
            c_p['smoot_repeat']=self.Der_param.smoot_repeat
            c_p['interpolation']=self.Der_param.interpolation
        else:
            ini=[c_p[i] for i in ['smoot', 'interpolation', 'L1','L2']]
            self.Der_param=DERIVparam_spline(self.top_der,ini)
            c_p['smoot']=self.Der_param.smoot
            c_p['interpolation']=self.Der_param.interpolation
        PPset.spectra.call_di=c_p  
        del self.Der_param
        del self.top_der
        
        
    def Perform(self):
        c_p=PPset.spectra.call_di
        p_e=PPset.spectra.call_pe
        c_p['L1']=float(self._deriv_start.get())
        c_p['L2']=float(self._deriv_end.get())
        c_p['L1i']=float(eval(self._INTxan_start.get()))
        c_p['L2i']=float(eval(self._INTxan_end.get()))
        #-----------------Max derivate  ---------------------    
        if self._check_deriv.get():
            header=list(PPset.spectra.header)
            print "\n ---Derivative Calculation---" , num_deriv
            if num_deriv:    
                for item in PPset.spectra:
                    if __verbose__: print "Xanes derivative"
                    item.bm29Num_der(window_len=c_p['smoot_num'], 
                                     step=c_p['interpolation'],
                                     L1=c_p['L1'],L2=c_p['L2'],
                                     repeat=c_p['smoot_repeat'])
            else:    
                if self.interpolation !=0:
                    self.x_deriv=numpy.arange(c_p['L1'],c_p['L2'],
                                              c_p['interpolation'])
                else:
                    self.x_deriv=bt.dat_Truncate(PPset.spectra[0].energy, 
                                                     c_p['L1'], c_p['L2'])
                for item in PPset.spectra:
                    if __verbose__: print "Xanes derivative"
                    item.bm29derE(sampling=self.x_deriv, L1=c_p['L1'],\
                                  L2=c_p['L2'], s=c_p['smoot']/100) 
                  
                    
  
         
        #-----------------XANES norm  ---------------------  
        if self._check_xan.get():
            print "\n ---XANES Normalization---"      
            header=list(PPset.spectra.header)
            pb = ttk.Progressbar(self.quadro_perform, orient='horizontal', 
                                             mode='determinate',
                                             maximum=len(PPset.spectra))
            pb.pack(side = LEFT,anchor = W, expand = 1, fill = X)            
            for item in PPset.spectra:
                if __verbose__: print "Xanes norm"
                pb.step()
                pb.update_idletasks()
                item.XANES_Norm(**p_e)
            if __verbose__: print "Xanes norm done"
            pb.destroy()
            #self._check_xan.set(0)
            #-----------------Integral---------------------
        #-----------------XANES int  ---------------------
        if self._check_INT.get():
            if self._xflatten.get() and True or False:
               for i in PPset.spectra:i.INTxan= i.bm29int(L1=x1, L2=x2, attribute='flat')
            else :
              for i in PPset.spectra:
                i.INTxan= i.bm29int(L1=c_p['L1i'],L2=c_p['L2i'],attribute='nor')
            #-----------------   End   ---------------------
        #put some reasonable value in the other case
        if    c_p['L1']==round(min(PPset.spectra[0].E),3) \
          and c_p['L2']==round(max(PPset.spectra[0].E),3) :
            c_p['L1']=round(PPset.spectra[0].e0 -50, 2)
            c_p['L1']=round(PPset.spectra[0].e0 +80, 2)
        if    c_p['L1i']==round(min(PPset.spectra[0].E),3) \
          and c_p['L2i']==round(max(PPset.spectra[0].E),3) :
            c_p['L1i']=round(PPset.spectra[0].e0 -50, 2)
            c_p['L1i']=round(PPset.spectra[0].e0 +80, 2)   
        PPset.spectra.call_di=c_p
        PPset.spectra.call_pe=p_e            
        self.Define_Plot()
        print "\n---module XANES done\n"
        

    def Define_Plot(self):
        param=PPset.spectra.call_pe
        #-----------------Max derivate  ---------------------    
        if self._check_deriv.get():
            header=list(PPset.spectra.header)
            if num_deriv:    
                self.derivate_PlSa_But.x_array= [item.NumDer.x_int for item in PPset.spectra]
                self.derivate_PlSa_But.y_array= [item.NumDer.deriv for item in PPset.spectra]
                self.derivate_PlSa_But.comments= [header for item in PPset.spectra]
            else:    
                self.derivate_PlSa_But.x_array= [self.x_deriv for item in PPset.spectra]
                self.derivate_PlSa_But.y_array= [item.E_MuFp for item in PPset.spectra]
                self.derivate_PlSa_But.comments= [header for item in PPset.spectra]                    
                    
            for item in self.derivate_PlSa_But.comments: 
                c1 ="# Derivative calc. between "+ self._deriv_start.get() + \
                                             " and "+ self._deriv_end.get()+"\n"
                #item.append(c1)
                if num_deriv:
                    c1 = "# Num. derivative calc.  with smoot= %1.8f ," \
                                   "interpolation= %1.4f, repeated444= %2d\n" %(
                              self.smoot, self.interpolation ,self.smoot_repeat)
                else:
                    c1 = "# Spl derivative  calc.  with smoot= %1.8f ,"\
                                                "interpolation= %1.4f\n" %(
                                                self.smoot, self.interpolation)
                item.append(c1)
                item.append("#L E  Derivate_smot"+str(self.smoot)+"\n")    
         
            self.Max_PlSa_But.x_array= [PPset.x]
            self.Max_PlSa_But.comments=[]                                 
            self.Max_PlSa_But.comments.append(header)
            c1 ="# Max derivative calc. between "+ self._deriv_start.get()+" and "+ self._deriv_end.get()+"\n"
            self.Max_PlSa_But.comments[0].append(c1)
            if num_deriv: 
                c1 = "# Max derivative calc.  with smoot= %1.8f ,interpolation= %1.4f, repeated= %1.4f\n" %(
                                                self.smoot, self.interpolation,self.smoot_repeat)
            self.Max_PlSa_But.comments[0].append(c1)
            self.Max_PlSa_But.comments[0].append(PPset.spectra.header)
            self.Max_PlSa_But.comments[0].append( "#L  index   Derivate_Max\n")
            for item in PPset.spectra:
                self.Max_PlSa_But.y_array= [[item.NumDer.x_int[numpy.argmax(item.NumDer.deriv)] for item in PPset.spectra]]        



        #-----------------XANES norm  ---------------------  
        if self._check_xan.get():
            header=list(PPset.spectra.header)
            self.Xanes_PlSa_But.x_array= [item.energy for item in PPset.spectra]
            self.Xanes_PlSa_But.y_array= [item.norm for item in PPset.spectra]
            self.Xanes_PlSa_But.comments= [header for item in PPset.spectra]
            ##comment how calculated XANES norm
            c1 ="# Xanes normalization calc. with "
            for i in ['e0','pre1','pre2']: c1+="%s = %s, " %(i, str(PPset.spectra.call_pe[i]))
            self.Xanes_PlSa_But.comments[0].append(c1+'\n')
            c2 = "# Xanes normalization calc. with"
            for i in ['norm1', 'norm2']: c1+="%s = %s, " %(i, str(PPset.spectra.call_pe[i]))
            c2+=", flatted= "+str(self._xflatten.get() and True or False)
            self.Xanes_PlSa_But.comments[0].append(c2+'\n')
            #add nuovo E Norm for all comments
            self.Xanes_PlSa_But.comments[0].append("# E  Nor\n")
    
            #-----------------iff e0---------------------
            self.Eo_PlSa_But.x_array= [PPset.x]
            self.Eo_PlSa_But.comments=[]
            self.Eo_PlSa_But.comments.append(list(header[:-1]))
            ##comment
            self.Eo_PlSa_But.comments[0].append( "#  index  iff_Eo\n")
            self.Eo_PlSa_But.y_array= [[item.e0 for item in PPset.spectra]]        
            #-----------------iff ej---------------------
            self.Ej_PlSa_But.x_array= [PPset.x]
            self.Ej_PlSa_But.comments=[]
            self.Ej_PlSa_But.comments.append(list(header[:-1]))
            self.Ej_PlSa_But.comments[0].append( "# index  iff_Ej\n")
            self.Ej_PlSa_But.y_array= [[item.edge_step for item in PPset.spectra]]
            #-----------------Integral---------------------
        if self._check_INT.get():
            self.INTxan_PlSa_But.x_array= [PPset.x]
            self.INTxan_PlSa_But.comments=[]
            self.INTxan_PlSa_But.comments.append(list(self.Xanes_PlSa_But.comments[0]))
                
            self.INTxan_PlSa_But.comments[0].append( 
                                 "# Int Eo cAlculated with parameter %s , %s%s"
                                               %(str(self._INTxan_start.get()), 
                                             str(self._INTxan_end.get()),"\n"))
            self.INTxan_PlSa_But.comments[0].append( "#L  INDEX  Int\n")
            self.INTxan_PlSa_But.y_array= [[item.INTxan for item in PPset.spectra]]
        print "\n---module XANES done\n"         






    def FIn(self, event):
        self._deriv_start.set(PPset.spectra.call_di['L1'])
        self._deriv_end.set(PPset.spectra.call_di['L2'])
        self._INTxan_start.set(PPset.spectra.call_di['L1i'])
        self._INTxan_end.set(PPset.spectra.call_di['L2i'])
    def FOut(self, event):
        PPset.spectra.call_di['L1']=self._deriv_start.get()
        PPset.spectra.call_di['L2']=self._deriv_end.get()
        PPset.spectra.call_di['L1i']=self._INTxan_start.get()
        PPset.spectra.call_di['L2i']=self._INTxan_end.get()      

            
                





if __name__ == "__main__":
   import bm29  
   filenames=["D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0000_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0001_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0002_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0003_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0004_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0005_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0006_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0007_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0008_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0009_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0010_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0011_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0012_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0013_0.up"]
   filenames=filenames*5       
   for i in filenames:
       PPset.spectra.append(bm29.bm29file(i))
   PPset.spectra.header=['#pipppo\n','#questo eun test\n']   
   PPset.x=range(1,len(PPset.spectra)+1)  
   radice = Tk()
   radice.title("XANES GUI")
   pippo = XANES(radice)
   pippo._deriv_start.set(6400)
   pippo._deriv_end.set(6700)
   pippo._INTxan_start.set(6400)
   pippo._INTxan_end.set(6700)   
   radice.mainloop()
