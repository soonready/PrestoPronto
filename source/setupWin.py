from cx_Freeze import setup, Executable
import scipy
from os.path import dirname


from cx_Freeze import hooks
def load_scipy_patched(finder, module):
    """the scipy module loads items within itself in a way that causes
        problems without the entire package and a number of other subpackages
        being present."""
    finder.IncludePackage("scipy._lib")  # Changed include from scipy.lib to scipy._lib
    finder.IncludePackage("scipy.misc")

hooks.load_scipy = load_scipy_patched





com_file=['./Doc',
          'feff6l.exe',
          'README.txt',
          'LICENCE.txt',
          'PrestoPronto.iss']
scipy_path = dirname(scipy.__file__)
com_file.append(scipy_path)



packages = [] 
path = [] 

excluded_mod=["collections.abc","PyQt4","PyQt4.QtGui",
              "win32gui","pywin", "tcl", "pywin.debugger", 
              "pywin.debugger.dbgcon","pywin.dialogs", 
              "pywin.dialogs.list", "win32com.server","email"]
included_mod=[ "FileDialog",
               "lmfit"]
           
before_included=["Tix","scipy.special._ufuncs_cxx","scipy.integrate.vode",
                  "scipy.integrate.lsoda","scipy.sparse.csgraph._validation"]

#GUI2Exe_Target_1 = Executable(
#    script = "script.pyw",
#    initScript = None,
#    base = 'Win32GUI',
#    targetName = "app.exe",
#    compress = True,
#    copyDependentFiles = True,
#    appendScriptToExe = False,
#    appendScriptToLibrary = False,
#    icon = "icon.png"
#    ) 

setup(
        name = "PrestoPronto",
        version = "0.6",
        author='carmelo prestipino',
        author_email='carmelo.prestipino@univ-rennes1.fr',
        url='http://code.google.com/p/prestopronto/',
        description = "QEXAFS data analysis software",
        options = {"build_exe": { 
                                 "includes" : included_mod,           #    comman
                                 "excludes" : excluded_mod,           #    comman 
                                 "packages": packages,                #    comman
                                 "path": path,                         #    comman                          
                                 "optimize" : 2,                      #    comman
                                 "compressed" : True,                 #    comman
                                 "include_files":com_file}            #    comman
                                 },                                   #   if a comman icon is wanted  "icon" : "./PP.ico",
        executables = [Executable(script ="Prestopronto.py",icon = "./PP.ico"),
                       Executable(script ="PCA_GUI.py", icon = "./PG.ico"),
                       Executable(script ="LinComb_GUI.py", icon = "./PF.ico")
                       ]
        )        
