
import matplotlib
matplotlib.use('TkAgg')
from  utility import Browse_file 
matplotlib.interactive(False)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from Tkinter import *
import tkFileDialog
import bm29_tools as bt
import numpy                                                                                                  




        



class Correct:
    def __init__(self, genitore):
        
        #--- costanti per il controllo della disposizione
        #--- dei pulsanti
        # impostazione delle variabili di controllo Tkinter,
        # controllate dai pulsanti radio
        self._dsold = StringVar()                                                            
        self._dsnew = StringVar()
        self._dsse = StringVar()
        self._pos  = StringVar()
        self._npos  = StringVar()
        self._dspos = StringVar() 
        self._dsse = StringVar() 
        self._dsold.set(3.13542)
        self._dsnew.set(3.13467)
        self._dsse.set(3.13467)
        self._pos.set(7200)
        self._npos.set(7200)
        self._dspos.set(7123)       
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
                                                                                             
        # 'quadro_fileselezione'
        self.filesel = Browse_file(self.quadro_controllo, "Filenames", 0)                      
        
        # 'quadro_standard'
        self.standardsel = Browse_file(self.quadro_controllo, "Standard", 1) 
        ################################################################################################
        # 'quadro_change dspacing'
        self.quadro_ds = LabelFrame(self.quadro_controllo)    #,text = "Correction"
        self.quadro_ds.pack(side = TOP, expand = YES, fill = BOTH,ipadx = 5, ipady = 3)
        # Si aggiungono alcuni sottoquadri a 'dspacing'
        self.chds = IntVar()
        self.quadro_check_ds = LabelFrame(self.quadro_ds, text = "Change d-spacing")
        self.quadro_check_ds.pack(side = TOP, expand = YES,  anchor = W ,ipadx = 5, ipady = 9) #fill = X,
        self.check_ds=Checkbutton(self.quadro_check_ds, textvariable="pippo" ,variable=self.chds, )
        self.check_ds.pack(side = LEFT, expand = YES, fill = BOTH, anchor = N,ipadx = 5, ipady = 1)
        
        self.quadro_dslimits = Frame(self.quadro_ds)
        self.quadro_dslimits.pack(side = TOP, expand = YES, fill = BOTH, anchor = N,ipadx = 5, ipady = 5)
        
        self.quadro_dsold = LabelFrame(self.quadro_dslimits, text = "old-d spacing")
        self.quadro_dsold.pack(side = LEFT, expand = YES, fill = BOTH, anchor = N,ipadx = 5, ipady = 5)
        self._entry_ds_old= Entry(self.quadro_dsold, width = 20, textvariable=self._dsold)
        self._entry_ds_old.pack(side = LEFT, ipadx = 5, ipady = 3)
        
        self.quadro_dsnew = LabelFrame(self.quadro_dslimits, text = "new-d spacing")
        self.quadro_dsnew.pack(side = LEFT, expand = YES, fill = BOTH, anchor = N,ipadx = 5, ipady = 5)
        self._entry_ds_new= Entry(self.quadro_dsnew, width = 20, textvariable=self._dsnew)
        self._entry_ds_new.pack(side = LEFT, ipadx = 5, ipady = 3)
        
        self.quadro_dspos = LabelFrame(self.quadro_dslimits, text = "Edge position")
        self.quadro_dspos.pack(side = LEFT, expand = YES, fill = BOTH, anchor = N,ipadx = 5, ipady = 5)
        self._entry_dspos= Entry(self.quadro_dspos, width = 20, textvariable=self._dspos)
        self._entry_dspos.pack(side = LEFT, ipadx = 5, ipady = 3)
        ###################################################################################################
        
        
        
        
        ##################################################################################################
        # 'quadro_Shift Edge '
        self.quadro_se = LabelFrame(self.quadro_controllo)    #,text = "Correction"
        self.quadro_se.pack(side = TOP, expand = YES, fill = BOTH,ipadx = 5, ipady = 3)
        # Si aggiungono alcuni sottoquadri a 'dspacing'
        self.chse = IntVar()
        self.quadro_check_se = LabelFrame(self.quadro_se, text = "Constant angle Shift Edge")
        self.quadro_check_se.pack(side = TOP, expand = YES,  anchor = W ,ipadx = 5, ipady = 1) #fill = X,
        self.check_se=Checkbutton(self.quadro_check_se, textvariable="pippo" ,variable=self.chse)
        self.check_se.pack(side = LEFT, expand = YES, fill = BOTH, anchor = S,ipadx = 5, ipady = 5)
        
        self.quadro_selimits = Frame(self.quadro_se)
        self.quadro_selimits.pack(side = TOP, expand = YES, fill = BOTH, anchor = N,ipadx = 5, ipady = 5)
        
        self.quadro_dsold = LabelFrame(self.quadro_selimits, text = "d spacing")
        self.quadro_dsold.pack(side = LEFT, expand = YES, fill = BOTH, anchor = N,ipadx = 5, ipady = 5)
        self._entry_ds_old= Entry(self.quadro_dsold, width = 20, textvariable=self._dsse)
        self._entry_ds_old.pack(side = LEFT, ipadx = 5, ipady = 3)

        self.quadro_pos = LabelFrame(self.quadro_selimits, text = "Energy Edge")
        self.quadro_pos.pack(side = LEFT, expand = YES, fill = BOTH, anchor = N,ipadx = 5, ipady = 5)
        self._entry_se_pos= Entry(self.quadro_pos, width = 20, textvariable=self._pos)
        self._entry_se_pos.pack(side = LEFT, ipadx = 5, ipady = 3)
        self.quadro_npos = LabelFrame(self.quadro_selimits, text = "New Energy Edge")
        self.quadro_npos.pack(side = LEFT, expand = YES, fill = BOTH, anchor = N,ipadx = 5, ipady = 5)
        self._entry_se_npos= Entry(self.quadro_npos, width = 20, textvariable=self._npos)
        self._entry_se_npos.pack(side = LEFT, ipadx = 5, ipady = 3)
        ########################################################################################### 
        



        ########################################################################################### 
        # 'quadro_button '
        self.quadro_button1 = Frame(self.quadro_controllo)
        self.quadro_button1.pack(side = TOP, expand = YES, fill = BOTH,pady = 10,
                                  ipadx = 5, ipady = 5)
        self.pulsante_preview = Button(self.quadro_button1,
                                      command = self.plotall,
                                      text = "Preview first file",
                                      background = "violet",
                                      width = 15,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_preview.pack(side = LEFT, anchor = W)           
    
        self.pulsante_Doit = Button(self.quadro_button1,
                              command = self.Correct_file,
                              text = "Do it",
                              background = "violet",
                              width = 15,
                              padx = "3m",
                              pady = "2m")
        self.pulsante_Doit.pack(side = LEFT, anchor = W)  
    ###########################################################################################
        


                                    
    def Correct_file(self):
        if (self.chse.get()) or (self.chds.get()):      
            if self.chds.get():                                                                            
                spos=   float(eval(self._dspos.get()))
                sold =  float(eval(self._dsold.get()))
                snew  = float(eval(self._dsnew.get()))    
                if self.chse.get():
                    p1= float(eval(self._pos.get()))          
                    p2= float(eval(self._npos.get()))  
                    ds_1= float(eval(self._dsse.get()))
                    ashift = bt.E2T(p2, ds_1)-bt.E2T(p1, ds_1)
                else: ashift =0
                for item in self.filesel.spectra:
                    item.E= bt.dspa_A_change(self.filesel.spectra[0].E, dsold , dsnew ,dspos ,ashift)
                    writefile = item.fullfilename +".cor"
############change for Bm29 files comment
                    bt.writedata(writefile,vstack((item.E,item.Mu)))
            elif self.chse.get():  
                ds_1= float(eval(self._dsse.get()))
                p1= float(eval(self._pos.get()))
                p2= float(eval(self._npos.get()))  
                shift = bt.E2T(p2, ds_1)-bt.E2T(p1, ds_1) 
                for item in self.filesel.spectra:
                    item.E= bt.Ashif(self.filesel.spectra[0].E,ds_1,shift)
                    writefile = item.fullfilename +".cor"
                    bt.writedata(writefile,vstack((item.E,item.Mu)))
            

                                                                                              
    def plotall(self):
        if (self.chse.get()) or (self.chds.get()):      
            if self.chds.get():                                                                            
                dspos=   float(eval(self._dspos.get()))
                dsold =  float(eval(self._dsold.get()))
                dsnew  = float(eval(self._dsnew.get()))    
                if self.chse.get():
                    p1= float(eval(self._pos.get()))          
                    p2= float(eval(self._npos.get()))  
                    ds_1= float(eval(self._dsse.get()))
                    ashift = bt.E2T(p2, ds_1)-bt.E2T(p1, ds_1)
                else: ashift =0    
                self.E1= bt.dspa_A_change(self.filesel.spectra[0].E, dsold , dsnew ,dspos ,ashift)
            elif self.chse.get():         
                ds_1= float(eval(self._dsse.get()))
                p1= float(eval(self._pos.get()))
                p2= float(eval(self._npos.get()))  
                shift = bt.E2T(p2, ds_1)-bt.E2T(p1, ds_1) 
                print "correct pippo1", shift , ds_1,  p1, p2
                self.E1= bt.Ashif(self.filesel.spectra[0].E,ds_1,shift)
        else:  self.E1= self.filesel.spectra[0].E
        #pylab.interactive(True) 
        if  not(hasattr(self, 'top')) or not(self.top.winfo_exists()):                                             
             self.top = Toplevel()
             self.top.title('Grafico')
             self.fig = matplotlib.figure.Figure(figsize=(5,4), dpi=100)
             self.canvas = FigureCanvasTkAgg(self.fig, master = self.top)
             self.toolbar = NavigationToolbar2TkAgg(self.canvas,  self.top )
             self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
             self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)                 
             self.figsub = self.fig.add_subplot(111)
             self.figsub.set_autoscale_on(True)                                  
             self.lines = self.figsub.plot(self.standardsel.spectra[0].E, self.standardsel.spectra[0].Mu, label ="standard")
             self.lines += self.figsub.plot(self.E1, self.filesel.spectra[0].Mu, label ="file")
             self.figsub.set_ylabel("Mu (a.u.)", fontsize = 8)
             self.figsub.set_xlabel("Energy (eV)", fontsize = 8)
             self.toolbar.update()   
             print  "pippo"       
             self.figsub.legend()
             self.canvas.draw()                                 
        self.lines[1].set_xdata(self.E1)
        self.figsub.set_autoscale_on(False)
        self.canvas.draw()                 

######################################################################################################################
                                          
if __name__ == "__main__":
  radice = Tk()
  pippo = Correct(radice)
  #pippo.Show()
  radice.mainloop()








