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
# authorization from Illinois Institute of Technology.import Ifeffit

import sys
#sys.path.append('C:\Python26\Lib\site-packages\Ifeffit')
#import Ifeffit  
import os
import numpy  as np
from xtables import elements, QN_Transition 
from scipy.interpolate import LSQUnivariateSpline as Spline
global iff                            
global __verbose__
__verbose__ = False#True#

MAX_FILESIZE= 12e9





# now import larch-specific Python code
import delarch 
from delarch import xafs, Group
from delarch.utils import fixName
from delarch.xafs.feffit import feffit_report as myfeffit_report




# create an empty Group
def colname(txt):
    return fixName(txt.strip().lower()).replace('.', '_')
def getfloats(txt):
    words = [w.strip() for w in txt.replace(',', ' ').split()]
    try:
        return [float(w) for w in words]
    except:
        return None    



#

#
class EmptyC(object):
    def __init__(self,**kwg):
        for i,item in kwg.iteritems():
            setattr(self, i, item)
        pass    
            
#

def read_ascii(fname, labels=None, sort=False, sort_column=0, 
                                       COMMENTCHARS = '#;%*!$'):
    """read a column ascii column file, returning a group containing the data from the file.

    read_ascii(filename, labels=None, sort=False, sort_column=0)

    If the header is one of the forms of
        KEY : VAL
        KEY = VAL
    these will be parsed into a 'attrs' dictionary in the returned group.

    If labels is left the default value of None, column labels will be tried to
    be created from the line immediately preceeding the data, or using 'col1', 'col2',
    etc if column labels cannot be figured out.   The labels will be used to create
    1-d arrays for each column

    The group will have a 'data' component containing the 2-dimensional data, it will also
    have a 'header' component containing the text of the header -- an array of lines.
    If a footer (text after the block of numerical data) is in the file, the array of
    lines for this text will be put in the 'footer' component.

    """
    
    if not os.path.isfile(fname):
        raise OSError("File not found: '%s'" % fname)
    if os.stat(fname).st_size > MAX_FILESIZE:
        raise OSError("File '%s' too big for read_ascii()" % fname)

    finp = open(fname, 'r')
    text = finp.readlines()
    finp.close()

    _labelline, ncol = None, None
    data, footers, headers = [], [], []

    attrs = {'filename': fname}

    text.reverse()
    section = 'FOOTER'

    for line in text:
        line = line[:-1].strip()
        if len(line) < 1:
            continue
        # look for section transitions (going from bottom to top)
        if section == 'FOOTER' and getfloats(line) is not None:
            section = 'DATA'
        elif section == 'DATA' and getfloats(line) is None:
            section = 'HEADER'
            _labelline = line
        # act of current section:
        if section == 'FOOTER':
            footers.append(line)
        elif section == 'HEADER':
            headers.append(line)
        elif section == 'DATA':
            data.append(line)
            
        
    
    
    # reverse header, footer, data, convert to arrays
    footers.reverse()
    headers.reverse()
    data.reverse()
    data =np.loadtxt(data).transpose()

    # try to parse attributes from header text
    header_attrs = {}
    for hline in headers:
        hline = hline.strip().replace('\t', ' ')
        if len(hline) < 1: continue
        if hline[0] in COMMENTCHARS:
            hline = hline[1:].strip()
        keywds = []
        if ':' in hline: # keywords in  'x: 22'
            words = hline.split(':', 1)
            keywds = words[0].split()
        elif '=' in hline: # keywords in  'x = 22'
            words = hline.split('=', 1)
            keywds = words[0].split()
        if len(keywds) == 1:
            key = colname(keywds[0])
            if key.startswith('_'):
                key = key[1:]
            if len(words) > 1:
                header_attrs[key] = words[1].strip()

    ncols, nrow = data.shape
    
    # set column labels
    _labels = ['col%i' % (i+1) for i in range(ncols)]
    if labels is None:
        if _labelline is None:
            _labelline = ' '.join(_labels)
        if _labelline[0] in COMMENTCHARS:
            _labelline = _labelline[1:].strip()
        _labelline = _labelline.lower()
        try:
            labels = [colname(l) for l in _labelline.split()]
        except:
            labels = []
    elif isinstance(labels, str):
        labels = labels.replace(',', ' ')
        labels = [colname(l) for l in labels.split()]

    for i, lab in enumerate(labels):
        try:
            _labels[i] = lab
        except:
            pass

    attrs['column_labels'] = _labels
    if sort and sort_column >= 0 and sort_column < nrow:
         data = data[:,np.argsort(data[sort_column])]
         
         
         

    group=ExaPy(data=data, headers=headers)

    for i, nam in enumerate(_labels):
        setattr(group, nam.lower(), data[i])
        
    if len(footers) > 0:
        setattr(group, 'footer', footers)
        
    for key, val in attrs.items():
        setattr(group, key, val)

    group.atgrp=Group(**header_attrs)
    return group






class ExaPy(Group):
    """EXAFS class defined in order to analyze the Mu signals
    it define till now three function 
    XANES_Norm results in array attributes Nor
    EXAFS_EX   results in array attributes k, chi, Bkg
    FT_T results in array attributes mag  pha real imag 
    """
   
    def XANES_Norm(self, e0=None, step=None, nnorm=3, nvict=0, 
             pre1=None, pre2=-50, norm1=100, norm2=None, make_flat=True, **kwd):
          """pre edge subtraction, normalization for XAFS from larch 
          This performs a number of steps:
             1. determine E0 (if not supplied) from max of deriv(mu)
             2. fit a line of polymonial to the region below the edge
             3. fit a polymonial to the region above the edge
             4. extrapolae the two curves to E0 to determine the edge jump
          
          Arguments
          ----------
           e0:      edge energy, in eV.  If None, it will be determined here.
           step:    edge jump.  If None, it will be determined here.
           pre1:    low E range (relative to E0) for pre-edge fit
           pre2:    high E range (relative to E0) for pre-edge fit
           nvict:   energy exponent to use for pre-edg fit.  See Note
           norm1:   low E range (relative to E0) for post-edge fit
           norm2:   high E range (relative to E0) for post-edge fit
           nnorm:   degree of polynomial (ie, nnorm+1 coefficients will be found) for
                    post-edge normalization curve. Default=3 (quadratic), max=5
           make_flat: boolean (Default True) to calculate flattened output.
           _larch   : Interpreter class (please not touch)
          
          
          Returns
          -------
           None          
          The following attributes will be written to the group:
          -------
              e0          energy origin
              edge_step   edge step
              norm        normalized mu(E)
              flat        flattened, normalized mu(E)
              pre_edge    determined pre-edge curve
              post_edge   determined post-edge, normalization curve
              dmude       derivative of mu(E)
          
          Notes
          -----
           1 nvict gives an exponent to the energy term for the fits to the pre-edge
             and the post-edge region.  For the pre-edge, a line (m * energy + b) is
             fit to mu(energy)*energy**nvict over the pre-edge region,
             energy=[e0+pre1, e0+pre2].  For the post-edge, a polynomial of order
             nnorm will be fit to mu(energy)*energy**nvict of the post-edge region
             energy=[e0+norm1, e0+norm2]."""
          
          xafs.pre_edge(self,  e0=e0, step=step, nnorm=nnorm,
                                 nvict=nvict, pre1=pre1, pre2=pre2, norm1=norm1, 
                                                    norm2=norm2, make_flat=True)
          return   


        
        

    def EXAFS_EX(self, rbkg=1, nknots=None, e0=None,
         edge_step=None, kmin=0, kmax=None, kweight=1, dk=0.1,
         win='hanning', k_std=None, chi_std=None, nfft=2048, kstep=0.05,
         pre_edge_kws=None, nclamp=4, clamp_lo=1, clamp_hi=1,
         calc_uncertainties=False, **kws):
         """Use Autobk algorithm to remove XAFS background from larch
         Parameters:
         -----------
           rbkg:      distance (in Ang) for chi(R) above
                      which the signal is ignored. Default = 1.
           e0:        edge energy, in eV.  If None, it will be determined.
           edge_step: edge step.  If None, it will be determined.
           pre_edge_kws:  keyword arguments to pass to pre_edge()
           nknots:    number of knots in spline.  If None, it will be determined.
           kmin:      minimum k value   [0]
           kmax:      maximum k value   [full data range].
           kweight:   k weight for FFT.  [1]
           dk:        FFT window window parameter.  [0]
           win:       FFT window function name.     ['hanning']
           nfft:      array size to use for FFT [2048]
           kstep:     k step size to use for FFT [0.05]
           k_std:     optional k array for standard chi(k).
           chi_std:   optional chi array for standard chi(k).
           nclamp:    number of energy end-points for clamp [2]
           clamp_lo:  weight of low-energy clamp [1]
           clamp_hi:  weight of high-energy clamp [1]
           calc_uncertaintites:  Flag to calculate uncertainties in
                                 mu_0(E) and chi(k) [False]
         -----------                                  
         # if e0 or edge_step are not specified, get them, either from the
         # passed-in group or from running pre_edge()                      
         
         Output arrays are written to the provided group"""
         args=dict(locals())
         del args["self"],args["kws"]
         xafs.autobk(self, **args)
         return           
             
        

    def FT_F(self, kmin=0, kmax=None, kweight=0, dk=1, dk2=None, 
             with_phase=False, window='kaiser', rmax_out=10, nfft=2048, 
             kstep=0.05, **kws ):
        """    forward XAFS Fourier transform, from chi(k) to chi(R), using
        common XAFS conventions from larch.
        
        Parameters:
        -----------
          rmax_out: highest R for output data (10 Ang)
          kweight:  exponent for weighting spectra by k**kweight
          kmin:     starting k for FT Window
          kmax:     ending k for FT Window
          dk:       tapering parameter for FT Window
          dk2:      second tapering parameter for FT Window
          window:   name of window type
          nfft:     value to use for N_fft (2048).
          kstep:    value to use for delta_k (0.05 Ang^-1).
          with_phase: output the phase as well as magnitude, real, imag  [False]
        
        Returns:
        ---------
          None   -- outputs are written to supplied group.
        
        Notes:
        -------
        Arrays written to output group:
            kwin               window function Omega(k) (length of input chi(k)).
            r                  uniform array of R, out to rmax_out.
            chir               complex array of chi(R).
            chir_mag           magnitude of chi(R).
            chir_re            real part of chi(R).
            chir_im            imaginary part of chi(R).
            chir_pha           phase of chi(R) if with_phase=True
                               (a noticable performance hit)
        
        Supports First Argument Group convention 
        (with group member names 'k' and 'chi')"""
        args=dict(locals())#; args.update(kws)
        del args["self"],args["kws"]
        if not(kmax): args["kmax"]=self.k[-1]
        xafs.xftf(self,  **args)
        return
  
         
         
    def FT_R(self, rmin=0, rmax=20, with_phase=False,
            dr=1, dr2=None, rw=0, window='kaiser', qmax_out=None,
            nfft=2048, kstep=0.05,  **kws):
        """reverse XAFS Fourier transform, from chi(R) to chi(q).
        calculate reverse XAFS Fourier transform
        This assumes that chir_re and (optional chir_im are
        on a uniform r-grid given by r.    
        Parameters:
        ------------
          r:        1-d array of distance, or group.
          chir:     1-d array of chi(R)
          group:    output Group
          qmax_out: highest *k* for output data (30 Ang^-1)
          rweight:  exponent for weighting spectra by r^rweight (0)
          rmin:     starting *R* for FT Window
          rmax:     ending *R* for FT Window
          dr:       tapering parameter for FT Window
          dr2:      second tapering parameter for FT Window
          window:   name of window type
          nfft:     value to use for N_fft (2048).
          kstep:    value to use for delta_k (0.05).
          with_phase: output the phase as well as magnitude, real, imag  [False]
        
        Returns:
        ---------
          None -- outputs are written to supplied group.
        
        Notes:
        -------
        Arrays written to output group:
            rwin               window Omega(R) (length of input chi(R)).
            q                  uniform array of k, out to qmax_out.
            chiq               complex array of chi(k).
            chiq_mag           magnitude of chi(k).
            chiq_re            real part of chi(k).
            chiq_im            imaginary part of chi(k).
            chiq_pha           phase of chi(k) if with_phase=True
                               (a noticable performance hit)
        
        Supports First Argument Group convention (with group member names 'r' and 'chir')"""
        args=dict(locals()); args.update(kws)
        del args["self"],args["kws"] 
        xafs.xftr(self,  **args)
        return
        
        



    
    def FIT(self,pathlist=None, pars=None,  transform=None, fit=True):
        """fast automatic fit"""
        #define self.pathlist
        if pathlist is None:
            if hasattr(self, "pathlist"):
                pass
            else:
                raise Exception("no defined paths to use in the fit")
        elif all([type(i) is str for i in pathlist]):
            self.pathlist=_PathsList(pathlist)
        elif all([type(i) is xafs.feffdat.FeffPathGroup for i in pathlist]):
            self.pathlist=pathlist
        #print 'definite Pathlist'    
        #define self.paramgroup
        if pars is None:
            for item in self.pathlist: 
                _oneshellpar(item.label,paramgroup=self.paramgroup)
        else:
           self.paramgroup= pars
        #define self.transform
        if transform is None:
            if hasattr(self, 'transform'):
                pass
            else:
                self.transform=TransformGroup()
        else: 
            self.transform=transform
        data=Group(k=self.k, chi=self.chi)        
        self.dataset=FeffitDataSet(data=data, pathlist=self.pathlist, 
                                   transform=self.transform)
        if fit:
            self.fit_out = feffit(params=self.paramgroup, datasets=self.dataset)
            self.fit_report = feffit_report(self.fit_out)
        return
        


#
class ParamGroup(Group):
    """a class to contain parameters
       show all the parameter inside
    """
    def __repr__(self):
        lista=dir(self)
        return 'ParamGroup(%s)' %', '.join(lista)

def _oneshellpar( label="0", amp=1, del_e0=0, sig2=0.003, del_r=0, vary=True,
                 paramgroup=None):  
    """quick do a group of parameter for a single shell
    Parameters
    ---------
       If a paramgroup is in input 
          return the refreshed paramgroup otherwise return a paramgroup
       label: a string defining number of path 
       vary a all parameter flag"""
       
    ritorna=False
    if paramgroup is None:
        paramgroup=ParamGroup()
        ritorna=True
    vario={amp:True, del_e0:True, sig2:True, del_r:True}    
    if vary is True: vary={'amp':True, 'del_e0':True, 'sig2':True, 'del_r':True} 
    if vary is False:vary={'amp':False,'del_e0':False,'sig2':False,'del_r':False} 
    if type(vary)==type(dict):
        if len(vary)!=4: raise ValueError('only 4 argument')
        
    setattr(paramgroup, "amp"+label,    Parameter(amp, vary=vary['amp'],min=0.05))
    setattr(paramgroup, "del_e0"+label, Parameter(del_e0, vary=vary['del_e0'], 
                                                              min=-10, max=10 ))
    setattr(paramgroup, "sig2"+label,   Parameter(sig2, vary=vary['sig2'], 
                                                              min=0, max=0.08))
    setattr(paramgroup, "del_r"+label,  Parameter(del_r, vary=vary["del_r"], 
                                                           min=-.08, max=0.08 ))
    
    if ritorna: return paramgroup
    return  

class Parameter(delarch.Parameter):
    """ returns a parameter object: a floating point value with bounds that can
    be flagged as a variable for a fit, or given an expression to use to
    automatically evaluate its value (as a thunk).
    
    >>> x = param(12.0, vary=True, min=0)
    will set the value to 12.0, and allow it be varied by changing x._val,
    but its returned value will never go below 0.
    
    >>> x = param(expr='sqrt(2*a)')
    will have a value of sqrt(2*a) even if the value of 'a' changes after
    the creation of x
    """        
    def __init__(self, value=0, min=None, max=None, vary=False, name=None, 
             expr=None, stderr=None, correl=None, units=None, decimals=5, **kws):
        args=dict(locals()); args.update(kws)
        del args["self"],args["kws"] 
        super(Parameter, self).__init__(**args)
        
             
#
def FeffPathGroup(filename=None,  label=None, s02=None,
             degen=None, e0=None,ei=None, deltar=None, sigma2=None,
             third=None, fourth=None):
    """Feff Path Group from a *feffNNNN.dat* file.

    Parameters:
    -----------
      filename:  name (full path of) *feffNNNN.dat* file
      label:     label for path   [file name]
      degen:     path degeneracy, N [taken from file]
      s02:       S_0^2    value or parameter [1.0]
      e0:        E_0      value or parameter [0.0]
      deltar:    delta_R  value or parameter [0.0]
      sigma2:    sigma^2  value or parameter [0.0]
      third:     c_3      value or parameter [0.0]
      fourth:    c_4      value or parameter [0.0]
      ei:        E_i      value or parameter [0.0]

    For all the options described as **value or parameter** either a
    numerical value or a Parameter (as created by param()) can be given.

    Returns:
    ---------
        a FeffPath Group.
    """
    args=dict(locals())
    x= xafs.feffdat.feffpath(**args)
    scatters=[i[0] for i in x.geom]
    scatters[0]=scatters[0]+"_a"
    scatters.append(scatters[0])
    x.geomg= "->".join(scatters)
    return x


def _PathsList(filenames,labels=None):
        """quick do a list of path and a group of parameter associated for 
           multiple shells
        Parameters
        ---------
           filenames: list of filemnames from path or a list of path class
           label: a string defining number of path 
           vary a all parameter flag
        """
        pathlist=list()
        methvar = zip(['s02', 'e0', 'sigma2', 'deltar'],              #nome variabili
                      ["amp", "del_e0", "sig2", "del_r"])             #nome parameter
        
        for j,item in enumerate(filenames):
            pathtype=FeffPathGroup(filename=item)
            if labels is None:
                pathtype.label='_%s'%(pathtype.label[-8:-4])
                if any([i.label for i in pathlist])==pathtype.label:
                    pathtype.label=pathtype.label+'_b'
            else:
                pathtype.label='_%s'%(label)
            for meth_item, var_item in methvar: 
                setattr(pathtype, meth_item, var_item+pathtype.label)
            pathlist.append(pathtype)       
        return pathlist
#
class TransformGroup(xafs.TransformGroup):
    """A Group of transform parameters.
    The apply() method will return the result of applying the transform,
    ready to use in a Fit.   This caches the FT windows (k and r windows)
    and assumes that once created (not None), these do not need to be
    recalculated....
    
    That is: don't simply change the parameters and expect different results.
    If you do change parameters, reset kwin / rwin to None to cause them to be
    recalculated."""
    def __init__(self, kmin=0, kmax=20, kweight=2, dk=4, dk2=None, 
                 window='kaiser', nfft=2048, kstep=0.05, rmin=0, rmax=10, dr=0,
                 dr2=None, rwindow='hanning', fitspace='r',  **kws):
        args=dict(locals()); args.update(kws)
        del args["self"],args["kws"] 
        super(TransformGroup, self).__init__(**args)

    
class FeffitDataSet(xafs.FeffitDataSet):
    """a data + a list of path class + TransformGroup
    """
    def __init__(self, data=None, pathlist=None, transform=None, **kws):
        args=dict(locals()); del args["self"]
        super(FeffitDataSet, self).__init__(**args) 




def feffit(params, datasets, rmax_out=10, path_outputs=True,  **kws):
    """execute a Feffit fit: a fit of feff paths to a list of datasets

    Parameters:
    ------------
      paramgroup:   group containing parameters for fit
      datasets:     Feffit Dataset group or list of Feffit Dataset group.
      rmax_out:     maximum R value to calculate output arrays.
      path_output:  Flag to set whether all Path outputs should be written.

    Returns:
    ---------
      a fit results group.  This will contain subgroups of:

        datasets: an array of FeffitDataSet groups used in the fit.
        params:   This will be identical to the input parameter group.
        fit:      an object which points to the low-level fit.

     Statistical parameters will be put into the params group.  Each
     dataset will have a 'data' and 'model' subgroup, each with arrays:
        k            wavenumber array of k
        chi          chi(k).
        kwin         window Omega(k) (length of input chi(k)).
        r            uniform array of R, out to rmax_out.
        chir         complex array of chi(R).
        chir_mag     magnitude of chi(R).
        chir_pha     phase of chi(R).
        chir_re      real part of chi(R).
        chir_im      imaginary part of chi(R).
        
    Examples:
    ---------
      
    """
    return xafs.feffit(params, datasets,  rmax_out=10, path_outputs=True, **kws)

def feffit_report(result, min_correl=0.1, with_paths=True ):
    """return a printable report of fit for feffit

    Parameters:
    ------------
      result:      Feffit result, output group from feffit()
      min_correl:  minimum correlation to report [0.1]
      wit_paths:   boolean (True/False) for whether to list all paths [True]

    Returns:
    ---------
      printable string of report.

    """
    return myfeffit_report(result, min_correl=0.1, with_paths=True)


#
def QSFEFF(Absorber, Scatterer, rad=2,edge="K",geometry='Tetrahedral'): 
    """generate a feff file to calculate a scattering phase and amplitude 
       for a couple absorber scatterer ata distance rad for the edge 
       and the geometry defined
       input:
       -Absorber, Scatterer=string
       -Edge = K, L1, L2, L3
       -Geometry = Tetrahedral, Sq Planar, Octahedral, Icosahedral
    """    
    EdgeN=  str(QN_Transition.index(edge)+1)
    Ct = Absorber
    Sc = Scatterer
    rad_s=str(rad)
    #routine to run a feff script!
    #puts all work in the folder fefftemp
    #finput=open("feff.inp","w")
        
        
    if geometry=='Tetrahedral':
            d=round((rad/ 1.7320508),4)
            d1=str(d)
            geotext=" 0.0000              0.0000         0.0000         0   "+Absorber+"   0.00 \n " 
            geotext+=  d1+"              "+d1+"          "+d1+"         1   "+Scatterer+"   "+rad_s+"\n"
            geotext+= "-"+d1+"            -"+d1+"         "+d1+"         1   "+Scatterer+"   "+rad_s+"\n"
            geotext+= "-"+d1+"             "+d1+"        -"+d1+"         1   "+Scatterer+"   "+rad_s+"\n "
            geotext+= d1+"              -"+d1+"          -"+d1+"         1   "+Scatterer+"   "+rad_s
                   
    if geometry=='Sq Planar':                                
            d=str(rad)
            geotext=" 0.0             0.0          0.0       0   "+Absorber+"              0.0\n"
            geotext+=  d+"          0          0          1   "+Scatterer+"     "+rad_s+"\n"
            geotext+=  "-"+d+"          0         0          1   "+Scatterer+"     "+rad_s+"\n"
            geotext+=  "0          "+d+"          0          1   "+Scatterer+"     "+rad_s+"\n"
            geotext+=  "0         -"+d+"          0          1   "+Scatterer+"     "+rad_s           
                                              
    if geometry=='Octahedral':
            d=str(rad)
            geotext="  0.00        0.00       0.00      0    "+Absorber+"      Ct\n"    
            geotext+=  d+"       0.00        0.00       1  "+Scatterer+"      "+rad_s+"\n"
            geotext+=  "-"+d+"   0.00        0.00       1 "+Scatterer+"      "+rad_s+"\n"
            geotext+=  "0.00       "+d+"     0.00          1  "+Scatterer+"      "+rad_s+"\n"
            geotext+=  "0.00      -"+d+"     0.00          1  "+Scatterer+"      "+rad_s+"\n"
            geotext+=  "0.00       0.00      "+d+"          1  "+Scatterer+"      "+rad_s+"\n"    
            geotext+=  "0.00       0.00     -"+d+"          1  "+Scatterer+"      "+rad_s    
                        
    if geometry=='Icosahedral':
            d=rad/ 1.41421356
            d1=str(d)
            geotext=" 0.0          0.0           0.0           0   "+Absorber+"  0.0000\n"       
            geotext+=  d1+"           "+d1+"                0.0        1   Sc      "+rad_s+"\n" 
            geotext+=  d1+"               0.0              "+d1+"      1   Sc      "+rad_s+"\n" 
            geotext+=  "0.0               "+d1+"           "+d1+"      1   Sc      "+rad_s+"\n"
            geotext+=  "-"+d1+"          -"+d1+"              0.0          1   Sc      "+rad_s+"\n"
            geotext+=  "-"+d1+"               0.0             -"+d1+"      1   Sc      "+rad_s+"\n"
            geotext+=  "0.0              -"+d1+"          -"+d1+"      1   Sc      "+rad_s+"\n"                           
            geotext+=  "-"+d1+"           "+d1+"              0.0          1   Sc      "+rad_s+"\n"
            geotext+=  "-"+d1+"               0.0              "+d1+"      1   Sc      "+rad_s+"\n"
            geotext+=  "0.0              -"+d1+"           "+d1+"      1   Sc      "+rad_s+"\n"
            geotext+=  d1+"          -"+d1+"              0.0          1   Sc      "+rad_s+"\n"
            geotext+=  d1+"              0.0              -"+d1+"      1   Sc      "+rad_s+"\n"
            geotext+=  "0.0               "+d1+"          -"+d1+"      1   Sc      "+rad_s                 
    #begin file writing                                                                                            
    N_Absorber = str(elements.index(Absorber))
    N_Scatterer = str(elements.index(Scatterer))
    feffinput = "* This file created by Quando ho un nome te lo dico   \n"
    feffinput += "TITLE "+Absorber+"<->"+Scatterer+" Single Scatering \n"
    feffinput += "HOLE     "+EdgeN+"   1.0\n"          
    feffinput += "CONTROL  1 1 1 1 1 1\n"    
    feffinput += "PRINT    1 0 0 0 0 3\n"
    feffinput += "RMAX "+str(rad+.40)+"\n"      
    feffinput += "POTENTIALS\n"
    feffinput += "  0  "+N_Absorber+"  "+Absorber+"\n"    
    feffinput += "  1  "+N_Scatterer+"  "+Scatterer+"\n"    
    feffinput += "\n"
    feffinput += "ATOMS\n"
    feffinput += " * x          y          z          ipot tag dist\n"
    feffinput += geotext

    return feffinput
        

    
