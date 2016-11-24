import ttk
from   Tkinter import *
import tkFileDialog
import bm29                                                                           
import numpy
import utility as ut
import bm29_tools as bt
import exapy
import os
import ConfigParser
#import zipfile for zipped files
import text
from scipy import interpolate
try:
     from PyMca5.PyMcaIO.specfile import Specfile
except ImportError:
     from PyMca.specfile import Specfile
    
import PPset

from PPset import filesel_spectra as fil_spec



def getfloats(txt):
    words = [w.strip() for w in txt.replace(',', ' ').split()]
    try:
        return [float(w) for w in words]
    except:
        return None    


class Define_attt:
    def __init__(self,genitore,value,pos1, pos2): 
      #-----------------------------      Declare      --------------------------------------------------        
        self._name=StringVar()
        self.line=int(pos1.split('.')[0])-1
        self.value=value
      #-----------------------------      Define       --------------------------------------------------
        self._name.set('T1')
        self.dying=False
        self.pos1=pos1
        self.pos2=pos2        
      #-----------------------------      Structure    --------------------------------------------------        
        self.attr = Frame(genitore)
        self.attr.pack(side=TOP, expand=YES, fill=X, anchor=N)
        self.NameLabel = Label(self.attr,  text = "Name")
        self.NameLabel.pack(side = LEFT, anchor=W, fill = X, pady= 3, ipadx = 5, ipady=5)
        self.NameEntry = Entry(self.attr,  textvariable =  self._name, width=6, justify=CENTER )
        self.NameEntry.pack(side = LEFT, anchor=W, fill = X, pady= 1, ipadx = 2, ipady=5)
        self.ValueLabel = Label(self.attr,  text = '= %s'%value, justify=LEFT)
        self.ValueLabel.pack(side = LEFT, anchor=W, fill = X, expand=YES, pady= 3, ipadx = 5, ipady=5)   
        self.deleteB = Button(self.attr,
                                      command = self.delete,
                                      text = "Del",
                                      background = "Violet",
                                      width = 3,
                                      padx = "1m",
                                      pady = "1m")
        self.deleteB.pack(side = LEFT, anchor = E, pady = 1, padx=1) 
        self.NameEntry.focus()
      #--------------------------   Function --------------------------------------------------
    def delete(self):
        self.attr.destroy()
        self.dying=True
##########################        Gen importer   ################################################################
class Col_line_Gen:
    def __init__(self, genitore, label, array, row): 
      #-----------------------------      Declare      --------------------------------------------------
        self._check= IntVar()
        self._label=label
        self._position= IntVar()
        self._compo=IntVar()

      #-----------------------------      Define       --------------------------------------------------  
        self.array=array 
        row= row
        self._check.set(False)
      #-----------------------------      Structure    --------------------------------------------------
        self.check = Checkbutton(genitore, variable=self._check, width=2)#, command=self.underline )
        self.check.grid(row= row, column=0)
        
        self.label= Label(genitore, text=self._label)
        self.label.grid(row= row, column=1)       
        
        self.column= Spinbox(genitore, from_ = 1, to = self.array.shape[1], 
                             textvariable= self._position, width = 3)      
        self.column.grid(row= row, column=2)
        
        self.pulsante_Plot = Button(genitore ,
                                      command = self.plot,
                                      text = "Plot",
                                      background = "DeepPink2",
                                      width = 7,
                                      padx = "1m",
                                      pady = "1m")
        self.pulsante_Plot.grid(row= row, column=3)   
        
      #-----------------------------      Functios    --------------------------------------------------
    def plot(self): 
        title= "{0:s}  column {1:d}".format(self._label, int(self._position.get()))
        x_array=[numpy.arange(self.array.shape[0])]
        y_array=[self.array[:,int(self._position.get())-1]]
        graph = ut.Graph()
        graph.plot(x_array, y_array, title= title)




##########################        Gen importer   ################################################################

class Column_Window:
    def __init__(self,filenames):
      #--------------------------   Declare-------------------------------------------------
        self.filenames=filenames
        #self._ChaCom=StringVar()
        self._mode=StringVar()
        
        self._ChaSpl=StringVar()
      #--------------------------   Define--------------------------------------------------  
        self.column_names=["E", "Mu", "Ref", "I0", "I1", "I2"]
        self.column_list=[]
        self._mode.set("transmission")
        
        self._ChaSpl.set('=:,')
      #--------------------------  Top level + reload--------------------------------------------------        
        #self.top_txt = Toplevel()
        #self.top_txt.title("view  first file")         

        self.top = Toplevel(takefocus=True)
        self.top.title("define column of interest")    

        self.win_text = Frame(self.top) 
        self.win_text.pack(side=LEFT,expand=YES, fill=BOTH)
        self.text=text.ScrolledText( parent=self.win_text, file=self.filenames[0],hor=True, active=False)

        self.top_con= Frame(self.top) 
        self.top_con.pack(side=LEFT,expand=YES)

        self.win_comment = Frame(self.top_con)
        self.win_comment.pack(side=TOP,expand=YES)
        self.win_comment.focus()

        #Label(self.win_comment,text="Comment character").grid(row= 0, column=0) 
        #self.Entry_Value =Entry(self.win_comment, textvariable =  self._ChaCom, width=8, justify=CENTER )
        #self.Entry_Value.grid(row= 0, column=1) 
        #self.Reload_B = Button(self.win_comment, text="Reload array" ,
        #                              command = self.load,
        #                              background = "Violet",
        #                              width = 13,
        #                              padx = "3m",
        #                              pady = "2m").grid(row= 0, column=2)
      #--------------------------   Params  Entries--------------------------------------------------
        self.win_column = Frame(self.top_con)
        self.win_column.pack(side=TOP,expand=YES)
      #--------------------------   Mode array --------------------------------------------------        

        self.quadro_mode = Frame(self.win_column)
        self.quadro_mode.pack(side = TOP, anchor=W, fill = X, pady= 0, ipadx = 0, ipady = 0, expand = N)
        
        self.combo_type= ttk.Combobox(self.quadro_mode , textvariable=self._mode, state ="readonly",
                    values=("transmission", "fluorescence"))
        self.combo_type.pack(side = LEFT)       
        
        self.quadro_column = Frame(self.win_column)
        self.quadro_column.pack(side = TOP,  fill = X)
        
      #--------------------------   Header-------------------------------------------------- 
      
        Label(self.quadro_column, text="Use       ").grid(row=0, column=0) 
        Label(self.quadro_column, text="   ").grid(row=0, column=1)        
        Label(self.quadro_column, text="Column   ").grid(row=0, column=2)
        Label(self.quadro_column, text="    ").grid(row=0, column=3)  
        Label(self.quadro_column, text="   ").grid(row=0, column=4)  
      #--------------------------   Set lines --------------------------------------------------        
        self.load()

      #--------------------------   Button --------------------------------------------------
        self.quadro_buttonp = Frame(self.win_column)      
        self.quadro_buttonp.pack(side = TOP,  fill = X) 
        self.buttonMu = Button(self.quadro_buttonp,
                                      command = self.Muplot,
                                      text = "plot Mu",
                                      background = "Violet",
                                      width = 13,
                                      padx = "3m",
                                      pady = "3m")
        self.buttonMu.pack(side = LEFT, anchor = W,pady = 10, padx=5)
        self.buttonRef = Button(self.quadro_buttonp,
                                      command = self.Refplot,
                                      text = "plot Ref",
                                      background = "Violet",
                                      width = 13,
                                      padx = "3m",
                                      pady = "3m")
        self.buttonRef.pack(side = LEFT, anchor = W,pady = 10, padx=5) 
      #--------------------------   Button --------------------------------------------------        
        self.quadro_button = Frame(self.win_column)      
        self.quadro_button.pack(side = TOP,  fill = X) 
        self.save_cons = Button(self.quadro_button,
                                      command = self.opens,
                                      text = "Define Column",
                                      background = "Green",
                                      width = 13,
                                      padx = "3m",
                                      pady = "3m")
        self.save_cons.pack(side = LEFT, anchor = W,pady = 10, padx=5) 

  
        
      #--------------------------   Wait --------------------------------------------------    
        self.top.wait_window()
      #--------------------------   Function --------------------------------------------------
    

            
    
    def load(self):
        if self.column_list==[]:
            with open(self.filenames[0]) as f: data=f.readlines()
            header=[item for item in data[0:50] if not(getfloats(item))]
            self.array=numpy.loadtxt(fname=data,  skiprows =len(header))
            for i,item in enumerate(self.column_names):
                    self.column_list.append(Col_line_Gen(self.quadro_column, label=item, array=self.array,
                                         row=i+1))          
        return

    def Muplot(self):
        E=self.array[:,int(self.column_list[0]._position.get())-1]
        if self.column_list[1]._check.get():
            Mu=self.array[:,int(self.column_list[1]._position.get())-1]
        elif self.column_list[3]._check.get() and self.column_list[4]._check.get():
            I0=self.array[:,int(self.column_list[3]._position.get())-1] 
            I1=self.array[:,int(self.column_list[4]._position.get())-1]           
            if self._mode.get()=="transmission":Mu=numpy.log(I0/I1)
            elif self._mode.get()=="fluorescence":Mu=I1/I0
        else: raise ValueError("\n\nneither Mu nor I0-I1 defined\n\n") 
        graph = ut.Graph()
        graph.plot( [E],[Mu], title= "Mu")
        
   
        
    def Refplot(self):    
        E=self.array[:,self.column_list[0]._position.get()-1]
        if self.column_list[2]._check.get():
            Ref=self.array[:,int(self.column_list[2]._position.get())-1] 
        elif self.column_list[5]._check.get() and self.column_list[4]._check.get():
            I1=self.array[:,int(self.column_list[4]._position.get())-1] 
            I2=self.array[:,int(self.column_list[5]._position.get())-1]
            Ref=numpy.log(I1/I2)
        graph = ut.Graph()
        graph.plot( [E], [Ref], title= "Ref")


    def opens(self):
        
        #check minimum information
        colsname=[item._label for item in self.column_list if 
                                                             item._check.get()]
        if ('Mu' in colsname):pass
        elif  ('I0' in colsname) and ('I1' in colsname): pass                                                     
        else: 
            raise ValueError("neither Mu nor I0-I1 defined") 
            return

        #remove frame
        self.top_con.pack_forget()
        self.top_attr= Frame(self.top) 
        self.top_attr.pack(side=LEFT,expand=YES, fill=BOTH)
        self.win_attr = Frame(self.top_attr)
        self.win_attr.pack(side=TOP,expand=YES, fill=BOTH,anchor=N)
        
        Label(self.win_attr,text="splitter character").pack(side=TOP,expand=NO, fill=Y, anchor=N) 
        self.Entry_Value =Entry(self.win_attr, textvariable =  self._ChaSpl, width=8, justify=CENTER )
        self.Entry_Value.pack(side=TOP,expand=NO, anchor=N)
        Label(self.win_attr, text="select value and click righ mouse on text\n"+
             "to add new attribute").pack(side=TOP,expand=NO, fill=X,anchor=N) 
        self.frame_attr= Frame(self.win_attr)
        self.frame_attr.pack(side=TOP,expand=YES, fill=Y)
        self.quadro_button2 = Frame(self.win_attr)      
        self.quadro_button2.pack(side = TOP,  fill = X) 
        self.save_conss = Button(self.quadro_button2,
                                      command = self.opens2,
                                      text = "Define Attr",
                                      background = "Green",
                                      width = 13,
                                      padx = "3m",
                                      pady = "3m")
        self.save_conss.pack(side = LEFT, anchor = W,pady = 10, padx=5)    
        self.rmenu = Menu(None, tearoff=0, takefocus=0)
        self.rmenu.add_command(label='create attr', command=self.popupattr)
        self.text.text.bind('<Button-3>',self.popup)#, add='')
        self.text.text.tag_configure("selected", background="yellow")
        self.attribute_list=[]
        
    def popup(self,e):
        a,b= self.text.text.index(SEL_FIRST), self.text.text.index(SEL_LAST)
        if a==b:return
        self.rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")


        
    def popupattr(self):
        self.attribute_list=[i for i in self.attribute_list if not(i.dying)]
        text = self.text.text.get(SEL_FIRST, SEL_LAST)
        self.text.text.tag_add("selected", SEL_FIRST, SEL_LAST)
        a,b= self.text.text.index(SEL_FIRST), self.text.text.index(SEL_LAST)
        self.attribute_list.append(Define_attt(self.frame_attr,text,a,b))


    def opens2(self):
        def linesplit(line): 
            # create a line that is splitted in a list
            for itemchar in self._ChaSpl.get():
                line=line.replace(itemchar,' ')
            return line.split() 
            
        fil_spec.header=self.text.gettext()
        fil_spec.header=fil_spec.header.split('\n')
        fil_spec.header=[item+'\n' for item in fil_spec.header[0:PPset.max_head] 
                                                        if not(getfloats(item))]
        #-------------  Search if is necessary to add # in front of the file                               
        TF=lambda x: False if x[0]=='#' else True                              
        if any([TF(i) for i in fil_spec.header]):
            for i,item in enumerate(fil_spec.header):
               fil_spec.header[i]='#'+item
        fil_spec.header.append('# first file header relevant properties' \
                               '(sample temperature, ring current etc) could' \
                               'be saved in the define_x tab\n')
        # define the attributes
        fil_spec.other_pro=dict()
        texto=self.text.gettext().split('\n')
        for item in self.attribute_list:
            item.name=item._name.get()
            iline=linesplit(texto[item.line])
            item.field=iline.index(item.value)
            fil_spec.other_pro[item._name.get()]=[]
            
        #Define correspondance col position   
        cols=numpy.array(map(int,[item._position.get() for item in 
                            self.column_list if item._check.get()]))-1
        colsname=[item._label for item in self.column_list if
                                                             item._check.get()]
                                                             
        # Main cycle open all files

        pb = ttk.Progressbar(self.top_attr, orient='horizontal', mode='determinate',
                                             maximum=len(self.filenames))
        pb.pack(side=TOP,expand=NO, fill=X,anchor=N)
        try:
            for j,item in enumerate(self.filenames):
                with open(item) as f: data=f.readlines()
                i_array=numpy.loadtxt(fname=data,  skiprows =len(fil_spec.header),
                                                      usecols=cols).T
                energy=i_array[colsname.index('E')].squeeze()
                if 'Mu' in colsname:
                    mu=i_array[colsname.index('Mu')].squeeze()
                    fil_spec.append(bm29.bm29file([energy,mu]))
                else: 
                    I0=i_array[colsname.index('I0')].squeeze() 
                    I1=i_array[colsname.index('I1')].squeeze()           
                    if self._mode.get()=="transmission":mu=numpy.log(I0/I1)
                    elif self._mode.get()=="fluorescence":mu=I1/I0
                    fil_spec.append(bm29.bm29file([energy,mu]))
                    fil_spec[-1].I0=I0
                
                if 'Ref' in colsname:
                    fil_spec[-1].ref=i_array[colsname.index('Ref')].squeeze()   
                elif ('I2' in colsname) and ('I2' in colsname):
                    I2=i_array[colsname.index('I2')].squeeze() 
                    I1=i_array[colsname.index('I1')].squeeze()
                    fil_spec[-1].ref=numpy.log(I1/I2)
                
    
                for item in self.attribute_list:
                   iline=linesplit(data[item.line]) 
                   fil_spec.other_pro[item.name].append(iline[item.field])
                pb['value']=j
                pb.update_idletasks()
        except :
            print "\n\nError reading the file {}\n".format(item)
            
            
               
        # Main cycle    other_pro 
        for item in fil_spec.other_pro.keys():
            try:
               fil_spec.other_pro[item]= numpy.array(map(
                                                float,fil_spec.other_pro[item]))
            except ValueError:
               pass
        #print fil_spec.other_pro
        deriv=max(numpy.gradient(fil_spec[0].mu))
        dspac=  3.13467 if E<22500 else 1.63702
        for item in fil_spec: item.dspac=dspac
        pb['value']= len(self.filenames)
        self.top.destroy()        

        
        

##########################      SPEC  col##################################################################
##########################        Gen Qe   ################################################################
class Gen_QE():
    def __init__(self, genitore):
      #-----------------------------      Declare      --------------------------------------------------
        self.before = StringVar()
        self.after  = StringVar()
        #self.energy = StringVar()
        self._function= StringVar()
        self._function_p= StringVar()
        self._All_spectra= StringVar()
        self._c_range = IntVar()
      #-----------------------------      Define       --------------------------------------------------
        self._function.set("Ref.der.")
        self._function_p.set("Ref")        
        self._All_spectra.set("first spectra     ")        

      #-----------------------------      Windows       --------------------------------------------------
        self.filesel = ut.Browse_filename(genitore, "Filenames", 0)
        self.filesel.pulsanteA.configure(command= self.browse_command2)
      #--------------------------- Quadro correction ---------------------------------------------- 
        self.quadro_Define = LabelFrame(genitore,  text = "Allign spectra respect to")
        self.quadro_Define.pack(side = TOP, anchor=W, fill = X, pady= 3, ipadx = 5, ipady = 3, expand = N)   #, expand = YES
       #--------------------------- Quadro correction 1---------------------------------------------- 
        self.quadro_Define1 = Frame(self.quadro_Define)
        self.quadro_Define1.pack(side = TOP, anchor=W, fill = X, pady= 0, ipadx = 0, ipady = 0, expand = N)        
        self.combo_All= ttk.Combobox(self.quadro_Define1 , state ="readonly",
                                     textvariable=self._All_spectra,values=('first spectra     ', 'Calibration sample'))
        self.combo_All.pack(side=LEFT)

        
        Label(self.quadro_Define1, text=" using ").pack(side = LEFT)
        self.combo_Cal= ttk.Combobox(self.quadro_Define1 ,   textvariable=self._function,
                         values=( 'Ref.der.','Ref','-I0','Cal. Mu','Cal. der.'))
        self.combo_Cal.pack(side=LEFT)
        #self.combo_Cal.insert(0, 'Ref.der.')
    
        Frame(self.quadro_Define1).pack(side = LEFT, anchor=W, fill = X, pady= 2, ipadx = 10, padx=5, ipady = 3, expand = Y)
        Button(self.quadro_Define1,
              command = self.plot_set_Energy,
              text = "Plot  correction ",
              background = "violet",
              width = 15,
              padx = "1m",
              pady = "2m").pack(side = LEFT, anchor = W)
       #--------------------------- Quadro correction 2----------------------------------------------  
        self.quadro_Define2 = Frame(self.quadro_Define)
        self.quadro_Define2.pack(side = TOP, anchor=W, fill = X, pady= 3, ipadx = 0, ipady = 3, expand = N)  
        Label(self.quadro_Define2, text="In the range").pack(side = LEFT)    
        self.check_range=Checkbutton(self.quadro_Define2, variable=self._c_range )
        self.check_range.pack(side = LEFT,  fill = Y ,anchor = W, ipady = 1)
        Label(self.quadro_Define2, text=" between ").pack(side = LEFT)
        self.Define_before = Entry(self.quadro_Define2,   textvariable= self.before, width = 10 )#
        self.Define_before.pack(side = LEFT, padx = 5, ipadx =5  ,ipady = 3)
        Label(self.quadro_Define2, text=" and ").pack(side = LEFT)
        self.Define_after = Entry(self.quadro_Define2,   textvariable= self.after, width = 10 )
        self.Define_after.pack(side = LEFT, padx = 5,  ipadx = 5 ,ipady = 3)  
        Label(self.quadro_Define2, text=" eV ").pack(side = LEFT)
       #--------------------------- Quadro correction 3----------------------------------------------  
        self.quadro_Define3 = Frame(self.quadro_Define)
        self.quadro_Define3.pack(side = TOP, anchor=W, fill = X, pady= 0, ipadx = 0, ipady = 0, expand = N)         
        
        self.calibsel = ut.Browse_file(self.quadro_Define3, "Calibration Sample", 1)
    
      #--------------------------- Quadro plot cor ----------------------------------------------         
        self.quadro_plot = LabelFrame(genitore, text="Plot ")
        self.quadro_plot.pack(side = TOP, expand = YES, fill = X, pady = 10,
                                  ipadx = 5, ipady = 5)
        self.combo_Plot= ttk.Combobox(self.quadro_plot ,  state ="readonly",
                        textvariable=self._function_p,        values=('Ref.der.', 'Ref','-I0')  )
        self.combo_Plot.pack(side=LEFT)
   
        self.pulsante_Plot_nc = Button(self.quadro_plot ,
                                      command = lambda x= "not": self.plot_all(x),
                                      text = "not corrected",
                                      background = "DeepPink2",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Plot_nc.pack(side = LEFT, anchor = W)
        self.pulsante_Plot_c = Button(self.quadro_plot ,
                                      command = lambda z= "cor": self.plot_all(z),
                                      text = "  corrected  ",
                                      background = "DeepPink2",
                                      width = 10,
                                      padx = "3m",
                                      pady = "2m",
                                      relief="ridge",#"solid",#"groove",#"flat",
                                      state=DISABLED)
        self.pulsante_Plot_c.pack(side = LEFT, anchor = W)
      #--------------------------- Quadro perform ----------------------------------------------
        self.quadro_buttonp3 = LabelFrame(genitore, text="Apply correction")
        self.quadro_buttonp3.pack(side = TOP, expand = YES, fill = X, pady = 10,
                                  ipadx = 5, ipady = 5)
        self.pulsante_Defcor = Button(self.quadro_buttonp3,
                                      command = self.correct,
                                      text = "Apply correction",
                                      background = "Violet",
                                      width = 10,
                                      padx = "5m",
                                      pady = "2m")
        self.pulsante_Defcor.pack(side = LEFT, anchor = W)
        self.pulsante_Remcor = Button(self.quadro_buttonp3, 
                                      command = self.rem_correct,
                                      text = "Remove correction",
                                      background = "Violet",
                                      width = 10,
                                      padx = "5m",
                                      pady = "2m")
        self.pulsante_Remcor.pack(side = LEFT, anchor = W)


    ##########################function################################################################
    def browse_command2(self):
        self.filesel.browse_command()
        fil_spec[:]=[]
        
        #### inizio adjust if no trailing zeros are present on the numbers
        lungh_str=map(len,self.filesel.filenames)
        lset=set(lungh_str)
        if len(lset)>1:
          lungh_str=numpy.array(lungh_str)  
          li_ol=numpy.array(self.filesel.filenames)  
          li_ne=[]
          for lu in sorted(lset):
              li_ne.extend(li_ol[lungh_str==lu])
          self.filesel.filenames=li_ne    
        #### fine adjust if no trailing zeros are present on the numbers      
            
        
        colwin=Column_Window(self.filesel.filenames)
        #colwin.top_con.wait_window()
        self.pulsante_Defcor.configure(relief="raised")
        try:
            fil_spec[0].bm29derRef()
            Eo_test=bt.max_range(fil_spec[0].E, fil_spec[0].E_RefFp)
            self.before.set(round(Eo_test-50))
            self.after.set(round(Eo_test+50))  
            self._c_range.set(1)
        except:
            pass
        return
        


    def plot_all(self, ptype): 
        if ptype=="not":
            if hasattr(fil_spec[0], "oldE"):
                x_array=[item.oldE for item in fil_spec]
            else:
                x_array=[item.energy for item in fil_spec]
        if ptype=="cor":
            if hasattr(fil_spec[0], "oldE"):
                x_array=[item.energy for item in fil_spec]
            else: 
                print "\nCorrection still not applied\n\
                        press the button\n"
                return
        if self._function_p.get()=='Ref.der.':   
            try:
                for item in  fil_spec: item.bm29derRef()
                y_array=[item.E_RefFp for item in fil_spec]
                title="derivate reference"
            except:
                print "reference not measured"
                return            
            
        elif self._function_p.get()=='Ref':            
            try:
                y_array=[item.ref for item in fil_spec]
                title="reference"                
            except:
                print "reference not measured"
                return
        elif self._function_p.get()=='-I0':    
                y_array=[item.I0 for item in fil_spec]
                title= "I0"
        if ptype== "cor": title=title+" corrected"   
        self.graph = ut.Graph()
        self.graph.plot(x_array, y_array, title= title)
    



    def set_Energy(self):
        self.Energy_row=[]
        self._function.get()
        if self._c_range.get():
            before =float(self.before.get())
            after=float(self.after.get())
        else:
            before, after= None, None
        if self._function.get() == "-I0":
            Y= lambda x: -x.I0/abs(max(-x.I0))
        elif self._function.get() == 'Ref.':
            Y= lambda x: x.ref
        elif self._function.get() == 'Ref.der.':
            for item in fil_spec: item.bm29derRef()
            Y= lambda x: x.E_RefFp/max(x.E_RefFp)
        elif self._function.get() == 'Cal. Mu':
            Y= lambda x: x.Mu
        elif self._function.get() == 'Cal. der.':
            self.calibsel.spectra[0].bm29derRef()
            Y= lambda x: x.E_Fp/max(x.E_MuFp)            
            
        if  self._c_range.get():
            L = lambda objecto,x: x.compress((objecto.E>before)&(objecto.E<after))
        else:
            L = lambda objecto,x: x        
        if self._All_spectra.get() =='first spectra     ':
            if self._function.get() =='Cal. Mu' or self._function.get() =='Cal. der.':
                print "\nnot clear input\nasking to use first sample and calibration...."
            splinex1y1 = interpolate.splrep(fil_spec[0].E,Y(fil_spec[0]))
        elif self._All_spectra.get() =='Calibration sample':
            if self._function.get() =='Ref.' or self._function.get() =='Ref.der.':
                print "\nATTENTION you are using reference of calibration file\n"
                raise ValueError()
            try:
                splinex1y1 = interpolate.splrep(self.calibsel.spectra[0].E,Y(self.calibsel.spectra[0]))
            except:
                self.calibsel.spectra[0]=bm29.bm29file(self.calibsel.spectra[0].data)
            self.calibsel.spectra[0].bm29derE()
            if self._function.get() == 'Ref.':
                splinex1y1 = interpolate.splrep(self.calibsel.spectra[0].E, self.calibsel.spectra[0].Mu)
            elif self._function.get() == 'Ref.der.':    
                splinex1y1 = interpolate.splrep(self.calibsel.spectra[0].E, self.calibsel.spectra[0].E_MuFp)
        self.standard_Energy=bt.max_range(fil_spec[0].E, Y(fil_spec[0]),before,after) 
           
        for item in  fil_spec:
            self.Energy_row.append(float(ut.fitcalibration(x2=L(item,item.E), y2=L(item,Y(item)),
                                                     param=[0],splinex1y1=splinex1y1)))
           

        
    def plot_set_Energy(self):
        self.set_Energy()
        x_array= [range(len(fil_spec))]
        y_array= [self.Energy_row]
        self.graph = ut.Graph()
        self.graph.plot(x_array, y_array, title= "Energy shift")   

    def correct(self):
        self.set_Energy()
        if hasattr(fil_spec[0], "oldE"):            
            pass
        else:  
            for item in fil_spec: item.oldE=item.E
        for i,item in enumerate(fil_spec):
            item.energy= bt.MvEAshift(item.E,item.dspac, self.standard_Energy-self.Energy_row[i],
                                 self.standard_Energy)
        print "\nCorrection applyed\n"            
        self.pulsante_Defcor.configure(relief="sunken")
        self.pulsante_Plot_c.configure(relief="raised",state=NORMAL)
        
    def rem_correct(self):
        for item in fil_spec:
            item.energy=item.oldE
            del item.oldE    
        self.pulsante_Defcor.configure(relief="raised")
        self.pulsante_Plot_c.configure(relief="ridge",state=DISABLED)        
        print "\nCorrection removed\n"
            
       
##################################       DispCal    #####################################################
class DispCal():
    def __init__(self, genitore):
      #-----------------------------      Declare      --------------------------------------------------
        self.A = StringVar()
        self.B = StringVar()
        self.C = StringVar()
        self._r =StringVar()
        self.v = IntVar()
        self.v.set(2)


      #-----------------------------      Define      --------------------------------------------------
        self.A.set(0)
        self.B.set(1)
        self.C.set(0)
      #-----------------------------      geometry      --------------------------------------------------
        self.Cal_sel = ut.Browse_filename(genitore, "Calibration sample", 1)
        self.Disp_sel = ut.Browse_filename(genitore, "Dispersive Calibration sample", 1)
        self.quadro_Title = Frame(genitore)
        self.quadro_Title.pack(side = TOP, anchor= W, expand = Y, fill = BOTH)
        Label(self.quadro_Title, text= " Energy = A + B*Pixel + C*Pixel**2             ").pack(side=LEFT, anchor=N)
        Radiobutton(self.quadro_Title, text="Write text",
                                        variable=self.v,
                                        value=1,
                                        command= self.radio_command
                                        ).pack(side=LEFT,   anchor=N)
        Radiobutton(self.quadro_Title, text="Use sliders",
                                        variable=self.v,
                                        value=2,
                                        command= self.radio_command
                                        ).pack(side=LEFT,  anchor=N)
      #-----------------------------      Calibration---------------------------------------------
        self.quadro_sliders = Frame(genitore)
        self.quadro_sliders.pack(side = TOP, anchor= W, expand = Y, fill = BOTH)
        self.quadro_A = Frame(self.quadro_sliders)
        self.quadro_A.pack(side =TOP, fill=BOTH)
        self.Aslider = Scale( self.quadro_A, from_=-.05, to=.05,
                                            command= self.setredraw_A,
                                            variable= self.A,
                                            resolution=0.0000001,
                                            orient=HORIZONTAL, # label= "A",
                                            showvalue=0
                                            )
        self.Aslider.pack(side = LEFT,fill = X, anchor = W,pady = 3, ipady = 0, expand = Y)
        Label(self.quadro_A,text= " A ").pack(side=LEFT)#, anchor = SW
        #self.entry_A= Entry(self.quadro_A, width = 9, textvariable = self.A)
        #self.entry_A.pack(side = LEFT, ipadx = 5, ipady = 1, fill = Y, pady= 2)
        #self.entry_A.bind("<Key>", self.keymove)
        #self.entry_A.bind("<Return>", self.keyenter)
        self.quadro_B = Frame(self.quadro_sliders)
        self.quadro_B.pack(side =TOP, fill =BOTH)
        self.Bslider = Scale( self.quadro_B,
                                     from_=0, to=1.5,
                                     command= self.setredraw_B,
                                     variable= self.B,
                                     resolution=0.00001,
                                     orient=HORIZONTAL,#label= "Angular shift"
                                     showvalue=0,
                                     )
        self.Bslider.pack(side = LEFT,fill = X, anchor = W,pady = 3, ipady = 0, expand = Y)
        Label(self.quadro_B,text= " B ").pack(side=LEFT)
        self.quadro_C = Frame(self.quadro_sliders)
        self.quadro_C.pack(side =TOP, fill=BOTH)
        self.Cslider = Scale( self.quadro_C, from_=-.00005, to=.00005,
                             command= self.setredraw_B,
                             variable= self.C,
                             resolution=0.00000001,
                             orient=HORIZONTAL,
                             showvalue=0,
                             )
        self.Cslider.pack(side = LEFT,fill = X, anchor = W,pady = 3, ipady = 0, expand = Y)
        Label(self.quadro_C,text= " C ").pack(side=LEFT)



        self.quadro_ABCtext = Frame(genitore)
        self.quadro_ABCtext.pack(side = TOP, expand = N, fill = X, pady = 2,
                                  ipadx = 5, ipady = 5)
        self.entry_A= Entry(self.quadro_ABCtext, width = 9, textvariable = self.A, state='readonly')
        self.entry_A.pack(side = LEFT, ipadx = 5, ipady = 1, fill = None, pady= 2)
        Label(self.quadro_ABCtext, text= " A   ").pack(side=LEFT)
        self.entry_B= Entry(self.quadro_ABCtext, width = 9, textvariable = self.B, state='readonly')
        self.entry_B.pack(side = LEFT, ipadx = 5, ipady = 1, fill = None, pady= 2)
        Label(self.quadro_ABCtext, text= " B   ").pack(side=LEFT)
        self.entry_C= Entry(self.quadro_ABCtext, width = 9, textvariable = self.C, state='readonly')
        self.entry_C.pack(side = LEFT, ipadx = 5, ipady = 1, fill = None, pady= 2)
        Label(self.quadro_ABCtext, text= " C   ").pack(side=LEFT)




        self.quadro_buttonp1 = Frame(genitore)
        self.quadro_buttonp1.pack(side = TOP, expand = N, fill = X, pady = 2,
                                  ipadx = 5, ipady = 5)
        self.pulsante_plot = Button(self.quadro_buttonp1,
                                      command = self.plot,
                                      text = "Plot Mu",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_plot.pack(side = LEFT, anchor = W)
        self.pulsante_dplot = Button(self.quadro_buttonp1,
                                      command = self.dplot,
                                      text = "Plo Derivative",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_dplot.pack(side = LEFT, anchor = W)
        self.pulsante_Fitder = Button(self.quadro_buttonp1,
                                      command = self.fitder,
                                      text = "Fit Derivative",
                                      background = "violet",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Fitder.pack(side = LEFT, anchor = W)        
        
        


        self.pulsante_Select = Button(self.quadro_buttonp1,
                                      command = self.select,
                                      text = "Select",
                                      background = "Green",
                                      width = 8,
                                      padx = "3m",
                                      pady = "2m")
        self.pulsante_Select.pack(side = LEFT, anchor = W)

        self.quadro_push = Frame(genitore)
        self.quadro_push.pack(side = TOP, expand = YES, fill = BOTH,pady = 10,
                                  ipadx = 5, ipady = 5)




      #-----------------------------      Browsefiles ---------------------------------------------
        self.filesel = ut.Browse_filename(genitore, "Experiment Filenames", 0)
        self.filesel.pulsanteA.configure(command= self.browse_command2)



    #def keymove(self,event):
        #self.entry_A.configure(bg="yellow")
        #self.entry_B.configure(bg="yellow")
        #self.entry_C.configure(bg="yellow")
    #    pass

    #def keyenter(self,event):
        #self.A.get()
        #self.B.get()
        #self.C.get()
        #self.entry_A.configure(bg="white")
        #self.entry_B.configure(bg="white")
        #self.entry_C.configure(bg="white")
    #    pass

    def radio_command(self):
        
        if self.v.get() ==1:
                              #use text
            self.Aslider.configure(variable= 0,  state = DISABLED, )   #command= None,
            self.Bslider.configure(variable= 1,  state = DISABLED, )   #command= None,
            self.Cslider.configure(variable= 0,  state = DISABLED, )   #command= None,
            self.entry_A.configure(state = NORMAL, )
            self.entry_B.configure(state = NORMAL, )
            self.entry_C.configure(state = NORMAL, )

        if self.v.get() ==2:   #use slider
            A=float(self.A.get())
            print A
            self.Aslider.configure(from_ = A*0.985,
                                   to =A*1.015)
            self.Aslider.configure(state = ACTIVE  ,variable=self.A)    #, command= self.setredraw_A
            self.Bslider.configure(state = ACTIVE , variable=self.B)    #,command= self.setredraw_B
            self.Cslider.configure(state = ACTIVE , variable=self.C)    #,command= self.setredraw_B
            self.entry_A.configure(state = 'readonly', )
            self.entry_B.configure(state = 'readonly', )
            self.entry_C.configure(state = 'readonly', )
        pass

    def plot(self):     
        if  self.A.get()+self.B.get()+self.C.get()=="010":
            self.pre_allig()                                         
        #if self.pulsante_dplot.configure()['relief'][-1]=='raised':
        #    self.pre_allig()
        self.graph= ut.Graph()
        self.graph.top.protocol("WM_DELETE_WINDOW", self.topcallback_plot)
        self.graph.plot([self.newE],[self.disp.Nor])  
        self.graph.plot([self.calib.E],[self.calib.Nor])             
        self.pulsante_plot.configure(relief="sunken", state=DISABLED) 


    def dplot(self):
        if  self.A.get()+self.B.get()+self.C.get()=="010":
            self.pre_allig()                                         
        #if self.pulsante_plot.configure()['relief'][-1]=='raised':
        #    self.pre_allig()
        self.graphd= ut.Graph()
        self.graphd.top.protocol("WM_DELETE_WINDOW", self.topcallback_dplot)
        self.graphd.plot([self.newE],[self.disp.E_MuFp/max(self.disp.E_MuFp)], comment=["Disp."])#self.disp.Ej])
        self.graphd.plot([self.calib.E],[self.calib.E_MuFp/max(self.calib.E_MuFp)], comment=["Calib."])#self.calib.Ej])
        self.pulsante_dplot.configure(relief="sunken", state=DISABLED)      
                                                                               
    def fitder(self):
        if  self.A.get()+self.B.get()+self.C.get()=="010":
            self.pre_allig()  
            print "get a new pre allignment"
        param=map(float,[self.A.get(),self.B.get(),self.C.get()])    
        print "param=",param
        param=ut.fitcalibration(self.calib.E, numpy.gradient(self.calib.Mu), \
                                self.disp.E, numpy.gradient(self.disp.Mu), param)
        self.A.set(param[0])
        self.B.set(param[1])
        self.C.set(param[2]) 
        
        print "fitted param=",param
        self.setredraw_A(param) 
        self.setredraw_B(param)    
        
        
        
    def pre_allig(self):
            self.calib= bm29.sfigati(self.Cal_sel.filenames[0])
            self.calib.bm29derE()
            self.calib.XANES_Norm()
            self.calib_maxi=self.calib.E_MuFp.argmax()
            print self.calib_maxi
            print self.calib.E[self.calib_maxi]

            self.disp= bm29.sfigati(self.Disp_sel.filenames[0])
            self.disp.bm29derE()
            self.disp.XANES_Norm()
            self.disp_maxi=self.disp.E_MuFp.argmax()
            print self.disp_maxi
            print self.disp.E[self.disp_maxi]
            
            
            first_calibration=self.calib.E[self.calib_maxi]- self.disp.E[self.disp_maxi]
            self.A.set(first_calibration)
            
            #self.Aslider.configure(from_ = self.calib.E[self.calib_maxi]*0.985,
            #                       to =self.calib.E[self.calib_maxi]*1.015)
            self.Aslider.configure(from_ = first_calibration*0.985,
                       to =first_calibration*1.015)
            
            self.newE= self.newf(numpy.arange(len(self.disp.E)))


    def setredraw_A(self,value):
        pippo = value
        if hasattr(self, "calib") and hasattr(self, "disp"):
            self.newE = self.newf(numpy.arange(len(self.disp.E)))
            try:
                self.graph.curves[0].set_xdata(self.newE)
                self.graph.canvas.draw()
            except: pass
            try:
                self.graphd.curves[0].set_xdata(self.newE)
                self.graphd.canvas.draw()
            except: pass
        pass           

    def setredraw_B(self,value):
        pippo = value
        shift = float(self.A.get())
        if hasattr(self, "calib") and hasattr(self, "disp"):
            Ealmax= self.newE[self.disp_maxi]
            diff_E   = self.newf(self.disp_maxi)-Ealmax
            self.A.set(shift - diff_E)
            self.newE = self.newf(numpy.arange(len(self.disp.E)))
            try:
                self.graph.curves[0].set_xdata(self.newE)
                self.graph.canvas.draw()
            except: pass
            try:
                self.graphd.curves[0].set_xdata(self.newE)
                self.graphd.canvas.draw()
            except: pass
        pass



    def newf(self, pippo):
           newE = (float(self.A.get())) \
                  +float(self.B.get())*pippo     \
                  +float(self.C.get())*pippo**2
           return newE


    def topcallback_plot(self):
        self.pulsante_plot.configure(relief="raised", state=NORMAL)
        self.graph.top.destroy()

    def topcallback_dplot(self):
        self.pulsante_dplot.configure(relief="raised", state=NORMAL)
        self.graphd.top.destroy()

    def select(self):
        global Dis_coeff
        Dis_coeff[0]=float(self.A.get())
        Dis_coeff[1]=float(self.B.get())
        Dis_coeff[2]=float(self.C.get())
                                                            
    def browse_command2(self):
        global fil_spec
        buffero = []
        self.filesel.browse_command()
        for i in self.filesel.filenames:
            buffero.append(bm29.disperati(i))
        try:
            for i in buffero:
                i.calibrate(*Dis_coeff)
                i.bm29ize()
                fil_spec.extend(i.spectra)
        except AttributeError:
            print "Error file not open" 
        del buffero
########################################################################################################    

if __name__ == "__main__":
   radice = Tk()
   radice.title("EXAFS GUI")
   pippo = Gen_QE(radice)
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
   colwin=Column_Window(filenames)   
   radice.mainloop()   




