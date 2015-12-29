from cx_Freeze import setup, Executable

#includes = ["scipy.linalg","numpy"]
#copyDependentFiles=True
setup(
        name = "PCA_GUI",
        version = "0.0.1",
        author='carmelo prestipino',
        author_email='carmelo.prestipino@univ-rennes1.fr',
        url='http://code.google.com/p/prestopronto/',
        description = "PCA_GUI for QEXAFS",
        data_files = [ ('doc', ['doc\Doc.pdf']), ('', ['README.txt'])],
        options = {"build_exe": {"icon" : "./PG.ico", "includes" : []}},
        executables = [Executable("PCA_GUI.py")])
        
#"includes": includes,   #"excludes": excludes,#"packages": packages,#"path": path