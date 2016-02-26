from   Tkinter import *
import bm29                                                                           
import numpy
import utility as ut
import bm29_tools as bt
import Rebin
#import zipfile for zipped files


import PPset




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
        self.num=0
        self.top = Toplevel()
        self.top.title("REBIN PARAMETER")        
       #--------------------------   Prepare group  --------------------------------------------------
        dif =lambda x: numpy.argmax(numpy.gradient(x.mu)/numpy.gradient(x.energy))
        Eo=PPset.filesel_spectra[0].energy[dif(PPset.filesel_spectra[0])]
        self.Edgep.set(Eo)
        self.evaluatepar()
       #--------------------------   Graphic win  --------------------------------------------------
        self.graphframe = Frame(self.top)        
        self.graphframe.pack(side = TOP, fill=BOTH, expand=YES)
        self.grap_win=ut.ParamGraph(self.graphframe, PPset.filesel_spectra, "energy", ["mu",])
        self.grap_win.plot(self.num)        
        self.grap_win.paramplot(self.get_param(), ["b","g","k","r","b"], 
                                ["Min","XAN","Eo","EXAFS","Max"])
        if len(PPset.filesel_spectra)>1:
            self.grap_win.slider.configure(command= self.panor2)
        #self.grap_win.onmoving=self.onmoving
        self.grap_win.canvas.mpl_disconnect(self.grap_win.mov_link)
        self.grap_win.mov_link=self.grap_win.canvas.mpl_connect(
                                           'motion_notify_event', self.onmoving)

    def evaluatepar(self):
        Eo=float(eval(self.Edgep.get()))
        E=PPset.filesel_spectra[self.num].energy
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
        spec=  PPset.filesel_spectra[self.num]
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
        listcomment=[]
        comment="#"
        if self._c_aver.get() and (self._aver.get()>1):
            comment+= " averaged each {0:4d} spectra,".format(aver)
            self.lista_iter = range(0,len(filesel),aver)
            for item in self.lista_iter:
                list_ave=[PPset.filesel_spectra[ii] for ii in filesel[item:item+aver]]                
                E, Mu  = bt.spectra_average([[i.E,i.Mu]for i in list_ave])
                PPset.spectra.append(bm29.bm29file([E,Mu]))
                try:
                    PPset.spectra[-1].T1=bt.dat_average(
                          [i.T1 for i in PPset.filesel_spectra[item:item+aver]])
                    PPset.spectra[-1].T2=bt.dat_average(
                          [i.T2 for i in PPset.filesel_spectra[item:item+aver]])
                except: pass
                try:
                    PPset.spectra[-1].start_time_ep=bt.dat_average(
                        [i.start_time_ep for i in PPset.filesel_spectra[item:item+aver]])
                except: pass
                listcomment.append(PPset.filesel_spectra[item].comments)
        else:
            for item  in [PPset.filesel_spectra[i] for i in filesel]:
                data = numpy.transpose(numpy.vstack((item.E,item.Mu)))
                PPset.spectra.append(bm29.bm29file(data))
                try:    PPset.spectra[-1].T1=item.T1
                except: pass
                try:    PPset.spectra[-1].T2=item.T2
                except: pass
                try:    PPset.spectra[-1].start_time_ep=item.start_time_ep
                except: pass
                listcomment.append(item.comments)

        if self._c_Trun.get():
            comment+= " truncate between {0:5.9f} and{1:5.9f} ,".format(trunbef, trunaft)              
            for i,item in enumerate(PPset.spectra):
                data = numpy.transpose(numpy.vstack((item.E,item.Mu)))
                data = bt.dat_Truncate(data, trunbef, trunaft)
                PPset.spectra[i].E, PPset.spectra[i].Mu = map(numpy.ravel, 
                                                              numpy.hsplit(data,2))
                #spectra[i]=bm29.bm29file(data)
                    
        if self._c_Rebin.get():
            comment+= " rebin with param.{0:5.7f},{1:5.7f},{2:5.7f},{3:5.7f},{4:5.7f},{5:5.7f},".format(Eo, predg, postedg, pstep, xstep, kstep)  
            for i,item in enumerate(PPset.spectra):
                data = numpy.transpose(numpy.vstack((item.E,item.Mu)))
                try:
                   data=bt.rebin(data, 0, Eo, predg, postedg, pstep, xstep, kstep, file='', msgStream=None)
                   PPset.spectra[i]=(bm29.bm29file(data))
                except bt.RebinError, self.rebinerror:
                   top = Toplevel()
                   Label(top, text = "Rebin not performed      " + self.rebinerror.parameter).pack(expand = YES)
                   break
        
        
        if comment== "#": comment = "#L E  Mu  \n"
        else: comment = comment[:-1]+"\n" +"#L E  Mu  \n" 
        for i, item in enumerate(PPset.spectra) :
            listcomment[i][-1]= comment
            item.comments= listcomment[i]
        x=range(1,len(PPset.spectra)+1)
        self.Avesel_PlSa_But.x_array= [item.E for item in PPset.spectra]
        self.Avesel_PlSa_But.y_array= [item.Mu for item in PPset.spectra]
        self.Avesel_PlSa_But.comments= [item.comments for item in PPset.spectra]
        
        print "\n---module average done---\n"       
        pass
    
    
    
if __name__ == "__main__":
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
       PPset.filesel_spectra.append(bm29.bm29file(i))
   x=range(1,len(PPset.spectra)+1)    
   radice = Tk()
   radice.title("Avesel")
   pippo = Avesel(radice)
   pippo.before.set(round(min(PPset.filesel_spectra[0].energy),2))
   pippo.after.set(round(max(PPset.filesel_spectra[0].energy),2))
   radice.mainloop()    