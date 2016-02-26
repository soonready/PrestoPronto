#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Name: rebin-algbm29.py
# Purpose: An algorithm to perform XAFS data reduction.
# Author: C. Prestipino based on rebin-alg.py by Ken McIvor
# at Illinois Institute of Technology
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


import xtables
import bisect
import scipy

#h ≈ 4,1343359×10-15 eV⋅s 



def spectra_average(lista_spetra):
    """a function that average several spectra stored in a list
    lista_spetra. Each element of the list must contain in position 0 
    the x_array and in position 1 the y_array
    """
    x0= lista_spetra[0][0]    
    x_array=[item[0] for item in lista_spetra]
    z=x0==x_array
    if type(z)!=bool:
        if z.all():
            return x0, dat_average([item[1] for item in  lista_spetra])
    Ave=scipy.zeros(lista_spetra[0][0].shape)   
    for item in lista_spetra:
        Ave+=scipy.interp(x0,item[0],item[1])
    return x0, Ave/len(lista_spetra)   
    

    
        
    
def datalize(*arg):
    return scipy.transpose((scipy.vstack((arg))))


def max_range(E,Y,before=None,after=None):
        """a function that find the energy point
        corrispondent to the max of a second row in a range
        """



        if before and  before<scipy.amin(E):
            raise ValueError("before<min(col 0)")        
        if after>scipy.amax(E):
            raise ValueError("before>max(col 0)")
        if before>after:
            raise ValueError("before>after")    
        
        data=dat_Truncate(datalize(E,Y),before,after) if (before or after)!= None else datalize(E,Y)
        argmax=scipy.argmax(data[:,1])        
        return data[argmax,0]
        

def time_scan(start,end,monovelocity,dspacing,stepfordegree=36000.0):
        """defined the parameter mono_velocity, 
        the start and the end of the scan in eV or KeV
        and the dspacind in A, 
        give the time necessary for the scan
        output in sec"""
        speed =  monovelocity/stepfordegree
        Astart = E2T(start,dspacing)
        Aend = E2T(end,dspacing)
        time = (Astart - Aend)/speed 
        return  time


def npoints_filter( edgeE, monovelocity, dspacing,minEstep =.5):
        """suggent the couple filter number of points,
        defining the parameter mono_velocity
        Energy edge and  minimum energy step at the edge 
        and the dspacind in A, 
        give the time necessary for the scan"""
        
        if  (maxstep>minEstep>minstep):
                pass
        elif ((maxstep/1000)>minEstep>(minstep/1000)):
                minEstep *=1000
        else: raise ValueError("possible value for minEstep are between .1 and 5 eV") 
        if edgeE < 90: edgeE *=1000 
        steptime = time_scan(edgeE,edgeE+minEstep,monovelocity,dspacing)
        totaltime/steptime

def dat_average(lista_Data):
        """a function that average several arrays/float/integer
        stored in a list
        receive in input a list"""
        if type(lista_Data[0])==float:
            return sum(lista_Data)/len(lista_Data)
        elif type(lista_Data[0])==int:
            return float(sum(lista_Data[0]))/len(lista_Data)
        elif type(lista_Data[0])==scipy.ndarray:
                Ave=scipy.zeros(lista_Data[0].shape)            
                try: 
                    for  item in lista_Data:
                      Ave += item
                except ValueError:
                      raise ValueError('number of points different in betweeen Data \n average not done')
                      return
                return Ave/len(lista_Data)
   
   
def dat_Truncate(Data,before=None,after=None,ind=0,direction="Column"):
        """a function that truncate a bidiemnsional array  or a list of array
        
        Data : a bidimensional numpy array or a list of monodimensional array 
        direction : string with value Column or Row,define wich kind of truncation
        index : index of the column or row  respect wich trucation is done
        before :all data with value smaller than it are cutted
        after :all data with value bigger than it are cutted
        ------
        if data is a list the direction keyworl will be ignored
        N.B.
        the index column must be in a growing order
        -------
        Returns 
        a truncate array if input was array, else a list
        
        """
        if (before or after)== None:
            raise ValueError, (
                   '  any limit defined for truncation')
        if (before > after):
            if after ==None: pass
            else:
                raise ValueError, (
                   '  before= %f bigger than after = %f any value remain!')  %(
                               before, after)

        if direction=="Row" or direction=="Column":
                    pass
        else: raise ValueError, (
                       ' direction = string with value Column or Row,')
        
        if  isinstance(Data,list):
            sbefore= bisect.bisect_left(Data[ind],before)
            safter=  bisect.bisect_right(Data[ind],after)
            if (after) == None:
                Data=[item[sbefore:] for item in Data]
            elif (before) == None:
                Data=[item[:safter] for item in Data]
            else:  
                Data=[item[sbefore:safter] for item in Data]
            return Data        

            
            
        if len(Data.shape)==1:
            Data=scipy.compress(((before< Data)&(Data<after)),Data) #axis =0
        else:    
            if direction=="Row":
                    Data=Data.transpose()
            sbefore= bisect.bisect_left(Data[:,ind],before)
            safter=  bisect.bisect_right(Data[:,ind],after)
            if (after) == None:
                Data=Data[sbefore:,:]
            elif (before) == None:
                Data=Data[:safter,:]
            else:   
                Data=Data[sbefore:safter,:]
            if direction=="Row":
                    Data=Data.transpose()
        return Data






def MvEAshift(data,dspacing,Eini,Efin):
    """a function to perform angular
    shift on an array of energy
    using as input the enregy point where it is
    and where it shold be        
    data could be a monodimensional array or 
    pluridimensional with E array as first column
    data could be in eV or KeV
    """
    Tini=E2T(Eini,dspacing)
    Tfin=E2T(Efin,dspacing)
    Ashift= Tfin-Tini
    return Ashif(data,dspacing,Ashift)




def Ashif(data,dspacing,shift):
    """a function to perform angular
    shift on an array of energy
    data could be a monodimensional array or 
    pluridimensional with E arrai as first column
    """
    try:
        if data.shape[1]:
               if data[0,0] > 90:  #eV
                   data[0,:] = T2E((E2T(data[0,:], dspacing) + shift),dspacing)
               else:                     #KeV
                   data[0,:] = 1.0E-3*(T2E((E2T(data[0,:], dspacing) + shift),dspacing))
    except:
         if data.shape[0]:
             if data[0] > 90:  #eV
                 data = T2E((E2T(data, dspacing) + shift),dspacing)
             else:                     #KeV
                 data[:] = 1.0E-3*(T2E((E2T(data[0:], dspacing) + shift),dspacing))
    return data


def dspa_A_change(E,dold,dnew,Edge,shift=0.0):
    """a function to change the dspanig of an array of Energy 
    keeping the Enegy =Edge equal in the two array
    dold = old_dspacing
    dnew = new dspacing
    Egede enrgy that should not change
    addition shift in angle (optional)
    """
    print dold, dnew, Edge, shift
    shift= E2T(Edge, dnew)-E2T(Edge, dold)+shift
    E = T2E((E2T(E, dold) + shift),dnew)
    return E





def T2E(Degree,dspacing):
          """from angle and dspacing return the energy in eV
             in diffraction condition
             E=hc/(sin(theta)*2d)))
          """
          Ener  = 1.23984E4/(scipy.sin(scipy.radians(Degree))*2*dspacing)
          return Ener
          
def T2d_s(Degree,Ener,wavelenghts=False):
          """from Theta angle and Energyg return the d_spacing
             if wavelengh is true Energy is espressed in wavelenght
          """
          if wavelenghts: 
             return E2W(Ener)/(2*(scipy.sin(scipy.radians(Degree))))
          else:
             return Ener/(2*(scipy.sin(scipy.radians(Degree))))
          
          
          
          
def E2T(Ener,dspacing):
       """Calculate The angle for an Energy in eV or KeV given a dspacing
          accept, "integer", "float", monodimensional array
          return corrisponding angle in degree
       """
       if ((type(Ener) ==float) or (type(Ener) ==int) or (type(Ener) ==scipy.float64) or (type(Ener) ==scipy.float32)):
           if Ener> 1000:
               the = scipy.rad2deg(scipy.arcsin((1.23984E-6/(Ener))*1E10/(2*dspacing)))
           if Ener < 1000:
              the = scipy.rad2deg(scipy.arcsin((1.23984E-6/(Ener*1000))*1E10/(2*dspacing)))
       else:
           if Ener[0]> 1000:
               the = scipy.rad2deg(scipy.arcsin((1.23984E-6/(Ener))*1E10/(2*dspacing)))
           if Ener[0] < 1000:
               the = scipy.rad2deg(scipy.arcsin((1.23984E-6/(Ener*1000))*1E10/(2*dspacing)))
       return the



def E2W(Ener):
        """Convert from Energy to waelenght (angstrom)
        E=hv hplank =6.626e-34 Js or 4.13566733 eV/s
        v=frequency = c/W c=299792458 m/s
        E=hc/W
        """
        if Ener > 1000:
            WL = (1.23984E-6/Ener)*1E10
        if Ener < 1000:
            WL = (1.23984E-6/((Ener)))*1E7
        return WL
def W2E(WL):                          
       Ener = (1.23984E-6/(WL*1E-10))
       return Ener

def opendata(inputf):
     inFile = file(inputf, 'r')
     data = scipy.loadtxt(inFile)
     if data[0,0]<90:
          data[:,0] *= 1000
     inFile.close
     return data

def writedata(fileout,data):
    outFile = file(fileout, 'a')
    if data[0,0]>90 :
      for i in range (0, data.shape[0]):
        data[i,0] /= 1000
    scipy.savetxt(outFile,data)
    outFile.close
    return 

def ktoE(E,Eo):
    return (E/0.512)**2 + Eo       
def Etok(E, Eo):
      """Calculate K for some energy level E, using the edge energy argument
      passed to rebin().
      """
      return 0.512317 * scipy.sqrt(E - Eo)




def grid(start, stop, stepSize):
        """Create an array which can be used as an abscissa for interpolation.
        Returns an array of regular values, increasing by 'stepSize', which go from
        'start' to 'stop' inclusively.
        """
        r = scipy.arange(start, stop + stepSize, stepSize)
        while r[-1] > stop:
                r = r[:-1]
        if r[-1] < stop:
                r = scipy.resize(r, (r.shape[0]+1, ) )
                r[-1] = stop+stepSize/2
        return r


class RebinError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

def rebin(data, eColumn=1, Eo=0, before= 30, after=20, pstep=5, xstep=.5, kstep=.03, file='', msgStream=None):
        """XAFS data reduction.
        'data' is a Numerical Python matrix (rank 2 array) which contains the XAFS
        data to be reduced.  'eColumn' is the column index of the energy values of
        each point.  'Eo' is the edge energy of the data.

        All points for which the energy is lower than 'Eo'-'before' are
        reduced to a new set of points in which the energy varies in
        equally-spaced steps in energy-space, defined by 'pstep'.

        All points for which the energy is between  'Eo'-'before' and 'Eo'+'after'
        are reduced to a new set of points in which the energy varies in
        equally-spaced steps in energy-space, defined by 'xstep'.

        All points for which the energy is greater than 'Eo'+'after' are
        reduced to a new set of points in which the energy varies in
        equally-spaced steps in k-space, defined by 'kstep'.
        'file' is the file name corresponding to this data set, and if specified
        will be used in any exceptions raised by this functions.

        If 'msgStream' is specified it must be an output stream (an object
        implementing a write() method),        which will used to print status
        information.
        """
        def cleanup(data,eColumn,inverted,keV):
            if inverted: data=data[::-1]
            if keV : data[:,eColumn]=data[:,eColumn]/1000
            
        # if data are reversed it invert the data
        if Eo==0:        
            raise RebinError('%sE0 not defined' % file)
        
        # if data are reversed it invert the data
        if data[0,eColumn] >  data[5,eColumn]:
               inverted=True
               data = data[::-1]
        else: inverted=False
        # if file is in keV
        if data[5,eColumn] <  90:
               keV = True
               data[:,eColumn]=data[:,eColumn]*1000
        else: keV = False  
        
        def k2E(k,Eo=Eo):  return (k/0.512)**2 + Eo 
        def k(E, Eo=Eo): return 0.512 * scipy.sqrt(E - Eo)


        # if file is specified, reformat it for use in error messages
        if file:
                file = '[%s] ' % file


        # acquire the energy vector of the data and find its minimum and maximum
        #define star of k rebining
        #define star of Xanes rebinning
        E = data[:,eColumn]
        startk = Eo + after        # valore EXAFS
        startx = Eo - before       # valore Xanes
        Min, Max = min(E), max(E)
        if Max <= Eo:
                 cleanup(data,eColumn,inverted,keV)
                 raise RebinError(
                       '%sno energy values larger than Eo (incomplete data set?)'% file)
        if Max <= startk:
                cleanup(data,eColumn,inverted,keV)
                raise RebinError('%sthe value of "after" is too large' % file)
        if Min >= startx:
                cleanup(data,eColumn,inverted,keV)
                raise RebinError('%sthe value of "before" is too large' % file)
                cleanup(data,eColumn,inverted,keV)


        # Generate the regular preedge xanes and k-space abscissa that will be rebined to.
        # grid(start, end, step) returns a vector of values from 'start' to 'end'
        # by 'step', inclusive.
        startPointx = bisect.bisect_right(E, startx)               
        startPointk = bisect.bisect_right(E, startk)
        if msgStream: 
                msgStream.write('%s%d points in E from %.4f to %.4f (Eo = %.4f)\n' %
                        (file, eRange.shape[0], start, Max, Eo))
        pgrid = scipy.arange(Min, startx , pstep)
        if pgrid[-1] > startx - xstep:                              #da rivedere
            pgrid = pgrid[:-1]    
            print "WARNING  preedge and xanes step similar" 
            
        Ecros= Eo+(0.256*xstep/kstep)**2    
        if Ecros>startk: startk=Ecros+.5
        xgrid = scipy.arange(startx,startk, xstep)
        kgrid = k2E(scipy.arange(k(xgrid[-1]+xstep), k(Max)+kstep, kstep))
        
        binE = scipy.concatenate((pgrid,xgrid,kgrid)) 
        if msgStream:                                                                                       
               msgStream.write(
                       '%srebinning to %d points in k-space from %.4f to %.4f\n'
                       % (file, kgrid.shape[0], kgrid[0], kgrid[-1]))




                                                 

        # newData is matrix which is BINCOUNT-1 rows long and contains the same
        # number of columns as the data matrix.  It accumulates the sums of the
        # points which fall in each bin
        newData = scipy.zeros((len(binE) -1, data.shape[1]), data.dtype)

                                            
        # binCounts is a vector of BINCOUNT elements, which accumulates the number
        # of points that fall in each bin
        binCounts = scipy.zeros(len(binE)-1)
        for i in range(0, len(E)):
            where = scipy.searchsorted(binE, E[i]) 
            #print where, binE[where], binE[where+1]
            if where==len(binE)-1: where-=1
            try:
                newData[where] += data[i]
                binCounts[where] += 1
            except:
                print where
                print binE.shape
                print newData.shape
                return
        # check that all of the bins contain data
        for i in range(0, newData.shape[0]):        
               if binCounts[i] == 0:
                        cleanup(data,eColumn,inverted,keV)
                        stringunit= "k" if E[i]>startk else "E"
                        raise RebinError('%sbin %d (%.4f < %s < %.4f) is empty'
                                % (file, i, binE[i], stringunit , binE[i+1]))
        # average the binned points
        for i in range(0, newData.shape[0]):
                newData[i,:] /= binCounts[i]
        if (keV):
                newData[:,eColumn]=newData[:,eColumn]/1000
                data[:,eColumn]=data[:,eColumn]/1000
        return newData



