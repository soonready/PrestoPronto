Presto-Pronto is an algorithm initially developed to perform XAFS data reduction for QEXAFS measures taken at
 BM23 (ex BM29) X-ray absorption beamline at ESRF. With the same philosophy of manage a large amount of spectra 
taken in a time resolved experiment the program are able to integrate the ID24 the dispersive absorption beamline at ESRF.
 Now, more QEXAFS and dispersive beamlines from other synchrotrons are addeded and the idea is increase this number.
The program was written in Python version 2.6, for run the program with the source code you need to install 
previosly Python 2.6 plus the libraries: numpy, matplotlib and scipy. 
The program runs with the Prestopronto.py file.
For windows users there is a instalation file available at: 

https://code.google.com/p/prestopronto/downloads/list

Any bug or problem, please let me know:

http://code.google.com/p/prestopronto/issues/list?can=1&q=
or email
carmelo.Prestipino@gmail.com


Best regards


Carmelo Prestipino <carmelo.prestipino@univ-rennes1.fr>
########################################################
#  Dr. Carmelo Prestipino                              #
#  CNRS-Université de Rennes 1                         #
#  Sciences Chimiques de Rennes - UMR 6226             #
#  Matériaux Inorganiques: Chimie Douce et Réactivité  #
#  Campus de Beaulieu, Bât 10B                         #
#  F-35042 RENNES  (France)                            #
#  Tel (+33) 2 23 23 65 31                             #
########################################################

Executable file: PrestoPronto
Author: Carmelo Prestipino 

Copyright 2009 ESRF

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL ILLINOIS INSTITUTE OF TECHNOLOGY BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

version b.1.0.0
17/5/2016
all passed under Larch
several bug corrections
progress bar added
infinite path can be used in fit

version b.0.8.0 
bur solving 
introduced possibility to plot residual after component reconstruction in PCA_GUI



version b.0.6.6
Made interactive windows for first derivative
added PCA_GUI beta


version b.0.6.6
bug fixes 
added interactive windows for rebin parameter



version b.0.6.5
new grap interactive test for XAnes normalization
new function for smooting (more predictable degree of smooting)


version b.0.6.3
ini-files 
test XANES nomalization



version b.0.6.1
bug on SAMBA files resolved

