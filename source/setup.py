from setuptools import setup, find_packages

setup(
	name = "PrestoPronto",
	version = "1.0.0",
        author='carmelo prestipino',
        author_email='carmelo.prestipino@univ-rennes1.fr',
        url='http://code.google.com/p/prestopronto/',
        description = "QEXAFS data analysis software",
	py_modules = '''Alligbm29 Correct LinComb PPExafs PPInput text varimaxH
                        bm29 exapy molcomp PCA PPset Rebin TScrolledFrame
			varimax bm29_tools musst PPAvesel PPFit PPXanes
			session utility xtables
		     '''.split(),
	scripts = ['PrestoPronto.py', 'PCA_GUI.py', 'LinComb_GUI.py']
)
