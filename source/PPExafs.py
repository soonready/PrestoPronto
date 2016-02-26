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
###########################################################################################clas####
class EXAFSparam(object):
    def __init__(self, genitore):
        self.genitore=genitore
       #--------------------------   Declare--------------------------------------------------
        self._Eop    = StringVar()
        self._skmin  = StringVar()
        self._skmax  = StringVar()
        self._rbkg   = StringVar()
        self.kweigth = IntVar()
        self.kweigthp= IntVar()
        
        self.parN= ["e0" , "kmin", "kmax", "rbkg", "kweight"]

       #--------------------------   Define--------------------------------------------------
        self.num=0
        
        if PPset.spectra.param["e0"]: self._Eop.set(PPset.spectra.param["e0"]) 
        else:      self._Eop.set("Ifeffit default")   
        
        if PPset.spectra.param["kmin"]: self._skmin.set(PPset.spectra.param["kmin"])
        else:      self._skmin.set(0)
        
        if PPset.spectra.param["kmax"]: self._skmax.set(PPset.spectra.param["kmax"]) 
        else:      self._skmax.set("Ifeffit default") 
        
        if PPset.spectra.param["rbkg"]: self._rbkg.set(PPset.spectra.param["rbkg"]) 
        else:      self._rbkg.set(1)         
              
        if PPset.spectra.param["kweight"]: self.kweigth.set(PPset.spectra.param["kweight"])
        else:      self.kweigth.set(1) 
        
        self.kweigthp.set(1)
       #------------------------------------------------------
        self.param_win = Frame(genitore)
        self.param_win.pack(side=LEFT)
        
        self.quadro_Eop = LabelFrame(self.param_win, text = "Eo")
        self.quadro_Eop.pack(side = TOP,  fill = X)
        self._entry_Eop= Entry(self.quadro_Eop, width = 10, textvariable=self._Eop)
        self._entry_Eop.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_skmin = LabelFrame(self.param_win, text = "skmin")
        self.quadro_skmin.pack(side = TOP,  fill = X)
        self._entry_skmin= Entry(self.quadro_skmin, width = 10, textvariable=self._skmin)
        self._entry_skmin.pack(side = LEFT, padx = 5, ipady = 3, fill = X)

        self.quadro_skmax = LabelFrame(self.param_win, text = "skmax")
        self.quadro_skmax.pack(side = TOP,  fill = X)
        self._entry_skmax= Entry(self.quadro_skmax, width = 10, textvariable=self._skmax)
        self._entry_skmax.pack(side = LEFT, padx = 5, ipady = 3, fill = X)
        
        self.quadro_rbkg = LabelFrame(self.param_win, text = "rbkg")
        self.quadro_rbkg.pack(side = TOP,  fill = X)
        self._entry_rbkg= Entry(self.quadro_rbkg, width = 10, textvariable=self._rbkg)
        self._entry_rbkg.pack(side = LEFT, padx = 5, ipady = 3, fill = X)
        
        self.quadro_spin_kweigth = LabelFrame(self.param_win, text = "k_wgt  k_plot")
        self.quadro_spin_kweigth.pack(side = TOP,  fill = X, ipady=2, anchor = W, padx=2)
        self.spin_kweigth = Spinbox(self.quadro_spin_kweigth, from_ = 0, to = 3, textvariable= self.kweigth, width = 2)
        self.spin_kweigth.pack(side = LEFT ,anchor = W, padx = 5, ipadx = 1, ipady = 3) #, expand = YES,  fill = BOTH

        self.spin_kweigthp = Spinbox(self.quadro_spin_kweigth, from_ = 0, to = 3, textvariable= self.kweigthp, width = 2)
        self.spin_kweigthp.pack(side = LEFT ,anchor = W, padx = 8, ipadx = 2, ipady = 3) #, expand = YES,  fill = BOTH
        self.rerefresh = Button(self.param_win,
                                     command = self.refresh,#lambda x= self.num: self.refresh(x),
                                      text = "refresh",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.rerefresh.pack(side = TOP, anchor = W, padx = 5, pady = 3)

        self.resave = Button(self.param_win,
                                      command = self.saveparam,
                                      text = "Save param",
                                      background = "green",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.resave.pack(side = TOP, anchor = W, padx = 5, pady = 3)
        
       #--------------------------   Graphic win  --------------------------------------------------
        self.graphframeM = Frame(genitore)        
        self.graphframeM.pack(side = LEFT, fill=BOTH, expand=YES)
        self.graphframeE = Frame(genitore)        
        self.graphframeE.pack(side = LEFT, fill=BOTH, expand=YES)
        self.graphframeF = Frame(genitore)        
        self.graphframeF.pack(side = LEFT, fill=BOTH, expand=YES)
        self.grap_winM=ut.ParamGraph(self.graphframeM, PPset.spectra, "energy", ["mu", "bkg"])
        self.grap_winE=ut.ParamGraph(self.graphframeE, PPset.spectra, "k", ["chiw"])
        self.grap_winF=ut.ParamGraph(self.graphframeF, PPset.spectra, "r", ["chir_mag"])
        self.grap_winF.slider.pack_forget()
        self.grap_winE.slider.pack_forget()
        self.grap_winM.slider.pack_forget()

        if (len(PPset.spectra)>1):
            self.slider = Scale(genitore, from_= 0, to=len(PPset.spectra)-1,
                                         command =self.panor2, 
                                         orient=VERTICAL,
                                         label= "Spectra"
                                         )
        self.slider.pack(side = LEFT,fill = Y, anchor = N,pady = 5, ipady = 0)
        self.grap_winE.pick=self.grap_winE.canvas.mpl_connect('pick_event', self.onpick)                     # new pick release link
        self.grap_winE.release=self.grap_winE.canvas.mpl_connect('button_release_event', self.onrelease)
        self.grap_winE.canvas.mpl_connect('figure_leave_event', self.onout)
        self.grap_winF.pick=self.grap_winF.canvas.mpl_connect('pick_event', self.onpick)                     # new pick release link
        self.grap_winF.release=self.grap_winF.canvas.mpl_connect('button_release_event', self.onrelease)
        self.grap_winF.canvas.mpl_connect('figure_leave_event', self.onout) 
        self.grap_winM.pick=self.grap_winM.canvas.mpl_connect('pick_event', self.onpick)                     # new pick release link
        self.grap_winM.release=self.grap_winM.canvas.mpl_connect('button_release_event', self.onrelease)
        self.grap_winM.canvas.mpl_connect('figure_leave_event', self.onout) 
        self.out=False
        self.preposted()  
        self.onrelease("pippo")
        self.refresh()
        self.refresh()

        # new pick release link

        genitore.wait_window()            
        
   #--------------------------  mouse Function  ----------------------------------------------------- 
    def onout(self,event_p):
        self.out=True
        
    def onpick(self,event_p):
        if event_p.artist in self.grap_winE.parmlines: 
            self.out=False
            self.grap_winE.param_num= self.grap_winE.parmlines.index(event_p.artist)            
            self.grap_winE.mov_link=self.grap_winE.canvas.mpl_connect(
                                           'motion_notify_event', self.onmovingE)
        if event_p.artist in self.grap_winF.parmlines: 
            self.out=False
            self.grap_winF.param_num= self.grap_winF.parmlines.index(event_p.artist)            
            self.grap_winF.mov_link=self.grap_winF.canvas.mpl_connect(
                                           'motion_notify_event', self.onmovingF) 
        if event_p.artist in self.grap_winM.parmlines: 
            self.out=False
            self.grap_winM.param_num= self.grap_winM.parmlines.index(event_p.artist)            
            self.grap_winM.mov_link=self.grap_winM.canvas.mpl_connect(
                                           'motion_notify_event', self.onmovingM)         
        else:
            return True
        return True    
        
    def onrelease(self,event_r):
        #print "release"
        if hasattr(self.grap_winE, "mov_link"):
            self.grap_winE.canvas.mpl_disconnect(self.grap_winE.mov_link)
        if hasattr(self.grap_winF, "mov_link"):
            self.grap_winF.canvas.mpl_disconnect(self.grap_winF.mov_link)
        if hasattr(self.grap_winM, "mov_link"):
            self.grap_winM.canvas.mpl_disconnect(self.grap_winM.mov_link)    
        if self.out:
            return
        string_params= [self._Eop, self._skmin, self._skmax, 
                                    self._rbkg, self.kweigth]
                          
        for item in zip(self.parN,string_params):
            #print PPset.spectra.param[item[0]], item[0]
            item[1].set(round(PPset.spectra.param[item[0]],2))
        self.refresh()   


    def onmovingE(self, event):
        if self.out:
           onrelease(self,"pippo")
           return
        param_n=self.grap_winE.param_num
        Epar=['kmin','kmax']
        PPset.spectra.param[Epar[param_n]]=round(event.xdata,2)
        Epar=['Fkmin','Fkmax']
        PPset.spectra.param[Epar[param_n]]=round(event.xdata,2)        
        self.panor2(self.num)
        
    def onmovingF(self, event):
        param_n=self.grap_winF.param_num
        Epar=['rbkg']
        PPset.spectra.param[Epar[param_n]]=round(event.xdata,2)
        self.panor2(self.num)        
        
    def onmovingM(self, event):
        param_n=self.grap_winM.param_num
        Epar=['e0']
        PPset.spectra.param[Epar[param_n]]=round(event.xdata,2)
        self.panor2(self.num)         
   #--------------------------  Function  -----------------------------------------------------         
    
    def preposted(self):
        """ perform EXAFS calc"""
        #print"pass form prposted"
        if len(PPset.spectra)>0:
            spectrum=PPset.spectra[self.num]
            try:
                spectrum.EXAFS_EX(**PPset.spectra.param)
                spectrum.FT_F(**PPset.spectra.param)
                spectrum.chiw=spectrum.chi*spectrum.k**int(self.kweigthp.get())
            except Exception as wert:    
                print "proposted bad", PPset.spectra.param, "\n"
                print wert, "\n"
            for item in self.parN:
                PPset.spectra.param[item]=round(getattr(spectrum,item),2)
            #for i in self.parN:
            #    print "preposted",i,PPset.spectra.param[i]    
        #print "finisch preposted"
        return
            
    def refresh(self):
        """refresh picture when parameter are change in the textbox\n\n"""
        self.saveparam(destroy=False)
        self.preposted()              #perform calc#
        
        self.grap_winE.figsub.clear()
        self.grap_winE.plot(self.num)
        valuesE = numpy.array([PPset.spectra.param[i] for i in ["kmin", "kmax"]])
        self.grap_winE.paramplot(valuesE, ["g"]*2, ["kmin", "kmax"])
        self.grap_winE.panor(self.num)
        
        self.grap_winF.figsub.clear()        
        self.grap_winF.plot(self.num)
        self.grap_winF.paramplot([PPset.spectra.param["rbkg"]], ["r"],["rbkg"])
        self.grap_winF.panor(self.num)
        
        self.grap_winM.figsub.clear()        
        self.grap_winM.plot(self.num) 
        self.grap_winM.paramplot([PPset.spectra.param["e0"]], ["r"],["e0"])        
        self.grap_winM.panor(self.num) 
        
            
    def panor2(self,event):
        """when the params are moved slider is moved"""
        self.num=int(event)
        self.preposted()
        self.grap_winE.panor(self.num)
        self.grap_winF.panor(self.num)
        self.grap_winM.panor(self.num) 
            
           
            
    
    def saveparam(self, destroy=True):
        ##########################################################################
        def error_message(Name):
            print "\nPlease write a numerical value for "+ Name +"\n" +  \
                     "for Larch default, write \"None\" or \"default\" \n"
        ##########################################################################
        def check_input(Name, variable, default):
            xxx=variable.get()
            if "default" in xxx:PPset.spectra.param[Name]=default
            elif xxx=='None':PPset.spectra.param[Name]=default  
            else:
                try:   PPset.spectra.param[Name] = round(float(variable.get()),2)
                except SyntaxError:error_message(Name)
        ##########################################################################        
        check_input("e0",self._Eop,None)
        check_input("kmin",self._skmin,0)
        check_input("kmax",self._skmax,None)
        check_input("Fkmin",self._skmin,0)
        check_input("Fkmax",self._skmax,None)        
        check_input("rbkg",self._rbkg,1)
        PPset.spectra.param["kweight"] = self.kweigth.get()
        if destroy:
            self.genitore.destroy()
        return
        


    ##################
###########################################################################################clas####
class FTparam(object):
    def __init__(self, genitore):
        self.genitore=genitore
       #--------------------------   Declare--------------------------------------------------
        self._kstart      = StringVar()
        self._kend        = StringVar()
        self.FTweigth     = IntVar()
        self._FTWind      = StringVar()
        self._dk          = StringVar()
        self.kweigthp= IntVar()
        
        self.parN= [ "Fkmin", "Fkmax", "Fkweight"]

       #--------------------------   Define--------------------------------------------------
        packLabelFrame = {"side" : TOP,  "expand" : YES, "anchor" : W, "pady" : 3}
        packEntry      = {"side" : LEFT,   "anchor" : W, "pady" : 6, "padx" : 3, "fill" : X }  
        self.num=0
        self.kweigthp.set(1)

        
        if PPset.spectra.param["dk"]:      self._dk.set(PPset.spectra.param["dk"]) 
        else:      self._dk.set("Ifeffit default")   
        
        if PPset.spectra.param["Fkmin"]:   self._kstart.set(PPset.spectra.param["Fkmin"])
        else:      self._kstart.set(0)
        
        if PPset.spectra.param["Fkmax"]:   self._kend.set(PPset.spectra.param["Fkmax"]) 
        else:      self._kend.set("Ifeffit default") 
              
        if PPset.spectra.param["Fkweight"]:self.FTweigth.set(PPset.spectra.param["Fkweight"])
        else:      self.FTweigth.set(1) 

        if PPset.spectra.param["window"]:  self._FTWind.set(PPset.spectra.param["window"])
        else:     self._FTWind.set('kaiser')
        
       #------------------------------------------------------
        self.param_win = Frame(genitore)
        self.param_win.pack(side=LEFT)
        
        self.quadro_FT = LabelFrame(self.param_win, text = "Foward FT")    #,text = "Correction"
        self.quadro_FT.pack(side = TOP,  fill = X, pady= 3, ipadx = 5, ipady = 3)
        self.quadro_FT1 = Frame(self.quadro_FT)
        self.quadro_FT1.pack(side = TOP,  fill = X)
        self.quadro_FTweigth = LabelFrame(self.quadro_FT1, text = "FT_wgt Plot_wgt")
        self.quadro_FTweigth.pack(**packLabelFrame)
        self.spin_FTweigth = Spinbox(self.quadro_FTweigth, from_ = 0, to = 3, textvariable= self.FTweigth, width = 3)
        self.spin_FTweigth.pack(side = LEFT ,anchor = S, pady=5, padx = 5, ipadx = 1)
        self.spin_kweigthp = Spinbox(self.quadro_FTweigth, from_ = 0, to = 3, textvariable= self.kweigthp, width = 2)
        self.spin_kweigthp.pack(side = LEFT ,anchor = W, padx = 8, ipadx = 2, ipady = 3) #, expand = YES,  fill = BOTH
        #Label(self.quadro_FT1, text = "FT_weigth", justify = LEFT).pack(side = LEFT, anchor = S, pady=10)
        self.quadro_FTwin = LabelFrame(self.quadro_FT1, text = "FT_win")
        self.quadro_FTwin.pack(**packLabelFrame)
        self.combo_FTw= ttk.Combobox(self.quadro_FTwin , state="readonly",   
                     textvariable=self._FTWind, width=5,
                     values=('kaiser', 'hanning', 'welch', 'sine'))
        self.combo_FTw.pack(side = LEFT ,anchor = S, pady=5, padx = 5, ipadx = 1)
        self.quadro_FT_lim1 = LabelFrame(self.quadro_FT1, text = "k start")
        self.quadro_FT_lim1.pack(**packLabelFrame)
        self._entry_FT_kstart= Entry(self.quadro_FT_lim1, width = 7, textvariable=self._kstart)
        self._entry_FT_kstart.pack(**packEntry)
        self.quadro_FT_lim2 = LabelFrame(self.quadro_FT1, text = "k end")
        self.quadro_FT_lim2.pack(**packLabelFrame)        
        self._entry_FT_kend= Entry(self.quadro_FT_lim2, width = 7, textvariable=self._kend)
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

        self.rerefresh = Button(self.param_win,
                                     command = self.refresh,#lambda x= self.num: self.refresh(x),
                                      text = "refresh",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.rerefresh.pack(side = TOP, anchor = W, padx = 5, pady = 3)

        self.resave = Button(self.param_win,
                                      command = self.saveparam,
                                      text = "Save param",
                                      background = "green",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.resave.pack(side = TOP, anchor = W, padx = 5, pady = 3)
        
       #--------------------------   Graphic win  --------------------------------------------------
        #self.graphframeM = Frame(genitore)        
        #self.graphframeM.pack(side = LEFT, fill=BOTH, expand=YES)
        self.graphframeE = Frame(genitore)        
        self.graphframeE.pack(side = LEFT, fill=BOTH, expand=YES)
        self.graphframeF = Frame(genitore)        
        self.graphframeF.pack(side = LEFT, fill=BOTH, expand=YES)
        #self.grap_winM=ut.ParamGraph(self.graphframeM, PPset.spectra, "energy", ["mu", "bkg"])
        self.grap_winE=ut.ParamGraph(self.graphframeE, PPset.spectra, "k", ["chiw","kwin"])
        self.grap_winF=ut.ParamGraph(self.graphframeF, PPset.spectra, "r", ["chir_mag"])
        self.grap_winF.slider.pack_forget()
        self.grap_winE.slider.pack_forget()
        #self.grap_winM.slider.pack_forget()
        #
        if (len(PPset.spectra)>1):
            self.slider = Scale(genitore, from_= 0, to=len(PPset.spectra)-1,
                                         command =self.panor2, 
                                         orient=VERTICAL,
                                         label= "Spectra"
                                         )
        self.slider.pack(side = LEFT,fill = Y, anchor = N,pady = 5, ipady = 0)
        self.grap_winE.pick=self.grap_winE.canvas.mpl_connect('pick_event', self.onpick)                     # new pick release link
        self.grap_winE.release=self.grap_winE.canvas.mpl_connect('button_release_event', self.onrelease)
        self.grap_winE.canvas.mpl_connect('figure_leave_event', self.onout)
        #self.grap_winM.pick=self.grap_winM.canvas.mpl_connect('pick_event', self.onpick)                     # new pick release link
        #self.grap_winM.release=self.grap_winM.canvas.mpl_connect('button_release_event', self.onrelease)
        #self.grap_winM.canvas.mpl_connect('figure_leave_event', self.onout) 
        self.out=False
        #self.preposted()  
        #self.onrelease("pippo")
        #self.refresh()
        #self.refresh()
        # new pick release link
        genitore.wait_window()            
        
   #--------------------------  mouse Function  ----------------------------------------------------- 
    def onout(self,event_p):
        self.out=True
        
    def onpick(self,event_p):
        if event_p.artist in self.grap_winE.parmlines: 
            self.out=False
            self.grap_winE.param_num= self.grap_winE.parmlines.index(event_p.artist)            
            self.grap_winE.mov_link=self.grap_winE.canvas.mpl_connect(
                                           'motion_notify_event', self.onmovingE)
        else:
            return True
        return True    
        
    def onrelease(self,event_r):
        #print "release"
        if hasattr(self.grap_winE, "mov_link"):
            self.grap_winE.canvas.mpl_disconnect(self.grap_winE.mov_link)
        if hasattr(self.grap_winF, "mov_link"):
            self.grap_winF.canvas.mpl_disconnect(self.grap_winF.mov_link)
        if self.out:
            return
        string_params= [self._kstart, self._kend]
                          
        for item in zip(self.parN,string_params):
            #print PPset.spectra.param[item[0]], item[0]
            item[1].set(round(PPset.spectra.param[item[0]],2))
        self.refresh()   


    def onmovingE(self, event):
        if self.out:
           onrelease(self,"pippo")
           return
        param_n=self.grap_winE.param_num
        Epar=['kmin','kmax']
        PPset.spectra.param[Epar[param_n]]=round(event.xdata,2)
        self.panor2(self.num)
        
      
        

   #--------------------------  Function  -----------------------------------------------------         
    def preposted(self):
        """ perform EXAFS calc"""
        #print"pass form prposted"
        if len(PPset.spectra)>0:
            spectrum=PPset.spectra[self.num]
            try:
                spectrum.EXAFS_EX(**PPset.spectra.param)
                spectrum.chiw=spectrum.chi*spectrum.k**int(self.kweigthp.get())
            except Exception as wert:    
                print "proposted bad", PPset.spectra.param    
                print wert, "\n"
            try:    
                spectrum.FT_F(**PPset.spectra.param)

            except Exception as wert:    
                print "proposted bad", PPset.spectra.param
            for item in self.parN:
                PPset.spectra.param[item]=round(getattr(spectrum,item),2)
            #for i in self.parN:
            #    print "preposted",i,PPset.spectra.param[i]    
        #print "finisch preposted"
        return
            
    def refresh(self):
        """refresh picture when parameter are change in the textbox\n\n"""
        self.saveparam(destroy=False)
        self.preposted()              #perform calc#
        
        self.grap_winE.figsub.clear()
        self.grap_winE.plot(self.num)
        valuesE = numpy.array([PPset.spectra.param[i] for i in ["kmin", "kmax"]])
        self.grap_winE.paramplot(valuesE, ["g"]*2, ["kmin", "kmax"])
        self.grap_winE.panor(self.num)
        
        self.grap_winF.figsub.clear()        
        self.grap_winF.plot(self.num)
        self.grap_winF.panor(self.num)
        
        
            
    def panor2(self,event):
        """when the params are moved slider is moved"""
        self.num=int(event)
        self.preposted()
        self.grap_winE.panor(self.num)
        self.grap_winF.panor(self.num)
            
           
            
    
    def saveparam(self, destroy=True):
        ##########################################################################
        def error_message(Name):
            print "\nPlease write a numerical value for "+ Name +"\n" +  \
                     "for Larch default, write \"None\" or \"default\" \n"
        ##########################################################################
        def check_input(Name, variable, default):
            xxx=variable.get()
            if "default" in xxx:PPset.spectra.param[Name]=default
            elif xxx=='None':PPset.spectra.param[Name]=default  
            else:
                try:   PPset.spectra.param[Name] = round(float(variable.get()),2)
                except SyntaxError:error_message(Name)
        ##########################################################################        
        check_input("Fkmin",self._kstart,0)
        check_input("Fkmax",self._kend,None)
        check_input("dk",self._dk,1)
        PPset.spectra.param["window"] = self._FTWind.get()        
        PPset.spectra.param["Fkweight"] = self.FTweigth.get()
        if destroy:
            self.genitore.destroy()
        return
        


    ##################










        
 
















        
 









###########################################################################################clas####
class EXAFT():
    def __init__(self, genitore):
      #-------------------------------    declare    ----------------------------------------------
        self._check_FT    = IntVar()
        self._check_exa   = IntVar()
        self.kweigthplot  = IntVar()
        packLabelFrame = {"side" : LEFT,  "expand" : YES, "anchor" : W, "pady" : 3}
        packEntry      = {"side" : LEFT,   "anchor" : W, "pady" : 6, "padx" : 3, "fill" : X }   # "expand" : YES,
      #---------------------------------  set      ------------------------------------------

        self._check_exa.set(1)
        self.kweigthplot.set(1)
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
        self.button_FT_default = Button(self.quadro_FT1,
                                        command = self.FTparam,
                                        text = "FT param.",
                                        background = "violet",
                                        width = 10,
                                        padx = "3m",
                                        pady = "2m")
        self.button_FT_default.pack(side = LEFT, anchor = W, padx = 5, pady = 2)
        self.quadro_FT2 = Frame(self.quadro_FT)    #,text = "Correction"
        self.quadro_FT2.pack(side = TOP,  fill = BOTH, pady=2,expand= YES,)

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
        self.exa_PlSa_But.y_array= [item.chi*item.k**w for item in PPset.spectra]

    def plot2(self):
        self.bkg_PlSa_But.plot()
        self.bkg_PlSa_But.graph.clear()
        self.bkg_PlSa_But.graph.plot([i.E   for i in PPset.spectra],
                                           [i.Mu  for i in PPset.spectra])
        self.bkg_PlSa_But.graph.plot( self.bkg_PlSa_But.x_array,
                                        self.bkg_PlSa_But.y_array)

    def Perform(self):
        self._check_exa.get()
        self._check_FT.get()
        #-----------------         EXAFS      ---------------------
        if self._check_exa.get():
            w = self.kweigthplot.get()
            for item in PPset.spectra:
                ceck=item.EXAFS_EX(**PPset.spectra.param)
            self.exa_PlSa_But.x_array= [item.k for item in PPset.spectra]
            self.exa_PlSa_But.y_array= [item.chi*item.k**w for item in PPset.spectra]
            self.exa_PlSa_But.comments= [item.comments[:-1] for item in PPset.spectra]
            self.exa_PlSa_But.title = "EXAFS chi*k**"+str(w)
            c1="#L k  chik**"+ str(self.kweigthplot.get())+"\n"
            for item in self.exa_PlSa_But.comments: item.append(c1)
            self.bkg_PlSa_But.x_array= [item.E for item in PPset.spectra]
            self.bkg_PlSa_But.y_array= [item.bkg for item in PPset.spectra]
            self.bkg_PlSa_But.comments= [item.comments[:-1] for item in PPset.spectra]
            for item in self.bkg_PlSa_But.comments: item.append("#L E  bkg\n")
        #-----------------         FT      ---------------------
        if self._check_FT.get():
            w = self.FTweigth.get()
            k_min=float(eval(self._kstart.get()))
            k_max=float(eval(self._kend.get()))
            _dk  =float(eval(self._dk.get()))
            for item in PPset.spectra:
                item.FT_F( k_min , 0 ,k_max, _dk, self.FTweigth.get(), self._FTWind.get())
            self.FTMg_PlSa_But.x_array= [item.r for item in PPset.spectra]
            self.FTMg_PlSa_But.y_array= [item.mag for item in PPset.spectra]
            self.FTMg_PlSa_But.comments= [item.comments[:-1] for item in PPset.spectra]
            self.FTMg_PlSa_But.title = "FT chi*k**"+str(w)
            c1="#L R  FT_Mg"+str(self.FTweigth.get())+"\n"
            for item in self.exa_PlSa_But.comments: item.append(c1)
            self.FTMg_PlSa_But.title = "FT chi*k**"+str(w)
            c1= "#L R  FT_Im*k**"+str(self.FTweigth.get())+"\n"
            for item in self.FTMg_PlSa_But.comments: item.append(c1)
            self.FTIm_PlSa_But.x_array= [item.r for item in PPset.spectra]
            self.FTIm_PlSa_But.y_array= [item.imag for item in PPset.spectra]
            self.FTIm_PlSa_But.comments= [item.comments[:-1] for item in PPset.spectra]
            c1="#L R  FT_Im"+str(self.FTweigth.get())+"\n"
            for item in self.FTIm_PlSa_But.comments: item.append(c1)
        return

    def EXAFSparam(self):
        if hasattr(self, "topX"): return
        self.topX = Toplevel()
        self.topX.title("EXAFS PARAMETER") 
        self.EXE_par=EXAFSparam(self.topX)
        del self.EXE_par
        del self.topX
        
    def FTparam(self):
        if hasattr(self, "topX"): return
        self.topX = Toplevel()
        self.topX.title("FT PARAMETER") 
        self.FT_par=FTparam(self.topX)
        del self.FT_par
        del self.topX

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
   for i in filenames:
       PPset.spectra.append(bm29.bm29file(i))
   x=range(1,len(PPset.spectra)+1)    
   radice = Tk()
   radice.title("EXAFS GUI")
   pippo = EXAFT(radice)
   radice.mainloop()