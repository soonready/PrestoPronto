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
    '''
       x,y + parameter for coefficent
       label 
       x,     x corresponding to the y
       y,     y
       x0:    x point on wich the linear combination fit should be done
       
       value: start value for coefficent  
       fix=(False), could be varing during the fit??
       mini=None,  mini value 
       maxi=None,  max value 
       expr=None   expression for define constrain
       EX:
       LinComb.standard(label=_label, x=spectra[0].x, y=.spectra[0].y, x0=x_array,
                     value=float2(start_value),fix=float2(item._fix.get()),
                     mini=float2(item._mini.get()),maxi=float2(item._maxi.get())
    '''
    def __init__(self, label,x,y, x0=None,  value=None, fix=False, 
                                     mini=None,maxi=None,expr=None, auto=False):  
        self.label=label
        self.param= lmfit.Parameter(self.label, value=value, vary=not(fix), expr=expr,
                                                                min=mini, max=maxi)
        self.x=x
        self.y=y
        self.x0=x0
        self.auto=value
        if x0 is None:
            pass
        elif np.array_equal(self.x,x0): 
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
    """odered dict of standard class+
       a property. Standard_Parameters=lmfit.Parameters()
       the key is defined by the label
       normally to add item use add function
       -------------------------------
       ex:
       Lista_Standard=standard_list(c,b)
       Lista_Standard.add(a)
                                                
    """
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
        """convenience function for adding a standard:
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
        as input x,y, standards
        an numpy array with data n_points X n_spectra 
        standard = special class [ordered dict standard list]
        self.x=x
        self.y=y
        self.standard_list= standards
        self.D=set of all y0 per ogni standard
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
            #print item.param.value, str(item.param.value), repr(item.param.value)
            if item.auto is None: n_auto+=1.0
            else:residual-= item.param.value
        if n_auto>0:    
            average=residual/n_auto
            for key,dic_value in self.standards_list.iteritems():
                if dic_value.auto is None:
                    self.standards_list.Standard_Parameters[key].value=average
        self.D= np.column_stack([self.standards_list[key].y0 for key in self.standards_list])
        #####test####
        #print 'average', average
        #for key,dic_value in self.standards_list.iteritems():
        #    print key, self.standards_list.Standard_Parameters[key].value
        
            

        
    def solve(self, verbose=False):
        def residual(params, D, data=None):
            # unpack parameters:
            #  extract .value attribute for each parameter
            column_coeff=np.array([item.value for item in params.values()])
            model =np.dot(D,column_coeff)  
            if data is None:
                return model
            return (model - data)
        self.result = lmfit.minimize(residual, self.standards_list.Standard_Parameters, args=(self.D, self.y))
        if verbose:
            print self.result.chisqr
            print 'Best-Fit Values:'
            for name, par in self.result.params.items():
                print '  %s = %.4f +/- %.4f ' % (name, par.value, par.stderr)
        
        

################################################################################
################################################################################

