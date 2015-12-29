from Tkinter import *
import tkFileDialog
import bm29_tools as bt
import utility               
import matplotlib
matplotlib.interactive(False)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

class REBIN:
  def __init__(self, genitore):
  
    #--- costanti per il controllo della disposizione
    #--- dei pulsanti

   
    # impostazione delle variabili di controllo Tkinter,
    # controllate dai pulsanti radio
    self.Edgep = StringVar()
    self.Prep = StringVar()
    self.Postp = StringVar()
    self.Edges = StringVar()
    self.Pres = StringVar()
    self.Posts = StringVar()
    self.labelfiletext = StringVar()
    self.before = StringVar()
    self.after = StringVar()   
    
    self.Edgep.set(24350)
    self.Prep.set(30)
    self.Postp.set(20)
    self.Edges.set(.5)
    self.Pres.set(5)
    self.Posts.set(.03)
     
    

    #---------------

    self.mioGenitore = genitore
    #self.mioGenitore.geometry("640x400")
    
    
    ### Il quadro principale si chiama 'quadro_grande'
    self.quadro_grande = Frame(genitore) ###
    self.quadro_grande.pack(expand = YES, fill = BOTH)	
    ### Viene usata l'orientazione ORIZZONTALE (da sinistra a expand = YES,
    ### destra) all'interno di 'quadro_grande'.
    ### Dentro 'quadro_grande' si creano 'quadro_controllo' e


    # 'quadro_controllo' - praticamente tutto tranne la
    # dimostrazione
    self.quadro_controllo = Frame(self.quadro_grande) ###
    self.quadro_controllo.pack(side = TOP, fill = BOTH, padx = 10,
                               pady = 5, ipadx = 5, ipady = 5)

    # All'interno di 'quadro_controllo' si creano un'etichetta
    # per il titolo e un 'quadro_pulsanti'

    mioMessaggio = "REBIN"
    Label(self.quadro_controllo,
      text = mioMessaggio,
      justify = LEFT).pack(side = TOP, anchor = W)


    ################################################################################################        
    # 'quadro_fileselezione'
    self.filesel = utility.Browse_file(self.quadro_controllo, "Qexafs", 0)                     
    self.filesel.pulsanteA.configure(command= self.browse_command2)
    ################################################################################################
    #if hasattr(self.filesel, 'spectra'):  self.spectra = self.filesel.spectra
    #if hasattr(self.filesel, 'spectra'):  print "pippo"
    ################################################################################################   
    #'Quadro_Truncate
    self.quadro_Trun = LabelFrame(self.quadro_controllo,
           text = "Truncate")    
    self.quadro_Trun.pack(side = TOP, expand = YES, fill = BOTH,
                              ipadx = 5, ipady = 5)    
    self.quadro_before = LabelFrame(self.quadro_Trun,
           text = "before")
    self.quadro_after = LabelFrame(self.quadro_Trun,
           text = "after")
    self.quadro_before.pack(side = LEFT, expand = YES,
                                   fill = BOTH, anchor = N, ipadx = 5, ipady = 5)
    self.quadro_after.pack(side = LEFT, expand = YES,
                                   fill = BOTH, anchor = N,ipadx = 5, ipady = 5)

    self._entry_before= Entry(self.quadro_before,
         width = 20, textvariable=self.before)   
    self._entry_before.pack(side = LEFT, expand = NO,
                               ipadx = 5, ipady = 3)
    self._entry_after= Entry(self.quadro_after,
         width = 20, textvariable=self.after)   
    self._entry_after.pack(side = LEFT, expand = NO,
                               ipadx = 5, ipady = 3)

    
    
    
    ################################################################################################   
    # 'quadro_Range'
    self.quadro_range = LabelFrame(self.quadro_controllo,
           text = "Range")    
    self.quadro_range.pack(side = LEFT, expand = YES, fill = BOTH,
                              ipadx = 5, ipady = 5)

    # Si aggiungono alcuni sottoquadri a 'Range'
    self.quadro_Edgep = LabelFrame(self.quadro_range,
           text = "Edge in eV")
    self.quadro_Prep = LabelFrame(self.quadro_range,
           text = "Preedge")
    self.quadro_Postp = LabelFrame(self.quadro_range,
           text = "EXAFS")
    self.quadro_Edgep.pack(side = TOP, expand = YES,
                                   fill = BOTH, anchor = N, ipadx = 5, ipady = 5)
    self.quadro_Prep.pack(side = TOP, expand = YES,
                                   fill = BOTH, anchor = N,ipadx = 5, ipady = 5)
    self.quadro_Postp.pack(side = TOP, expand = YES,
                                   fill = BOTH, anchor = N,ipadx = 5, ipady = 5
    )


  
    self._entry_Edgep= Entry(self.quadro_Edgep,
         width = 20, textvariable=self.Edgep)   
    self._entry_Edgep.pack(side = LEFT, expand = NO,
                               ipadx = 5, ipady = 3)
    self._entry_Prep= Entry(self.quadro_Prep,
         width = 20, textvariable=self.Prep)   
    self._entry_Prep.pack(side = LEFT, expand = NO,
                               ipadx = 5, ipady = 3)
    self._entry_Postp= Entry(self.quadro_Postp,
         width = 20,textvariable=self.Postp)   
    self._entry_Postp.pack(side = LEFT, expand = NO,
                               ipadx = 5, ipady = 3,
    )


    # 'quadro_step'
    self.quadro_step = LabelFrame(self.quadro_controllo,
           text = "Step",
    )    
    self.quadro_step.pack(side = LEFT, expand = YES, fill = BOTH,
                              ipadx = 5, ipady = 5)

    # Si aggiungono alcuni sottoquadri a 'step'
    self.quadro_Edges = LabelFrame(self.quadro_step,
           text = "Edge")
    self.quadro_Pres = LabelFrame(self.quadro_step,
           text = "Preedge")
    self.quadro_Posts = LabelFrame(self.quadro_step,
           text = "EXAFS")
    self.quadro_Edges.pack(side = TOP, expand = YES,
                                   fill = BOTH, anchor = N, ipadx = 5, ipady = 5)
    self.quadro_Pres.pack(side = TOP, expand = YES,
                                   fill = BOTH, anchor = N,ipadx = 5, ipady = 5)
    self.quadro_Posts.pack(side = TOP, expand = YES,
                                   fill = BOTH, anchor = N,ipadx = 5, ipady = 5)

    self._entry_Edges= Entry(self.quadro_Edges,
         width = 20,textvariable=self.Edges)   
    self._entry_Edges.pack(side = LEFT, expand = NO,
                               ipadx = 5, ipady = 3)
    self._entry_Pres= Entry(self.quadro_Pres,
         width = 20,textvariable=self.Pres)   
    self._entry_Pres.pack(side = LEFT, expand = NO,
                               ipadx = 5, ipady = 3)
    self._entry_Posts= Entry(self.quadro_Posts,
         width = 20,textvariable=self.Posts)   
    self._entry_Posts.pack(side = LEFT, expand = NO,
                               ipadx = 5, ipady = 3
    )
################################################################################################   

    # 'pulsanti finali'
    self.quadro_pulsanti = Frame(self.quadro_grande )    
    self.quadro_pulsanti.pack(side = LEFT, expand = YES, fill = BOTH,padx = 10,
                              pady = 5,
                              ipadx = 5,
			      ipady = 5)    
    self.pulsante_rebsave = Button(self.quadro_pulsanti,
                                   command = self.rebinfiles,
                                  text = "Rebin and save", 
                                  background = "violet", 
                                  width = 15, 
                                  padx = "3m", 
                                  pady = "2m")
    self.pulsante_rebsave.pack(side = LEFT, anchor = N)
    self.pulsante_plot = Button(self.quadro_pulsanti,
    	    			  command = self.plot,
                                  text = "Plot", 
                                  background = "green", 
                                  width = 15, 
                                  padx = "3m", 
                                  pady = "2m")
    self.pulsante_plot.pack(side = LEFT, anchor = N
    )


        
        
        
  def rebinfiles(self):
    Eo = float(eval(self.Edgep.get()))
    predg= float(eval(self.Prep.get()))
    postedg = float(eval(self.Postp.get()))
    xstep = float(eval(self.Edges.get()))
    pstep = float(eval(self.Pres.get()))
    kstep = float(eval(self.Posts.get())) 
    pstep = float(eval(self.Pres.get()))
    kstep = float(eval(self.Posts.get()))     
    trunbef= float(eval(self.before.get()))/1000
    trunaft= float(eval(self.after.get()))/1000  

    self.spectra = self.filesel.spectra
    for item in self.spectra:
        print "pippo1"
        rebdata=bt.dat_Truncate(item.data, trunbef, trunaft)    
        rebdata = bt.rebin(rebdata, 0, Eo, predg, postedg, pstep, xstep, kstep, file='', msgStream=None) 
        writefile = item.fullfilename +".reb"
        item.bm29write(writefile,rebdata)
                                 


  def plot(self):
    #print self.Edgep 
    Eo = float(eval(self.Edgep.get()))
    predg= float(eval(self.Prep.get()))
    postedg = float(eval(self.Postp.get()))
    xstep = float(eval(self.Edges.get()))
    pstep = float(eval(self.Pres.get()))
    kstep = float(eval(self.Posts.get())) 
    pstep = float(eval(self.Pres.get()))                            
    kstep = float(eval(self.Posts.get()))     
    trunbef= float(eval(self.before.get()))/1000
    trunaft= float(eval(self.after.get()))/1000  
    item = self.filesel.spectra[0]
    rebdata = bt.dat_Truncate(item.data, trunbef, trunaft)
    try:                
       rebdata=bt.rebin(rebdata, 0, Eo, predg, postedg, pstep, xstep, kstep, file='', msgStream=None)
    except bt.RebinError, e: 
       self.graph = utility.Graph(e.parameter)
       self.graph.plot([item.E,rebdata[:,0]*1000], [item.Mu,rebdata[:,1]],["original","Truncated"],e.parameter+"\n only truncated data")
       return
    self.graph = utility.Graph("")
    self.graph.plot([item.E, rebdata[:,0]*1000], [item.Mu,rebdata[:,1]],["original","rebinned"])
    return
                
              
  def browse_command2(self):
    self.filesel.browse_command()
    self.before.set((min(self.filesel.spectra[0].EkeV))*1000)
    self.after.set((max(self.filesel.spectra[0].EkeV))*1000)
    #print "pippo"                                     
	                                                         
	 
if __name__ == "__main__":	 
        radice = Tk()
        pippo = REBIN(radice)
        radice.mainloop()                                   

    
