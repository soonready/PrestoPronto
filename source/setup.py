from cx_Freeze import setup, Executable

import sqlalchemy
import larch
import larch_plugins
#includes = ["scipy.linalg","numpy"]
#copyDependentFiles=True



excludes = ["pywin", "tcl", "pywin.debugger", "pywin.debugger.dbgcon","pywin.dialogs", "pywin.dialogs.list", "win32com.server","email"] 
#includes = ["PyQt4.QtCore","PyQt4.QtGui","win32gui","win32com","win32api","html.parser","sys","threading","datetime","time","urllib.request","re","queue","os"] 

                



com_file=['./Doc',
          'feff6l.exe',
          'README.txt',
          'LICENCE.txt',
          'PrestoPronto.iss']




packages = [] 
path = [] 
excluded_mod=["Panda","PyQt4","PyQt4.QtGui","win32gui","pywin", "tcl", 
              "pywin.debugger", "pywin.debugger.dbgcon","pywin.dialogs",
              "pywin.dialogs.list", "win32com.server","email"
              '_imagingtk', 'PIL._imagingtk', 'ImageTk',
              'PIL.ImageTk', 'matplotlib.tests', 'qt', 'PyQt4Gui', 'IPython',
              'pywin', 'pywin.dialogs', 'pywin.dialogs.list']#,"mathplotlib"
              
included_mod=["scipy.special._ufuncs_cxx",
               "scipy.constants",
               "scipy.integrate.vode",
               "scipy.integrate.lsoda",
               "scipy.sparse.csgraph._validation",
               "FileDialog",
               "lmfit",
               "xtables"]#,"matplotlib.backends.backend_tkagg"]#"Tix"

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
        version = "1.0",
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
#"includes": includes,   #"excludes": excludes,#"packages": packages,#"path": path
#"includes": includes,   #"excludes": excludes,#"packages": packages,#"path": path