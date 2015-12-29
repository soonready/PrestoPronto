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
import Ifeffit  
import numpy  as np
from tables import elements, QN_Transition 
from scipy.interpolate import LSQUnivariateSpline as Spline
global iff 
global __verbose__
__verbose__ = False#True#

       
class exaPy:
    """EXAFS class defined in order to analyze the Mu signals
    it define till noz three function 
    XANES_Norm results in array attributes Nor
    EXAFS_EX   results in array attributes k, chi, Bkg
    FT_T results in array attributes mag  pha real imag 
    """
    def __init__(self, E = None, Mu = None):
         self.E=E
         self.Mu = Mu
         self.Eo=0
         self.ej=0
         self.pr_es=0
         self.pr_ee=0  
         self.po_es=0
         self.po_ee=0 
         self.flatten = 1  
         self.rbkg=1.0
         self.skmin=0.0
         self.skmax=0  
         self.skweight=0
         self.skwindow="kaiser-bessel"
         self.norm_order=2
         self.kmin=0.0
         self.kmax=0  
    
    def XANES_Norm2(self, Eo=0, pr_es= 0, pr_ee=0, po_es=0 , po_ee=0, flatten = 1):
          """perform XANES normalization
          E= energu array, Mu = absorbtion array
          pr_es and pr_ee start and end of preedge(negative value)
          po_es and po_ee start and end post edge normalization
          returns:
          self.Nor = Xanes normalize,
          self.Eo= e0
          self.ej = edge step,  """
          if  self.E==None or self.Mu==None:          
              raise exaPyError, ('no E and Mu defined ')
          iff=Ifeffit.Ifeffit()
          iff.put_array("my.energy", self.E)                                          
          iff.put_array("my.xmu", self.Mu)
          pre_edge_com = "pre_edge(my.energy, my.xmu, group =my" 
          if (Eo!=0): pre_edge_com += ",e0= %f" % Eo 
          if (pr_es!=0): pre_edge_com += ", pre1= %f" % pr_es
          if (pr_ee!=0): pre_edge_com += ", pre2= %f" % pr_ee
          if (po_es!=0): pre_edge_com += ", norm1= %f" % po_es
          if (po_ee!=0): pre_edge_com += ", norm2= %f" % po_ee
          iff.ifeffit(pre_edge_com +")")
          Eo = iff.get_scalar("e0")        
          Ej = iff.get_scalar("edge_step")
          if (po_ee == 0):
               pre_edge_com += ", norm2= %f" % (max(self.E)-Eo-5)
               iff.ifeffit(pre_edge_com +")")
          print pre_edge_com +")"
          norm = iff.get_array("my.norm")
          self.pr_es = iff.get_scalar("pre1")
          self.pr_ee = iff.get_scalar("pre2")
          self.po_es = iff.get_scalar("norm1")
          self.po_ee = iff.get_scalar("norm2")   
          self.Eo = Eo
          self.Ej = Ej
          self.Nor = norm
          if (flatten):                           
               n0 = iff.get_scalar("norm_c0")
               n1 = iff.get_scalar("norm_c1")
               n2 = iff.get_scalar("norm_c2")
               p0 = iff.get_scalar("pre_offset")
               p1 = iff.get_scalar("pre_slope")
               ej = iff.get_scalar("edge_step")    
               flat = lambda x: 0 if (x <= Eo) else (p0-n0+ej)+ (p1-n1)*x - n2*x**2
               for i,item in enumerate(self.Nor): self.Nor[i] = item +flat(self.E[i])/ej # 
          return   


    def XANES_Norm(self, Eo=0, pr_es= 0, pr_ee=0, po_es=0 , po_ee=0, flatten = 1, n_postpoly=3, operation={"p":True,"n":True}):
          """perform XANES normalization
          E= energu array, Mu = absorbtion array
          Eo = Edge enrgy (max first derivative)
          pr_es and pr_ee start and end of preedge (pr_es =start of spectra, pr_ee =Eo-50 )
          po_es and po_ee start and end post edge normalization
          n_postpoli= degree of polinomial for post edge normalization
          operation = dictionary with key "p" and "n" and boolean values define if perform pre
                     edge subtraction and/or normalization
          returns:
          self.Nor = Xanes normalize,
          self.Eo= e0
          self.ej = edge step,  """
          if  self.E==None or self.Mu==None:          
              raise exaPyError, ('no E and Mu defined ')
          
          # derivative obtained by method of local difference
          dif=np.gradient(self.Mu)/np.gradient(self.E)
       
          
          if (Eo==0):    Eo= self.E[np.argmax(dif)]
          if (pr_es==0): pr_es= min(self.E)-Eo
          if (pr_ee==0): pr_ee= -50
          if (po_es==0): po_es= 150
          if (po_ee==0): po_ee= max(self.E)-Eo
          


          if operation["p"]:
              preedgecond=(self.E>(Eo+pr_es))&(self.E<=(Eo+pr_ee))
              self.preedge_poly=np.poly1d(np.polyfit(self.E[preedgecond],self.Mu[preedgecond], 1))
          else: self.preedge_poly=np.poly1d([0])
              
              
          postedgecond= (self.E>Eo+po_es)&(self.E<=Eo+po_ee)
          self.postedge_poly=np.poly1d(np.polyfit(self.E[postedgecond],self.Mu[postedgecond], n_postpoly))
          
          Ej= self.postedge_poly(Eo)-self.preedge_poly(Eo) if operation["n"] else 1.0
          norm= (self.Mu-self.preedge_poly(self.E))/Ej
          
          if (flatten):
              polyflat=self.postedge_poly-self.preedge_poly 
              norm[self.E>Eo]=  norm[self.E>Eo]-(polyflat(np.compress(self.E>Eo,self.E))/Ej -1)
          #flat = lambda x: 0 if (x <= Eo) else (p0-n0+ej)+ (p1-n1)*x - n2*x**2
          #for i,item in enumerate(self.Nor): self.Nor[i] = item +flat(self.E[i])/ej 

        
          self.pr_es = pr_es
          self.pr_ee = pr_ee
          self.po_es = po_es
          self.po_ee = po_ee   
          self.Eo = Eo
          self.Ej = Ej
          self.Nor = norm
          del norm
          if __verbose__:
              print "pre_edge(Eo= %5.2f,pr_es= %5.2f ,pr_ee %5.2f ,po_es %5.2f ,po_ee= %5.2f, flatten= %i)" %(Eo, pr_es ,pr_ee,po_es ,po_ee, flatten)
          # 
          return 










        
        
        
        
        
        
    #def EXAFS_EX2(self, Eo=0, knot=0, wknot=0 rbkg=1.0, skmin=0.0, skmax=0, skweight=0,
    #           sdk=0, skwindow="kaiser-bessel", pr_es= 0, pr_ee=0, 
    #           po_es=0 , po_ee=0, norm_order=0): 
    #     """Function for the exptattion of EXAFS signal
    #     input parameters:
    #        E= energu array, 
    #        Mu = absorbtion array
    #        knot=array of knot, 
    #        wknot=array with the weigh of splines
    #        rbkg = paremeter rbkg 
    #        skweight= kweight for FT
    #        skmin and skmax for FT
    #        sdk  apodization
    #        pr_es and pr_ee = start and end of preedge
    #        po_es and po_ee = start and end post edge normalization
    #     returns attributes:
    #        Eo =edge energy
    #        ej =edge step
    #        Bkg =Mu_0 background array 
    #        chi =chi array
    #        k  = k array  
    #     """ 
    #LSQUnivariateSpline(self.E, self.Mu, t, w=None, bbox=[, None, None], k=3)   
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    def EXAFS_EX(self, Eo=0, rbkg=1.0, skmin=0.0, skmax=0, skweight=0,
               sdk=0, skwindow="kaiser-bessel", pr_es= 0, pr_ee=0, 
               po_es=0 , po_ee=0, norm_order=0):
         """Function for the exptattion of EXAFS signal
         input parameters:
            E= energu array, 
            Mu = absorbtion array
            rbkg = paremeter rbkg 
            skweight= kweight for FT
            skmin and skmax for FT
            sdk  apodization
            pr_es and pr_ee = start and end of preedge
            po_es and po_ee = start and end post edge normalization
         returns attributes:
            Eo =edge energy
            ej =edge step
            Bkg =Mu_0 background array 
            chi =chi array
            k  = k array  
         """        
         iff=Ifeffit.Ifeffit()
         iff.put_array("my.energy", self.E)
         iff.put_array("my.xmu", self.Mu)       
         spline_com = "spline(my.energy, my.xmu, group =my" 
         if (Eo!=0): spline_com += ",e0= %f" % Eo 
         if (pr_es!=0): spline_com += ", pre1= %f" % pr_es
         if (pr_ee!=0): spline_com += ", pre2= %f" % pr_ee
         if (po_es!=0): spline_com += ", norm1= %f" % po_es
         if (po_ee!=0): spline_com += ", norm2= %f" % po_ee
         if (rbkg!=1): spline_com += ",  rbkg= %f" % rbkg
         if (skmin!=0): spline_com += ", kmin= %f" % skmin
         if (skmax!=0): spline_com += ", kmax = %f" % skmax
         if (skweight!=0): spline_com += ", kweight= %f" % skweight
         if (sdk!=0): spline_com += ", dk= %f" % sdk
         if (skwindow!="kaiser-bessel"): spline_com += ", kwindow= %s" % skwindow
         if (norm_order!=2): spline_com += ", norm_order = %f" % norm_order
         iff.ifeffit(spline_com +")")      
         self.Eo = iff.get_scalar("e0")                                              
         self.ej = iff.get_scalar("edge_step")
         self.pr_es = iff.get_scalar("pre1")
         self.pr_ee = iff.get_scalar("pre2")
         self.pr_os = iff.get_scalar("norm1")
         self.pr_oe = iff.get_scalar("norm2")   
         self.skmin = iff.get_scalar("kmin")
         self.skmax = iff.get_scalar("kmax")
         self.skweight = iff.get_scalar("kweight")
         self.bkg = iff.get_array("my.bkg")        
         self.chi = iff.get_array("my.chi")
         self.k =   iff.get_array("my.k")             
         #Norm = iff.get_array("my.norm")
         return                
        

    def FT_F(self,  kmin=0 , rmax_out=0 ,kmax=0, dk=0.5, kweight=-1, kwindow='hanning' ):
         """FT_F fourie transform an exafs sygnal
         E= energu array, Mu = absorbtion array
         pr_es and pr_ee start and end of preedge
         po_es and po_ee start and end post edge normalization
         returns:e0, edge step """ 
         iff=Ifeffit.Ifeffit()
         iff.put_array("my.chi", self.chi)
         iff.put_array("my.k", self.k)    
         ffts_com = "fftf(real = my.chi, k = my.k, group =my"
         if (kmin!=0): ffts_com += ", kmin= %f" % kmin
         if (kmax!=0): ffts_com += ", kmax= %f" % kmax
         else:  ffts_com += ", kmax= %f" % max(self.k)
         if (rmax_out!=0): ffts_com += ", rmax_out= %f" % rmax_out                                              
         if (dk!=0): ffts_com += ", dk= %f" % dk  
         if (kweight!=-1): ffts_com += ", kweight= %f" % kweight 
         else:  ffts_com += ", kweight= 2"          
         ffts_com +=", kwindow= %s" % kwindow
         iff.ifeffit(ffts_com +")") 
         self.mag  =iff.get_array("my.chir_mag")    
         self.pha  =iff.get_array("my.chir_pha")    
         self.real =iff.get_array("my.chir_re")    
         self.imag =iff.get_array("my.chir_im")
         self.r    =iff.get_array("my.r")
         return    
         
         
    def FT_R(self, real, imag,  r,  rmin=0 , rmax=3, dr=0.0, rweight=-1, rwindow='hanning' ):
         """FT_T fourie transform an exafs sygnal
         E= energu array, Mu = absorbtion array
         pr_es and pr_ee start and end of preedge
         po_es and po_ee start and end post edge normalization
         returns:e0, edge step """ 
         iff=Ifeffit.Ifeffit()
         iff.put_array("my.real", Real)
         iff.put_array("my.imag", Img)
         iff.put_array("my.r", r)
         ffts_com = "fftf(real = my.chi, imag = my.imag, k = my.k, group =my"
         if (Rmin!=0): ffts_com += ", rmin= %f" % kmin
         if (Rmax!=3): ffts_com += ", rmax= %f" % kmax
         else:ffts_com += ", rmax= %f" % kmax
         if (dk!=0): ffts_com += ", dr= %f" % dk  
         if (rweight!=-1): ffts_com += ", rweight= %f" % kweight 
         else:  ffts_com += ", rweight= 2"  
         ffts_com +=", rwindow= %s" % rwindow
         iff.ifeffit(ffts_com +")") 
         self.chiq  =iff.get_scalar("my.chiq_mag")    
         self.q =iff.get_scalar("my.q")    
         return    
                  
         
         
         
    def FIT(self, kmin=0, kmax=0, rmin=0, rmax=6, dk=.5, kweight=2,kwindow="hanning", fit_space = "R", path=[]):
        """EXAFS Fit function
        E= energu array, Mu = absorbtion array
        pr_es and pr_ee start and end of preedge
        po_es and po_ee start and end post edge normalization
        returns:e0, edge step 
        path     list of path class
        """ 
        iff=Ifeffit.Ifeffit() 
        #iff.ifeffit("show @scalars")
        iff.put_array("my.chi", self.chi)
        iff.put_array("my.k", self.k)
        
        for index,item in enumerate(path):
            pathcom=[]
            pathcom.append("path(%d, feff = \"%s\")"       %(index+1, item.feff_file)      )   
            pathcom.append("path(%d, degen =     n%d)"      %(index+1, index+1)               )   
            pathcom.append("path(%d, e0        = e%d)"      %(index+1, index+1)               )   
            pathcom.append("path(%d, sigma2    = s%d)"      %(index+1, index+1)               )   
            pathcom.append("path(%d, delr = r%d-reff)"      %(index+1, index+1)               )
            pathcom.append("path(%d, force_read=  %s)"      %(index+1, item.force_read)     )  
            #----------------------------------    
            pathcom.append("%s  n%d    = %f"  %(item.degen_minimize, index+1, item.degen_start))   
            pathcom.append("%s  e%d    = %f"  %(item.e0_minimize   , index+1, item.e0_start   ))   
            pathcom.append("%s  r%d    = %f"  %(item.r_minimize    , index+1, item.r_start   ))   
            pathcom.append("%s  s%d    = %f"  %(item.ss2_minimize  , index+1, item.ss2_start  ))
            print "***********"
            for ip in pathcom: 
                print ip
                iff.ifeffit(ip)
        print "************************"
        #iff.ifeffit("show @paths")
        #print "************************"        
        fitcom= "feffit(1-%d, group=my_fit, chi=my.chi, k=my.k" % len(path)
        #fitcom= "feffit(1-%d, group=my_fit, chi=my.chi, k=my.k, kweight=2, kmax=16, rmax=3"
        fitcom += ", kmin=%s"  % kmin
        if (kmax!=0): fitcom += ", kmax=%f" % kmax
        else:  fitcom += ", kmax=%.2f" % max(self.k)     
        fitcom +=    ", rmin=%s"  % rmin
        fitcom +=    ", rmax=%s"  % rmax
        fitcom += ", kweight=%s"  % kweight
        fitcom +=      ", dk=%s"  % dk          
        fitcom +=", kwindow=%s"  % kwindow
        fitcom +=", fit_space=%s"  % fit_space 
        print fitcom+")"
        ceck=iff.ifeffit(fitcom+")") 
        print "check= ", ceck
        self.fit_res = {}
        for itera in range(len(path)):
            for item in "ners":
                pa = item+str(itera+1)
                self.fit_res[pa] = iff.get_scalar(pa) 
                delta_pa = "delta_"+pa
                self.fit_res[delta_pa] = iff.get_scalar(delta_pa)
            pass
        pass
        print "************************"
        #iff.ifeffit("show @group=my_fit")
        #iff.ifeffit("show @group=my")        
        #print self.fit_res
        #iff.ifeffit("show @scalars")        
        self.fit_chi  =iff.get_array("my_fit.chi")    
        self.fit_mag  =iff.get_array("my_fit.chir_mag")    
        self.fit_imag =iff.get_array("my_fit.chir_im")
    
    
    
    
class path:    
    #class param(self, )
    def __init__(self,feff):                              
        self.feff_file = str(feff)
        self.force_read="false"
        self.para=["degen", "s02", "e0", "delr", "sigma2"]
        feffpath=open(feff)
        while (True):
            line=feffpath.readline()
            if line[1]=="-": break
        line=feffpath.readline()           
        line = line.split()
        self.nlegs, self.deg, self.reff = line[0:3]
        line=feffpath.readline()         
        geom=[]
        while (True):
            line=feffpath.readline()
            #print line
            #print line[4]
            if line[4]=="k": break
            geom.append(line.split()[5])
        self.geom= "<->".join(geom)            
        feffpath.close()
        self.degen_start=   float(self.deg)
        self.s02_start=     float(1)
        self.e0_start=      float(0)
        self.ss2_start =    float(0.005) 
        self.r_start=       float(self.reff)
        setattr(self, "r_minimize",  "guess")
        setattr(self, "degen_minimize",  "guess")
        setattr(self, "s02_minimize",  "def")  
        setattr(self, "e0_minimize",  "guess")
        setattr(self, "ss2_minimize",  "guess")    
        return  








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
    feffinput += "RMAX = "+str(rad+.40)+"\n"      
    feffinput += "POTENTIALS\n"
    feffinput += "  0  "+N_Absorber+"  "+Absorber+"\n"    
    feffinput += "  1  "+N_Scatterer+"  "+Scatterer+"\n"    
    feffinput += "\n"
    feffinput += "ATOMS\n"
    feffinput += " * x          y          z          ipot tag dist\n"
    feffinput += geotext

    return feffinput
        

    
