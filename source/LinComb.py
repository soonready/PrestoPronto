#!/usr/bin/env python
""" a small class for Principal Component Analysis
   Usage:
       p = PCA(A)
   In:
       A: an array of e.g. 1000 observations x 20 variables, 1000 rows x 20 columns
       the column are the collected spectra
   
   Out:
       pV autovalue
       pR matrice componenti (sono righe)
       pU matrice componenti (sono righe) non pesata per autovalori
       pC matrice loading (sono colonne)

   Methods:
   Notes:
   See also:
       http://en.wikipedia.org/wiki/Principal_component_analysis
       http://en.wikipedia.org/wiki/Singular_value_decomposition
       Press et al., Numerical Recipes (2 or 3 ed), SVD
       PCA micro-tutorial
       iris-pca .py .png
   
"""

import lmfit
import asteval
import numpy as np
from scipy import interpolate
from collections import OrderedDict as OrdDict
import warnings
import re
NAME_MATCH = re.compile(r"[a-z_][a-z0-9_]*$").match

def _issymbol_name(name):
    "input is a valid name"
    lname = name[:].lower()
    return NAME_MATCH(lname) is not None

try:
    from asteval import Interpreter, NameFinder, valid_symbol_name
    HAS_ASTEVAL = True
except:
    HAS_ASTEVAL = False
    valid_symbol_name = _issymbol_name
#########################################################################################################
class standard():
    def __init__(self, label,x,y,x0=None,  value=None, fix=False, mini=None,maxi=None,expr=None):  
        self.label=label
        self.param= lmfit.Parameter(self.label, value=value, vary=not(fix), expr=expr,
            min=mini, max=maxi)
        self.x=x
        self.y=y
        self.x0=x0
        if x0==None:
            pass
        elif all(self.x==x0): 
            self.y0=self.y
        else:
            self.spline = interpolate.splrep(x, y, s=0)
            self.y0=interpolate.splev(self.x0, self.spline, der=0, ext=2)
    
            
    def interpolation(self,x0):
        if not hasattr(self, "spline"):
            self.spline = interpolate.splrep(self.x, self.y, s=0)
        if np.array_equal(x0,self.x0):
            return
        else:    
            self.x0=x0    
            self.y0=interpolate.splev(self.x0, self.spline, der=0, ext=2)
            
    def refresh(self,**keywd):
        for item in keywd:
            if hasattr(self.param, item):
                setattr(self.param,item,keywd[item])
            else:    
                raise ValueError("'%s' is not a key of Parameter" % item)            
            
            
            
            


#########################################################################################################
class standard_list(OrdDict):    
    def __init__(self, *args):
        OrdDict.__init__(self)
        self.Standard_Parameters=lmfit.Parameters()
        for item in args:
            OrderedDict.__setitem__(self,item.label, item)
            self.Standard_Parameters.__setitem__(item.label,item.param)


    def __setitem__(self, key, standard_instance):
        if key not in self:
            if not valid_symbol_name(key):
                raise KeyError("'%s' is not a valid Parameters name" % key)
        if standard_instance is not None and not isinstance(standard_instance, standard):
            raise ValueError("'%s' is not a Standars" % standard_instance)
        OrdDict.__setitem__(self,key, standard_instance)
        self.Standard_Parameters.__setitem__(key, standard_instance.param)
        
        
    def add(self, standard_instance):
        """convenience function for adding a Parameter:
        with   p = Parameters()
        p.add(name, value=XX, ....)

        is equivalent to
        p[name] = Parameter(name=name, value=XX, ....
        """
        self.__setitem__(standard_instance.label, standard_instance)

        
        

    



#########################################################################################################
class LinComb():
    """
        a class for LinComb analysis 
        as input ,x,y, standards
        an numpy array with data n_points X   n_spectra 
        standard = special class [ordered dict standard list]
   """
    def __init__(self,x,y, standards):
        self.x=x
        self.y=y
        self.standards_list=standards
        n_auto=0
        residual=1
        #to make a first estimation of the values
        #ipothesis is that the total is 1 and all standard 
        # have similar weigh if not specified
        for item in self.standards_list.itervalues():
            item.interpolation(self.x)
            if item.param.value==None: n_auto+=1.0
            else:residual-= item.param.value
        if n_auto>0:    
            average=residual/n_auto
            for key,dic_value in self.standards_list.iteritems():
                if dic_value.param.value==None:
                    self.standards_list.Standard_Parameters[key].value=average
            
        self.D= np.column_stack([self.standards_list[key].y0 for key in self.standards_list])

        
            

        
    def solve(self):
        def residual(params, D, data=None):
            # unpack parameters:
            #  extract .value attribute for each parameter
            column_coeff=np.array([item.value for item in params.values()])
            model =np.dot(D,column_coeff)  
            if data is None:
                return model
            return (model - data)
        self.result = lmfit.minimize(residual, self.standards_list.Standard_Parameters, args=(self.D, self.y))
        #print self.result.chisqr
        #print 'Best-Fit Values:'
        #for name, par in self.standards_list.Standard_Parameters.items():
        #    print '  %s = %.4f +/- %.4f ' % (name, par.value, par.stderr)
        
        

################################################################################
################################################################################

