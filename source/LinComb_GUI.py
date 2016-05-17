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


from   Tkinter import *
import ttk
#import tkFileDialog
import numpy
import utility as ut
import bm29_tools as bt
import LinComb
import os

      
global __verbose__                                                                    
__verbose__=False#True
global __version__
__version__= "a.0.0.1"







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
class STANDARD(LabelFrame):
    def __init__(self, master, **kw):
        LabelFrame.__init__(self,*[master], **kw)
      #-------------------------------    declare    ----------------------------------------------
        self._label=StringVar()
        self._mini= StringVar()
        self._maxi=StringVar()
        self._start_value=StringVar()
        self._fix= IntVar()
        self._active= IntVar()
      #-------------------------------    define     ----------------------------------------------       
        self._label.set("")
        self._maxi.set("1.01")
        self._mini.set("-0.01")
        self._start_value.set("auto")
        self._fix.set(0)
        self._active.set(1)
      #-------------------------------    geometry    ----------------------------------------------
        self.configure(bg="Moccasin")
        self.file_sel = ut.Browsefile_plot_mono(self, "Sample singlefile", 1)
        self.file_sel.quadro1.pack(side = TOP, expand = YES, fill = X , anchor = N,
                              ipadx = 0, ipady = 0, pady=0)
        self.file_sel.quadro_Br.pack(side = LEFT, expand = YES, fill = X , anchor = W,
                                  ipadx = 5, ipady = 0)
        self.file_sel.fse.quadro_selezione.pack( pady=0,ipady = 0)
        self.file_sel.fse.pulsanteA.configure(command= self.Browsefile2, height=1)
        self.file_sel.fse.pulsanteA.pack(side = LEFT, expand = NO, ipadx = 5, ipady = 0 ,pady =0)
        
        
        frame1=Frame(self)
        frame1.pack(side=TOP, fill=X,anchor=W, ipadx = 0, ipady = 0 )
        lab_pack ={"row" : 0, "sticky": N+S  ,  "ipadx" : 0, "ipady" : 0, "padx": 3}
        zgrid=lambda x: lab_pack.update({"column":x}) or lab_pack
        ut.LabelCheck(frame1, Ltext = "Active",Var=self._active,
                      manager="grid",labelframepack=zgrid(0),
                      entrypack ={"side" : LEFT, "padx" : 5, "ipady" : 0})
        ut.LabelEntry(frame1, Ltext = "Start Value", EtextVar=self._start_value,
                      manager="grid",labelframepack=zgrid(2),
                      entrypack ={"side" : LEFT, "padx" : 5, "ipady" : 0})
        ut.LabelCheck(frame1, Ltext = "Fix", Var=self._fix, 
                      manager="grid",labelframepack=zgrid(4),
                      entrypack ={"side" : LEFT, "padx" : 5, "ipady" : 0})
        ut.LabelEntry(frame1, Ltext = "Label", EtextVar=self._label,
                      manager="grid",labelframepack=zgrid(6),
                      entrypack ={"side" : LEFT, "padx" : 5, "ipady" : 0, "pady" : 0})   
        ut.LabelEntry(frame1, Ltext = "min", EtextVar=self._mini,
                      manager="grid",labelframepack=zgrid(8),
                      entrypack ={"side" : LEFT, "padx" : 5, "ipady" : 0, "pady" : 0})
        ut.LabelEntry(frame1, Ltext = "max", EtextVar=self._maxi,
                      manager="grid",labelframepack=zgrid(10),
                      entrypack ={"side" : LEFT, "padx" : 5, "ipady" : 0, "pady" : 0})
      #-------------------------------    Destroy button    ----------------------------------------------        
        self.DelButton= Button(frame1, command = self.destroy,
                      text = "Del",
                      width = 3, height=0)
        self.DelButton.grid(zgrid(11))
    #-------------------------------    End init          -----------------------------        
    def Browsefile2(self):
        self.file_sel.browse_command2()  
        self._label.set(self.file_sel.fse.labelfiletext.get()[:4])


  

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
        self.file_sel.quadro1.pack_configure(expand=False, fill=X)
        self.file_sel.fse.pulsanteA.configure(command= self.browse_command3)
      #-----------------------------      Browsefiles ---------------------------------------------        
      #-----------------------------      Range setup ---------------------------------------------  
        self.quadro_Define = LabelFrame(genitore,  text = "Setup")
        self.quadro_Define.pack(side = TOP, anchor=W, fill = X, pady= 3, ipadx = 5, ipady = 3, expand = N)  
      #-----------------------------     Select   files     --------------------------------------------------
        self.Sel_range = ut.LabelEntry(self.quadro_Define,  Ltext = "Select spectra       ex. 2,5-15,23"
                                       , EtextVar= self._sel, Ewith = 25)#
        self.Sel_range.LabFr.pack(**labelpack)
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
      #------------------------------      STANDARD      -----------------------------------------------' 
        ttk.Separator(genitore, orient=HORIZONTAL).pack(side = TOP, anchor= N, expand = N, fill = X)
        ttk.Separator(genitore, orient=HORIZONTAL).pack(side = TOP, anchor= N, expand = N, fill = X) 

        Quadro_Par2=LabelFrame(genitore, text="STANDARDS")
        Quadro_Par2.pack(side = TOP, anchor= W, expand =1, fill = BOTH, pady=0)    

        self.CanvasFrame = Canvas(Quadro_Par2)
        self.CanvasFrame.pack(side=LEFT, expand=True, fill=BOTH )
        slider = Scrollbar(Quadro_Par2, orient=VERTICAL, command=self.CanvasFrame.yview)
        slider.pack(side=LEFT, expand=0, fill=Y, anchor=W, padx=0)
        self.CanvasFrame['yscrollcommand'] = slider.set
        
        self.TableFrame2 =Frame(self.CanvasFrame)
        #self.TableFrame2.pack(side=LEFT, expand=0, fill=BOTH, anchor=W )
        self.TableFrame2.grid(column=0,row=0, sticky=N+E+W+S )
        self.CanvasFrame.bind('<Configure>', lambda evt: wippo(evt))
        self.width=0
        def wippo(evt):
            self.CanvasFrame.itemconfig(self.canvasframeid, width=evt.width)
        #####################--------define path list
        self.Path_list=list()

        self.canvasframeid=self.CanvasFrame.create_window(0, 0, anchor=NW, window=self.TableFrame2)
        self.CanvasFrame.update_idletasks()        
        self.CanvasFrame.config(scrollregion=self.CanvasFrame.bbox("all"))
          
        self.Standard_list=[]
        self.Standard_list.append(STANDARD(self.TableFrame2, text="Standard 1"))#, text="STARDARD frame"
        self.Standard_list[-1].grid(column=0,row=0, sticky=N+E+W, pady= 3, ipadx = 0, ipady = 0)
        self.TableFrame2.grid_columnconfigure(0,weight=1)
        #prova.pack(side=TOP, expand=True, fill=X)
      #-----------------------------      Perform  ---------------------------------------------
      


        ###################--------button add path
        Quadro_Par3=Frame(genitore)
        Quadro_Par3.pack(side = TOP, anchor= W, expand =N, fill = BOTH, pady=15)         
        Button(Quadro_Par3, text="Add one Standard" ,command = self.add_standard,    
                                      width = 13 
                                      ).pack(side=LEFT, padx=3, pady=1,anchor =N)
        Quadro_Par4=Frame(genitore)
        Quadro_Par4.pack(side = TOP, anchor= W, expand =N, fill = BOTH, pady=15)         
        self.Button_fit=Button(Quadro_Par4, text="FIT" ,command = self.Perform,    
                                      width = 13 
                                      )                                  
        self.Button_fit.pack(side=LEFT, padx=3, pady=1,anchor =N)                                  
                                      
    #-----------------------------      Functions  --------------------------------------                                      
 
    def add_standard(self):
        self.Standard_list.append(STANDARD(self.TableFrame2, text=""))
        #self.Standard_list[-1].grid(column=0,row=(len(self.Standard_list)-1), sticky=N+E+W, pady= 3, ipadx = 0, ipady = 0)
        self.standard_renumber_conf()   
        
    def remove_standard(self,n):
        self.Standard_list[n].destroy()
        del self.Standard_list[n]
        self.standard_renumber_conf()
        
        
    def standard_renumber_conf(self):
        for i,item in enumerate(self.Standard_list):
            item.config(text="Standard "+str(i+1))
            item.grid(row=i, sticky=N+E+W, pady= 3, ipadx = 0, ipady = 0)
            item.DelButton.config(command=lambda :self.remove_standard(i))
        self.TableFrame2.grid_columnconfigure(0,weight=1)
        self.CanvasFrame.update_idletasks()        
        self.CanvasFrame.config(scrollregion=self.CanvasFrame.bbox("all")) 



    #-----------------------------      Functions Browse --------------------------------------------
    def browse_command3(self):
        self.file_sel.browse_command2()        
        self._fromf.set(min(self.file_sel.spectra[0].x))
        self._tof.set(max(self.file_sel.spectra[0].x))   
        self._sel.set("1-"+ str(len(self.file_sel.spectra)))
    #-----------------------------      Functions  Param---------------------------------------------
    def ranges(self):
        if not hasattr(self.file_sel, "spectra"):
            print "\n"*5+"#"*20+"\nno spectra defined\n"
            return
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
    
        #self.grap_win.onmoving=self.onmoving
        
      
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
        global linear_comb
        global sel  # define the range of spectra used
        global x_array
        sel=ut.string_range(self._sel.get())
        x_array=self.file_sel.x_array[0]
        start, end =  self.retr_ranges()    
        Lista_Standard=LinComb.standard_list()
        def float2(x):
            try:
                return float(x)
            except:
                return None
        for item in self.Standard_list:
            if item._active.get():
                if item._label.get() in Lista_Standard.keys():
                   item._label.set(item._label.get()[:-1]+str(self.Standard_list.index(item))) 
                Lista_Standard.add(LinComb.standard(label=item._label.get(),
                                                x=item.file_sel.spectra[0].x,
                                                y=item.file_sel.spectra[0].y,
                                                x0=x_array,
                                                value=float2(item._start_value.get()),
                                                fix=float2(item._fix.get()),
                                                mini=float2(item._mini.get()),
                                                maxi=float2(item._maxi.get())
                                                ))
                



        linear_comb=list()
        trunc=lambda x : bt.dat_Truncate([x_array,self.file_sel.spectra[x].y], start, end)
        #for the column in selected spectra
        for column in sel:
            x,y=trunc(column)
            linear_comb.append(LinComb.LinComb(
                               x,y, Lista_Standard))

        self.Coeff=list()
        self.Coeff_error=list()
        self.residual=list()
        self.total=list()
        self.total_error=list()
        self.chisq=list()
        # non so perche??
        linear_comb[0].solve()
        for item in linear_comb:
            item.solve()
            value=[par.param.value for par in item.standards_list.itervalues()]
            error=[par.stderr for par in item.standards_list.Standard_Parameters.itervalues()]
            self.Coeff.append(value)
            self.Coeff_error.append(error) 
            self.total.append(sum(value))
            self.total_error.append(sum(error))            
            self.residual.append(item.result.residual)
            self.chisq.append(item.result.chisqr)
        #print self.Coeff    
        self.Coeff=numpy.transpose(numpy.array(self.Coeff))    
        self.Coeff_error=numpy.transpose(numpy.array(self.Coeff_error)) 
        print "#"*20,"\nFit Done"
            
        


#########################################################################################################
##################################       REsults     ####################################################
        
class Results_Plot(LabelFrame):
    def __init__(self, genitore):
        
        
        self.plot = Frame(genitore)
        self.plot.pack(fill=BOTH)

        self.quadro_PlotP1 = LabelFrame(self.plot, text ="Plotp1")
        self.quadro_PlotP1.pack(side = TOP, expand = YES, anchor=N, fill =X)
        self.quadro_PlotP1.grid_columnconfigure(0, weight=1)
        self.quadro_PlotP1.grid_columnconfigure(1, weight=1)

        
        self.quadro_n1Bu= LabelFrame(self.quadro_PlotP1, text="Compare")
        self.quadro_n1Bu.grid(column=0,row=0, sticky=N+E+W+S )
        self.n1_PlSa_But=ut.PloteSaveB(self.quadro_n1Bu, ext="" ,comment= ["Compare single spectra\n"], title="sample")
        self.n1_PlSa_But.Button_plot.configure(command=self.Compare)
        self.n1_PlSa_But.Button_save.configure(command=self.Compare_save)       
        
        self.quadro_n2Bu= LabelFrame(self.quadro_PlotP1, text="chisq")
        self.quadro_n2Bu.grid(column=1,row=0, sticky=N+E+W+S)
        self.n2_PlSa_But=ut.PloteSaveB(self.quadro_n2Bu, ext="" ,comment= ["chisq evolution\n"], title="Residuals")

        
        self.quadro_n3Bu= LabelFrame(self.quadro_PlotP1, text="Coeff.")
        self.quadro_n3Bu.grid(column=0,row=1, sticky=N+E+W+S )
        self.n3_PlSa_But=ut.PloteSaveB(self.quadro_n3Bu, ext="" ,comment= ["coefficent\n"], 
                                       title="Coeff.",error=True, xlabel="spectra",ylabel="Fraction" )
        
        self.quadro_n4Bu= LabelFrame(self.quadro_PlotP1, text="Sum of coeff.")
        self.quadro_n4Bu.grid(column=1,row=1, sticky=N+E+W+S )
        self.n4_PlSa_But=ut.PloteSaveB(self.quadro_n4Bu, ext="" ,comment= ["Sum of coeff.\n"], 
                                       title="Sum of coeff.",error=True)
            
    
    
    
    def Comn_res(self):
        global linear_comb
        global sel
        global x_array
        spectro=[]
        #------------------------
        name=[]
        for standard_name in linear_comb[0].standards_list:
            name.append(standard_name)
        #------------------------
        D=ut.datalize(*[item.y0 for item in linear_comb[0].standards_list.itervalues()])
        self.total=numpy.dot(D,self.Coeff)
        
        for i,item  in enumerate(linear_comb):
            component=D*self.Coeff.T[i]
            spectro.append(Cspectro(item.x, item.y,self.total.T[i],item.result.residual,name,*component.T))
        return spectro,name
        
    def Compare_save(self):
        global linear_comb
        if hasattr(self,"total"):      pass
        else:   spectro,name =self.Comn_res()
        self.n1_PlSa_But.x_array=[x_array for i in linear_comb]
        self.n1_PlSa_But.y_array=[item.y for item  in linear_comb]
        self.n1_PlSa_But.z_array=[self.total.T[i] for i in range(len(linear_comb))]
        self.n1_PlSa_But.save()
        
        

    def Compare(self):
        if hasattr(self,"total"):      pass
        else:   spectro,name =self.Comn_res()
        self.num=0
        self.top = Toplevel()
        self.top.title("COMPARES  ")#+ str(self.comp.get())+ " component")        
      #--------------------------   Graphic win  --------------------------------------------------
        self.graphframe = Frame(self.top)        
        self.graphframe.pack(side = LEFT, fill=BOTH, expand =YES)
        self.grap_win=ut.ParamGraph(self.graphframe, spectro, "x", ["exp","sim","res"]+name)
        self.grap_win.plot(self.num)

class Cspectro:
    def __init__(self,x,y,z,r,name,*args):
        self.x=x
        self.exp=y
        self.sim=z
        self.res=r
        for i,item in enumerate(name):
            setattr(self,item,args[i])

#########################################################################################################
##################################       ITFA     #######################################################
#########################################################################################################
#########################################################################################################



class LinComb_GUI:
    def __init__(self, genitore):
        

        os.chdir(os.path.join(os.environ['HOMEDRIVE'],os.environ['HOMEPATH']))
        #menu
        self.menu=mymenu(genitore)
        self.menu.filemenu.entryconfig(index=0, command= lambda : self.Setlimit("opensf"))    


        self.nb = ttk.Notebook(genitore)
        self.nb.pack(expand=True, fill=BOTH)
  
        #----------------------------------------------------------------------
        self.p1 = Frame(self.nb)
        self.nb.add(self.p1, text="Setup, Standards")

        self.SETUP= SETUP(self.p1)
        self.SETUP.Button_fit.configure(command= self.perform_FIT)
        #-----------------------------------------------------------------------
        self.p2 = Frame(self.nb)        
        self.nb.add(self.p2, text="FIT results")
        self.Results= Results_Plot(self.p2)
        #self.PCA.pul_compo.configure(command= self.reduce_c)        
        #-----------------------------------------------------------------------
        #self.p3 = Frame(self.nb)        
        #self.nb.add(self.p3, text="ITTFA_G")
        #self.ITTFA_G= ITTFA_G(self.p3)
        #genitore.rowconfigure(0,weigh=1)
        #genitore.columnconfigure(0,weigh=1)

    #--------------------Perform PCA--------------------------------------------
    def perform_FIT(self):
        global sel  # define the range of spectra used
        self.SETUP.Perform()
        self.Results.Coeff=self.SETUP.Coeff
        
        #compare individual fit                 
        self.Results.n1_PlSa_But.x_array=[sel for item in self.SETUP.Coeff]
        self.Results.n1_PlSa_But.y_array=list(self.SETUP.Coeff)
        self.Results.n1_PlSa_But.z_array=list(self.SETUP.Coeff_error)
        self.Results.n1_PlSa_But.legend=list( name for name in linear_comb[0].standards_list)

        
        #chisq
        self.Results.n2_PlSa_But.x_array=[sel]
        self.Results.n2_PlSa_But.y_array=[self.SETUP.chisq]
        
        
        self.Results.n4_PlSa_But.x_array=[sel]
        self.Results.n4_PlSa_But.y_array=[self.SETUP.total]
        self.Results.n4_PlSa_But.z_array=[self.SETUP.total_error]

        "Coeff."
        self.Results.n3_PlSa_But.x_array=[sel for item in self.SETUP.Coeff]
        self.Results.n3_PlSa_But.y_array=list(self.SETUP.Coeff)
        self.Results.n3_PlSa_But.z_array=list(self.SETUP.Coeff_error)
        self.Results.n3_PlSa_But.legend=list( name for name in linear_comb[0].standards_list)
        self.Results.n3_PlSa_But.comments[0]+="".join(["nb_spectra   ","  ".join(name for
                            name in linear_comb[0].standards_list),"\n"])
        
        try:
            del self.Results.total
        except:
            pass
        

        #for item in linear_comb:
        #                                       [item.NumDer.x_int for item in spectra]
        #        self.derivate_PlSa_But.y_array= [item.NumDer.deriv for item in spectra]
        #        self.derivate_PlSa_But.comments= [item.comments[:-1] for item in spectra]
            

            
        
        #self.PCA.Perform()
        #self.nb.select(1)
        


        



if __name__ == "__main__":
   radice = Tk()
   radice.title("LinearCom_GUI")
   pippo = LinComb_GUI(radice)
   #radice.protocol("WM_DELETE_WINDOW", destroy)
   radice.mainloop()








