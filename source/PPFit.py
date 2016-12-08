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
from copy import deepcopy
import ttk
import tkFileDialog
import numpy
import utility as ut
import os
import exapy

import PPset

from PPset import inivar



from TScrolledFrame import TScrolledFrame      
global __verbose__                                                                    
__verbose__=False#True#
global num_deriv
num_deriv=True







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
        self.genpath.pulsanteA.configure(background ="pale goldenrod", command=self.browse)
        self.genpath.filenames=[]
        Frame(genitore).pack(side = TOP, expand = YES, fill = X , anchor = W, ipady=2, pady=10)
        Define = Button(genitore, command = self.quit,  text = "Define and Quit", background ="green")
        Define.pack(side =TOP, anchor = W, ipady=5)

    def browse(self):
        self.genpath.browse_command()
        self.quit()
    def quit(self):
        self.active=False
        self.genitore.destroy()



    def feffgenerate(self):              
        geometry = self._geometry.get()
        edge = self._edge.get()
        bond = float(self._bond.get())
        Absorber = self._Absorber.get()
        Scatter = self._Scatter.get()
        feffinput=exapy.QSFEFF(Absorber, Scatter, bond , edge, geometry)
	# use dialog for directory
        feffdir = tkFileDialog.askdirectory(title= "Directory for save feff input end output")
        fefffile = os.path.join(feffdir, 'feff.inp')
        Start_Dir=os.getcwd()
        with open(fefffile, 'w') as f:
            f.write(feffinput)
        print "*************************************************"
        print "feff6l \"%s\"" % fefffile
        os.chdir(feffdir)
        # if feff0001.dat already exists, delete it first
        # this makes sense as we are not checking for the return value of os.system, so it is possible we end up reading a previously written version of it
        try:
            os.unlink(os.path.join(feffdir, "feff0001.dat"))
        except OSError as e:
            pass
        if os.name =="nt":
            command=os.path.join(inivar.get("PrestoPronto", "PrestoPronto_Dir"),
                                                                   "feff6l.exe")
            os.system(command.join('""'))
        elif os.name =="posix":
            #os.system(feff6)
            #command=os.path.join(inivar.get("PrestoPronto", "PrestoPronto_Dir"),
                                                                   #"feff6")
            os.system("feff6L")
        os.chdir(Start_Dir)
        print "*************************************************"
        self.genpath.filenames.append(os.path.join(feffdir, "feff0001.dat"))
        self.genitore.focus()

        #print self.genpath.filenames[0]
########################################################################################################
class Path(LabelFrame):
   def __init__(self, *args,**kws):
      #-------------------------------    declare    ----------------------------------------------
        self.plotfit    = StringVar()
        self.label_path1 =StringVar()         #define the label of path1
        self._check_n1  = IntVar()            #define if the corresponding parameter is refined
        self._check_s1  = IntVar()            #define if the corresponding parameter is refined
        self._check_r1  = IntVar()            #define if the corresponding parameter is refined
        self._check_e1  = IntVar()            #define if the corresponding parameter is refined
        self._check_path1 = IntVar()          #def. if corresponding path is used
        
        self._s1     = StringVar()            #entry for parameters
        self._r1     = StringVar()            #entry for parameters
        self._e1     = StringVar()            #entry for parameters
        self._n1     = StringVar()            #entry for parameters


        packLabelFrame = {"side" : LEFT,  "expand" : YES, "anchor" : W, "pady" : 3, "ipadx" :3}
        packEntry      = {"side" : LEFT,   "anchor" : W, "pady" : 3, "padx" : 0, "fill" : X }   # "expand" :
        LElfpack = {"side" : LEFT, "padx" :3, "ipadx" :0 }; LEepack ={"side" : LEFT, "expand" : NO, "padx" :0}
      #---------------------------------  set      ------------------------------------------
        self._check_path1
      #--------------------------------- Structure     ------------------------------------------      
      
        LabelFrame.__init__(self,*args,**kws)
        self.text=kws['text']

        self.pathselect_1=ut.Browse_filename(self, "Path name", singlefile=1)
        self.pathselect_1.quadro_selezione.pack(side = TOP,  ipadx = 0, ipady = 3 )
        self.pathselect_1.pulsanteA.configure(command = self.browse_command2_1, text="Path", width=8, background ="pale goldenrod" )
        self.quadro_Path1_var = Frame(self)
        self.quadro_Path1_var.pack(side = TOP,  fill = X, pady= 0, ipadx = 0, ipady = 0)
        self.path1_Buttoncheck = Checkbutton(self.quadro_Path1_var, text="Use   " ,variable=self._check_path1 )
        self.path1_Buttoncheck.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.n1_LE = ut.LabelEntry(self.quadro_Path1_var, Ltext = "n", EtextVar= self._n1, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.n1_check = Checkbutton(self.n1_LE.LabFr, text="",variable=self._check_n1)
        self.n1_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.r1_LE = ut.LabelEntry(self.quadro_Path1_var, Ltext = "r", EtextVar= self._r1, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.r1_check = Checkbutton(self.r1_LE.LabFr, text="",variable=self._check_r1)
        self.r1_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.s1_LE = ut.LabelEntry(self.quadro_Path1_var, Ltext = "ss", EtextVar= self._s1, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.s1_check = Checkbutton(self.s1_LE.LabFr, text="" ,variable=self._check_s1 )
        self.s1_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 0)
        self.e1_LE = ut.LabelEntry(self.quadro_Path1_var, Ltext = "e0", EtextVar= self._e1, Ewith = 5, SLtext ="",
                                   labelframepack =LElfpack,entrypack=LEepack)
        self.e1_check = Checkbutton(self.e1_LE.LabFr ,variable=self._check_e1 )
        self.e1_check.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1, padx = 1)
        
        
   #-----------------------------------Functions----------------------------------------------        
        
   def browse_command2_1(self):
        Path_Quadro=Toplevel()
        path1=QFeffGenerate(Path_Quadro)
        #Path_Quadro.wm_attributes("-topmost", True)
        Path_Quadro.wait_window()
        pathfilnam=path1.genpath.filenames[0]
        pathname=os.path.basename(pathfilnam)
        #print pathfilnam.replace('\\','/')
        self.path1 = exapy.FeffPathGroup(pathfilnam.replace('\\','/'))
        self.label_path1 = pathname + "      reff =" + str(self.path1.reff)+"  "
        self.label_path1+= self.path1.geomg+"  nleg="+str(self.path1.nleg)
        self.pathselect_1.labelfiletext.set(self.label_path1)
        self._n1.set(self.path1.degen)
        self._r1.set(self.path1.reff)
        self._e1.set(self.path1.e0)
        self._s1.set(0.005)
        self._check_n1.set(1)
        self._check_s1.set(1)
        self._check_r1.set(1)
        self._check_e1.set(1)
        self._check_path1.set(1)
        self.path1.degen=1
########################################################################################################
class FIT:
    def __init__(self, genitore):
      #-------------------------------    declare    ----------------------------------------------
        self.plotfit    = StringVar()
        self._kstart = StringVar()            #entry for fit parameters
        self._kend   = StringVar()            #entry for fit parameters
        self._Rstart = StringVar()            #entry for fit parameters
        self._Rend   = StringVar()            #entry for fit parameters
        self._kweigth= IntVar()               #entry for fit parameters
        self._Fspace = StringVar()            #entry for fit parameters
        self._PlotPath = StringVar()          # define the path in page 2 combobox
        self.PlotListPath = list()       
        self.rem_path= IntVar()               #spin remove



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
        self.nb.pack(fill=BOTH,expand=1)
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
        self.combo_fit_space= ttk.Combobox(self.quadro_fit_space, state="readonly", textvariable=self._Fspace,values=('k','r','q'))
        self.combo_fit_space.pack(**packEntry)
        
      #--------------------------------------Path list----------------------------------------------------
        self.quadro_Path1 = LabelFrame(self.p1, text = "Fit parameters")    #,text = "Correction"
        self.quadro_Path1.pack(side = TOP, fill='both', expand=1, pady= 1, ipadx = 0, ipady = 0)
        #Label(self.quadro_Path1,text = "Checkbutton on meaning refine").pack(
        #        side = TOP, fill=X, expand=0, pady= 1, ipadx = 0, ipady = 0)
        self.standardframe = TScrolledFrame(self.quadro_Path1)
        self.standardframe.pack(side = TOP,  pady= 1, ipadx = 0, ipady = 0, fill='both', expand=1)
        
        self.Path_list=list()
        self.Path_list.append(Path(self.standardframe.frame(),bd=5 ,text = "Path 1"))
        self.Path_list[-1].pack(side = TOP,  fill = X, pady= 1, ipadx = 0, ipady = 0)
        ###################--------button add path
        Quadro_Par3=Frame(self.p1)
        Quadro_Par3.pack(side = TOP, anchor= W, expand =N, fill = BOTH, pady=15)         
        Button(Quadro_Par3, text="Add one Path" ,command = self.add_path,    
                                      width = 13,
                                      background = "violet"
                                      ).pack(side=LEFT, padx=3, pady=1,anchor =W)
        Label(Quadro_Par3,text='   ').pack(side=LEFT, padx=3, pady=1,anchor =W)                              
        Button(Quadro_Par3, text="Rem. last Path" ,command = self.rem_pa,    
                                      width = 15,
                                      background = "violet"
                                      ).pack(side=LEFT, padx=3, pady=1,anchor =W)  
                                      

      #----------------------------------Quadro   Perform  -------------------------------------------------
        self.quadro_perform = LabelFrame(self.p1)    #,text = "Correction"
        self.quadro_perform.pack(side = TOP, anchor=S, fill = X, expand =NO)
        self.button_fit_per = Button(self.quadro_perform,
                                      command = self.perform,
                                      text = "Perform" ,
                                      background = "green",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m")
        self.button_fit_per.pack(side = LEFT, anchor = W, padx = 5, pady = 5)
        self.framepb=Frame(self.quadro_perform)
        self.framepb.pack(side = LEFT, expand =Y, fill=BOTH)
        self.radioframe = Frame(self.quadro_perform)
        self.radioframe.pack(side = LEFT)
        self.radio_plot_q= Radiobutton(self.radioframe, text="k", variable=self.plotfit, value="k",command = self.changeplot)
        self.radio_plot_q.pack(side= TOP,  anchor=E)
        self.radio_plot_r= Radiobutton(self.radioframe, text="R", variable=self.plotfit, value="R",command = self.changeplot)
        self.radio_plot_r.pack(side= TOP,  anchor=E)
        self.Fit_PlSa_But=ut.PloteSaveB(self.quadro_perform, ext="" ,comment= None, title="FIT Plot")

      ############---------------------------Page 2----------------------------------------------------
        self.p2 = Frame(self.nb)
        self.nb.add(self.p2, text="Plot Fit Results")
        self.nb.pack(fill=BOTH, expand=1)
        
        quadro_PlotP3 = LabelFrame(self.p2, text ='Plot residuals')
        quadro_PlotP3.pack(side = TOP, expand = YES, anchor=N, fill =X)
        quadro_rx2Bu= LabelFrame(quadro_PlotP3, text="red. chi 2")
        quadro_rx2Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.rx2_PlSa_But=ut.PloteSaveB(quadro_rx2Bu, ext="" ,comment= None, title="red. chi 2")     
        quadro_rfBu= LabelFrame(quadro_PlotP3, text="r-factor")
        quadro_rfBu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.rf_PlSa_But=ut.PloteSaveB(quadro_rfBu, ext="" ,comment= None, title="r-factor")             
        #------------------------combo box-----------------------------------------        
        quadro_Path_list = LabelFrame(self.p2, text ='Path ')
        quadro_Path_list.pack(side = TOP, expand = NO, anchor=N, fill =X)
        self.combo_Path_list= ttk.Combobox(quadro_Path_list, state="readonly", 
                                        textvariable=self._PlotPath, 
                                        values=self.PlotListPath,
                                        width=55)
        self.combo_Path_list.pack(**packEntry)
        self.combo_Path_list.bind('<<ComboboxSelected>>',self.PathVarplot)
        
        
        self.quadro_PlotP1 = LabelFrame(self.p2, text ='Fit results')
        self.quadro_PlotP1.pack(side = TOP, expand = YES, anchor=N, fill =X)
        #-------------------------- n1 r1-------------------------------------    
        self.quadro_PlotP1_1 = Frame(self.quadro_PlotP1)
        self.quadro_PlotP1_1.pack(side = TOP, expand = YES, anchor=N, fill=X)
        self.quadro_n1Bu= LabelFrame(self.quadro_PlotP1_1, text="n1")
        self.quadro_n1Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.n1_PlSa_But=ut.PloteSaveB(self.quadro_n1Bu, ext="" ,comment= None, title="n 1")
        self.quadro_r1Bu= LabelFrame(self.quadro_PlotP1_1, text="r1")
        self.quadro_r1Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.r1_PlSa_But=ut.PloteSaveB(self.quadro_r1Bu, ext="" ,comment= None, title="r 1")
        #-------------------------- s1 e1----------------------------------------
        self.quadro_PlotP1_2 = Frame(self.quadro_PlotP1)
        self.quadro_PlotP1_2.pack(side = TOP, fill=X)
        self.quadro_s1Bu= LabelFrame(self.quadro_PlotP1_2, text="s1")
        self.quadro_s1Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.s1_PlSa_But=ut.PloteSaveB(self.quadro_s1Bu, ext="" ,comment= None, title="s 1")
        self.quadro_e1Bu= LabelFrame(self.quadro_PlotP1_2, text="e1")
        self.quadro_e1Bu.pack(side = LEFT, expand=Y, padx = 3, fill =X)
        self.e1_PlSa_But=ut.PloteSaveB(self.quadro_e1Bu, ext="" ,comment= None, title="e 1")

 

    def add_path(self):
        last=len(self.Path_list)+1
        self.Path_list.append(Path(self.standardframe.frame(),bd=5 ,text = "Path %d"%(last)))
        self.Path_list[-1].pack(side = TOP,  fill = X, pady= 1, ipadx = 0, ipady = 0)
        #self.SpinRem.configure(to=last)
        self.standardframe.reposition()


    def rem_pa(self):
        self.Path_list[-1].destroy()
        del self.Path_list[-1]
        #self.SpinRem.configure(to=last)
        self.standardframe.reposition()

    def perform(self):
        w =self._kweigth.get()
        kmin      =  float(self._kstart.get())
        try:
            kmax =  float(self._kend.get())
        except ValueError:
            kmax=max(PPset.spectra[0].k)
        rmin      =  float(self._Rstart.get())
        rmax      =  float(self._Rend.get())
        kweight   =  self._kweigth.get()
        fit_space =  self._Fspace.get()
        PPset.spectra.TG= exapy.TransformGroup(kmin=kmin, kmax=kmax,dk=4,
                                      kweight=kweight, window='kaiser',rmin=rmin,
                                      rmax=rmax,  fitspace=fit_space)        

      #------------------ Pathlist et Pars --------------------------------
        self.FeffPaths=list()
        self.Params=exapy.ParamGroup()
        methvar = zip(['s02', 'e0', 'sigma2', 'deltar'],              #nome variabili
                      ["amp_", "del_e0_", "sig2_", "-reff+del_r_"])   #nome parameter
        
        self.PlotListPath=list()    
        for j,item in enumerate(self.Path_list):
            if item._check_path1:
                for meth_item, var_item in methvar: 
                    setattr(item.path1, meth_item, var_item+str(j))                
                self.FeffPaths.append(item.path1)
                exapy._oneshellpar( label='_%s'%(str(j)), 
                                    amp    = float(item._n1.get()),
                                    del_e0 = float(item._e1.get()), 
                                    sig2   = float(item._s1.get()),
                                    del_r  = float(item._r1.get()),
                                    vary   ={'amp'   :item._check_n1.get(),
                                             'del_r' :item._check_r1.get(),
                                             "sig2"  :item._check_s1.get(),
                                             "del_e0":item._check_e1.get()},
                                    paramgroup=self.Params)
                dr=getattr(self.Params, 'del_r_%s'%(str(j)))
                setattr(dr, 'max', item.path1.reff*2)
                setattr(dr, 'min', item.path1.reff*0.2)
                self.PlotListPath.append('%s) %s'%(str(j), item.label_path1))
        self._PlotPath.set(self.PlotListPath[0])
        self.combo_Path_list.configure(values=self.PlotListPath)
      #---------------------------Fit --------------------------------
        pb = ttk.Progressbar(self.framepb, orient='horizontal', 
                                             mode='determinate',
                                             maximum=len(PPset.spectra))
        pb.pack(side = LEFT,anchor = W, expand = 1, fill = X)

        param_label= dir(self.Params)
        for item in PPset.spectra:
            item.FIT(pathlist=self.FeffPaths, pars=self.Params, 
                     transform=PPset.spectra.TG)
            item.paramgroup=exapy.ParamGroup(**item.paramgroup.__dict__)
            for jtem in param_label:
                setattr(item.paramgroup,jtem, deepcopy(getattr(self.Params,jtem)))
            if len(PPset.spectra)<10:
                print item.fit_report
            pb.step() ; pb.update_idletasks()
        pb.destroy()    
      #---------------------------Post Fit --------------------------------
        print '############################################\n\n'
        fitheader=PPset.spectra.header[:]
        # fill button for residuals rx2 and rf (red. chi2 and rfactor)
        self.rx2_PlSa_But.x_array=[PPset.x]
        self.rx2_PlSa_But.y_array=[[item.paramgroup.chi_reduced for item in PPset.spectra]]
        fitheaderrx2=fitheader[:].append('#spectra reduced chi2\n')
        self.rx2_PlSa_But.comments = [[fitheaderrx2]]
        self.rf_PlSa_But.x_array=[PPset.x]
        self.rf_PlSa_But.y_array=[[item.paramgroup.rfactor for item in PPset.spectra]]  
        fitheaderrf=fitheader[:].append('#spectra r-factor\n')
        self.rf_PlSa_But.comments = [[ fitheaderrf]]
        # fill button for experimental and fit plot
        self.Fit_PlSa_But.comments = [fitheader for item in PPset.spectra]
        self.changeplot()
        self.PathVarplot(self.PlotListPath[0])



    def changeplot(self):
        w =self._kweigth.get()
        if self.plotfit.get()=="R":
            self.Fit_PlSa_But.x_array = [item.dataset.data.r for item in PPset.spectra]
            self.Fit_PlSa_But.y_array = [item.dataset.model.chir_mag for item in PPset.spectra]
            self.Fit_PlSa_But.z_array = [item.dataset.data.chir_mag for item in PPset.spectra for item in PPset.spectra]
            c1="# k  FT(magk**"+ str(self._kweigth.get())+")  exp\n"
            self.Fit_PlSa_But.comments[0].append(c1)
            self.Fit_PlSa_But.title = "$FT(\chi(k)*k^%d)$" %w
            self.Fit_PlSa_But.xlabel= '$R(\AA)$'
            self.Fit_PlSa_But.ylabel='$FT(k^%d\chi(k)) (\AA^{-%d})$'%(w,w+1)
            self.Fit_PlSa_But.ext =".FitFTMag"
        if self.plotfit.get()=="k":
            self.Fit_PlSa_But.x_array = [item.dataset.data.k for item in PPset.spectra]
            self.Fit_PlSa_But.y_array = [item.dataset.model.chi*item.dataset.model.k**w for item in PPset.spectra]
            self.Fit_PlSa_But.z_array = [item.dataset.data.chi*item.dataset.data.k**w for item in PPset.spectra]
            c1="# k  chik**"+ str(w)+"  exp\n"
            self.Fit_PlSa_But.comments[0].append(c1)
            self.Fit_PlSa_But.title = "chi(k)*k**%s" %w
            self.Fit_PlSa_But.title = "$\chi(k)*k^%d$" %w
            self.Fit_PlSa_But.xlabel= '$k(\AA^{-1})$'
            self.Fit_PlSa_But.ylabel='$k^%d\chi(k) (\AA^{-%d})$'%(w,w)
            self.Fit_PlSa_But.ext ="Fitk"
            

    def PathVarplot(self, evt):
        """
           function activated witht 
           the change in value of the combobox in page 2
        """
        xset= evt
        if isinstance(xset, Event): 
                   xset=self._PlotPath.get()
        number_Path= self.PlotListPath.index(xset)    
        x_att, y_att, z_att ="x_array","y_array","z_array"
        
        #define the path
        def dpat(name,attribute):
            lista=list()
            name+='_%s'%(str(number_Path))
            for i in PPset.spectra:
                ai=getattr(i.paramgroup, name)
                lista.append(getattr(ai, attribute))
            return lista        

        for n,j in zip("ners",['amp', 'del_e0' , 'del_r', 'sig2']):
            #define button to configure
            pa= n+str(1)
            st_attrib = pa+"_PlSa_But"
            bu_attrib= getattr(self, st_attrib)
            #set x
            setattr(bu_attrib, x_att, [PPset.x])
            #def y value
            yarray = [dpat(j, 'value')]
            #print yarray
            setattr(bu_attrib, y_att, yarray)
            zarray = [dpat(j, 'stderr')]
            setattr(bu_attrib, z_att, zarray)
            commentarray = ["# "+j+'_%s'%(str(number_Path)) for item in PPset.spectra]
            #setattr(bu_attrib, "comments", commentarray)
            setattr(bu_attrib, "error", True)
        self.r1_PlSa_But.y_array=[numpy.array(self.r1_PlSa_But.y_array[0])]    
        return
          
             
            
########################################################################################################


if __name__ == "__main__":
   import bm29 
   import ConfigParser 
   inivar=ConfigParser.ConfigParser()
   path_local_data=os.path.join(os.environ['APPDATA'],"PrestoPronto")  
   inifile=os.path.join(path_local_data,"PrestoPronto.ini")
   inivar.read(inifile)
 
   filenames=["D:\home\cprestip\mes documents\GitHub\example\Germanium.dat",
              "D:\home\cprestip\mes documents\GitHub\example\Germanium.dat",
              "D:\home\cprestip\mes documents\GitHub\example\Germanium.dat",
              "D:\home\cprestip\mes documents\GitHub\example\Germanium.dat",
              "D:\home\cprestip\mes documents\GitHub\example\Germanium.dat",
              "D:\home\cprestip\mes documents\GitHub\example\Germanium.dat"]
   filenames1=["D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0000_0.up",
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
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0013_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0014_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0015_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0016_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0017_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0018_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0019_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0020_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0021_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0022_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0023_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0024_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0025_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0026_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0027_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0028_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0029_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0030_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0031_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0032_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0033_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0034_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0035_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0036_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0037_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0038_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0039_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0040_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0041_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0042_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0043_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0044_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0045_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0046_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0047_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0048_0.up",
              "D:/home/cprestip/mes documents/data_fit/bordeaux/Run4_bordeax/Ca2Mn3O8/raw/Ca2Mn3O8_ramp1_H2_0049_0.up"]
   #filenames=filenames*8           
   for i in filenames:
       PPset.spectra.append(bm29.bm29file(i))
   for i in PPset.spectra:
       i.EXAFS_EX(kmax=12) 
       i.FT_F()
   PPset.spectra.header=['pippo']    
   PPset.x=range(1,len(PPset.spectra)+1)    
   radice = Tk()
   radice.title("EXAFS GUI")
   pippo = FIT(radice)
   radice.mainloop()



