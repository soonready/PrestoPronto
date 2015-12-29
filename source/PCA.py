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

import numpy as np
import varimax as vari
import varimaxH as vari2
import warnings



class PCA():
    """
        a class for PCA analysis 
        as input an numpy array with data n_points X   n_spectra 
        principal attributes:
        self.D=R*C
        self.V autovalue
        self.R matrice componenti (colonne sonon pure component)
        self.U matrice componenti (colonne sonon pure component) non pesata per autovalori
        self.C matrice loading (righe sono evoluzione di una comonente lubgo il set)
    """
    def __init__(self, D):
        self.D=D
        self.use_constrain=False #True
        self.use_monotonicity=True
        self.constrains_list=[]#CONSTRAIN(0, "=", 0, 0),CONSTRAIN(1, "=", 0, 0),CONSTRAIN(2, "=", 1, 0),CONSTRAIN(2, "=", 0, 8)]
        self.n_col, self.n_row = self.D.shape if self.D.shape[0]<self.D.shape[1] else self.D.shape[::-1]
        #print self.n_col , self.n_row
        self.pca()
        self.EVAL_IND = IND_FUN(self.n_col,self.n_row,self.V)
        
    def pca(self):
        """do pca on the attribute self.D
           return a matrix of autovector 
           and a set of autovalori
        """    
        U,V,C=np.linalg.svd(self.D, full_matrices=False)
        
        if np.trapz(U[:,0])<0:
            print "U negativo"
            self.C, self.U =-C,-U
        else:
            print "U positivo"
            self.C, self.U =C,U
        self.R=np.dot(self.U,np.diag(V))    
        self.V=V**2
        self.atov=V
        return 
        
    def red(self,n):  
        """
        reduce the D matrix
        input :number of component
        self.Cr #Define reduced componenti
        self.Ur #Define reduced componenti non pesata per autovalori
        self.Rr #Define reduced loadind
        """
        self.n_comp=n
        self.Cr=self.C[:n,:]                    
        self.Ur=self.U[:,:n]                    
        self.Rr=self.R[:,:n]                    
        self.Dr=np.dot(self.Rr,self.Cr)

        
        
    def varimax(self):
        """
        make a varimax rotation of self.C matrix
        output:
            self.Cr_rot matrix self.C rotated
            self.Rr_rot matrix self.R rotated     
            self.Needle matrix obtained from self.Cr_rot
                    1 for maximum concentration 0 for the rest
        """
        Crot, rot= vari2.varimax(self.Cr.T, normalize=True)        
        self.Cr_rot, self.rot =Crot.T, rot.T
        self.inv_rot=np.linalg.inv(self.rot)
        self.Rr_rot=np.dot(self.Rr,self.inv_rot)
        for i,item in enumerate(self.Cr_rot):  #Evaluate if main sign is negative
            if np.trapz(item)<0:               # and evantually invert
                self.Cr_rot[i,:]*=-1
                self.Rr_rot[:,i]*=-1        
        self.Needle=np.zeros(self.Cr_rot.shape)
        for r,item in enumerate(self.Cr_rot):
            c=np.argmax(item)
            self.Needle[r,c]=1.0
        #print self.Needle
            
        
    
    def EMiteraction(self):
        self.H=  np.dot(self.Ur,self.Ur.T)
        self.P=  np.dot(self.Cr.T,self.Cr)
    
    def refine(self,mat):                  #apply constrain on composition
        """matrice riga in cui una componente lungo il set
        """
        

            
        if self.use_constrain:
            for item in self.constrains_list:
                if item.use:
                    if item.c_type=="=":
                      mat[item.compo,item.position]=item.value
                    elif item.c_type==">":
                      if mat[item.compo,item.position] > item.value: pass
                      else: mat[item.compo,item.position]=item.value
                    elif item.c_type=="<":
                      if mat[item.compo,item.position] < item.value: pass
                      else: mat[item.compo,item.position]=item.value 
        
                
        if False:     # MARCOS METHOD
            for i in range(mat.shape[0]):
                Imax=mat[i,:].max()
                armax=mat[i,:].argmax()
                ars,=np.where(mat[i,:]<.01*Imax)
                low,high =0,mat[i,:].shape[0]             
                try: low=ars[ars<armax][-1]+1
                except: pass
                try: high=ars[ars>armax][0]
                except: pass
                
                mat[i,:low]=0
                mat[i,high:]=0
            pass
        pass


        if self.use_monotonicity:
            armax=np.argmax(mat,1)
            Imax=np.amax(mat,1)
            for i in range(mat.shape[0]):
                gra=mat[i,:armax[i]]-mat[i,1:armax[i]+1]
                mat[i,:armax[i]]=  np.where(gra<0, mat[i,:armax[i]] ,mat[i,1:armax[i]+1])
                
                gra=mat[i,armax[i]+1:]-mat[i,armax[i]:-1]
                mat[i,armax[i]+1:]=np.where(gra<0, mat[i,armax[i]+1:], mat[i,armax[i]:-1])      
            pass
        pass
 

    
    
        mat=np.where(mat<0,0,mat)
        mat=np.where(mat>1,1,mat)
        return mat


    def ITTFA(self):
        """
        take care in this version the Needle matrix is evolutive????
        create matrix
        self.Cr_t= true component
        self.Rr_t= true loading after iteraction
        """
        def norm_C(C, norma=1):
            nor=np.tile(np.sum(C,0),(C.shape[0],1))
            return norma*C/nor
        def fuzzy(C,norm): 
            C=norm_C(C, norm)
            return C+(1-norm)*np.random.rand(*C.shape)
            
            

        old_one=self.Needle
        conv = lambda :np.abs((self.Needle-old_one)).max()            
                    
        lim_con=np.amax(self.Cr_rot)*1E-4
      

        i=0
        j=0
        #while True:
        while True: 
            while True:
                #old_one_d =conv()
                i+=1
                old_one=self.Needle
                self.Needle=np.dot(self.Needle,self.P)       #cycle 
                self.Needle=self.refine(self.Needle)         #impose constrain
                if conv()<lim_con:
                    print "out 1, iteration" ,i
                    print "criteria", conv(), "limit", lim_con
                    break
                if i>1001:  
                    print "criteria", conv(), "limit", lim_con
                    print "error convergence not reached after 1000 cycles"
                    break
                pass    
            j+=1   
            print j
            if np.amax(np.fabs(self.Needle-norm_C(self.Needle)))<0.01:
                self.Needle=norm_C(self.Needle)
                break
            if j>3:
                    print "normalization criteria not reached ",np.amax(np.fabs(self.Needle-norm_C(self.Needle)))
                    print "error convergence not reached after 1000 cycles"
                    break
            else:
                self.Needle=norm_C(self.Needle)
                self.Needle=self.refine(self.Needle)  
                print self.Needle-norm_C(self.Needle)
                
        pass    
            #if abs(1-np.average(np.sum(self.Needle,0)))>0.001:
            #    magic_n= lambda :np.average(np.sum(self.Needle,0))
            #    print "prenormalization", magic_n(),"\n"
            #    self.Needle/=magic_n()
            #    self.Needle=fuzzy(self.Needle,.90)
            #else: 
            #    break
        #pass
                
        self.Cr_t=self.Needle
        print "\nnormalization done"
        self.Cr_t=norm_C(self.Cr_t)
        
        # calculation of R matrix
        T=np.dot(self.Cr_t,self.Cr.T)
        self.Rr_t=np.dot(self.Rr, np.linalg.inv(T))
        return   
    






################################################################################
################################################################################
class IND_FUN():
    """
        a class for store and compute indicator function 
        as input the data n_spectra X n_points 
    """
    def __init__(self,n_col,n_row,eigenvalue):
        self.n_col      =  n_col
        self.n_row      =  n_row
        self.V =  eigenvalue
        self.__ind_fun__()
        self.__ss__()
       
                               
    def __ind_fun__(self):
        """calculate the f function and 
           function IND from Malinowsky  
           look at http://www.vub.ac.be/fabi/multi/pcr/pages/framemenu.html
           http://onlinelibrary.wiley.com/doi/10.1002/cem.1191/pdf
           self.cumVp = cumulative variance
           self.RE  = real error
           self.REV = reduced eigenvalues
           self.IND = malinowsky IND factor
           self.F   = malinowsky F test
        """
        self.cumVp = (np.cumsum(self.V)/np.sum(self.V))*100.000          
        
        #RcumV =np.flipud(np.cumsum(np.flipud(self.V))) 
        RcumV =np.cumsum(self.V[::-1])[::-1]
        r=np.arange(self.n_col)+1
        
        #Calculate RE and IND function
        #print "\n",RcumV[0:8]
                       
        self.RE=np.sqrt((RcumV[1:])/(self.n_row*(self.n_col-r[:-1])))
        IND=self.RE/(self.n_col-np.arange(1,self.n_col))**2
        self.IND=np.append(IND,0)  
        self.RE=np.append(self.RE,0)
        #IND(n_col=0)
        
        self.REV=(self.V)/((self.n_col-r+1)*(self.n_row-r+1))
        
        sumLow = np.flipud(np.cumsum(np.flipud((self.n_col-r+1)*(self.n_row-r+1))))
        #print sumLow.shape, self.cumV.shape
        self.F= self.REV[:-1]*(sumLow[1:])/(RcumV[1:])

        #MAD calculation
        def MADtest(x):
            MADx = np.median(np.abs(x - np.median(x)))
            test = (np.abs(x[0] - np.median(x)))/MADx if MADx>0 else 1
            return  True if test > 5 else False  
        n=np.arange(self.n_col)
        self.RSD = np.sqrt(RcumV/((self.n_row-n) * (self.n_col-n)))
        self.MAD= [MADtest(self.RSD[i:]) for i in n]
        self.RDS0=self.RSD[0]
        self.RSD, self.MAD=self.RSD[1:],self.MAD[1:]
        self.RSD =np.append(self.RSD, 0.0)
        self.MAD.append(np.NaN)   
        
        
        
        

        
    def __ss__(self):
        """
           self.SS  f (see eq. 4.83) Converted  into percent significance level 
        """  
        n_col =self.n_col if self.n_row>self.n_col else self.n_row
        self.SS=np.zeros(n_col)
        for j in range(1,n_col):                              #% Convert f (see eq. 4.83) into percent significance level 
            df=n_col-j                                        #%second degree fo freedom
            a=np.sqrt(self.F[j-1])/np.sqrt(df) 
            b=df/(df+self.F[j-1]) 
            jm= 1. if df%2 else 0.                                 #%1 if  df odd else 0  aka J
            n=(df-2)//2
            #print j,round(a,4),round(b,4),jm 
            cc = lambda n : cc(n-1)*(b*(fk(n)-1)/fk(n)) if n>0 else 1 
            ss = lambda n : ss(n-1)+cc(n) if n>0 else 1  
            fk = lambda n : jm+2*n 
            #print j,n,round(ss(n),4), fk(n)
            if jm<=0:                                           #% J even
                cl=.5+.5*a*np.sqrt(b)*ss(n) 
            elif (df-1)>0:                                      #%C-J>1
                cl=.5+(a*b*ss(n)+np.arctan(a))*.31831             
            else :                                              #%C-J=1
                cl=.5+np.arctan(a)*.31831 

            sl=100*(1-cl) 
            sl=2*sl 
            self.SS[j-1]=sl
            #print j,round(cl,4), self.SS[j-1]            
        self.SS[-1]=0

################################################################################
################################################################################
class  CONSTRAIN():
    def __init__(self, use, compo, c_type, value, position):
        self.use=use
        self.compo=compo
        self.c_type= c_type
        self.value=value
        self.position=position

#def pca(D):
 #    """do pca on a set of data n_spectra X n_points 
 #       return a matrix of autovector 
 #       and a set of autovalori
 #    """    
 #    Z=np.dot(D.transpose(),D)
 #    V,Q=np.linalg.eigh(Z, UPLO="U")   #fatto con la diagonalizzazione
 #    #print "Q", Q.shape
 #    R=np.dot(D,Q)
 #    #print "R",R.shape
 #    if V[-1]>V[0]:
 #        C=np.flipud(Q.T)
 #        R=np.fliplr(R) 
 #        V=V[::-1]
 #    #print "C",C.shape
 #    return C,R,V
 
 
 #sumV/= sumV[-1]
#
