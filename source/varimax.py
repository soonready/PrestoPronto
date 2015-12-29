#Varimax matrix rotation
#Coded in Python by Carmelo Prestipino in 2011 
#Adapted from MATLAB code 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#%
#% 	$Id: varimax.m 685 2008-10-30 15:46:09Z dmk $	
#%
#% Copyright (C) 2002 David M. Kaplan
#% Licence: GPL
#%
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#VARIMAX  Rotate EOF's according to varimax algorithm
#
#This is actually a generic varimax routine and knows nothing special about
#EOFs.  It expects a matrix of "loadings".  Typically (in state space
#rotation), these loadings are the expansion coefficients (aka Principal
#Component Time Series) for the truncated basis of eigenvectors (EOFs), but
#they could also be the EOFs*diag(L)^(1/2) (in the case of rotation in
#sample space).  See below for equations defining these matrices.
#
#Usage: [new_loads, R] = varimax( loadings, normalize, tolerance, max_it )
#
#where all but the loadings are optional.  The loadings is a matrix with
#more rows than columns (typically, one column for each EOF).  R is the
#rotation matrix used to generate the new loadings.
#
#normalize determines whether or not to normalize the rows or columns of
#the loadings before performing the rotation.  If normalize is true, then
#the rows are normalized by there individual vector lengths.  Otherwise, no
#normalization is performed (default).  After rotation, the matrix is
#renormalized. Normalizing over the rows corresponds to the Kaiser
#normalization often used in factor analysis.
#
#tolerance defaults to 1e-10 if not given.  max_it specifies the maximum
#number of iterations to do - defaults to 1000.
#
#After the varimax rotation is performed, the new EOFs (in the case that
#the EC's were rotated - state space) can be found by new_EOFs =
#EOFs*R.
#
#Definitions of matrices mentioned above:
#
#Z = ECs * (EOFs)'       # where ' stands for matrix transpose
#(EOFs)' * EOFs = I      # where I is the identity matrix
#(ECs)' * ECs = L        # where L is diagonal
#
#In state space rotation, we have the following definitions:
#
#ECs = loadings
#new_loads = new_ECs = ECs * R
#new_EOFs = EOFs * R
#
#This function is derived from the R function varimax in the mva
#library.    
#  slygh arrangemnt ...
#import numpy as np
from numpy import dot, ones, diag, tile, sqrt, eye
import numpy.linalg as linalg


def varimax( x, normalize=True, positive=True, tol=1e-10, max_it=1000): #
    if len(x.shape)!=2:
        raise ValueError, 'AMAT must be 2-dimensional'
    elif len(x.shape)==2:     
        p,nc= x.shape
        if normalize:
            rl = tile(sqrt(diag(dot(x,x.T))), (nc,1) ).T#; % By rows.l = repmat( sqrt(diag( x*x' )), [1,nc] ); % By rows.
            x = x/rl
    TT = eye(nc)
    d=0
    
    for i in range(max_it):
        z = dot(x,TT)
        c0=dot(ones((1,p)),(z**2))
        c1=diag(c0.squeeze())/p
        c3= z**3 - dot(z,c1)
        B= dot(x.T,c3)
        U,S,V= linalg.svd(B,full_matrices=True)
        
        TT = dot(U,V)
        
        d2 = d
        d= sum(S)
        if d< d2*(1+tol): 
            print "varimax done in ", i , " iteration"  
            break

    x= dot(x,TT)
    
    if positive:
        for i,item in enumerate(x.T):                      #I taker each column and I test if is sum positive
            if sum(item) < 0:                              #if not i multiplie it for -1
                x[:,i] =  -1*item 
                TT[:,i] = -1*TT[:,i]

    return x,TT


