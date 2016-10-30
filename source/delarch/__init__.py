from symboltable import Group, isgroup
from lmfit import Parameter, Parameters
#from fitting.minimizer import eval_stderr
from lmfit.uncertainties import correlated_values
from lmfit.minimizer     import eval_stderr

paramGroup=Parameters()
#from .fitting import Minimizer, Parameter, isParameter, param_value
#global paramGroup
#paramGroup=None