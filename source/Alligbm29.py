#Name: Alligbm29.py
# Purpose: A script to perform BM29 Qexafs allignment                        
# Author: C. Prestipino at Rennes university
#                                                                               
#                                  
# Copyright 2007 ESRF
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
# Except as contained in this notice, the name of Illinois Institute
# of Technology shall not be used in advertising or otherwise to promote
# the sale, use or other dealings in this Software without prior written
# authorization from Illinois Institute of Technology. 



import utility
import matplotlib
#matplotlib.use('TkAgg')
import utility                                                                  
import bm29_tools
from Tkinter import *
matplotlib.interactive(False)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg   

class allign:
    def __init__(self, genitore):
        self.Ash = StringVar()                                           
        self.Ash.set(0.00000)
        #---------------
        self.mioGenitore = genitore                                         
        self.mioGenitore.geometry("640x400")
        self.quadro_grande = Frame(genitore) ###
        self.quadro_grande.pack(expand = YES, fill = BOTH)
        self.quadro_controllo = Frame(self.quadro_grande) ###
        self.quadro_controllo.pack(side = TOP, fill = BOTH, padx = 10,
                                   pady = 5, ipadx = 5, ipady = 5)
        
        # All'interno di 'quadro_controllo' si creano un'etichetta
        # per il titolo e un 'quadro_pulsanti'
        mioMessaggio = "Bm29 QEXAFS backslash allignment"
        Label(self.quadro_controllo,                                        
          text = mioMessaggio,
          justify = LEFT).pack(side = TOP, anchor = W)
          
          
        ################################################################################################        
        # 'quadro_fileselezione'
        self.filesel = utility.Browse_file(self.quadro_controllo, "Qexafs", 1)                      

        # 'quadro_standard'
        self.standardsel = utility.Browse_file(self.quadro_controllo, "Standard", 1) 
        ################################################################################################
        self.Aslider = Scale( self.quadro_controllo, from_=-.05, to=.05,
                                                     command= self.setredraw,
                                                     variable= self.Ash, 
                                                     resolution=0.001,
                                                     orient=HORIZONTAL,
                                                     label= "Angular shift")
        self.Aslider.pack(side = TOP,fill = BOTH, anchor = W,pady = 15, ipady = 0)
        ################################################################################################
      #'quadro_change dspacing' and Angular shift
        self.quadro_ds_A = LabelFrame(self.quadro_controllo)    #,text = "Correction"
        self.quadro_ds_A.pack(side = TOP, expand = YES, fill = BOTH,ipadx = 5, ipady = 3)
        self.quadro_A = LabelFrame(self.quadro_ds_A, text = "Angular shift")
        self.quadro_A.pack(side = LEFT, expand = NO, fill = BOTH, anchor = N,ipadx = 5, ipady = 5)
        self.entry_A= Entry(self.quadro_A, width = 20, textvariable = self.Ash)
        self.entry_A.pack(side = LEFT, ipadx = 5, ipady = 3)
        self.entry_A.bind("<Key>", self.keymove)
        self.pulsante_Mu = Button(self.quadro_ds_A,
                                      command = self.plot_Mu,                   
                                      text = "Plot  Mu",
                                      background = "violet",
                                      width = 15,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Mu.pack(side = RIGHT, anchor = E)
        self.pulsante_MuFp = Button(self.quadro_ds_A,
		                      command = self.plot_MuFp,                   
                                      text = "Plot MuFp",
                                      background = "violet",
                                      width = 15,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_MuFp.pack(side = RIGHT, anchor = E)
	                                              
        #self.lbl = Label(self.quadro_ds_A, text = "", bg = "white", fg = "seagreen", font=("arial", 16, "bold") )
        #self.lbl.pack(side = RIGHT, anchor = E)
        ################################################################################################

     
    def plot_Mu(self):
        shift=float(self.Ash.get())
        self.pulsante_Mu.configure(relief="sunken")
        self.pulsante_MuFp.configure(relief="raised")
        self.Ec= bm29_tools.Ashif(self.filesel.spectra[0].E, self.filesel.spectra[0].dspac ,shift)        
        if  not(hasattr(self, 'top')) or not(self.top.winfo_exists()): 
             self.cr_graph()
             self.qexaplot = self.figsub.plot(self.standardsel.spectra[0].E, self.standardsel.spectra[0].Mu, label ="standard")
             self.qexaplot += self.figsub.plot(self.Ec, self.filesel.spectra[0].Mu, label ="file")     
             self.figsub.set_ylabel("Mu (a.u.)", fontsize = 8)
             self.figsub.set_xlabel("Energy (eV)", fontsize = 8)
             self.toolbar.update()   
             self.figsub.legend()
             self.canvas.draw()                                            
             self.figsub.set_autoscale_on(False)
        else:                                                                                     
            self.qexaplot[0].set_ydata(self.standardsel.spectra[0].Mu)
            self.qexaplot[1].set_ydata(self.filesel.spectra[0].Mu)
            print type(self.filesel.spectra[0].Mu)
            ymin=min(list(self.filesel.spectra[0].Mu) + list(self.standardsel.spectra[0].Mu))
            ymax=max(list(self.filesel.spectra[0].Mu)+list(self.standardsel.spectra[0].Mu))
            srange = (ymax-ymin) 
            ymin = ymin - abs(srange*.1) 
            ymax = ymax + abs(srange*.1)	       
            #print ymax                      
            self.figsub.axis([self.standardsel.spectra[0].E[0]-20,
                      self.standardsel.spectra[0].E[-1]+20,
                      ymin, ymax])	     
            self.drawagain()
            self.figsub.set_autoscale_on(False)                                      
                           

                                                                                         

    def plot_MuFp(self):
        self.pulsante_Mu.configure(relief="raised")
        self.pulsante_MuFp.configure(relief="sunken")	    
        self.filesel.spectra[0].bm29derE()
        self.standardsel.spectra[0].bm29derE()
        shift=float(self.Ash.get())    
        self.Ec= bm29_tools.Ashif(self.filesel.spectra[0].E, self.filesel.spectra[0].dspac ,shift)        
        if  not(hasattr(self, 'top')) or not(self.top.winfo_exists()):
             self.cr_graph()
             self.qexaplot = self.figsub.plot(self.standardsel.spectra[0].E, self.standardsel.spectra[0].E_MuFp, label ="standard")
             self.qexaplot += self.figsub.plot(self.Ec, self.filesel.spectra[0].E_MuFp, label ="file")     
             self.figsub.set_ylabel("first derivative Mu (a.u.)", fontsize = 8)
             self.figsub.set_xlabel("Energy (eV)", fontsize = 8)        
             self.figsub.legend()
             self.canvas.draw()                                 
        else: 
         #self.figsub.set_autoscale_on(True)
         print self.figsub.set_autoscale_on(True)     
         self.qexaplot[0].set_ydata(self.standardsel.spectra[0].E_MuFp)
         self.qexaplot[1].set_ydata(self.filesel.spectra[0].E_MuFp)
         ymin=min(list(self.filesel.spectra[0].E_MuFp)+list(self.standardsel.spectra[0].E_MuFp))     
         ymax=max(list(self.filesel.spectra[0].E_MuFp)+list(self.standardsel.spectra[0].E_MuFp))
         srange = (ymax-ymin) 
         ymin = ymin - abs(srange*.1)
         ymax = ymax + abs(srange*.1)
         self.figsub.axis([self.standardsel.spectra[0].E[0]-20,
                       self.standardsel.spectra[0].E[-1]+20,
                   ymin, ymax]) 
         self.drawagain()                   
         self.figsub.set_autoscale_on(False)        
                                                      

    def keymove(self,event):
        shift=self.Ash.get()
        #print type(event.char)
        #print shift                                  
        try:
          if int(event.char) in range(10):
               shift+=event.char
               print shift
        except:
              print shift, type(shift)   
        if  (hasattr(self.filesel, 'spectra') ):           #and hasattr(self.standardsel, 'spectra')
             self.Ec= bm29.Ashif(self.filesel.spectra[0].E, self.filesel.spectra[0].dspac , float(shift))
             self.drawagain()
                     
    def setredraw(self,value):
        pippo = value
        #self.lbl.configure(text= pippo)         
        #self.Ash.set(str(pippo))                                                                                         
        if  (hasattr(self.filesel, 'spectra') ):           #and hasattr(self.standardsel, 'spectra')
             self.Ec= bm29_tools.Ashif(self.filesel.spectra[0].E, self.filesel.spectra[0].dspac ,float(pippo))
             self.drawagain()
             #self.fig.refresh()
             #pylab.focus()                           
             #radice.focus()
        pass                                                                                   



    def cr_graph(self,title='Grafico'):  
        self.top = Toplevel()                                                    
        self.top.title(title)
    #self.top.protocol("WM_DELETE_WINDOW", self.topcallback)
        self.fig = matplotlib.figure.Figure(figsize=(5,4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.top)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas,  self.top )
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)                 
        self.figsub = self.fig.add_subplot(111)
        self.figsub.set_autoscale_on(True)   
    
    def topcallback(self):
        self.pulsante_Mu.configure(relief="raised")
        self.pulsante_MuFp.configure(relief="raised")
        self.top.destroy()
    
    
    def drawagain(self): 
             self.qexaplot[1].set_xdata(self.Ec)              
             self.fig.canvas.draw()                                                                     

if __name__ == "__main__":                                                
  radice = Tk()
  pippo = allign(radice)
  radice.mainloop()
                                                                
