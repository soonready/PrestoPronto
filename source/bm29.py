#Name: bm29.py
# Purpose: An algorithm to perform XAFS data reduction.
# Author: C. Prestipino based on ifeffit engine by Matt Newville
# some piece of code has been inspired/translate/copyed by sequentially
# Bruce Ravel athena arthemis
# Sam Web sixpack
# Rehr ecc... feff
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
# Except as contained in this notice, the name of ESRF 
# shall not be used in advertising or otherwise to promote
# the sale, use or other dealings in this Software without prior written
# authorization from ESRF.


import scipy
import exapy
import numpy as np
from scipy import interpolate
import os
import time
import bisect














class SmDerInt():
    """class for numerical(gradient method) derivation.
    
    optionally will do a pre smooth 
    after if used function ..... vwill evaluate an imnterpolation
    
    input:
        y: the input signal 
        x: abscissa of input signal

    example:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
    """
    def __init__(self, y, x=None, ):
        self.y = y
        self.x = x
        self.x_int=x

        
        
    def der(self, der_ord=1, smoot_l= True):
        """derivate by method numpy.gradient
        input:
        der: order of derivative
        smoot_l: logical flag if True  used the smooted else the not smooted
        attribute
        self.deriv attribute in wich is defined the derivative.
        """
        Y =  self.smooth if smoot_l == True else  self.y
        x_denom = 1 if self.x==None else np.gradient(self.x)
        #devz = lambda der_ord: np.gradient(devz(der_ord-1))/x_denom  if der_ord!=1 else np.gradient(Y)/x_denom
        #self.deriv=devz(der_ord)
        self.deriv=np.gradient(Y)/x_denom

    def interpol(self,step):
        if self.x==None:
            raise ValueError("interpolation possible only with x defined") 
            return
        self.x_int= np.arange(self.x[0],self.x[-1],step)
        spline = interpolate.splrep(self.x, self.deriv)  
        self.deriv = interpolate.splev(self.x_int,spline,der=0)
            
       
        

    def smooth(self,window_len=3,window='flat', repeat=1):
        """smooth the data using a window with requested size.
        
        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal 
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.
        
        input:
            x: the input signal 
            window_len: the dimension of the smoothing window; should be an odd integer
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.
    
        output:
            the smoothed signal
            
        example:
    
        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)
        
        see also: 
        
        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter
     
        TODO: the window parameter could be the window itself if an array instead of a string 
        
        """
        

        x= self.y
        self.window_len = window_len
        self.window= 'flat'
        
        if x.ndim != 1:
            raise ValueError, "smooth only accepts 1 dimension arrays."
    
        if x.size < window_len:
            raise ValueError, "Input vector needs to be bigger than window size."
    
        if window_len<3:
            self.smooth=  x
            return 
    
        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
    
    

        #s=x
       
        #print  "\n\n\ns len=",(len(s))
        if window == 'flat': #moving average
            w=np.ones(window_len,'d')
        else:
            w=eval('np.'+window+'(window_len)')
        
        for i in range(repeat):
            s=np.r_[x[(window_len-1)/2:0:-1],x,x[-2:-(window_len-1)/2-2:-1]]   
            y=np.convolve(w/w.sum(),s,mode='valid')
            x=y
        if repeat>0:
            self.smooth=  y
        else:  self.smooth=  x  
        #print  "smo len=",(len(y))
         
        return 








    

class FileFormatError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)







class bm29file(exapy.ExaPy):
    """classe file di BM29 dovrebbe aprire un file leggerlo leggere le
    informazioni dei commenti. ha delle funzioni per il calcolo della derivata prima
    e dell angolo del monocromatore per ogni punto di enegia \n
    datinput: should be or a string or an numpy array with first column an Energy(eV or keV) 
    and as second column a Mu
    datinput =could be a strin with filenames or a numpy array or  a list of two array
    All_Column= True all column, False 2 column, Minimum E Mu I0 Ref 
    """
    def __init__(self,  datinput,  All_Column=True):
          self.All_Column=All_Column
          tipo =str(type(datinput)).split("'")[-2] 
          # you could zrite also "if type(x) == type(str())"
          #print "bm29 instance type", tipo
          if tipo == "numpy.ndarray":
              if all(datinput[:,0]<90): 
                   self.E = datinput[:,0]*1000
              else:
                   self.E = datinput[:,0]
              self.Mu=datinput[:,1]
              self.All_Column = False
          elif tipo == "list":
              if all(datinput[0]<90): 
                  self.E =scipy.array(datinput[0])*1000 
              else: 
                  self.E = scipy.array(datinput[0])
              self.Mu=scipy.array(datinput[1])
              self.All_Column = False
          elif (tipo == "str") or (tipo == "unicode"):
               self.fullfilename = datinput
               self.name = os.path.basename(self.fullfilename)
               self.directory = os.path.dirname(self.fullfilename)
               self.bm29open()
          else:
              print "porca troia"
          super(bm29file, self).__init__(energy=self.E, mu=self.Mu)
 


    def bm29open(self):
        """function to open a bm29 file, define a series of array with the same name
        of column defined in the file
        """
        self.comments = []   #comments in the file
        self.footer= []
        self.com_range=[]    #limit in the comments"""        
        inFile = open(self.fullfilename, 'r')
        while True:
                self.comments.append(inFile.readline())
                if self.comments[-1][:2] == "#L": break
                if len(self.comments)>50: 
                    inFile.close()
                    raise FileFormatError('more than 50 line of comments')
        if "BM29" in self.comments[0]: pass
        elif "BM23" in self.comments[0]: pass
        else:raise FileFormatError('neither BM29 nor BM23 are present in the comments')
        if self.All_Column:
                self.data= scipy.loadtxt(inFile)
        else:
                self.data= scipy.loadtxt(inFile, usecols=(0, 1))
        inFile.seek(-120, 2)
        pippo = inFile.readlines()
        for item in pippo[-2:]: self.footer.append(item)
        inFile.close
        del pippo
        self.separator="# -------------------------------------------------------\n"
        self.com_range=[i for i in xrange(len(self.comments)) if self.comments[i]==self.separator]        
        self.start_time= time.strptime(" ".join(self.comments[0].split()[-5:]), "%a %b %d %H:%M:%S %Y")
        self.start_time_ep=time.mktime(self.start_time)
        try:
           self.comments_T=[i for i in xrange(len(self.comments)) if self.comments[i].find("Sample temperature")>0][0]
           #print self.comments_T
           self.T1,self.T2 = [float(item) for item in self.comments[self.comments_T].replace(",","").split()[-2:]]
           #print self.T1

        except: pass
        
        self.col_head =self.comments[-1].split()[1:]
        for i in range(self.data.shape[1]):
                nomestring = "self."+''.join([ c for c in self.col_head[i] if c not in ('[', ']')])
                valuestring = " = self.data[:,"+str(i)+"]"
                exec(nomestring+valuestring)
        try:
            self.E = self.EkeV*1000
        except:
            pass
        try:
            self.Mu = self.alpha
        except:
            pass
        try:
            self.dspac = eval(self.comments[6].split()[4])
        except:
            pass            

        
        if self.All_Column == False: 
            if hasattr(self, "data") : del self.data 
            if hasattr(self, "EkeV") : del self.EkeV
            if hasattr(self, "alpha"): del self.alpha
        if self.All_Column == "minimum":    
            if hasattr(self, "data") : del self.data 
            if hasattr(self, "EkeV") : del self.EkeV
            if hasattr(self, "alpha"): del self.alpha   
            if hasattr(self, "point_nb"): del self.point_nb   
            if hasattr(self, "qg1"):        del self.qg1
            if hasattr(self, "T1"): 
                if isinstance(self.T1, scipy.ndarray): del self.T1  
            if hasattr(self, "T2"):         
                if isinstance(self.T2, scipy.ndarray): del self.T2 
            if hasattr(self, "E_hdhkeV"): del self.E_hdhkeV  
            if hasattr(self, "log_i1_i2"):  del self.log_i1_i2  
            if hasattr(self, "Scal1"):      del self.Scal1 
            if hasattr(self, "Scal2"):      del self.Scal2 
            if hasattr(self, "elapseT"):    del self.elapseT
            if hasattr(self, "time"):       del self.time  
            if hasattr(self, "i0_raw"):     del self.i0_raw
            if hasattr(self, "i1_raw"):     del self.i1_raw  
            if hasattr(self, "I1"):         del self.I1
            if hasattr(self, "I2"):         del self.I2
        return

    def bm29write(self, filename= None,  newdata=None, comment=True, newdatacol_head=None, columns=None):
        """function to write a bm29 file, define a series of array with the same name
        of column defined in the file
        input \n
        filename =>string
        newdata =>numpy array
        comment =>boolean or new comments line
        col_head =>string heders of column
        columns =>list of strings with the columns to write 
        P.S or newdata and col_head or columns
        """
        if not(filename):
            try:
                filename =getattr(self,"fullfilename")
            except:
                raise FileFormatError('no filename specified and self.fullfilenames not defined')
        if os.path.exists(filename):
                filename += ".1"
        outFile = open(filename, 'w')
        
        if comment is True:
            if hasattr(self, "comments"):
                outFile.writelines(self.comments[:-2])
        elif comment is False:
              pass
        else: outFile.writelines(comment)
        if newdata is None:
            if columns:
                outFile.writelines("#N "+str(len(columns))+ "\n")   
                col_head= "#L "+" ".join(columns)
                outFile.writelines(col_head+"\n")
                f=lambda x: getattr(self,x)
                newdata= scipy.column_stack(map(f,columns))
            else:
                if self.All_Column == False:
                    outFile.writelines("#N 2\n")                    
                    outFile.writelines("#L   E     Mu\n")
                    newdata= scipy.column_stack((self.E, self.Mu))
                elif self.All_Column == True: 
                    try: 
                        outFile.writelines(self.comments[-2])                        
                        outFile.write("#L  "+" ".join(getattr(self, "col_head")))
                        outFile.write("\n")
                        newdata = self.data
                    except:
                        pass    
        scipy.savetxt(outFile, newdata, fmt= '%1.10f')
        outFile.close
        return
        
    #def bm29.average for the future

    def bm29A(self):
            """define an A attribute with monochromator angle position
            corrisponding to each energy point of the spectra """
            self.A = scipy.rad2deg(scipy.arcsin((1.23984E-6/(self.E))*1E10/(2*self.dspac)))
    def __bm29splE__(self, L1=None, L2=None, s=0):
            """ spline interpolation of Mu spectra in the range L1 L2
            define an attribute E_splineMu conteining a spline object """
            if L1==self.E[0]: L1=None
            elif L1: L1=bisect.bisect_left(self.E, L1)
            if L2==self.E[-1]: L2=None                
            elif  L2:L2= bisect.bisect_right(self.E, L2)
            #print sum(self.Mu[L1:L2])
            spercent=(s*(sum(self.Mu[L1:L2]-min(self.Mu[L1:L2]))))**2
            #print spercent
            self.E_splineMu = interpolate.splrep(self.E[L1:L2], self.Mu[L1:L2], s=spercent)
    def bm29splNor(self, L1=None, L2=None, s=0):
            """ spline interpolation of Normalized Mu spectra in the range L1 L2
            define an attribute E_splineNor conteining a spline object  """
            if not hasattr(self, 'Nor'): self.XANES_Norm()
            self.E_splineNor = interpolate.splrep(self.E,self.Nor,xb=L1, xe=L2 , s=s)
    def __bm29splRef__(self, L1=None, L2=None, s=0):
            """ spline interpolation of ref Mu spectra in the range L1 L2
            define anA attribute E_splineMu conteining a spline object """
            self.E_splineRef = interpolate.splrep(self.E,self.ref,xb=L1, xe=L2,s=s)            
    def bm29derE(self, sampling=None, L1=None, L2=None, s=0, spline=True):
            """ \n compute the analitic first derivative between L1 and L2 of Mu spline
            L1 and L2 are the two faculttive limits and sampling is an array containing 
            the energy point for which the first derivative of Mu will be calculated
            s=0 smoot factor sum((y-g(x)))<=x
            spline force to reevaluate the spline
            """
            #if not hasattr(self, 'E_splineMu'): self.bm29splE( L1, L2, s)
            if spline:
                self.__bm29splE__(L1, L2, s)
            if sampling==None: sampling=self.E
            self.E_MuFp = interpolate.splev(sampling,self.E_splineMu,der=1)
    def bm29derRef(self, sampling=None, L1=None, L2=None):
            if not hasattr(self, 'E_splineRef'): self.__bm29splRef__( L1, L2)
            if sampling==None: sampling=self.E
            self.E_RefFp = interpolate.splev(sampling,self.E_splineRef,der=1)            
    def bm29int_Mu(self, L1=None, L2=None):
            """ compute the analitic integral between L1 and L2 of Mu spline"""
            if not hasattr(self, 'E_splineMu'): self.__bm29splE__()
            return interpolate.splint(L1, L2, self.E_splineMum, full_output=0)
    def bm29int_Nor(self, L1=None, L2=None):
            """ compute the analitic integral between L1 and L2 of Mu Normalized spline """
            if not hasattr(self, 'E_splineNor'): self.bm29splNor()
            return interpolate.splint(L1, L2, self.E_splineNor, full_output=0)
            
    def bm29Num_der(self, window_len=1, step=0, L1=None, L2=None, repeat=1):
        if L1==self.E[0]: L1=None
        elif L1: L1=bisect.bisect_left(self.E, L1)
        if L2==self.E[-1]: L2=None                
        elif  L2:L2= bisect.bisect_right(self.E, L2)
        
        self.NumDer= SmDerInt( self.Mu[L1:L2], self.E[L1:L2])
        window_len=window_len*2+1
        #print "windows lengen=",  window_len
        self.NumDer.smooth(window_len= window_len, window='flat', repeat=repeat)
        self.NumDer.der(der_ord=1, smoot_l = True)
        if step==0: return
        else:
            self.NumDer.interpol(step)

        











def sfigati(inputo, add=0.0):
    """una funzione per aprire file che non vengono ne da bm29 ne bm23
    si fa entrare un file e ne ritorna una classe bm29
    """
    try:
       pippo =bm29file(inputo) 
       return pippo
    except FileFormatError: print "NON bm29"
    try:
       pippo =sambafile(inputo) 
       return pippo
    except FileFormatError: print "NON samba"
    filedata=open(inputo, "r")
    filedata.readline()
    data=scipy.loadtxt(filedata)
    data[:,0]=data[:,0]+add
    return bm29file(data[:,:2])
    
    
def openSinglefile(filename):
    inFile = open(filename, 'r')
    buffero= scipy.loadtxt(inFile)    
    inFile.close()
    x_array=buffero[:,0]
    spectra=[]
    for item in scipy.hsplit(buffero[:,1:], buffero.shape[1]-1):
        spectra.append(generic(x_array,scipy.ravel(item)))
    return spectra
    
    
class generic():
    def __init__(self,  x,y):
        self.x=x
        self.y=y
    
    
    
class disperati():    
    """utilizzatori di ID24 che non possono usare la Sublime
        datinput =string with filenames or a numpy array or  a list of two array
    """
    def __init__(self,  datinput):
        self.comments = []
        self.fullfilename = datinput
        self.name = os.path.basename(self.fullfilename)
        inFile = open(datinput, 'r')
        inFile.readline()
        self.comments.append("# ID24 datafile"+  self.name + "\n")
        self.data= scipy.loadtxt(inFile)
        inFile.close

    def calibrate(self, calA=0,calB=1,calC=0):
        """define a first energy column define as A+B*x+c*x**2"""
        pixel= scipy.arange(self.data.shape[0])
        try:
            self.energy = calA+ calB*pixel+calC*pixel**2
        except TypeError:
            print '\n \ndo you have define A B C ?\n\n '
        
    def bm29ize(self):
        """transform the data of id24 in a list of bm29 instance"""
        self.spectra=[]
        for n,item in enumerate(scipy.hsplit(self.data[:,1:], self.data.shape[1]-1)):
            self.spectra.append(bm29file([self.energy, item[:,0]]))
            self.spectra[n].comments= list(self.comments)
            self.spectra[n].comments.append("# spectra number "+str(n)+ "\n")
            self.spectra[n].comments.append("#  ---------------------------------"+ "\n")
            self.spectra[n].comments.append("#L E  Mu"+ "\n")            
    pass




class sambafile(bm29file):
    def bm29open(self):
        """function to open a bm29 file, define a series of array with the same name
        of column defined in the file
        """
        self.comments = []   #comments in the file
        self.footer= []
        self.com_range=[]    #limit in the comments"""        
        inFile = open(self.fullfilename, 'r')
        while True:
                self.comments.append(inFile.readline())
                if self.comments[-1][:3] == "#En": break
                if self.comments[-1][:3] == "#L ": print "#L"; break                
                if len(self.comments)>50: 
                    inFile.close()
                    raise FileFormatError('more than 50 line of comments')
        if self.All_Column:
                self.data= scipy.loadtxt(inFile)
        else:
                self.data= scipy.loadtxt(inFile, usecols=(0, 2))

        try:
            self.date=[i for i in xrange(len(self.comments)) if self.comments[i].find(
                                                      "Time")>0]
            self.Time= float(self.date[-1].split("=")[-1])   
        except: pass
        
        
        self.col_head =self.comments[-1].lstrip("#L").split()
        if self.data.shape[1]< len(self.col_head):
            self.col_head.pop(-2) 
        for i in range(self.data.shape[1]):
                nomestring = "self."+''.join([ c for c in self.col_head[i] if c not in ('[', ']', "#")])
                valuestring = " = self.data[:,"+str(i)+"]"
                exec(nomestring+valuestring)
        try:
            self.E = self.Energy
        except:
            pass
        try:
            self.ref = self.mus
        except:
            pass        
        try:
            self.Mu = self.mux
        except:
            pass
        #self.dspac = eval(self.comments[2].split("=")[-1])
        
        if self.All_Column == False: 
            if hasattr(self, "data") : del self.data 
            if hasattr(self, "Energy") : del self.Energy
            if hasattr(self, "mux"): del self.mux
        if self.All_Column == "minimum":    
            if hasattr(self, "data") : del self.data 
            if hasattr(self, "I0"):         del self.I0           
            if hasattr(self, "I1"):         del self.I1
            if hasattr(self, "I2"):         del self.I2
            if hasattr(self, "data") : del self.data 
            if hasattr(self, "Energy") : del self.Energy
            if hasattr(self, "mux"): del self.mux
        return
    


#import pippo





#import numpy, scipy
#
#filtsize = 3
#a = numpy.arange(100).reshape((10,10))
#b = numpy.lib.stride_tricks.as_strided(a, shape=(a.size,filtsize), strides=(a.itemsize, a.itemsize))
#for i in range(0, filtsize-1):
#    if i > 0:
#        b += numpy.roll(b, -(pow(filtsize,2)+1)*i, 0)
#filtered = (numpy.sum(b, 1) / pow(filtsize,2)).reshape((a.shape[0],a.shape[1]))
#scipy.misc.imsave("average.jpg", filtered)






















###paste for future
            ############################################################################################
            # step = lambda x: 0 if (x <= Eo) else 1
            # intstep = lambda x: Efin -Eo
            #
            # from scipy.optimize import leastsq
            # ## Parametric function: 'v' is the parameter vector, 'x' the independent varible
            # fp = lambda v, x: v[0]/(x**v[1])*sin(v[2]*x)
            #
            #
            #
            #
            #
            # ## Noisy function (used to generate data to fit)
            # v_real = [1.5, 0.1, 2.]
            # fn = lambda x: fp(v_real, x)
            #
            # ## Error function
            # e = lambda v, x, y: (fp(v,x)-y)
            #
            # ## Generating noisy data to fit
            # x = linspace(xmin,xmax,n)
            # y = fn(x) + rand(len(x))*0.2*(fn(x).max()-fn(x).min())
            #
            # ## Initial parameter value
            # v0 = [3., 1, 4.]
            #
            # ## Fitting
            # v, success = leastsq(e, v0, args=(x,y), maxfev=10000)
            #
            #
            #
            #
            # #    def bm29derA(self, sampling=None):
            # #     if not hasattr(self, 'A'): self.bm29A()
            # #     self.A_spline = interpolate.splrep(self.A*-1,self.Mu,s=0)
            # #     if not(sampling): sampling=self.A
            # #       self.A_Mu = interpolate.splev(sampling*-1,self.A_spline,der=0)
            # #       self.A_MuFp = interpolate.splev(sampling*-1,self.A_spline,der=1)
                 #
