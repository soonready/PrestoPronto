#Name: Prestopronto.py
# Purpose: Gui to perform XAFS data reduction.
# Author: C. Prestipino based
#
# Copyright 2016 ISCR
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
# Except as contained in this notice, the name of ESRF
# shall not be used in advertising or otherwise to promote
# the sale, use or other dealings in this Software without prior written
# authorization from ISCR.

##here  a list of supported fileformat from header
class bm29_bm23():
    def recoon(header):
        return or(('BM23' in header[0]),('BM23' in header[0]))
    
    def define_labels(labeline):
        labeline=labeline[2:].replace('alpha','mu')
        
    def define_basedata(group):
        group['energy']=group['e_kev_']*1000
        
    
   
    

bm29_bm23=dict()
bm29['name']='bm29_bm23'
bm29['recon']=bm29_bm23recoon(header)
bm29['define_label']=define_labels(labeline)








fileforma